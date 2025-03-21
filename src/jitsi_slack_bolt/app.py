import os
import logging

from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix

from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics

from slack_bolt import App as BoltApp
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.oauth.callback_options import CallbackOptions
from slack_bolt.oauth.oauth_flow import SuccessArgs, FailureArgs
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_bolt.response import BoltResponse

from listeners import register_listeners
from util.store import InMemoryStorageProvider, WorkspaceStore
from util.vault import VaultStorageProvider
from util.config import JitsiConfiguration, StorageType
from util.config import when_ready, child_exit
from util.slack_store import WorkspaceInstallationStore
from util.postgres import PostgresStorageProvider

# bolt callbacks
def success(args: SuccessArgs) -> BoltResponse:
    return args.default.success(args)

def failure(args: FailureArgs) -> BoltResponse:
    return BoltResponse(status=args.suggested_status_code, body=args.reason)

from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics

# gunicorn callbacks
def when_ready(server):
    GunicornPrometheusMetrics.start_http_server_when_ready(8000)

def child_exit(server, worker):
    GunicornPrometheusMetrics.mark_process_dead_on_child_exit(worker.pid) 

class JitsiSlackApp:
    def __init__(self):
        # load configuration from environment
        self.config = JitsiConfiguration.from_env()

        logging.basicConfig(level=getattr(logging, self.config.debug_level))
        self.logger = logging.getLogger("jitsi-slack")
        self.logger.info("starting jitsi-slack")

        self.logger.info(
            f"initializing workspace store with default server: {self.config.default_server}"
        )
        self.workspace_store = WorkspaceStore()
        self.workspace_store.set_workspace_server_url("default", self.config.default_server)

        self.logger.info(f"initializing bolt app in {self.config.slack_app_mode} mode")
        if self.config.slack_app_mode == "socket":
            self.bolt_app = BoltApp(token=os.environ.get("SLACK_BOT_TOKEN"))
        elif self.config.slack_app_mode == "oauth":
            self.bolt_app = BoltApp(
                signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
                installation_store=WorkspaceInstallationStore(self.workspace_store),
                oauth_settings=OAuthSettings(
                    client_id=os.environ.get("SLACK_CLIENT_ID"),
                    client_secret=os.environ.get("SLACK_CLIENT_SECRET"),
                    scopes=["chat:write", "commands", "im:write", "users:read"],
                    user_scopes=[],
                    redirect_uri=None,
                    state_store=WorkspaceInstallationStore(self.workspace_store),
                    state_validation_enabled=False,  # TODO: seems needed for install from link?
                    callback_options=CallbackOptions(success=success, failure=failure),
                ),
            )

        @self.bolt_app.middleware
        def log_request(logger, body, next):
            logger.debug(body)
            return next()

        @self.bolt_app.event("app_uninstalled")
        def handle_app_uninstalled(event, logger):
            if "team_id" not in event:
                logger.warn(f"app_uninstalled event missing team_id: {event}")
            else:
                logger.info(f"App uninstalled from workspace {event['team_id']}")
                self.workspace_store.delete_workspace(event["team_id"])

        @self.bolt_app.event("tokens_revoked")
        def handle_tokens_revoked(event, logger):
            if "team_id" not in event:
                logger.warn(f"tokens_revoked event missing team_id: {event}")
            else:
                logger.info(f"Tokens revoked for workspace {event['team_id']}")
                self.workspace_store.delete_workspace(event["team_id"])

        self.logger.info(f"registering bolt listeners for {self.config.slash_cmd}")
        register_listeners(
            self.bolt_app, self.workspace_store, self.config.default_server, self.config.slash_cmd
        )

        if self.config.slack_app_mode == "oauth":
            self.init_flask_app()

        # initializes the app's data storage provider
        if self.config.data_store_provider == StorageType.MEMORY:
            self.logger.info("initializing memory storage provider")
            self.workspace_store.set_provider(InMemoryStorageProvider())
        elif self.config.data_store_provider == StorageType.VAULT:
            self.logger.info("initializing vault storage provider")
            self.workspace_store.set_provider(
                VaultStorageProvider(
                    url=self.config.vault_url,
                    token=self.config.vault_token,
                    mount_point=self.config.vault_mount_point,
                    path_prefix=self.config.vault_path_prefix,
                )
            )
        elif self.config.data_store_provider == StorageType.POSTGRES:
            self.logger.info("initializing postgres storage provider")
            self.workspace_store.set_provider(
                PostgresStorageProvider(
                    host=self.config.db_host,
                    ip=self.config.db_ip,
                    port=self.config.db_port,
                    username=self.config.db_username,
                    password=self.config.db_password,
                    database_name=self.config.db_name,
                )
            )
        else:
            raise ValueError(f"Invalid storage provider: {self.config.data_store_provider}")

        self.logger.info("jitsi-slack is ready to go!")

    def init_flask_app(self):
        self.logger.info("setting up flask")
        self.flask_app = Flask(__name__)
        self.flask_handler = SlackRequestHandler(self.bolt_app)
        self.metrics = GunicornPrometheusMetrics(self.flask_app)

        @self.flask_app.route("/slack/events", methods=["POST"])
        def slack_events():
            self.logger.debug(f"received event {request}")
            return self.flask_handler.handle(request)

        # TODO: does this actually get called or does it go through oauth_redirect?
        @self.flask_app.route("/slack/install", methods=["GET"])
        def install():
            self.logger.debug(f"received install {request}")
            return self.flask_handler.handle(request)

        @self.flask_app.route("/slack/oauth_redirect", methods=["GET"])
        def oauth_redirect():
            self.logger.debug(f"received oauth redirect {request}")
            return self.flask_handler.handle(request)

        @self.flask_app.route("/health", methods=["GET"])
        @self.metrics.do_not_track()
        def health():
            self.logger.debug("health check")
            return "OK"

        if self.config.proxy_mode == "true":
            self.flask_app.wsgi_app = ProxyFix(
                self.flask_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
            )

    def get_flask_app(self):
        return self.flask_app

    def start(self):
        if self.config.slack_app_mode == "socket":
            SocketModeHandler(self.bolt_app, os.environ["SLACK_APP_TOKEN"]).start()
        elif self.config.slack_app_mode == "oauth":
            self.flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
            # self.bolt_app.start(3000)
        else:
            raise ValueError(f"Invalid Slack app mode: {self.config.slack_app_mode}")


jitsi_slack_app = JitsiSlackApp()
if jitsi_slack_app.config.slack_app_mode == "oauth":
    app = jitsi_slack_app.get_flask_app()


if __name__ == "__main__":
    jitsi_slack_app.start()

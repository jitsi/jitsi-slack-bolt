import os
import logging

from flask import Flask, request

from slack_bolt import App as BoltApp, BoltResponse
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_bolt.oauth.callback_options import CallbackOptions, SuccessArgs, FailureArgs
from slack_bolt.oauth.oauth_settings import OAuthSettings

from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore

from listeners import register_listeners
from util.store import InMemoryStorageProvider, WorkspaceStore
from util.vault import VaultStorageProvider
from util.config import JitsiConfiguration, StorageType
from util.slack_store import WorkspaceInstallationStore


def success(args: SuccessArgs) -> BoltResponse:
    # Do anything here ...
    # Call the default handler to return HTTP response
    return args.default.success(args)
    # return BoltResponse(status=200, body="Thanks!")

def failure(args: FailureArgs) -> BoltResponse:
    return BoltResponse(status=args.suggested_status_code, body=args.reason)


class JitsiSlackApp:
    def __init__(self):
        # load configuration from environment
        self.config = JitsiConfiguration.from_env()

        # set up logging
        logging.basicConfig(level=getattr(logging, self.config.debug_level))
        logger = logging.getLogger("jitsi-slack")
        logger.info("starting jitsi-slack")

        # initialize workspace store
        logger.info(f"initializing workspace store with default server: {self.config.default_server}")
        self.workspace_store = WorkspaceStore()
        self.workspace_store.set_workspace_server_url("default", self.config.default_server)

        logger.info("initializing bolt app")
        if self.config.slack_app_mode == "socket":
            self.bolt_app = BoltApp(token=os.environ.get("SLACK_BOT_TOKEN"))
        elif self.config.slack_app_mode == "oauth":
            self.bolt_app = BoltApp(
                signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
                installation_store=WorkspaceInstallationStore(self.workspace_store),
                oauth_settings=OAuthSettings(
                    client_id=os.environ.get("SLACK_CLIENT_ID"),
                    client_secret=os.environ.get("SLACK_CLIENT_SECRET"),
                    scopes=["chat:write", "commands", "im:write", "mpim:write", "users:read"],
                    user_scopes=[],
                    redirect_uri=None,
                    state_store=FileOAuthStateStore(expiration_seconds=600),
                    callback_options=CallbackOptions(success=success, failure=failure),
                )
            )

        @self.bolt_app.middleware
        def log_request(logger, body, next):
            logger.info(body)
            return next()

        @self.bolt_app.event("app_mention")
        def event_test(body, say, logger):
            logger.info(body)
            say("What's up?")

        @self.bolt_app.event("message")
        def handle_message():
            pass

        logger.info("registering bolt listeners")
        register_listeners(self.bolt_app, self.workspace_store, self.config.default_server, self.config.slash_cmd)

        logger.info("setting up flask")
        self.flask_app = Flask(__name__)
        self.flask_handler = SlackRequestHandler(self.bolt_app)

        @self.flask_app.route("/slack/events", methods=["POST"])
        def slack_events():
            return self.flask_handler.handle(request)

        @self.flask_app.route("/slack/install", methods=["GET"])
        def install():
            return self.flask_andler.handle(request)

        @self.flask_app.route("/slack/oauth_redirect", methods=["GET"])
        def oauth_redirect():
            return self.flask_handler.handle(request)

        @self.flask_app.route("/health", methods=["GET"])
        def health():
            return "OK"

        # initializes the app's data storage provider
        if self.config.data_store_provider == StorageType.MEMORY:
            logger.info("initializing memory storage provider")
            self.workspace_store.set_provider(InMemoryStorageProvider())
        elif self.config.data_store_provider == StorageType.VAULT:
            logger.info("initializing vault storage provider")
            self.workspace_store.set_provider(
                VaultStorageProvider(
                    url=self.config.vault_url,
                    token=self.config.vault_token,
                    mount_point=self.config.vault_mount_point,
                    path_prefix=self.config.vault_path_prefix,
                )
            )
        else:
            raise ValueError(f"Invalid storage provider: {self.config.data_store_provider}")
        
        logger.info ("jitsi-slack is ready to go!")


    def start(self):
        if self.config.slack_app_mode == "socket":
            SocketModeHandler(self.bolt_app, os.environ["SLACK_APP_TOKEN"]).start()
        elif self.config.slack_app_mode == "oauth":
            self.flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))
            #self.bolt_app.start(3000)
        else:
            raise ValueError(f"Invalid Slack app mode: {self.config.slack_app_mode}")


if __name__ == "__main__":
    app = JitsiSlackApp()
    app.start()

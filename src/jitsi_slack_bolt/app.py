import os
import logging

from slack_bolt import App as BoltApp
from slack_bolt.adapter.socket_mode import SocketModeHandler

from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.oauth_settings import OAuthSettings

from listeners import register_listeners
from util.store import InMemoryStorageProvider, WorkspaceStore
from util.vault import VaultStorageProvider
from util.config import JitsiConfiguration, StorageType
from util.slack_store import WorkspaceInstallationStore


class JitsiSlackApp:
    def __init__(self):
        # load configuration from environment
        self.config = JitsiConfiguration.from_env()

        # set up logging
        logging.basicConfig(level=getattr(logging, self.config.debug_level))
        logger = logging.getLogger("jitsi-slack")
        logger.info("starting jitsi-slack")

        # initialize workspace store
        self.workspace_store = WorkspaceStore()

        logger.info("initializing bolt app")
        if self.config.slack_app_mode == "socket":
            self.bolt_app = BoltApp(token=os.environ.get("SLACK_BOT_TOKEN"))
        elif self.config.slack_app_mode == "oauth":
            self.bolt_app = BoltApp(
                signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
                installation_store = WorkspaceInstallationStore(self.workspace_store)
                oauth_settings=OAuthSettings(
                    client_id=os.environ.get("SLACK_CLIENT_ID"),
                    client_secret=os.environ.get("SLACK_CLIENT_SECRET"),
                    scopes=["chat:write", "commands", "im:write", "mpim:write", "users:read"],
                    user_scopes=[],
                    redirect_uri=None,
                    state_store=FileOauthStateStore(expiration_seconds=600),
                    callback_options=CallbackOptions(success=success, failure=failure),
                )
            )

        logger.info("registering listeners")
        register_listeners(self.bolt_app, self.workspace_store, self.config.default_server, self.config.slash_cmd)

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

        logger.info(f"setting default server to {self.config.default_server}")
        self.workspace_store.set_workspace_server_url("default", self.config.default_server)
        
        logger.info ("jitsi-slack is ready to go!")

    def start(self):
        if self.config.slack_app_mode == "socket":
            SocketModeHandler(self.bolt_app, os.environ["SLACK_APP_TOKEN"]).start()
        elif self.config.slack_app_mode == "oauth":
            self.bolt_app.start(3000)
        else:
            raise ValueError(f"Invalid Slack app mode: {self.config.slack_app_mode}")

if __name__ == "__main__":
    app = JitsiSlackApp()
    app.start()

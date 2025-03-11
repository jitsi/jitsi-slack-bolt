import os
import logging
from slack_bolt import App as BoltApp
from slack_bolt.adapter.socket_mode import SocketModeHandler

from listeners import register_listeners
from logging import getLogger 
from util.store import InMemoryStorageProvider, WorkspaceStore
from util.vault import VaultStorageProvider
from util.config import JitsiConfiguration, StorageType


class JitsiSlackApp:
    def __init__(self):
        # Load configuration from environment
        self.config = JitsiConfiguration.from_env()

        # Set up logging
        logging.basicConfig(level=getattr(logging, self.config.debug_level))

        logger = getLogger("jitsi-slack")
        logger.info("starting jitsi-slack")

        self.workspace_store = WorkspaceStore()

        logger.info("initializing bolt app")
        self.bolt_app = BoltApp(token=os.environ.get("SLACK_BOT_TOKEN"))
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
        """Start the Slack Bolt app in socket mode."""
        SocketModeHandler(self.bolt_app, os.environ["SLACK_APP_TOKEN"]).start()


# next step will be to do OAUTH or socket mode and keep this in one file


if __name__ == "__main__":
    app = JitsiSlackApp()
    app.start()

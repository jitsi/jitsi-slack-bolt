from slack_bolt import App
from .jitsi_command import jitsi_callback
from jitsi_slack_bolt.util.store import WorkspaceStore

def register_listeners(app: App, workspace_store: WorkspaceStore, default_server: str):
    """Register all command listeners with the Bolt app."""
    app.command("/jitsi-test")(
        lambda ack, client, command, logger, respond: (
            jitsi_callback(ack, client, command, default_server, logger, respond, workspace_store)
        )
    )
    
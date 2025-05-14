from slack_bolt import App
from .jitsi_command import jitsi_callback


def register_listeners(app: App, slash_cmd: str):
    """Register all command listeners with the Bolt app."""
    app.command(slash_cmd)(
        lambda ack, client, command, logger, respond: (
            jitsi_callback(ack, client, command, logger, respond)
        )
    )

    app.action("join_button")(lambda ack: (ack()))

from slack_bolt import App
from .jitsi_command import jitsi_callback


def register_listeners(app: App):
    app.command("/jitsi-test")(jitsi_callback)

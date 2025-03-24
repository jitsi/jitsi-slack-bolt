"""
A Slack command handler for the /jitsi command that manages Jitsi room creation
and server configuration.

The module provides functionality to:
- Create Jitsi rooms
- Set and view default Jitsi servers for Slack workspaces
- Send direct messages to users with Jitsi room links

Commands:
  /jitsi : Creates a Jitsi room with a random name
  /jitsi server : Shows current server configuration for the workspace
  /jitsi server default : Resets server to default - https://meet.jit.si/
  /jitsi server <url> : Sets custom server URL for the workspace
  /jitsi @<user> : Creates a Jitsi room and sends it via DM

Dependencies:
  - slack_bolt
  - slack_sdk
  - logging
"""

from slack_bolt import Ack, Respond
from logging import Logger
from slack_sdk import WebClient

from jitsi_slack_bolt.util.store import WorkspaceStore
from jitsi_slack_bolt.listeners.jitsi_handlers import (
    slash_jitsi,
    slash_jitsi_server,
    slash_jitsi_dm,
    slash_jitsi_help,
)


def jitsi_callback(
    ack: Ack,
    client: WebClient,
    command: dict[str, any],
    default_server: str,
    logger: Logger,
    respond: Respond,
    workspace_store: WorkspaceStore,
):
    ack()

    if command["text"].startswith("server"):
        slash_jitsi_server(command, logger, respond, workspace_store)
    elif command["text"].startswith("@"):
        slash_jitsi_dm(client, command, logger, respond, workspace_store)
    elif command["text"].startswith("help"):
        slash_jitsi_help(respond)
    else:
        slash_jitsi(command, logger, respond, workspace_store)

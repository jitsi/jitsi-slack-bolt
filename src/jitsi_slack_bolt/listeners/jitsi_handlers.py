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

from slack_bolt import Respond
from logging import Logger
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler
from ..util.store import WorkspaceStore
from jitsi_slack_bolt.util.room_name import generate_room_name
from urllib.parse import urlparse, urljoin


def build_room_url(
    command: dict[str, any], workspace_store: WorkspaceStore, default_server: str
) -> str:
    server_url = workspace_store.get_workspace_server_url(command["team_id"], default_server)
    room_name = generate_room_name()
    room_url = f"{server_url}{room_name}"
    return f"{room_url}"


def slash_jitsi(
    command: dict[str, any],
    logger: Logger,
    respond: Respond,
    workspace_store: WorkspaceStore,
    default_server: str,
):
    """base slash command that creates a randomly generated Jitsi room name in the server's path"""

    room_url = build_room_url(command, workspace_store, default_server)
    respond(
        {
            "attachments": [
                {
                    "fallback": f"Jitsi meeting started at: {room_url}",
                    "title": f"Jitsi meeting started at: {room_url}",
                    "color": "#3AA3E3",
                    "attachment_type": "default",
                    "actions": [
                        {
                            "name": "join",
                            "text": "Join",
                            "type": "button",
                            "url": f"{room_url}",
                            "style": "primary",
                        }
                    ],
                }
            ]
        }
    )


def slash_jitsi_server(
    command: dict[str, any],
    logger: Logger,
    respond: Respond,
    workspace_store: WorkspaceStore,
    default_server: str,
):
    """slash command that sets or views the Jitsi server for the workspace"""
    decomp = command["text"].split(" ")

    if len(decomp) == 1:
        server_url = workspace_store.get_workspace_server_url(command["team_id"], default_server)
        respond(f"Your team's conferences are hosted at: {server_url}")
        return

    if len(decomp) == 2:
        if decomp[1] == "default":
            workspace_store.set_workspace_server_url(command["team_id"], default_server)
            respond(f"Your team's conference URL has been set to the default: ({default_server})")
            return
        else:
            parsed_url = urlparse(decomp[1])
            if not parsed_url.scheme or not parsed_url.netloc:
                respond(
                    f"Invalid format for a server URL. {parsed_url} must include scheme (e.g., https://) and hostname"
                )
                return
            url = urljoin(decomp[1], "/")
            workspace_store.set_workspace_server_url(command["team_id"], url)
            respond(f"Your team's conferences will be hosted at: {url}")
            return
    respond("usage: /jitsi server [default|<server>]")


def slash_jitsi_dm(
    client: WebClient,
    command: dict[str, any],
    logger: Logger,
    respond: Respond,
    workspace_store: WorkspaceStore,
    default_server: str,
):
    """slash command that creates a Jitsi room and sends it via DM to the specified user(s)"""
    user_ids = []
    usernames_to_dm = command["text"].split()

    # get workspace user list from slack (no way to look up a uid by name)
    # rate-limited to ~ 20 requests per minute so we add a retry handler to the client
    try:
        rate_limit_handler = RateLimitErrorRetryHandler(max_retry_count=6)
        client.retry_handlers.append(rate_limit_handler)
        ulist = client.users_list()
    except SlackApiError as e:
        logger.error(e)
        respond("Error setting up DM, please try again later.")
        return

    for user in ulist["members"]:
        if "@" + user["name"] in usernames_to_dm:
            user_ids.append(user["id"])

    try:
        resp = client.conversations_open(users=user_ids)
    except SlackApiError as e:
        logger.error(e)
        respond("Error setting up DM, please try again later.")
        return

    try:
        room_url = build_room_url(command, workspace_store, default_server)
        logger.info(f"{command}")
        resp = client.chat_postMessage(
            channel=resp["channel"]["id"],
            attachments=[
                {
                    "fallback": f"<@{command['user_name']}> would like you to join a Jitsi meeting at: {room_url}",
                    "text": f"<@{command['user_name']}> would like you to join a Jitsi meeting at: {room_url}",
                    "color": "#3AA3E3",
                    "actions": [
                        {
                            "name": "join",
                            "text": "Join",
                            "type": "button",
                            "url": f"{room_url}",
                            "style": "primary",
                        }
                    ],
                }
            ],
        )

    except SlackApiError as e:
        logger.error(e)
        respond("Error sending message, please try again.")
        return


def slash_jitsi_help(respond: Respond):
    """slash command that provides help for the /jitsi command"""
    respond(
        "How to use /jitsi:\n"
        + "`/jitsi` creates a new conference link in the current channel.\n"
        + "`/jitsi [@user1 @user2 ...]` will send direct messages to user1 and user2 to join a new conference.\n"
        + "`/jitsi server default` will set the server used for conferences to the default.\n"
        + "`/jitsi server https://foo.com/` will set the server used for conferences to https://foo.com/. You can use your own jitsi server."
    )

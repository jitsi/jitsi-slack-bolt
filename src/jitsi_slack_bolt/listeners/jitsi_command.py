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
from slack_sdk.errors import SlackApiError
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler

from jitsi_slack_bolt.util.room_name import generate_room_name


def slash_jitsi(respond):
    """base slash command that creates a randomly generated Jitsi room name in the server's path"""

    server_url = "https://meet.jit.si/"
    room_name = generate_room_name()
    room_url = f"{server_url}{room_name}"
    # TODO: pretty message
    respond(f"TODO: this will make a jitsi link to: {room_url}")


def slash_jitsi_server(command, respond):
    """slash command that sets or views the Jitsi server for the workspace"""
    decomp = command["text"].split(" ")

    if len(decomp) == 1:
        respond(
            "this should state the configured server for this workspace, or default server if there is none"
        )
        return

    if len(decomp) == 2:
        if decomp[1] == "default":
            respond("this will set the workspace server to default")
            return
        else:
            # check to make sure this is a url, fall out if it is not one
            respond(f"this will set the workspace server to {decomp[1]}")
            return
    respond("usage: /jitsi server [default|<server>]")


def slash_jitsi_dm(client: WebClient, command: dict[str, any], logger: Logger, respond: Respond):
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
        respond(f"error getting user list {e}")
        return

    for user in ulist["members"]:
        if "@" + user["name"] in usernames_to_dm:
            user_ids.append(user["id"])

    try:
        resp = client.conversations_open(users=user_ids)
    except SlackApiError as e:
        logger.error(e)
        respond(f"error opening conversation {e}")
        return

    try:
        resp = client.chat_postMessage(
            channel=resp["channel"]["id"],
            text="please let scott know you got this test DM :)",
        )
    except SlackApiError as e:
        logger.error(e)
        respond(f"error sending message {e}")
        return


def jitsi_callback(
    client: WebClient,
    ack: Ack,
    command: dict[str, any],
    logger: Logger,
    respond: Respond,
):
    ack()

    if command["text"].startswith("server"):
        slash_jitsi_server(command, respond)
    elif command["text"].startswith("@"):
        slash_jitsi_dm(client, command, logger, respond)
    else:
        # fall through to slash command if not 'server' or a @user
        slash_jitsi(respond)

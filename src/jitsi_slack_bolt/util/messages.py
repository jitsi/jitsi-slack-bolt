"""
Message block utilities for building Slack messages.

This module provides functions to create message blocks for Slack messages
used throughout the Jitsi Slack integration.
"""

from typing import Dict, Any, List


def build_help_message_blocks(slash_cmd: str, default_server_url: str) -> List[Dict[str, Any]]:
    """
    Build a Slack help message with rich text blocks showing available commands.

    Args:
        slash_cmd: The slash command name (e.g. "/jitsi")
        default_server_url: The default Jitsi server URL

    Returns:
        List of Slack message blocks containing formatted help information
    """
    return [
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": f"Welcome to the {slash_cmd} bot! Here's what you can do:",
                            "style": {
                                "bold": True,
                            },
                        }
                    ],
                },
                {
                    "type": "rich_text_list",
                    "style": "bullet",
                    "elements": [
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "style": {"code": True},
                                    "text": f"{slash_cmd}",
                                },
                                {
                                    "type": "text",
                                    "text": " creates a new conference link in the current channel using a randomized room name",
                                },
                            ],
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "style": {
                                        "code": True,
                                    },
                                    "text": f"{slash_cmd} <room_name>",
                                },
                                {
                                    "type": "text",
                                    "text": " creates a new conference link in the current channel with the specified room name",
                                },
                            ],
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "style": {
                                        "code": True,
                                    },
                                    "text": f"{slash_cmd} [@user1 @user2 ...]",
                                },
                                {
                                    "type": "text",
                                    "text": " sends direct messages to user1 and user2 to join a new conference.",
                                },
                            ],
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "style": {
                                        "code": True,
                                    },
                                    "text": f"{slash_cmd} server",
                                },
                                {
                                    "type": "text",
                                    "text": " shows the current server used for conferences.",
                                },
                            ],
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "style": {
                                        "code": True,
                                    },
                                    "text": f"{slash_cmd} server <url>",
                                },
                                {
                                    "type": "text",
                                    "text": " sets the server used for conferences to the specified URL, which may include a path.",
                                },
                            ],
                        },
                        {
                            "type": "rich_text_section",
                            "elements": [
                                {
                                    "type": "text",
                                    "style": {
                                        "code": True,
                                    },
                                    "text": f"{slash_cmd} server default",
                                },
                                {
                                    "type": "text",
                                    "text": f" will set the server URL used for conferences to the default ({default_server_url}).",
                                },
                            ],
                        },
                    ],
                },
            ],
        }
    ]


def build_join_message_blocks(message: str, room_url: str) -> List[Dict[str, Any]]:
    """
    Build a Slack message with blocks containing a message and a join button.

    Args:
        message: The message to display in the block
        room_url: The URL for the Jitsi meeting room

    Returns:
        List of Slack message blocks containing message and join button
    """
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "plain_text",
                "text": f"{message}",
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Click to Join"},
                    "style": "primary",
                    "url": f"{room_url}",
                    "action_id": "join_button",
                }
            ],
        },
    ]
    return blocks

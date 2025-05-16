import pytest
from jitsi_slack_bolt.util import build_join_message_blocks, build_help_message_blocks


class TestMessages:
    """Test the message utilities"""

    def test_build_join_message_blocks(self):
        """Test building message blocks for joining a meeting"""
        # Setup
        message = "Test meeting message"
        room_url = "https://meet.jit.si/test-meeting"

        # Action
        blocks = build_join_message_blocks(message, room_url)

        # Assert
        assert len(blocks) == 2
        assert blocks[0]["type"] == "section"
        assert blocks[0]["text"]["text"] == message
        assert blocks[1]["type"] == "actions"
        assert blocks[1]["elements"][0]["url"] == room_url
        assert blocks[1]["elements"][0]["text"]["text"] == "Click to Join"
        assert blocks[1]["elements"][0]["style"] == "primary"

    def test_build_help_message_blocks(self):
        """Test building help message blocks"""
        # Setup
        slash_cmd = "/jitsi"
        default_server_url = "https://meet.jit.si/"

        # Action
        blocks = build_help_message_blocks(slash_cmd, default_server_url)

        # Assert
        assert len(blocks) == 1
        assert blocks[0]["type"] == "rich_text"

        elements = blocks[0]["elements"]
        # Check header
        assert elements[0]["type"] == "rich_text_section"
        assert elements[0]["elements"][0]["text"].startswith("Welcome to the /jitsi bot!")

        # Check list of commands
        assert elements[1]["type"] == "rich_text_list"
        assert elements[1]["style"] == "bullet"

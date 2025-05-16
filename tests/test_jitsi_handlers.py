import pytest
from unittest.mock import MagicMock, patch
from jitsi_slack_bolt.listeners.jitsi_handlers import (
    build_room_url,
    build_join_message_blocks,
    slash_jitsi,
    slash_jitsi_server,
)


class TestJitsiHandlers:
    """Test the Jitsi handlers functionality"""

    def setup_method(self):
        """Setup for each test method"""
        # Create a mock logger
        self.logger = MagicMock()

        # Create a mock respond function
        self.respond = MagicMock()

        # Default server URL
        self.default_server_url = "https://meet.jit.si/"

        # Create a mock logger
        self.logger = MagicMock()

        # Create a mock respond function
        self.respond = MagicMock()

    def test_build_room_url_with_random_name(self, workspace_store):
        """Test building a room URL with a random name"""
        # Setup
        command = {"team_id": "test_team"}

        # Action
        server_url, room_url = build_room_url(command, workspace_store)

        # Assert
        assert server_url == self.default_server_url
        assert room_url.startswith(self.default_server_url)
        assert len(room_url) > len(self.default_server_url)

    def test_build_room_url_with_custom_room(self, workspace_store):
        """Test building a room URL with a custom room name"""
        # Setup
        command = {"team_id": "test_team"}
        room_str = "my-meeting"

        # Action
        server_url, room_url = build_room_url(command, workspace_store, room_str=room_str)

        # Assert
        assert server_url == self.default_server_url
        assert room_url == f"{self.default_server_url}my-meeting"

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

    def test_slash_jitsi_basic(self, workspace_store, mock_command):
        """Test the basic /jitsi slash command"""
        # Action
        slash_jitsi(mock_command, self.logger, self.respond, workspace_store)

        # Assert
        self.respond.assert_called_once()
        # Check that blocks and response_type were passed
        args, kwargs = self.respond.call_args
        assert "blocks" in kwargs
        assert "response_type" in kwargs
        assert kwargs["response_type"] == "in_channel"

    def test_slash_jitsi_server_view(self, workspace_store, mock_command):
        """Test the /jitsi server command to view current server"""
        # Setup
        command = mock_command.copy()
        command["text"] = "server"
        workspace_store.set_workspace_server_url(command["team_id"], "https://meet.example.com/")

        # Action
        slash_jitsi_server(command, self.logger, self.respond, workspace_store)

        # Assert
        self.respond.assert_called_once_with(
            "Your team's conferences are hosted at: https://meet.example.com/"
        )

    def test_slash_jitsi_server_set_default(self, workspace_store, mock_command):
        """Test the /jitsi server default command"""
        # Setup
        command = mock_command.copy()
        command["text"] = "server default"
        workspace_store.set_workspace_server_url(command["team_id"], "https://meet.example.com/")

        # Action
        slash_jitsi_server(command, self.logger, self.respond, workspace_store)

        # Assert
        self.respond.assert_called_once()
        assert "default" in self.respond.call_args[0][0]
        assert (
            workspace_store.get_workspace_server_url(command["team_id"]) == self.default_server_url
        )

    def test_slash_jitsi_server_set_custom(self, workspace_store, mock_command):
        """Test the /jitsi server <url> command"""
        # Setup
        custom_url = "https://meet.custom.com/"
        command = mock_command.copy()
        command["text"] = f"server {custom_url}"

        # Action
        slash_jitsi_server(command, self.logger, self.respond, workspace_store)

        # Assert
        self.respond.assert_called_once()
        assert custom_url in self.respond.call_args[0][0]
        assert (
            workspace_store.get_workspace_server_url(command["team_id"])
            == "https://meet.custom.com/"
        )

    def test_slash_jitsi_server_invalid_url(self, workspace_store, mock_command):
        """Test the /jitsi server command with an invalid URL"""
        # Setup
        invalid_url = "invalid-url"
        command = mock_command.copy()
        command["text"] = f"server {invalid_url}"

        # Action
        slash_jitsi_server(command, self.logger, self.respond, workspace_store)

        # Assert
        self.respond.assert_called_once()
        assert "Invalid format" in self.respond.call_args[0][0]

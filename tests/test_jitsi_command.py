import pytest
from unittest.mock import MagicMock, patch
from jitsi_slack_bolt.listeners.jitsi_command import jitsi_callback


class TestJitsiCommand:
    """Test the Jitsi command callback functionality"""

    def setup_method(self):
        """Setup for each test method"""
        self.ack = MagicMock()
        self.client = MagicMock()
        self.logger = MagicMock()
        self.respond = MagicMock()
        self.workspace_store = MagicMock()
        self.slash_cmd = "/jitsi"

    @patch("jitsi_slack_bolt.listeners.jitsi_command.slash_jitsi_server")
    def test_jitsi_server_command(self, mock_slash_jitsi_server):
        """Test the callback routes to slash_jitsi_server"""
        # Setup
        command = {"text": "server"}

        # Action
        jitsi_callback(
            ack=self.ack,
            client=self.client,
            command=command,
            logger=self.logger,
            respond=self.respond,
            slash_cmd=self.slash_cmd,
            workspace_store=self.workspace_store,
        )

        # Assert
        self.ack.assert_called_once()
        mock_slash_jitsi_server.assert_called_once_with(
            command, self.logger, self.respond, self.workspace_store
        )

    @patch("jitsi_slack_bolt.listeners.jitsi_command.slash_jitsi_dm")
    def test_jitsi_dm_command(self, mock_slash_jitsi_dm):
        """Test the callback routes to slash_jitsi_dm"""
        # Setup
        command = {"text": "@user"}

        # Action
        jitsi_callback(
            ack=self.ack,
            client=self.client,
            command=command,
            logger=self.logger,
            respond=self.respond,
            slash_cmd=self.slash_cmd,
            workspace_store=self.workspace_store,
        )

        # Assert
        self.ack.assert_called_once()
        mock_slash_jitsi_dm.assert_called_once_with(
            self.client, command, self.logger, self.respond, self.workspace_store
        )

    @patch("jitsi_slack_bolt.listeners.jitsi_command.slash_jitsi_help")
    def test_jitsi_help_command(self, mock_slash_jitsi_help):
        """Test the callback routes to slash_jitsi_help"""
        # Setup
        command = {"text": "help"}

        # Action
        jitsi_callback(
            ack=self.ack,
            client=self.client,
            command=command,
            logger=self.logger,
            respond=self.respond,
            slash_cmd=self.slash_cmd,
            workspace_store=self.workspace_store,
        )

        # Assert
        self.ack.assert_called_once()
        mock_slash_jitsi_help.assert_called_once_with(
            self.respond, self.slash_cmd, self.workspace_store
        )

    @patch("jitsi_slack_bolt.listeners.jitsi_command.slash_jitsi")
    def test_jitsi_default_command(self, mock_slash_jitsi):
        """Test the callback routes to slash_jitsi by default"""
        # Setup
        command = {"text": ""}

        # Action
        jitsi_callback(
            ack=self.ack,
            client=self.client,
            command=command,
            logger=self.logger,
            respond=self.respond,
            slash_cmd=self.slash_cmd,
            workspace_store=self.workspace_store,
        )

        # Assert
        self.ack.assert_called_once()
        mock_slash_jitsi.assert_called_once_with(
            command, self.logger, self.respond, self.workspace_store
        )

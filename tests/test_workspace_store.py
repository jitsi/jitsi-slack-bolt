import pytest
from jitsi_slack_bolt.util.store import WorkspaceStore, InMemoryStorageProvider


class TestWorkspaceStore:
    """Test the WorkspaceStore class"""

    def setup_method(self):
        """Setup for each test method"""
        self.store = WorkspaceStore()
        self.store._provider = InMemoryStorageProvider()  # Reset provider to in-memory for tests

    def test_workspace_server_url(self):
        """Test setting and getting workspace server URL"""
        # Setup
        workspace_id = "test_team"
        server_url = "https://meet.example.com/"

        # Action
        self.store.set_workspace_server_url(workspace_id, server_url)

        # Assert
        assert self.store.get_workspace_server_url(workspace_id) == "https://meet.example.com/"

    def test_default_workspace_server_url(self):
        """Test default workspace server URL when none is set"""
        # Setup
        workspace_id = "test_team"
        default_server = "https://meet.default.com/"

        # Set default server
        self.store.set_workspace_server_url("default", default_server)

        # Assert it returns the default when team's server is not set
        assert self.store.get_workspace_server_url(workspace_id) == "https://meet.default.com/"

    def test_workspace_oauth(self):
        """Test setting and getting workspace OAuth token"""
        # Setup
        workspace_id = "test_team"
        oauth_token = "xoxb-12345-abcde"

        # Action
        self.store.set_workspace_oauth(workspace_id, oauth_token)

        # Assert
        assert self.store.get_workspace_oauth(workspace_id) == oauth_token

    def test_delete_workspace(self):
        """Test deleting a workspace removes all its data"""
        # Setup
        workspace_id = "test_team"
        server_url = "https://meet.example.com/"
        oauth_token = "xoxb-12345-abcde"

        # Set data
        self.store.set_workspace_server_url(workspace_id, server_url)
        self.store.set_workspace_oauth(workspace_id, oauth_token)

        # Delete workspace
        self.store.delete_workspace(workspace_id)

        # Assert
        assert self.store.get_workspace_oauth(workspace_id) is None
        assert self.store.get_workspace_server_url(workspace_id) != "https://meet.example.com/"

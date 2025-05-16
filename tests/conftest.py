import pytest
from jitsi_slack_bolt.util.store import WorkspaceStore, InMemoryStorageProvider


@pytest.fixture
def workspace_store():
    """Fixture for a workspace store with in-memory storage"""
    store = WorkspaceStore()
    store._provider = InMemoryStorageProvider()

    # Set a default server URL
    default_server_url = "https://meet.jit.si/"
    store.set_workspace_server_url("default", default_server_url)

    return store


@pytest.fixture
def mock_command():
    """Fixture for a mock Slack command payload"""
    return {
        "team_id": "T12345",
        "user_id": "U12345",
        "user_name": "testuser",
        "channel_id": "C12345",
        "text": "",
        "command": "/jitsi",
    }

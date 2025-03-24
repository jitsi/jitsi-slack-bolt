from abc import ABC, abstractmethod
from typing import Optional, Dict


class StorageProvider(ABC):
    """Abstract base class for storage providers."""

    @abstractmethod
    def get_oauth(self, workspace_id: str) -> Optional[str]:
        pass

    @abstractmethod
    def set_oauth(self, workspace_id: str, oauth_token: str) -> None:
        pass

    @abstractmethod
    def get_server_url(self, workspace_id: str) -> Optional[str]:
        pass

    @abstractmethod
    def set_server_url(self, workspace_id: str, server_url: str) -> None:
        pass

    @abstractmethod
    def delete_workspace(self, workspace_id: str) -> None:
        """Delete all data for a workspace."""
        pass


class InMemoryStorageProvider(StorageProvider):
    """Default in-memory storage provider."""

    def __init__(self):
        self._oauth_tokens: Dict[str, str] = {}
        self._server_urls: Dict[str, str] = {}

    def get_oauth(self, workspace_id: str) -> Optional[str]:
        return self._oauth_tokens.get(workspace_id)

    def set_oauth(self, workspace_id: str, oauth_token: str) -> None:
        self._oauth_tokens[workspace_id] = oauth_token

    def get_server_url(self, workspace_id: str) -> Optional[str]:
        return self._server_urls.get(workspace_id)

    def set_server_url(self, workspace_id: str, server_url: str) -> None:
        self._server_urls[workspace_id] = server_url.rstrip("/")

    def delete_workspace(self, workspace_id: str) -> None:
        """Delete all data for a workspace."""
        self._oauth_tokens.pop(workspace_id, None)
        self._server_urls.pop(workspace_id, None)


class WorkspaceStore:
    """Storage utility for workspace-specific settings."""

    _instance = None
    _provider: StorageProvider = InMemoryStorageProvider()

    def set_provider(cls, provider: StorageProvider) -> None:
        """Set the storage provider to use."""
        cls._provider = provider

    def get_workspace_oauth(self, workspace_id: str) -> Optional[str]:
        """Get OAuth token for a workspace."""
        return self._provider.get_oauth(workspace_id)

    def set_workspace_oauth(self, workspace_id: str, oauth_token: str) -> None:
        """Store OAuth token for a workspace."""
        self._provider.set_oauth(workspace_id, oauth_token)

    def get_workspace_server_url(self, workspace_id: str) -> str:
        """Get Jitsi server URL for a workspace."""
        return self._provider.get_server_url(workspace_id) or self._provider.get_server_url(
            "default"
        )

    def set_workspace_server_url(self, workspace_id: str, server_url: str) -> None:
        """Set Jitsi server URL for a workspace."""
        self._provider.set_server_url(workspace_id, server_url)

    def delete_workspace(self, workspace_id: str) -> None:
        """Delete all data for a workspace."""
        self._provider.delete_workspace(workspace_id)

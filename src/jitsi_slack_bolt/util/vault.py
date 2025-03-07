from typing import Optional
import hvac
from .store import StorageProvider

# take a primary vault and backup vault
# always write to both
# read from first  and read from second if connection doesn't work
# collect metrics on all of this

class VaultStorageProvider(StorageProvider):
    """Hashicorp Vault-based storage provider."""

    def __init__(
        self, url: str, token: str, mount_point: str = "kv", path_prefix: str = "jitsi-slack"
    ):
        """Initialize Vault client.

        Args:
            url: Vault server URL
            token: Vault authentication token
            mount_point: KV secrets engine mount point
            path_prefix: Path prefix for storing secrets
        """
        self.client = hvac.Client(url=url, token=token)
        self.mount_point = mount_point
        self.path_prefix = path_prefix

    def _get_secret(self, workspace_id: str, key: str) -> Optional[str]:
        """Helper to read a secret from Vault."""
        try:
            path = f"{self.path_prefix}/{workspace_id}"
            result = self.client.secrets.kv.v2.read_secret_version(
                path=path, mount_point=self.mount_point
            )
            return result["data"]["data"].get(key)
        except (hvac.exceptions.VaultError, KeyError):
            return None

    def _set_secret(self, workspace_id: str, key: str, value: str) -> None:
        """Helper to write a secret to Vault."""
        path = f"{self.path_prefix}/{workspace_id}"

        # Read existing secrets to merge with new value
        try:
            current = self.client.secrets.kv.v2.read_secret_version(
                path=path, mount_point=self.mount_point
            )
            data = current["data"]["data"]
        except (hvac.exceptions.VaultError, KeyError):
            data = {}

        # Update with new value
        data[key] = value

        # Write back to Vault
        self.client.secrets.kv.v2.create_or_update_secret(
            path=path, secret=data, mount_point=self.mount_point
        )

    def get_oauth(self, workspace_id: str) -> Optional[str]:
        """Get OAuth token for a workspace."""
        return self._get_secret(workspace_id, "oauth_token")

    def set_oauth(self, workspace_id: str, oauth_token: str) -> None:
        """Store OAuth token for a workspace."""
        self._set_secret(workspace_id, "oauth_token", oauth_token)

    def get_server_url(self, workspace_id: str) -> Optional[str]:
        """Get Jitsi server URL for a workspace."""
        return self._get_secret(workspace_id, "server_url")

    def set_server_url(self, workspace_id: str, server_url: str) -> None:
        """Set Jitsi server URL for a workspace."""
        self._set_secret(workspace_id, "server_url", server_url.rstrip("/"))

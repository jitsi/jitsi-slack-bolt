from dataclasses import dataclass
from enum import Enum
import os
import logging
from typing import Optional


class StorageType(Enum):
    MEMORY = "memory"
    VAULT = "vault"
    POSTGRES = "postgres"


@dataclass
class JitsiConfiguration:
    """Configuration settings for Jitsi Slack integration."""

    data_store_provider: StorageType
    debug_level: str
    default_server: str
    slack_app_mode: str
    slash_cmd: str
    proxy_mode: Optional[str]
    vault_url: Optional[str] = None
    vault_token: Optional[str] = None
    vault_mount_point: Optional[str] = "kv"
    vault_path_prefix: Optional[str] = "jitsi-slack"
    db_host: Optional[str] = None
    db_ip: Optional[str] = None
    db_port: Optional[str] = None
    db_username: Optional[str] = None
    db_password: Optional[str] = None
    db_name: Optional[str] = "jitsi-slack"

    @classmethod
    def from_env(cls) -> "JitsiConfiguration":
        """Create configuration from environment variables."""
        provider_str = os.environ.get("STORAGE_PROVIDER", "memory").lower()
        try:
            provider = StorageType(provider_str)
        except ValueError:
            raise ValueError(f"Invalid storage provider: {provider_str}")

        debug_level = os.environ.get("DEBUG_LEVEL", "INFO").upper()
        if debug_level not in logging._nameToLevel:
            raise ValueError(f"Invalid debug level: {debug_level}")

        config = cls(
            data_store_provider=provider,
            debug_level=debug_level,
            default_server=os.environ.get("JITSI_DEFAULT_SERVER", "https://meet.jit.si/"),
            slack_app_mode=os.environ.get("SLACK_EVENTS_API_MODE", "socket"),
            slash_cmd=os.environ.get("SLACK_SLASH_CMD", "/jitsi"),
            proxy_mode=os.environ.get("PROXY_MODE", "false"),
            vault_url=os.environ.get("VAULT_URL", None),
            vault_token=os.environ.get("VAULT_TOKEN", None),
            vault_mount_point=os.environ.get("VAULT_MOUNT_POINT", "kv"),
            vault_path_prefix=os.environ.get("VAULT_PATH_PREFIX", "jitsi-slack"),
            db_host=os.environ.get("DB_HOST", None),
            db_ip=os.environ.get("DB_IP", None),
            db_port=os.environ.get("DB_PORT", None),
            db_username=os.environ.get("DB_USERNAME", None),
            db_password=os.environ.get("DB_PASSWORD", None),
            db_name=os.environ.get("DB_NAME", "jitsi-slack"),
        )

        if config.data_store_provider == StorageType.VAULT:
            if not config.vault_url or not config.vault_token:
                raise ValueError("Vault URL and token are required when using Vault storage")

        if config.data_store_provider == StorageType.POSTGRES:
            if not config.db_host or not config.db_ip:
                raise ValueError("Postgres host or IP is required when using Postgres storage")
            if not config.db_port:
                raise ValueError("Postgres port is required when using Postgres storage")
            if not config.db_username:
                raise ValueError("Postgres username is required when using Postgres storage")
            if not config.db_password:
                raise ValueError("Postgres password is required when using Postgres storage")
            if not config.db_name:
                raise ValueError("Postgres database name is required when using Postgres storage")

        return config

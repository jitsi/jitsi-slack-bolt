from typing import Optional
from sqlalchemy import URL
from sqlalchemy.orm import Session
from .store import StorageProvider
from .models import WorkspaceData, init_db


class PostgresStorageProvider(StorageProvider):
    """PostgreSQL-based storage provider using SQLAlchemy."""

    def __init__(
        self, host: str, ip: str, port: str, username: str, password: str, database_name: str
    ):
        """Initialize database connection.

        Args:
          host: Database host
          port: Database port
          ip: Database IP
          username: Database username
          password: Database password
          database_name: Database name
        """

        if host:
            hostname = host
        elif ip:
            hostname = ip
        else:
            raise ValueError("Either host or IP must be provided")

        url_object = URL.create(
            "postgresql+psycopg2",
            username=username,
            password=password,
            host=hostname,
            port=port,
            database=database_name,
        )

        self.engine = init_db(url_object)

    def get_oauth(self, workspace_id: str) -> Optional[str]:
        with Session(self.engine) as session:
            workspace = session.query(WorkspaceData).get(workspace_id)
            return workspace.oauth_token if workspace else None

    def set_oauth(self, workspace_id: str, oauth_token: str) -> None:
        with Session(self.engine) as session:
            workspace = session.query(WorkspaceData).get(workspace_id)
            if not workspace:
                workspace = WorkspaceData(workspace_id=workspace_id)
                session.add(workspace)
            workspace.oauth_token = oauth_token
            session.commit()

    def get_server_url(self, workspace_id: str) -> Optional[str]:
        with Session(self.engine) as session:
            workspace = session.query(WorkspaceData).get(workspace_id)
            return workspace.server_url if workspace else None

    def set_server_url(self, workspace_id: str, server_url: str) -> None:
        with Session(self.engine) as session:
            workspace = session.query(WorkspaceData).get(workspace_id)
            if not workspace:
                workspace = WorkspaceData(workspace_id=workspace_id)
                session.add(workspace)
            workspace.server_url = server_url.rstrip("/")
            session.commit()

    def delete_workspace(self, workspace_id: str) -> None:
        """Delete all data for a workspace."""
        with Session(self.engine) as session:
            workspace = session.query(WorkspaceData).get(workspace_id)
            if workspace:
                session.delete(workspace)
                session.commit()

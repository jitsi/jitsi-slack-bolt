from sqlalchemy import Column, String, create_engine, URL
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class WorkspaceData(Base):
    """SQL model for workspace settings and tokens."""

    __tablename__ = "workspace_data"

    workspace_id = Column(String, primary_key=True)
    oauth_token = Column(String)
    server_url = Column(String)


def init_db(database_url: URL):
    """Initialize database and create tables if they don't exist."""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine

import logging

from slack_sdk.oauth.installation_store.installation_store import InstallationStore
from slack_sdk.oauth.installation_store.models.installation import Installation
from typing import Optional
from .store import WorkspaceStore

class WorkspaceInstallationStore(InstallationStore):
    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, new_logger):
        self._logger = new_logger

    def __init__(self, workspace_store: WorkspaceStore):
        self.store = workspace_store
        self.logger = logging.getLogger(__name__)

    def save(self, installation: Installation) -> None:
        self.store.set_workspace_oauth(installation.team_id, installation.bot_token)
        self.logger.info(f"Installation saved: {installation}")

    def find_installation(self, team_id: Optional[str]) -> Optional[Installation]:
        if not team_id:
            self.logger.warning("find_installation called with no team_id")
            return None
        token = self.store.get_workspace_oauth(team_id)
        if token:
            installation = Installation(
                team_id=team_id,
                bot_token=token
            )
            self.logger.info(f"Installation found: {installation}") 
            return installation
        self.logger.info(f"Installation not found for team_id: {team_id}")
        return None

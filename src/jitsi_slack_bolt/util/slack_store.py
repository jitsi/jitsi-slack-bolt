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
        self.logger.info(f"installation saved: {installation}")

    def find_installation(
        self,
        *,
        enterprise_id: Optional[str],
        team_id: Optional[str],
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        lookup_id = ""
        if is_enterprise_install:
            self.logger.warning("find_installation called with is_enterprise_install")
            lookup_id = enterprise_id
        else:
            lookup_id = team_id
        token = self.store.get_workspace_oauth(lookup_id)
        if token:
            installation = Installation(user_id=user_id, team_id=team_id, bot_token=token)
            self.logger.debug(f"installation found: {installation}")
            return installation
        self.logger.info(f"installation not found for team_id: {team_id}")
        return None

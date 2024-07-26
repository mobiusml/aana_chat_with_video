from typing import TypedDict

from aana.api.api_generation import Endpoint
from aana.core.models.media import MediaId
from aana_chat_with_video.storage.repository.extended_video import (
    ExtendedVideoRepository,
)


class DeleteVideoOutput(TypedDict):
    """The output of the delete media endpoint."""

    media_id: MediaId


class DeleteVideoEndpoint(Endpoint):
    """Delete video endpoint."""

    async def initialize(self):
        """Initialize the endpoint."""
        await super().initialize()
        self.video_repo = ExtendedVideoRepository(self.session)

    async def run(self, media_id: MediaId) -> DeleteVideoOutput:
        """Delete media."""
        self.video_repo.delete(media_id)
        return DeleteVideoOutput(media_id=media_id)

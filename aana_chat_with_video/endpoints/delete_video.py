from typing import TypedDict

from aana.api.api_generation import Endpoint
from aana.core.models.media import MediaId
from aana.storage.session import get_session
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

    async def run(self, media_id: MediaId) -> DeleteVideoOutput:
        """Delete video."""
        with get_session() as session:
            ExtendedVideoRepository(session).delete(media_id)
        return DeleteVideoOutput(media_id=media_id)

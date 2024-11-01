from typing import TypedDict

from aana.api.api_generation import Endpoint
from aana.core.models.media import MediaId
from aana.core.models.video import VideoMetadata
from aana.storage.session import get_session
from aana_chat_with_video.storage.repository.extended_video import (
    ExtendedVideoRepository,
)


class LoadVideoMetadataOutput(TypedDict):
    """The output of the load video metadata endpoint."""

    metadata: VideoMetadata


class LoadVideoMetadataEndpoint(Endpoint):
    """Load video metadata endpoint."""

    async def run(self, media_id: MediaId) -> LoadVideoMetadataOutput:
        """Load video metadata."""
        with get_session() as session:
            video_metadata = ExtendedVideoRepository(session).get_metadata(media_id)
        return LoadVideoMetadataOutput(metadata=video_metadata)

from typing import TypedDict

from aana.api.api_generation import Endpoint
from aana.core.models.media import MediaId
from aana.core.models.video import VideoMetadata
from aana_chat_with_video.storage.repository.extended_video import (
    ExtendedVideoRepository,
)


class LoadVideoMetadataOutput(TypedDict):
    """The output of the load video metadata endpoint."""

    metadata: VideoMetadata


class LoadVideoMetadataEndpoint(Endpoint):
    """Load video metadata endpoint."""

    async def initialize(self):
        """Initialize the endpoint."""
        await super().initialize()
        self.video_repo = ExtendedVideoRepository(self.session)

    async def run(self, media_id: MediaId) -> LoadVideoMetadataOutput:
        """Load video metadata."""
        video_metadata = self.video_repo.get_metadata(media_id)
        return LoadVideoMetadataOutput(metadata=video_metadata)

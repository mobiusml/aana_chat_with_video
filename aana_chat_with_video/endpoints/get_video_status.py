from typing import TypedDict

from aana.api.api_generation import Endpoint
from aana.core.models.media import MediaId
from aana.core.models.video import VideoStatus
from aana_chat_with_video.storage.repository.extended_video import (
    ExtendedVideoRepository,
)


class VideoStatusOutput(TypedDict):
    """The output of the video status endpoint."""

    status: VideoStatus


class GetVideoStatusEndpoint(Endpoint):
    """Get video status endpoint."""

    async def initialize(self):
        """Initialize the endpoint."""
        await super().initialize()
        self.video_repo = ExtendedVideoRepository(self.session)

    async def run(self, media_id: MediaId) -> VideoStatusOutput:
        """Load video metadata."""
        video_status = self.video_repo.get_status(media_id)
        return VideoStatusOutput(status=video_status)

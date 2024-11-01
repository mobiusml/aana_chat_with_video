from typing import TypedDict

from aana.api.api_generation import Endpoint
from aana.core.models.media import MediaId
from aana.storage.session import get_session
from aana_chat_with_video.core.models.video_status import VideoStatus
from aana_chat_with_video.storage.repository.extended_video import (
    ExtendedVideoRepository,
)


class VideoStatusOutput(TypedDict):
    """The output of the video status endpoint."""

    status: VideoStatus


class GetVideoStatusEndpoint(Endpoint):
    """Get video status endpoint."""

    async def run(self, media_id: MediaId) -> VideoStatusOutput:
        """Load video metadata."""
        with get_session() as session:
            video_status = ExtendedVideoRepository(session).get_status(media_id)
        return VideoStatusOutput(status=video_status)

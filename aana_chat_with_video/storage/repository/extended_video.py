from sqlalchemy.orm import Session

from aana.core.models.media import MediaId
from aana.core.models.video import Video, VideoMetadata
from aana.storage.repository.video import VideoRepository
from aana_chat_with_video.storage.models.extended_video import (
    ExtendedVideoEntity,
    VideoProcessingStatus,
)


class ExtendedVideoRepository(VideoRepository[ExtendedVideoEntity]):
    """Repository for videos with additional metadata."""

    def __init__(self, session: Session):
        """Constructor."""
        super().__init__(session, ExtendedVideoEntity)

    def save(self, video: Video, duration: float | None = None) -> dict:
        """Saves a video to datastore.

        Args:
            video (Video): The video object.
            duration (float): the duration of the video object

        Returns:
            dict: The dictionary with video and media IDs.
        """
        video_entity = ExtendedVideoEntity(
            id=video.media_id,
            path=str(video.path),
            url=video.url,
            title=video.title,
            description=video.description,
            duration=duration,
        )
        self.create(video_entity)
        return video_entity

    def get_status(self, media_id: MediaId) -> VideoProcessingStatus:
        """Get the status of a video.

        Args:
            media_id (str): The media ID.

        Returns:
            VideoProcessingStatus: The status of the video.
        """
        entity: ExtendedVideoEntity = self.read(media_id)
        return entity.status

    def update_status(self, media_id: MediaId, status: VideoProcessingStatus):
        """Update the status of a video.

        Args:
            media_id (str): The media ID.
            status (VideoProcessingStatus): The status of the video.
        """
        entity: ExtendedVideoEntity = self.read(media_id)
        entity.status = status
        self.session.commit()

    def get_metadata(self, media_id: MediaId) -> VideoMetadata:
        """Get the metadata of a video.

        Args:
            media_id (MediaId): The media ID.

        Returns:
            VideoMetadata: The video metadata.
        """
        entity: ExtendedVideoEntity = self.read(media_id)
        return VideoMetadata(
            title=entity.title,
            description=entity.description,
            duration=entity.duration,
        )

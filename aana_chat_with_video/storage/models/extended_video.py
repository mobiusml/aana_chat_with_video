from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from aana.core.models.media import MediaId
from aana.storage.models.video import VideoEntity
from aana_chat_with_video.storage.models.extended_video_caption import (
    ExtendedVideoCaptionEntity,
)
from aana_chat_with_video.storage.models.extended_video_transcript import (
    ExtendedVideoTranscriptEntity,
)


class VideoProcessingStatus(str, Enum):
    """Enum for video status."""

    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ExtendedVideoEntity(VideoEntity):
    """ORM class for videos with additional metadata."""

    __tablename__ = "extended_video"

    id: Mapped[MediaId] = mapped_column(ForeignKey("video.id"), primary_key=True)
    duration: Mapped[float | None] = mapped_column(comment="Video duration in seconds")
    status: Mapped[VideoProcessingStatus] = mapped_column(
        nullable=False,
        default=VideoProcessingStatus.CREATED,
        comment="Processing status",
    )

    captions: Mapped[list[ExtendedVideoCaptionEntity]] = relationship(
        "ExtendedVideoCaptionEntity",
        back_populates="video",
        cascade="all, delete",
        uselist=True,
    )
    transcript: Mapped[list[ExtendedVideoTranscriptEntity]] = relationship(
        "ExtendedVideoTranscriptEntity",
        back_populates="video",
        cascade="all, delete",
        uselist=True,
    )

    __mapper_args__ = {  # noqa: RUF012
        "polymorphic_identity": "extended_video",
    }

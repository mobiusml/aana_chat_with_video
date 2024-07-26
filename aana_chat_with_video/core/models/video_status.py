from typing import Annotated, Any

from pydantic import Field, ValidationInfo, ValidatorFunctionWrapHandler, WrapValidator

from aana_chat_with_video.storage.models.extended_video import VideoProcessingStatus


def process_video_status(
    v: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> str:
    """Validates the media_id."""
    if isinstance(v, str):
        return VideoProcessingStatus(v)
    return v


VideoStatus = Annotated[
    VideoProcessingStatus,
    Field(description="Video processing status."),
    WrapValidator(process_video_status),
]
"""
Video processing status.
"""

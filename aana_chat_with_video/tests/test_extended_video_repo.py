# ruff: noqa: S101

import uuid
from importlib import resources

import pytest

from aana.core.models.video import Video, VideoMetadata
from aana.exceptions.db import MediaIdAlreadyExistsException, NotFoundException
from aana_chat_with_video.storage.models.extended_video import VideoProcessingStatus
from aana_chat_with_video.storage.repository.extended_video import (
    ExtendedVideoRepository,
)


@pytest.fixture(scope="function")
def dummy_video():
    """Creates a dummy video for testing."""
    media_id = str(uuid.uuid4())
    path = resources.path("aana.tests.files.videos", "squirrel.mp4")
    video = Video(
        path=path, media_id=media_id, title="Squirrel", description="A squirrel video"
    )
    return video


def test_save_video(db_session, dummy_video):
    """Tests saving a video."""
    video_repo = ExtendedVideoRepository(db_session)
    video_repo.save(dummy_video, duration=10)

    video_entity = video_repo.read(dummy_video.media_id)
    assert video_entity
    assert video_entity.id == dummy_video.media_id

    # Try to save the same video again
    with pytest.raises(MediaIdAlreadyExistsException):
        video_repo.save(dummy_video)

    video_repo.delete(dummy_video.media_id)
    with pytest.raises(NotFoundException):
        video_repo.read(dummy_video.media_id)


def test_get_metadata(db_session, dummy_video):
    """Tests getting video metadata."""
    video_repo = ExtendedVideoRepository(db_session)
    video_repo.save(dummy_video, duration=10)

    metadata = video_repo.get_metadata(dummy_video.media_id)
    assert isinstance(metadata, VideoMetadata)
    assert metadata.title == dummy_video.title
    assert metadata.description == dummy_video.description
    assert metadata.duration == 10

    video_repo.delete(dummy_video.media_id)
    with pytest.raises(NotFoundException):
        video_repo.get_metadata(dummy_video.media_id)


def test_status(db_session, dummy_video):
    """Tests getting and updating video status."""
    video_repo = ExtendedVideoRepository(db_session)
    video_repo.save(dummy_video, duration=10)

    assert video_repo.get_status(dummy_video.media_id) == VideoProcessingStatus.CREATED

    video_repo.update_status(dummy_video.media_id, VideoProcessingStatus.RUNNING)

    assert video_repo.get_status(dummy_video.media_id) == VideoProcessingStatus.RUNNING

    video_repo.delete(dummy_video.media_id)

    with pytest.raises(NotFoundException):
        video_repo.get_status(dummy_video.media_id)
        video_repo.update_status(dummy_video.media_id, VideoProcessingStatus.COMPLETED)

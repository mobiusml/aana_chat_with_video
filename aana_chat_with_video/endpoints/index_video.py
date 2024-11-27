from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Annotated, TypedDict
import asyncio
from aana.storage.session import get_session
from pydantic import Field

from aana.api.api_generation import Endpoint
from aana.core.models.asr import (
    AsrSegments,
    AsrTranscription,
    AsrTranscriptionInfo,
)
from aana.core.models.media import MediaId
from aana.core.models.vad import VadParams
from aana.core.models.video import VideoInput, VideoMetadata, VideoParams
from aana.core.models.whisper import BatchedWhisperParams
from aana.core.models.image_chat import ImageChatDialog

from aana.deployments.aana_deployment_handle import AanaDeploymentHandle
from aana.exceptions.db import MediaIdAlreadyExistsException
from aana.exceptions.io import VideoTooLongException
from aana.integrations.external.decord import generate_frames, get_video_duration
from aana.integrations.external.yt_dlp import download_video, get_video_metadata
from aana.processors.remote import run_remote
from aana.processors.video import extract_audio
from aana_chat_with_video.configs.settings import settings
from aana_chat_with_video.storage.models.extended_video import VideoProcessingStatus
from aana_chat_with_video.storage.repository.extended_video import (
    ExtendedVideoRepository,
)
from aana_chat_with_video.storage.repository.extended_video_caption import (
    ExtendedVideoCaptionRepository,
)
from aana_chat_with_video.storage.repository.extended_video_transcript import (
    ExtendedVideoTranscriptRepository,
)

if TYPE_CHECKING:
    from aana.core.models.audio import Audio
    from aana.core.models.video import Video


class IndexVideoOutput(TypedDict):
    """The output of the transcribe video endpoint."""

    media_id: MediaId
    metadata: VideoMetadata
    transcription: AsrTranscription
    transcription_info: AsrTranscriptionInfo
    segments: AsrSegments

    captions: Annotated[list[str], Field(..., description="Captions")]
    timestamps: Annotated[
        list[float], Field(..., description="Timestamps for each caption in seconds")
    ]

    transcription_id: Annotated[int, Field(..., description="Transcription Id")]
    caption_ids: Annotated[list[int], Field(..., description="Caption Ids")]


class IndexVideoEndpoint(Endpoint):
    """Transcribe video in chunks endpoint."""

    async def initialize(self):
        """Initialize the endpoint."""
        await super().initialize()
        self.asr_handle = await AanaDeploymentHandle.create("asr_deployment")
        self.vad_handle = await AanaDeploymentHandle.create("vad_deployment")
        self.captioning_handle = await AanaDeploymentHandle.create(
            "captioning_deployment"
        )

    async def run(  # noqa: C901
        self,
        video: VideoInput,
        video_params: VideoParams,
        whisper_params: BatchedWhisperParams,
        vad_params: VadParams,
    ) -> AsyncGenerator[IndexVideoOutput, None]:
        """Transcribe video in chunks."""
        media_id = video.media_id
        with get_session() as session:
            if ExtendedVideoRepository(session).check_media_exists(media_id):
                raise MediaIdAlreadyExistsException(table_name="media", media_id=video)
        
        video_duration = None
        if video.url is not None:
            video_metadata = get_video_metadata(video.url)
            video_duration = video_metadata.duration

        # precheck for max video length before actually download the video if possible
        if video_duration and video_duration > settings.max_video_len:
            raise VideoTooLongException(
                video=video,
                video_len=video_duration,
                max_len=settings.max_video_len,
            )

        video_obj: Video = await run_remote(download_video)(video_input=video)
        if video_duration is None:
            video_duration = await run_remote(get_video_duration)(video=video_obj)

        if video_duration > settings.max_video_len:
            raise VideoTooLongException(
                video=video_obj,
                video_len=video_duration,
                max_len=settings.max_video_len,
            )

        with get_session() as session:
            ExtendedVideoRepository(session).save(video=video_obj, duration=video_duration)

        yield {
            "media_id": media_id,
            "metadata": VideoMetadata(
                title=video_obj.title,
                description=video_obj.description,
                duration=video_duration,
            ),
        }

        try:
            with get_session() as session:
                ExtendedVideoRepository(session).update_status(
                    media_id, VideoProcessingStatus.RUNNING
                )
            audio: Audio = extract_audio(video=video_obj)

            # TODO: Update once batched whisper PR is merged
            # vad_output = await self.vad_handle.asr_preprocess_vad(
            #     audio=audio, params=vad_params
            # )
            # vad_segments = vad_output["segments"]

            transcription_list = []
            segments_list = []
            transcription_info_list = []
            async for whisper_output in self.asr_handle.transcribe_stream(
                audio=audio, params=whisper_params
            ):
                transcription_list.append(whisper_output["transcription"])
                segments_list.append(whisper_output["segments"])
                transcription_info_list.append(whisper_output["transcription_info"])
                yield {
                    "transcription": whisper_output["transcription"],
                    "segments": whisper_output["segments"],
                    "transcription_info": whisper_output["transcription_info"],
                }
            transcription = sum(transcription_list, AsrTranscription())
            segments = sum(segments_list, AsrSegments())
            transcription_info = sum(transcription_info_list, AsrTranscriptionInfo())

            captions = []
            timestamps = []
            frame_ids = []

            async for frames_dict in run_remote(generate_frames)(
                video=video_obj, params=video_params
            ):
                if len(frames_dict["frames"]) == 0:
                    break

                timestamps.extend(frames_dict["timestamps"])
                frame_ids.extend(frames_dict["frame_ids"])
                chat_prompt = "Caption the content of the following image in a single and concise sentence"
                dialogs = [
                    ImageChatDialog.from_prompt(prompt=chat_prompt, images=[frame]) for frame in frames_dict["frames"]
                ]

                # Collect the tasks to run concurrently and wait for them to finish
                captioning_tasks = [
                    asyncio.create_task(self.captioning_handle.chat(dialog)) for dialog in dialogs 
                ]
                captioning_output = await asyncio.gather(*captioning_tasks)
                captioning_output = [caption["message"].content for caption in captioning_output]
                captions.extend(captioning_output)

                yield {
                    "captions": captioning_output,
                    "timestamps": frames_dict["timestamps"],
                }

            with get_session() as session:
                transcription_entity = ExtendedVideoTranscriptRepository(session).save(
                    model_name=settings.asr_model_name,
                    media_id=video_obj.media_id,
                    transcription=transcription,
                    segments=segments,
                    transcription_info=transcription_info,
                )

                caption_entities = ExtendedVideoCaptionRepository(session).save_all(
                    model_name=settings.captioning_model_name,
                    media_id=video_obj.media_id,
                    captions=captions,
                    timestamps=timestamps,
                    frame_ids=frame_ids,
                )

                yield {
                    "transcription_id": transcription_entity.id,
                    "caption_ids": [c.id for c in caption_entities],
                }
        except BaseException:
            with get_session() as session:
                ExtendedVideoRepository(session).update_status(
                    media_id, VideoProcessingStatus.FAILED
                )
            raise
        else:
            with get_session() as session:
                ExtendedVideoRepository(session).update_status(
                    media_id, VideoProcessingStatus.COMPLETED
                )

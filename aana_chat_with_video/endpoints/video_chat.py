import json
from collections.abc import AsyncGenerator
from typing import Annotated, TypedDict

from pydantic import Field

from aana.api.api_generation import Endpoint
from aana.core.models.chat import Question
from aana.core.models.media import MediaId
from aana.core.models.sampling import SamplingParams
from aana.deployments.aana_deployment_handle import AanaDeploymentHandle
from aana.exceptions.db import UnfinishedVideoException
from aana.storage.models.extended_video import VideoProcessingStatus
from aana.storage.repository.extended_video import ExtendedVideoRepository
from aana.storage.repository.extended_video_caption import (
    ExtendedVideoCaptionRepository,
)
from aana.storage.repository.extended_video_transcript import (
    ExtendedVideoTranscriptRepository,
)
from aana_chat_with_video.configs.settings import settings
from aana_chat_with_video.utils.core import generate_combined_timeline, generate_dialog


class VideoChatEndpointOutput(TypedDict):
    """Video chat endpoint output."""

    completion: Annotated[str, Field(description="Generated text.")]


class VideoChatEndpoint(Endpoint):
    """Video chat endpoint."""

    async def initialize(self):
        """Initialize the endpoint."""
        await super().initialize()
        self.llm_handle = await AanaDeploymentHandle.create("llm_deployment")
        self.transcript_repo = ExtendedVideoTranscriptRepository(self.session)
        self.caption_repo = ExtendedVideoCaptionRepository(self.session)
        self.video_repo = ExtendedVideoRepository(self.session)

    async def run(
        self, media_id: MediaId, question: Question, sampling_params: SamplingParams
    ) -> AsyncGenerator[VideoChatEndpointOutput, None]:
        """Run the video chat endpoint."""
        # check to see if video already processed
        video_status = self.video_repo.get_status(media_id)
        if video_status != VideoProcessingStatus.COMPLETED:
            raise UnfinishedVideoException(
                media_id=media_id,
                status=video_status,
                message=f"The video data is not available, status: {video_status}",
            )

        transcription_output = self.transcript_repo.get_transcript(
            model_name=settings.asr_model_name, media_id=media_id
        )

        captions_output = self.caption_repo.get_captions(
            model_name=settings.captioning_model_name, media_id=media_id
        )

        video_metadata = self.video_repo.get_metadata(media_id)

        timeline_output = generate_combined_timeline(
            transcription_segments=transcription_output["segments"],
            captions=captions_output["captions"],
            caption_timestamps=captions_output["timestamps"],
        )
        timeline_json = json.dumps(
            timeline_output["timeline"], indent=4, separators=(",", ": ")
        )

        dialog = generate_dialog(
            metadata=video_metadata,
            timeline=timeline_json,
            question=question,
        )
        async for item in self.llm_handle.chat_stream(
            dialog=dialog, sampling_params=sampling_params
        ):
            yield {"completion": item["text"]}

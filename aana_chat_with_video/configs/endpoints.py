from aana_chat_with_video.endpoints.delete_video import DeleteVideoEndpoint
from aana_chat_with_video.endpoints.get_video_status import GetVideoStatusEndpoint
from aana_chat_with_video.endpoints.index_video import IndexVideoEndpoint
from aana_chat_with_video.endpoints.load_video_metadata import LoadVideoMetadataEndpoint
from aana_chat_with_video.endpoints.video_chat import VideoChatEndpoint

endpoints: list[dict] = [
    {
        "name": "index_video_stream",
        "path": "/video/index_stream",
        "summary": "Index a video and return the captions and transcriptions (streaming)",
        "endpoint_cls": IndexVideoEndpoint,
    },
    {
        "name": "video_metadata",
        "path": "/video/metadata",
        "summary": "Load video metadata",
        "endpoint_cls": LoadVideoMetadataEndpoint,
    },
    {
        "name": "video_chat_stream",
        "path": "/video/chat_stream",
        "summary": "Chat with video (streaming)",
        "endpoint_cls": VideoChatEndpoint,
    },
    {
        "name": "video_status",
        "path": "/video/status",
        "summary": "Get video status",
        "endpoint_cls": GetVideoStatusEndpoint,
    },
    {
        "name": "delete_media",
        "path": "/video/delete",
        "summary": "Delete video",
        "endpoint_cls": DeleteVideoEndpoint,
    },
]

from aana.core.models.media import MediaId
from aana_chat_with_video.storage.models.extended_video import VideoProcessingStatus


class UnfinishedVideoException(BaseException):
    """Exception raised when try to fetch unfinished video.

    Attributes:
        media_id (int | MediaId): The id of video.
        status (VideoStatus): The current video status.
        message (str): The error message.
    """

    def __init__(
        self, media_id: int | MediaId, status: VideoProcessingStatus, message: str
    ):
        """Constructor.

        Args:
            media_id (int | MediaId): The id of video.
            status (VideoStatus): The current video status.
            message (str): The error message.
        """
        super().__init__(media_id=media_id, status=status, message=message)
        self.media_id = media_id
        self.status = status
        self.message = message

    def __reduce__(self):
        """Used for pickling."""
        return (self.__class__, (self.media_id, self.status, self.message))

import copy
from typing import Union

from youtubesearchpython.core import VideoCore
from youtubesearchpython.core.comments import CommentsCore
from youtubesearchpython.core.constants import ResultMode, ChannelRequestType
from youtubesearchpython.core.hashtag import HashtagCore
from youtubesearchpython.core.playlist import PlaylistCore
from youtubesearchpython.core.suggestions import SuggestionsCore
from youtubesearchpython.core.transcript import TranscriptCore
from youtubesearchpython.core.channel import ChannelCore
from youtubesearchpython.core.recommendations import RecommendationsCore


class Video:
    @staticmethod
    async def get(
        videoLink: str,
        resultMode: int = ResultMode.dict,
        timeout: int = 2,
        get_upload_date: bool = False,
    ) -> Union[dict, None]:
        video = VideoCore(videoLink, None, resultMode, timeout, get_upload_date, "ANDROID")
        if get_upload_date:
            await video.async_html_create()
        await video.async_create()
        return video.result

    @staticmethod
    async def getInfo(
        videoLink: str, resultMode: int = ResultMode.dict, timeout: int = 2
    ) -> Union[dict, None]:
        video = VideoCore(videoLink, "getInfo", resultMode, timeout, False)
        await video.async_create()
        return video.result

    @staticmethod
    async def getFormats(
        videoLink: str, resultMode: int = ResultMode.dict, timeout: int = 2
    ) -> Union[dict, None]:
        video = VideoCore(videoLink, "getFormats", resultMode, timeout, False)
        await video.async_create()
        return video.result


class Suggestions:
    @staticmethod
    async def get(
        query: str, language: str = "en", region: str = "US", mode: int = ResultMode.dict
    ):
        suggestionsInternal = SuggestionsCore(language=language, region=region)
        suggestions = await suggestionsInternal._getAsync(query, mode)
        return suggestions

    def __init__(self, language: str = "en", region: str = "US"):
        self.suggestionsInternal = SuggestionsCore(language=language, region=region)

    async def get(self, query: str, mode: int = ResultMode.dict):
        return await self.suggestionsInternal._getAsync(query, mode)


class Playlist:
    playlistLink = None
    videos = []
    info = None
    hasMoreVideos = True
    __playlist = None

    def __init__(self, playlistLink: str):
        self.playlistLink = playlistLink

    async def init(self) -> None:
        self.__playlist = PlaylistCore(self.playlistLink, None, ResultMode.dict, 2)
        await self.__playlist.async_create()
        self.info = copy.deepcopy(self.__playlist.result)
        self.videos = self.__playlist.result.get("videos", [])
        self.hasMoreVideos = self.__playlist.continuationKey is not None

    async def getNextVideos(self) -> None:
        if not self.info:
            await self.init()
        else:
            await self.__playlist._async_next()
            self.videos = self.__playlist.result.get("videos", [])
            self.hasMoreVideos = self.__playlist.continuationKey is not None

    @staticmethod
    async def get(playlistLink: str) -> Union[dict, str, None]:
        playlist = PlaylistCore(playlistLink, None, ResultMode.dict, 2)
        await playlist.async_create()
        return playlist.result

    @staticmethod
    async def getInfo(playlistLink: str) -> Union[dict, str, None]:
        playlist = PlaylistCore(playlistLink, "getInfo", ResultMode.dict, 2)
        await playlist.async_create()
        return playlist.result

    @staticmethod
    async def getVideos(playlistLink: str) -> Union[dict, str, None]:
        playlist = PlaylistCore(playlistLink, "getVideos", ResultMode.dict, 2)
        await playlist.async_create()
        return playlist.result


class Hashtag(HashtagCore):
    def __init__(
        self, hashtag: str, limit: int = 60, language: str = "en", region: str = "US", timeout: int = None
    ):
        super().__init__(hashtag, limit, language, region, timeout)

    async def next(self) -> dict:
        self.response = None
        self.resultComponents = []
        if self.params is None:
            await self._asyncGetParams()
        await self._asyncMakeRequest()
        self._getComponents()
        return {"result": self.resultComponents}


class Comments:
    comments = []
    hasMoreComments = True
    __comments = None

    def __init__(self, playlistLink: str, timeout: int = None):
        self.timeout = timeout
        self.playlistLink = playlistLink

    async def init(self) -> None:
        if self.__comments is None:
            self.__comments = CommentsCore(self.playlistLink)
            await self.__comments.async_create()
            self.comments = self.__comments.commentsComponent
            self.hasMoreComments = self.__comments.continuationKey is not None

    async def getNextComments(self) -> None:
        if self.__comments is None:
            self.__comments = CommentsCore(self.playlistLink)
            await self.__comments.async_create()
        else:
            await self.__comments.async_create_next()
        self.comments = self.__comments.commentsComponent
        self.hasMoreComments = self.__comments.continuationKey is not None

    @staticmethod
    async def get(videoLink: str) -> Union[dict, str, None]:
        pc = CommentsCore(videoLink)
        await pc.async_create()
        return pc.commentsComponent


class Transcript:
    @staticmethod
    async def get(videoLink: str, params: str = None):
        transcript_core = TranscriptCore(videoLink, params)
        await transcript_core.async_create()
        return transcript_core.result


class Channel(ChannelCore):
    def __init__(self, channel_id: str, request_type: str = ChannelRequestType.playlists):
        super().__init__(channel_id, request_type)

    async def init(self):
        await self.async_create()

    async def next(self):
        await self.async_next()

    @staticmethod
    async def get(channel_id: str, request_type: str = ChannelRequestType.playlists):
        channel_core = ChannelCore(channel_id, request_type)
        await channel_core.async_create()
        return channel_core.result


class Recommendations:
    @staticmethod
    async def get(videoId: str, timeout: int = 2) -> Union[dict, None]:
        recommendations_core = RecommendationsCore(videoId, timeout)
        await recommendations_core.async_create()
        return recommendations_core.resultComponents

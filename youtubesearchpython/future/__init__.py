from typing import Any, Dict, Optional

from youtubesearchpython.core.search import ChannelSearchCore
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.search import SearchCore


class Search(SearchCore):
    '''Searches for videos, channels & playlists in YouTube (async version).

    Args:
        query (str): Sets the search query.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Sets the request timeout in seconds.
    See Also:
        For usage examples, see docs/search_examples.md (use await with async methods)
    '''
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (True, True, True)
        super().__init__(query, limit, language, region, None, timeout)

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()


class VideosSearch(SearchCore):
    '''Searches for videos in YouTube (async version).
    Args:
        query (str): Sets the search query.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Sets the request timeout in seconds.  
        is_live (bool, optional): When True, returns live streams only.
    See Also:
        For usage examples, see docs/search_examples.md (use await with async methods)
    '''
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None, is_live: Optional[bool] = None):
        self.searchMode = (True, False, False)
        super().__init__(query, limit, language, region, SearchMode.livestreams if is_live else SearchMode.videos, timeout)

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()


class ChannelsSearch(SearchCore):
    '''Searches for channels in YouTube (async version).
    Args:
        query (str): Sets the search query.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Sets the request timeout in seconds.
    See Also:
        For usage examples, see docs/search_examples.md (use await with async methods)
    '''
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (False, True, False)
        super().__init__(query, limit, language, region, SearchMode.channels, timeout)

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()


class PlaylistsSearch(SearchCore):
    '''Searches for playlists in YouTube (async version).
    Args:
        query (str): Sets the search query.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Sets the request timeout in seconds.
    See Also:
        For usage examples, see docs/search_examples.md (use await with async methods)
    '''
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (False, False, True)
        super().__init__(query, limit, language, region, SearchMode.playlists, timeout)

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()


class ChannelSearch(ChannelSearchCore):
    '''Searches for videos in specific channel in YouTube (async version).
    Args:
        query (str): Sets the search query.
        browseId (str): Channel ID to search within.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        searchPreferences (str, optional): Custom search preferences parameter.
        timeout (int, optional): Sets the request timeout in seconds. 
    See Also:
        For usage examples, see docs/search_examples.md (use await with async methods)
    '''
    def __init__(self, query: str, browseId: str, language: str = 'en', region: str = 'US', searchPreferences: str = "EgZzZWFyY2g%3D", timeout: Optional[int] = None):
        super().__init__(query, language, region, searchPreferences, browseId, timeout)

    async def next(self) -> Dict[str, Any]:
        return await self.async_next()


class CustomSearch(SearchCore):
    '''Performs custom search in YouTube with search filters or sorting orders (async version).
    Args:
        query (str): Sets the search query.
        searchPreferences (str): Sets the `sp` query parameter in the YouTube search request.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Sets the request timeout in seconds.
    See Also:
        For usage examples and available filters, see docs/search_examples.md (use await with async methods)
    '''
    def __init__(self, query: str, searchPreferences: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (True, True, True)
        super().__init__(query, limit, language, region, searchPreferences, timeout)

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()


import copy
from typing import Union

from youtubesearchpython.core import VideoCore
from youtubesearchpython.core.social import CommentsCore
from youtubesearchpython.core.constants import ResultMode, ChannelRequestType
from youtubesearchpython.core.social import HashtagCore
from youtubesearchpython.core.playlist import PlaylistCore
from youtubesearchpython.core.social import SuggestionsCore
from youtubesearchpython.core.social import TranscriptCore
from youtubesearchpython.core.social import ChannelCore
from youtubesearchpython.core.video import RecommendationsCore


class Video:
    @staticmethod
    async def get(
        videoLink: str,
        resultMode: int = ResultMode.dict,
        timeout: int = None,
        get_upload_date: bool = False,
        po_token: str = None,
        visitor_data: str = None,
        proxy: str = None,
    ) -> Union[dict, None]:
        video = VideoCore(videoLink, None, resultMode, timeout, get_upload_date, "ANDROID", po_token, visitor_data, proxy)
        if get_upload_date:
            await video.async_html_create()
        await video.async_create()
        return video.result

    @staticmethod
    async def getInfo(
        videoLink: str, resultMode: int = ResultMode.dict, timeout: int = None, po_token: str = None, visitor_data: str = None, proxy: str = None
    ) -> Union[dict, None]:
        video = VideoCore(videoLink, "getInfo", resultMode, timeout, False, po_token=po_token, visitor_data=visitor_data, proxy=proxy)
        await video.async_create()
        return video.result

    @staticmethod
    async def getFormats(
        videoLink: str, resultMode: int = ResultMode.dict, timeout: int = None, po_token: str = None, visitor_data: str = None, proxy: str = None
    ) -> Union[dict, None]:
        video = VideoCore(videoLink, "getFormats", resultMode, timeout, False, po_token=po_token, visitor_data=visitor_data, proxy=proxy)
        await video.async_create()
        return video.result


class Suggestions:
    '''Autocomplete search suggestions (unrelated to Recommendations, which
    fetches related/up-next *videos* for a given video ID - kept as
    separate classes on purpose, not to be merged).

    NOTE: this used to define `get` twice in this class body - a
    @staticmethod one-shot version, then an instance version further down.
    The second definition silently overwrote the first in the class dict,
    so `Suggestions.get(query, ...)` was actually calling the unbound
    instance method with `query` bound to `self` -> AttributeError.
    `get` now stays a single staticmethod (matches how it's actually used
    everywhere in this codebase); reusable-session usage lives under
    `session()` instead, so both styles work without colliding.
    '''
    @staticmethod
    async def get(
        query: str, language: str = "en", region: str = "US", timeout: int = None, mode: int = ResultMode.dict
    ):
        suggestionsInternal = SuggestionsCore(language=language, region=region, timeout=timeout)
        return await suggestionsInternal._getAsync(query, mode)

    @staticmethod
    def session(language: str = "en", region: str = "US", timeout: int = None) -> "SuggestionsSession":
        '''Returns a reusable session object for repeated queries without
        recreating the underlying client each time:
        `s = Suggestions.session(); await s.get("query")`.'''
        return SuggestionsSession(language, region, timeout)


class SuggestionsSession:
    def __init__(self, language: str = "en", region: str = "US", timeout: int = None):
        self.suggestionsInternal = SuggestionsCore(language=language, region=region, timeout=timeout)

    async def get(self, query: str, mode: int = ResultMode.dict):
        return await self.suggestionsInternal._getAsync(query, mode)


class Playlist:
    def __init__(self, playlistLink: str, timeout: int = None):
        self.playlistLink = playlistLink
        self.timeout = timeout
        self.videos = []
        self.info = None
        self.hasMoreVideos = True
        self.__playlist = None

    async def init(self) -> None:
        self.__playlist = PlaylistCore(self.playlistLink, None, ResultMode.dict, self.timeout)
        await self.__playlist.async_create()
        self.info = copy.deepcopy(self.__playlist.result)
        self.videos = self.__playlist.result.get("videos", [])
        self.hasMoreVideos = self.__playlist.continuationKey is not None

    async def getNextVideos(self) -> None:
        if self.__playlist is None:
            await self.init()
            return self.info
        await self.__playlist._async_next()
        self.info = copy.deepcopy(self.__playlist.result)
        self.videos = self.__playlist.result.get("videos", [])
        self.hasMoreVideos = self.__playlist.continuationKey is not None
        return self.info

    @staticmethod
    async def get(playlistLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        playlist = PlaylistCore(playlistLink, None, mode, timeout)
        await playlist.async_create()
        return playlist.result

    @staticmethod
    async def getInfo(playlistLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        playlist = PlaylistCore(playlistLink, "getInfo", mode, timeout)
        await playlist.async_create()
        return playlist.result

    @staticmethod
    async def getVideos(playlistLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        playlist = PlaylistCore(playlistLink, "getVideos", mode, timeout)
        await playlist.async_create()
        return playlist.result


class Hashtag(HashtagCore):
    def __init__(
        self, hashtag: str, limit: int = 60, language: str = "en", region: str = "US", timeout: int = None
    ):
        super().__init__(hashtag, limit, language, region, timeout)

    @staticmethod
    async def get(hashtag: str, mode: int = ResultMode.dict, limit: int = 60, language: str = "en", region: str = "US", timeout: int = None):
        core = HashtagCore(hashtag, limit, language, region, timeout)
        await core.async_create()
        return core.result(mode)

    async def next(self) -> dict:
        return await self._nextAsync()


class Comments:
    def __init__(self, videoLink: str, timeout: int = None):
        self.timeout = timeout
        self.videoLink = videoLink
        self.comments = {"result": []}
        self.hasMoreComments = True
        self.__comments = None

    async def init(self) -> None:
        if self.__comments is None:
            self.__comments = CommentsCore(self.videoLink, self.timeout)
            await self.__comments.async_create()
            self.comments = self.__comments.commentsComponent
            self.hasMoreComments = self.__comments.continuationKey is not None

    async def getNextComments(self) -> None:
        if self.__comments is None:
            self.__comments = CommentsCore(self.videoLink, self.timeout)
            await self.__comments.async_create()
        else:
            await self.__comments.async_create_next()
        self.comments = self.__comments.commentsComponent
        self.hasMoreComments = self.__comments.continuationKey is not None
        return self.comments

    @staticmethod
    async def get(videoLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        pc = CommentsCore(videoLink, timeout)
        await pc.async_create()
        if mode == ResultMode.json:
            import json
            return json.dumps(pc.commentsComponent, indent=4)
        return pc.commentsComponent


class Transcript:
    @staticmethod
    async def get(videoLink: str, params: str = None, mode: int = ResultMode.dict, timeout: int = None):
        transcript_core = TranscriptCore(videoLink, params, timeout)
        await transcript_core.async_create()
        if mode == ResultMode.json:
            import json
            return json.dumps(transcript_core.result, indent=4)
        return transcript_core.result


class Channel(ChannelCore):
    def __init__(self, channel_id: str, request_type: str = ChannelRequestType.playlists, timeout: int = None):
        super().__init__(channel_id, request_type, timeout)

    async def init(self):
        await self.async_create()

    async def next(self):
        await self.async_next()

    @staticmethod
    async def get(channel_id: str, request_type: str = ChannelRequestType.playlists, timeout: int = None):
        channel_core = ChannelCore(channel_id, request_type, timeout)
        await channel_core.async_create()
        return channel_core.result

class Recommendations:
    @staticmethod
    async def get(videoId: str, timeout: int = None) -> Union[dict, None]:
        recommendations_core = RecommendationsCore(videoId, timeout)
        await recommendations_core.async_create()
        return recommendations_core.resultComponents        


from typing import Optional, Union

from youtubesearchpython.core.video import StreamURLFetcherCore


class StreamURLFetcher(StreamURLFetcherCore):
    def __init__(self, proxy: str = None, cookies_file: str = None, po_token: str = None, visitor_data: str = None):
        super().__init__(proxy, cookies_file, po_token, visitor_data)

    async def _formats(self, source: Union[dict, str]) -> dict:
        if isinstance(source, dict):
            return source
        from youtubesearchpython.future.extras import Video
        return await Video.getFormats(source, po_token=self.po_token, visitor_data=self.visitor_data, proxy=self.proxy)

    async def get(self, videoFormats: Union[dict, str], itag: int, po_token: Optional[str] = None) -> Union[str, None]:
        if po_token is not None:
            self.set_po_token(po_token)
        self._getDecipheredURLs(await self._formats(videoFormats), itag)
        return self._streams[0]["url"] if len(self._streams) == 1 else None

    async def getAll(self, videoFormats: Union[dict, str], po_token: Optional[str] = None) -> dict:
        if po_token is not None:
            self.set_po_token(po_token)
        self._getDecipheredURLs(await self._formats(videoFormats))
        return {"streams": self._streams, "unresolved": self.unresolved()}


from youtubesearchpython.core.utils import *
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import aclose_clients, close_clients

__title__='yt-search-python'
__version__='2.2.1'
__author__='Prakhar-Shukla'
__license__='MIT'
__all__=['Search','VideosSearch','ChannelsSearch','PlaylistsSearch','CustomSearch','ChannelSearch','Video','Playlist','Suggestions','SuggestionsSession','Hashtag','Comments','Transcript','Channel','Recommendations','StreamURLFetcher','aclose_clients','close_clients','ResultMode','SearchMode','VideoUploadDateFilter','VideoDurationFilter','VideoSortOrder','ChannelRequestType','playlist_from_channel_id']
import sys as _sys
for _name in ('search','extras','streamurlfetcher'):
    _sys.modules[f'{__name__}.{_name}']=_sys.modules[__name__]

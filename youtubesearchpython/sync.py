from typing import Optional
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.search import SearchCore
from youtubesearchpython.core.search import ChannelSearchCore


class Search(SearchCore):
    '''Searches for videos, channels & playlists in YouTube.

    Args:
        query (str): Sets the search query.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Timeout for the request in seconds.
    See Also:
        For usage examples and output structure, see docs/search_examples.md
    '''
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: int = None):
        self.searchMode = (True, True, True)
        super().__init__(query, limit, language, region, None, timeout)
        self.sync_create()
        self._getComponents(*self.searchMode)

    def next(self) -> bool:
        return self._next()

class VideosSearch(SearchCore):
    '''Searches for videos in YouTube.
    Args:
        query (str): Sets the search query.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Timeout for the request in seconds.
        is_live (bool, optional): When True, returns live streams only.
    See Also:
        For usage examples and output structure, see docs/search_examples.md
    '''
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: int = None, is_live: Optional[bool] = None):
        self.searchMode = (True, False, False)
        super().__init__(query, limit, language, region, SearchMode.livestreams if is_live else SearchMode.videos, timeout)
        self.sync_create()
        self._getComponents(*self.searchMode)

    def next(self) -> bool:
        return self._next()


class ChannelsSearch(SearchCore):
    '''Searches for channels in YouTube.
    Args:
        query (str): Sets the search query.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Timeout for the request in seconds. 
    See Also:
        For usage examples and output structure, see docs/search_examples.md
    '''
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: int = None):
        self.searchMode = (False, True, False)
        super().__init__(query, limit, language, region, SearchMode.channels, timeout)
        self.sync_create()
        self._getComponents(*self.searchMode)

    def next(self) -> bool:
        return self._next()


class PlaylistsSearch(SearchCore):
    '''Searches for playlists in YouTube.
    Args:
        query (str): Sets the search query.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Timeout for the request in seconds.
    See Also:
        For usage examples and output structure, see docs/search_examples.md
    '''
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: int = None):
        self.searchMode = (False, False, True)
        super().__init__(query, limit, language, region, SearchMode.playlists, timeout)
        self.sync_create()
        self._getComponents(*self.searchMode)

    def next(self) -> bool:
        return self._next()


class ChannelSearch(ChannelSearchCore):
    '''Searches for videos in specific channel in YouTube.
    Args:
        query (str): Sets the search query.
        browseId (str): Channel ID to search within.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        searchPreferences (str, optional): Custom search preferences parameter.
        timeout (int, optional): Timeout for the request in seconds.
    See Also:
        For usage examples and output structure, see docs/search_examples.md
    '''

    def __init__(self, query: str, browseId: str, language: str = 'en', region: str = 'US', searchPreferences: str = "EgZzZWFyY2g%3D", timeout: int = None):
        super().__init__(query, language, region, searchPreferences, browseId, timeout)
        self.sync_create()

    def next(self):
        return self.sync_next()


class CustomSearch(SearchCore):
    '''Performs custom search in YouTube with search filters or sorting orders. 
       Predefined filters and sorting orders:
        - SearchMode.videos, SearchMode.channels, SearchMode.playlists
        - VideoUploadDateFilter.lastHour, .today, .thisWeek, .thisMonth, .thisYear
        - VideoDurationFilter.short, .long
        - VideoSortOrder.relevance, .uploadDate, .viewCount, .rating

    The value of `sp` parameter in the YouTube search query can be used as a search filter.
    Example: `EgQIBRAB` from https://www.youtube.com/results?search_query=NoCopyrightSounds&sp=EgQIBRAB 
    can be passed as `searchPreferences` to get videos uploaded this year.
    Args:
        query (str): Sets the search query.
        searchPreferences (str): Sets the `sp` query parameter in the YouTube search request.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Timeout for the request in seconds.
    See Also:
        For usage examples and available filters, see docs/search_examples.md
    '''
    def __init__(self, query: str, searchPreferences: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: int = None):
        self.searchMode = (True, True, True)
        super().__init__(query, limit, language, region, searchPreferences, timeout)
        self.sync_create()
        self._getComponents(*self.searchMode)
    
    def next(self):
        return self._next()


from typing import Union

from youtubesearchpython.core.social import ChannelCore
from youtubesearchpython.core.social import CommentsCore
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.social import HashtagCore
from youtubesearchpython.core.playlist import PlaylistCore
from youtubesearchpython.core.video import RecommendationsCore
from youtubesearchpython.core.social import SuggestionsCore
from youtubesearchpython.core.social import TranscriptCore
from youtubesearchpython.core.video import VideoCore


class Video:
    @staticmethod
    def get(videoLink: str, mode: int = ResultMode.dict, timeout: int = None, get_upload_date: bool = False, po_token: str = None, visitor_data: str = None, proxy: str = None) -> Union[
        dict, str, None]:
        '''Fetches information and formats for the given video link or ID.
        Returns None if video is unavailable.
        '''
        videoInternal = VideoCore(videoLink, None, mode, timeout, get_upload_date, po_token=po_token, visitor_data=visitor_data, proxy=proxy)
        if get_upload_date:
            videoInternal.sync_html_create()
        videoInternal.sync_create()
        return videoInternal.result

    @staticmethod
    def getInfo(videoLink: str, mode: int = ResultMode.dict, timeout: int = None, po_token: str = None, visitor_data: str = None, proxy: str = None) -> Union[dict, str, None]:
        '''Fetches only metadata (no streaming formats) for the given video link or ID.'''
        videoInternal = VideoCore(videoLink, "getInfo", mode, timeout, False, po_token=po_token, visitor_data=visitor_data, proxy=proxy)
        videoInternal.sync_create()
        return videoInternal.result

    @staticmethod
    def getFormats(videoLink: str, mode: int = ResultMode.dict, timeout: int = None, po_token: str = None, visitor_data: str = None, proxy: str = None) -> Union[
        dict, str, None]:
        '''Fetches only streaming formats for the given video link or ID.
        Returns None if video is unavailable.
        '''
        videoInternal = VideoCore(videoLink, "getFormats", mode, timeout, False, po_token=po_token, visitor_data=visitor_data, proxy=proxy)
        videoInternal.sync_create()
        return videoInternal.result


class Playlist:
    @staticmethod
    def get(playlistLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        playlistInternal = PlaylistCore(playlistLink, None, mode, timeout)
        playlistInternal.sync_create()
        return playlistInternal.result

    @staticmethod
    def getInfo(playlistLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        playlistInternal = PlaylistCore(playlistLink, "getInfo", mode, timeout)
        playlistInternal.sync_create()
        return playlistInternal.result

    @staticmethod
    def getVideos(playlistLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        playlistInternal = PlaylistCore(playlistLink, "getVideos", mode, timeout)
        playlistInternal.sync_create()
        return playlistInternal.result

    def __init__(self, playlistLink: str, timeout: int = None):
        self.result = None
        self.playlistLink = playlistLink
        self.timeout = timeout
        self.continuationKey = None
        self.hasMoreVideos = True
        self._playlist = PlaylistCore(self.playlistLink, None, ResultMode.dict, self.timeout)
        self._getFirstPage()

    def _getFirstPage(self):
        self._playlist.sync_create()
        self.result = self._playlist.result
        self.continuationKey = self._playlist.continuationKey
        self.hasMoreVideos = bool(self.continuationKey)

    def getNextVideos(self):
        if self.hasMoreVideos:
            self._playlist._next()
            self.result = self._playlist.result
            self.continuationKey = self._playlist.continuationKey
            self.hasMoreVideos = bool(self.continuationKey)
        return self.result


class Suggestions:
    '''Autocomplete search suggestions (unrelated to Recommendations, which
    fetches related/up-next *videos* for a given video ID - the two are
    kept as separate classes on purpose since they hit different endpoints
    and serve different purposes).

    NOTE: this used to define `get` twice in this class body - once as a
    @staticmethod, once as an instance method. The second definition
    silently overwrote the first in the class dict, so `Suggestions.get(...)`
    was actually calling the *instance* method unbound, with the query
    string bound to `self` -> AttributeError. Only one `get` can exist now.
    '''
    @staticmethod
    def get(query: str, language: str = 'en', region: str = 'US', timeout: int = None,
            mode: int = ResultMode.dict) -> Union[dict, str, None]:
        suggestionsInternal = SuggestionsCore(language, region, timeout)
        return suggestionsInternal._get(query, mode)

    @staticmethod
    def session(language: str = 'en', region: str = 'US', timeout: int = None) -> "SuggestionsSession":
        '''Returns a reusable session object for repeated queries without
        recreating the underlying client each time:
        `s = Suggestions.session(); s.get("query")`.'''
        return SuggestionsSession(language, region, timeout)


class SuggestionsSession:
    def __init__(self, language: str = 'en', region: str = 'US', timeout: int = None):
        self.suggestionsInternal = SuggestionsCore(language, region, timeout)

    def get(self, query: str, mode: int = ResultMode.dict) -> Union[dict, str, None]:
        return self.suggestionsInternal._get(query, mode)


class Hashtag(HashtagCore):
    '''Instance form fetches on construction (matches VideosSearch-style
    usage: `Hashtag("Bharat", limit=5).result()`, then `.next()` for more).
    A one-shot `Hashtag.get(...)` static helper is also available.
    '''
    def __init__(self, hashtag: str, limit: int = 60, language: str = 'en', region: str = 'US', timeout: int = None):
        super().__init__(hashtag, limit, language, region, timeout)
        self.sync_create()

    @staticmethod
    def get(hashtag: str, mode: int = ResultMode.dict, limit: int = 60, language: str = 'en',
            region: str = 'US', timeout: int = None) -> Union[dict, str, None]:
        hashtagInternal = HashtagCore(hashtag, limit, language, region, timeout)
        hashtagInternal.sync_create()
        return hashtagInternal.result(mode)


class Comments:
    def __init__(self, videoLink: str, timeout: int = None):
        self.videoLink = videoLink
        self.timeout = timeout
        self.comments = {"result": []}
        self.hasMoreComments = True
        self.__comments = None

    def init(self) -> None:
        if self.__comments is None:
            self.__comments = CommentsCore(self.videoLink, self.timeout)
            self.__comments.sync_create()
            self.comments = self.__comments.commentsComponent
            self.hasMoreComments = self.__comments.continuationKey is not None

    def getNextComments(self) -> dict:
        if self.__comments is None:
            self.init()
        else:
            self.__comments.sync_create_next()
            self.comments = self.__comments.commentsComponent
            self.hasMoreComments = self.__comments.continuationKey is not None
        return self.comments

    @staticmethod
    def get(videoLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[
        dict, str, None]:
        commentsInternal = CommentsCore(videoLink, timeout)
        commentsInternal.sync_create()
        if mode == ResultMode.json:
            import json
            return json.dumps(commentsInternal.commentsComponent, indent=4)
        return commentsInternal.commentsComponent


class Transcript:
    @staticmethod
    def get(videoLink: str, params: str = None, mode: int = ResultMode.dict, timeout: int = None) -> Union[
        dict, str, None]:
        '''`params` is the languageCode of a specific caption track, as
        returned in `languages[i]["params"]` from a previous call - pass it
        to fetch that language instead of the default/first one.
        NOTE: previously this always passed None through, so requesting an
        alternate language track silently did nothing.
        '''
        transcriptInternal = TranscriptCore(videoLink, params, timeout)
        transcriptInternal.sync_create()
        if mode == ResultMode.json:
            import json
            return json.dumps(transcriptInternal.result, indent=4)
        return transcriptInternal.result


class Channel(ChannelCore):
    '''Instance form: `Channel(id)` then `.init()`, `.next()`,
    `.has_more_playlists()`. A one-shot `Channel.get(...)` static helper is
    also available for a single call.
    '''
    def __init__(self, channel_id: str, request_type: str = ChannelRequestType.playlists, timeout: int = None):
        super().__init__(channel_id, request_type, timeout)

    def init(self):
        self.sync_create()

    def next(self):
        self.sync_next()

    @staticmethod
    def get(channelId: str, mode: str = ChannelRequestType.playlists, timeout: int = None) -> Union[
        dict, str, None]:
        channelInternal = ChannelCore(channelId, mode, timeout)
        channelInternal.sync_create()
        return channelInternal.result


class Recommendations:
    '''Related/up-next videos for a given video ID. Kept separate from
    Suggestions (autocomplete text) - different endpoint, different data,
    should not be merged into one class.
    '''
    @staticmethod
    def get(videoId: str, timeout: int = None) -> Union[
        dict, str, None]:
        recommendationsInternal = RecommendationsCore(videoId, timeout)
        recommendationsInternal.sync_create()
        return recommendationsInternal.resultComponents
            


from typing import Optional, Union

from youtubesearchpython.core.video import StreamURLFetcherCore


class StreamURLFetcher(StreamURLFetcherCore):
    def __init__(self, proxy: str = None, cookies_file: str = None, po_token: str = None, visitor_data: str = None):
        super().__init__(proxy, cookies_file, po_token, visitor_data)

    def _formats(self, source: Union[dict, str]) -> dict:
        if isinstance(source, dict):
            return source
        from youtubesearchpython.extras import Video
        return Video.getFormats(source, po_token=self.po_token, visitor_data=self.visitor_data, proxy=self.proxy)

    def get(self, videoFormats: Union[dict, str], itag: int, po_token: Optional[str] = None) -> Union[str, None]:
        if po_token is not None:
            self.set_po_token(po_token)
        self._getDecipheredURLs(self._formats(videoFormats), itag)
        return self._streams[0]["url"] if len(self._streams) == 1 else None

    def getAll(self, videoFormats: Union[dict, str], po_token: Optional[str] = None) -> dict:
        if po_token is not None:
            self.set_po_token(po_token)
        self._getDecipheredURLs(self._formats(videoFormats))
        return {"streams": self._streams, "unresolved": self.unresolved()}

import copy
from typing import Union

from youtubesearchpython.core.channel import ChannelCore
from youtubesearchpython.core.comments import CommentsCore
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.hashtag import HashtagCore
from youtubesearchpython.core.playlist import PlaylistCore
from youtubesearchpython.core.recommendations import RecommendationsCore
from youtubesearchpython.core.suggestions import SuggestionsCore
from youtubesearchpython.core.transcript import TranscriptCore
from youtubesearchpython.core.video import VideoCore


class Video:
    @staticmethod
    def get(videoLink: str, mode: int = ResultMode.dict, timeout: int = None, get_upload_date: bool = False) -> Union[
        dict, str, None]:
        '''Fetches information and formats for the given video link or ID.
        Returns None if video is unavailable.
        '''
        videoInternal = VideoCore(videoLink, None, mode, timeout, get_upload_date)
        if get_upload_date:
            videoInternal.sync_html_create()
        videoInternal.sync_create()
        return videoInternal.result

    @staticmethod
    def getInfo(videoLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        '''Fetches only metadata (no streaming formats) for the given video link or ID.'''
        videoInternal = VideoCore(videoLink, "getInfo", mode, timeout, False)
        videoInternal.sync_create()
        return videoInternal.result

    @staticmethod
    def getFormats(videoLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[
        dict, str, None]:
        '''Fetches only streaming formats for the given video link or ID.
        Returns None if video is unavailable.
        '''
        videoInternal = VideoCore(videoLink, "getFormats", mode, timeout, False)
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
        self._getFirstPage()

    def _getFirstPage(self):
        playlistInternal = PlaylistCore(self.playlistLink, None, ResultMode.dict, self.timeout)
        playlistInternal.sync_create()
        self.result = playlistInternal.result
        self.continuationKey = playlistInternal.continuationKey
        if not self.continuationKey:
            self.hasMoreVideos = False

    def getNextVideos(self):
        if self.hasMoreVideos:
            playlistInternal = PlaylistCore(self.playlistLink, None, ResultMode.dict, self.timeout)
            playlistInternal.continuationKey = self.continuationKey
            playlistInternal.sync_create()
            self.result['videos'].extend(playlistInternal.result['videos'])
            self.continuationKey = playlistInternal.continuationKey
            if not self.continuationKey:
                self.hasMoreVideos = False
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
            self.__comments = CommentsCore(self.videoLink)
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
        commentsInternal = CommentsCore(videoLink)
        commentsInternal.sync_create()
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
        transcriptInternal = TranscriptCore(videoLink, params)
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
    def __init__(self, channel_id: str, request_type: str = ChannelRequestType.playlists):
        super().__init__(channel_id, request_type)

    def init(self):
        self.sync_create()

    def next(self):
        self.sync_next()

    @staticmethod
    def get(channelId: str, mode: str = ChannelRequestType.playlists, timeout: int = None) -> Union[
        dict, str, None]:
        channelInternal = ChannelCore(channelId, mode)
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
            

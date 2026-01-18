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
        videoInternal = VideoCore(videoLink, None, mode, timeout, False)
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
        return videoInternal.formats


class Playlist:
    @staticmethod
    def get(playlistLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        playlistInternal = PlaylistCore(playlistLink, None, mode, timeout)
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
    @staticmethod
    def get(query: str, language: str = 'en', region: str = 'US', timeout: int = None) -> Union[
        dict, str, None]:
        suggestionsInternal = SuggestionsCore(language, region, timeout)
        return suggestionsInternal._get(query)

    def __init__(self, language: str = 'en', region: str = 'US', timeout: int = None):
        self.suggestionsInternal = SuggestionsCore(language, region, timeout)

    def get(self, query: str, mode: int = ResultMode.dict) -> Union[dict, str, None]:
        return self.suggestionsInternal._get(query, mode)


class Hashtag:
    @staticmethod
    def get(hashtag: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[
        dict, str, None]:
        hashtagInternal = HashtagCore(hashtag, mode, timeout)
        hashtagInternal.sync_create()
        return hashtagInternal.result


class Comments:
    @staticmethod
    def get(videoLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[
        dict, str, None]:
        commentsInternal = CommentsCore(videoLink)
        commentsInternal.sync_create()
        return commentsInternal.commentsComponent


class Transcript:
    @staticmethod
    def get(videoLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[
        dict, str, None]:
        transcriptInternal = TranscriptCore(videoLink, None)
        transcriptInternal.sync_create()
        if mode == ResultMode.json:
            import json
            return json.dumps(transcriptInternal.result, indent=4)
        return transcriptInternal.result


class Channel:
    @staticmethod
    def get(channelId: str, mode: str = ChannelRequestType.playlists, timeout: int = None) -> Union[
        dict, str, None]:
        channelInternal = ChannelCore(channelId, mode)
        channelInternal.sync_create()
        return channelInternal.result


class Recommendations:
    @staticmethod
    def get(videoId: str, timeout: int = None) -> Union[
        dict, str, None]:
        recommendationsInternal = RecommendationsCore(videoId, timeout)
        recommendationsInternal.sync_create()
        return recommendationsInternal.resultComponents

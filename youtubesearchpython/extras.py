import copy
from typing import Union

from youtubesearchpython.core import VideoCore
from youtubesearchpython.core.comments import CommentsCore
from youtubesearchpython.core.hashtag import HashtagCore
from youtubesearchpython.core.playlist import PlaylistCore
from youtubesearchpython.core.suggestions import SuggestionsCore
from youtubesearchpython.core.transcript import TranscriptCore
from youtubesearchpython.core.channel import ChannelCore
from youtubesearchpython.core.constants import *


class Video:
    @staticmethod
    def get(videoLink: str, mode: int = ResultMode.dict, timeout: int = None, get_upload_date: bool = False) -> Union[
        dict, str, None]:
        '''Fetches information and formats for the given video link or ID.
        Returns None if video is unavailable.
        '''
        videoInternal = VideoCore(videoLink, mode, timeout, get_upload_date)
        videoInternal.sync_create()
        return videoInternal.result

    @staticmethod
    def getFormats(videoLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[
        dict, str, None]:
        '''Fetches only streaming formats for the given video link or ID.
        Returns None if video is unavailable.
        '''
        videoInternal = VideoCore(videoLink, mode, timeout)
        videoInternal.sync_create()
        return videoInternal.formats


class Playlist:
    @staticmethod
    def get(playlistLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        playlistInternal = PlaylistCore(playlistLink, mode, timeout)
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
        playlistInternal = PlaylistCore(self.playlistLink, ResultMode.dict, self.timeout)
        playlistInternal.sync_create()
        self.result = playlistInternal.result
        self.continuationKey = playlistInternal.continuationKey
        if not self.continuationKey:
            self.hasMoreVideos = False

    def getNextVideos(self):
        if self.hasMoreVideos:
            playlistInternal = PlaylistCore(self.playlistLink, ResultMode.dict, self.timeout)
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
        suggestionsInternal.sync_create(query)
        return suggestionsInternal.result


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
        commentsInternal = CommentsCore(videoLink, mode, timeout)
        commentsInternal.sync_create()
        return commentsInternal.result


class Transcript:
    @staticmethod
    def get(videoLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[
        dict, str, None]:
        transcriptInternal = TranscriptCore(videoLink, None)
        transcriptInternal.sync_create()
        if mode == ResultMode.json:
            import json
            return json.dumps(transcriptInternal.result)
        return transcriptInternal.result


class Channel:
    @staticmethod
    def get(channelId: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[
        dict, str, None]:
        channelInternal = ChannelCore(channelId, mode, timeout)
        channelInternal.sync_create()
        return channelInternal.result

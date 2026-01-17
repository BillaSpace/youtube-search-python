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

        Args:
            videoLink (str): Link or ID of the video on YouTube.
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.
            timeout (int, optional): Timeout for the request in seconds.
            get_upload_date (bool, optional): Whether to fetch upload date. Defaults to False.

        Returns:
            Union[dict, str, None]: Video information as dict or JSON string, None if unavailable.
        
        See Also:
            For usage examples and output structure, see docs/examples/extras_examples.md
        '''
        videoInternal = VideoCore(videoLink, mode, timeout, get_upload_date)
        videoInternal.sync_create()
        return videoInternal.result

    @staticmethod
    def getFormats(videoLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        '''Fetches only streaming formats for the given video link or ID.
        Returns None if video is unavailable.

        Args:
            videoLink (str): Link or ID of the video on YouTube.
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.
            timeout (int, optional): Timeout for the request in seconds.

        Returns:
            Union[dict, str, None]: Streaming formats as dict or JSON string, None if unavailable.
        
        See Also:
            For usage examples, see docs/examples/extras_examples.md
        '''
        videoInternal = VideoCore(videoLink, mode, timeout)
        videoInternal.sync_create()
        return videoInternal.formats


class Playlist:
    @staticmethod
    def get(playlistLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        '''Fetches playlist information for the given playlist link or ID.

        Args:
            playlistLink (str): Link or ID of the playlist on YouTube.
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.
            timeout (int, optional): Timeout for the request in seconds.

        Returns:
            Union[dict, str, None]: Playlist information including videos.
        
        See Also:
            For usage examples and output structure, see docs/examples/extras_examples.md
        '''
        playlistInternal = PlaylistCore(playlistLink, mode, timeout)
        playlistInternal.sync_create()
        return playlistInternal.result

    def __init__(self, playlistLink: str, timeout: int = None):
        '''Creates a Playlist object for pagination.

        Args:
            playlistLink (str): Link or ID of the playlist on YouTube.
            timeout (int, optional): Timeout for the request in seconds.
        
        See Also:
            For pagination examples, see docs/examples/extras_examples.md
        '''
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
        '''Fetches the next set of videos in the playlist.

        Returns:
            dict: Updated result with additional videos.
        '''
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
    def get(query: str, language: str = 'en', region: str = 'US', timeout: int = None) -> Union[dict, str, None]:
        '''Gets search suggestions for the given query.

        Args:
            query (str): Search query to get suggestions for.
            language (str, optional): Sets the suggestion language. Defaults to 'en'.
            region (str, optional): Sets the suggestion region. Defaults to 'US'.
            timeout (int, optional): Timeout for the request in seconds.

        Returns:
            Union[dict, str, None]: Dictionary with 'result' key containing list of suggestions.
        
        See Also:
            For usage examples, see docs/examples/extras_examples.md
        '''
        suggestionsInternal = SuggestionsCore(language, region, timeout)
        suggestionsInternal.sync_create(query)
        return suggestionsInternal.result


class Hashtag:
    @staticmethod
    def get(hashtag: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        '''Gets videos for a given hashtag.

        Args:
            hashtag (str): Hashtag to search for (with or without # symbol).
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.
            timeout (int, optional): Timeout for the request in seconds.

        Returns:
            Union[dict, str, None]: Videos associated with the hashtag.
        
        See Also:
            For usage examples, see docs/examples/extras_examples.md
        '''
        hashtagInternal = HashtagCore(hashtag, mode, timeout)
        hashtagInternal.sync_create()
        return hashtagInternal.result


class Comments:
    @staticmethod
    def get(videoLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        '''Gets comments for a given video.

        Args:
            videoLink (str): Link or ID of the video on YouTube.
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.
            timeout (int, optional): Timeout for the request in seconds.

        Returns:
            Union[dict, str, None]: Comments with author, content, likes, etc.
        
        See Also:
            For usage examples and output structure, see docs/examples/extras_examples.md
        '''
        commentsInternal = CommentsCore(videoLink, mode, timeout)
        commentsInternal.sync_create()
        return commentsInternal.result


class Transcript:
    @staticmethod
    def get(videoLink: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        '''Gets transcript/captions for a given video.

        Args:
            videoLink (str): Link or ID of the video on YouTube.
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.
            timeout (int, optional): Timeout for the request in seconds.

        Returns:
            Union[dict, str, None]: Transcript segments and available languages.
        
        See Also:
            For usage examples and output structure, see docs/examples/extras_examples.md
        '''
        transcriptInternal = TranscriptCore(videoLink, None)
        transcriptInternal.sync_create()
        if mode == ResultMode.json:
            import json
            return json.dumps(transcriptInternal.result)
        return transcriptInternal.result


class Channel:
    @staticmethod
    def get(channelId: str, mode: int = ResultMode.dict, timeout: int = None) -> Union[dict, str, None]:
        '''Gets channel information for a given channel ID.

        Args:
            channelId (str): Channel ID (not channel URL).
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.
            timeout (int, optional): Timeout for the request in seconds.

        Returns:
            Union[dict, str, None]: Channel information including title, description, subscriber count, etc.
        
        See Also:
            For usage examples and output structure, see docs/examples/extras_examples.md
        '''
        channelInternal = ChannelCore(channelId, mode, timeout)
        channelInternal.sync_create()
        return channelInternal.result

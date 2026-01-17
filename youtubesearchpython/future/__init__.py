"""
Asynchronous implementation of yt-search-python.

This module provides async/await versions of all search and retrieval operations.
Use this for async applications, web frameworks (FastAPI, aiohttp), or when you need concurrent operations.
"""

from youtubesearchpython.future.search import Search, VideosSearch, ChannelsSearch, PlaylistsSearch, CustomSearch, ChannelSearch
from youtubesearchpython.future.extras import Video, Playlist, Suggestions, Hashtag, Comments, Transcript, Channel, Recommendations
from youtubesearchpython.future.streamurlfetcher import StreamURLFetcher
from youtubesearchpython.core.utils import *
from youtubesearchpython.core.constants import *


__title__        = 'youtube-search-python'
__version__      = '2.0.0'    
__author__       = 'Prakhar'
__license__      = 'MIT'

__all__ = [
    'Search', 'VideosSearch', 'ChannelsSearch', 'PlaylistsSearch', 
    'CustomSearch', 'ChannelSearch', 'Video', 'Playlist', 'Suggestions',
    'Hashtag', 'Comments', 'Transcript', 'Channel', 'Recommendations', 'StreamURLFetcher',
    'ResultMode', 'SearchMode', 'VideoUploadDateFilter', 'VideoDurationFilter',
    'VideoSortOrder', 'ChannelRequestType', 'playlist_from_channel_id'
]

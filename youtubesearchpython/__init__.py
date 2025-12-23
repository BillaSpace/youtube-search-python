"""
youtube-search-python v2 (updated & enhanced)
This is a maintained fork by Prakhar / Rajnish Mishra with compatibility fixes for httpx>=0.28.1+.
Original project by Hitesh Kumar Saini (alexmercerind).
"""

from youtubesearchpython.search import Search, VideosSearch, ChannelsSearch, PlaylistsSearch, CustomSearch, ChannelSearch
from youtubesearchpython.extras import Video, Playlist, Suggestions, Hashtag, Comments, Transcript, Channel
from youtubesearchpython.streamurlfetcher import StreamURLFetcher
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.utils import *

__title__        = 'youtube-search-python'
__version__      = '1.6.9+master'
__author__       = 'Prakhar'
__license__      = 'MIT'

''' Deprecated. Present for legacy support. '''
from youtubesearchpython.legacy import SearchVideos, SearchPlaylists
from youtubesearchpython.legacy import SearchVideos as searchYoutube

"""
youtube-search-python v2 as yt-search-python (upgraded & enhanced)
This is a maintained fork by Prakhar shukla with compatibility fixes for httpx>=0.28.1+.
Original project by Hitesh Kumar Saini (alexmercerind).
"""

from youtubesearchpython.search import Search, VideosSearch, ChannelsSearch, PlaylistsSearch, CustomSearch, ChannelSearch
from youtubesearchpython.extras import Video, Playlist, Suggestions, SuggestionsSession, Hashtag, Comments, Transcript, Channel, Recommendations
from youtubesearchpython.streamurlfetcher import StreamURLFetcher
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.utils import *

__title__        = 'yt-search-python'
__version__      = '2.1.0'
__author__       = 'Prakhar-Shukla'
__license__      = 'MIT'

''' Deprecated. Present for legacy support. '''
from youtubesearchpython.legacy import SearchVideos, SearchPlaylists
from youtubesearchpython.legacy import SearchVideos as searchYoutube

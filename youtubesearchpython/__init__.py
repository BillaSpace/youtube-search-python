from youtubesearchpython.sync import Search, VideosSearch, ChannelsSearch, PlaylistsSearch, CustomSearch, ChannelSearch, Video, Playlist, Suggestions, SuggestionsSession, Hashtag, Comments, Transcript, Channel, Recommendations, StreamURLFetcher
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.utils import *
from youtubesearchpython.core.requests import close_clients
__title__='yt-search-python'
__version__='2.2.1'
__author__='Prakhar-Shukla'
__license__='MIT'
from youtubesearchpython.legacy import SearchVideos, SearchPlaylists
from youtubesearchpython.legacy import SearchVideos as searchYoutube
import sys as _sys
from youtubesearchpython import sync as _sync
for _name in ('search','extras','streamurlfetcher'): _sys.modules[f'{__name__}.{_name}']=_sync

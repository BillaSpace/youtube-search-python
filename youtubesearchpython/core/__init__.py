from .video import VideoCore, RecommendationsCore, StreamURLFetcherCore
from .playlist import PlaylistCore
from .search import SearchCore, ChannelSearchCore
from .social import ChannelCore, CommentsCore, HashtagCore, SuggestionsCore, TranscriptCore
from .constants import *
import sys as _sys
from . import search as _search, video as _video, social as _social, requests as _requests
_aliases={'channelsearch':_search,'channel':_social,'comments':_social,'hashtag':_social,'suggestions':_social,'transcript':_social,'recommendations':_video,'streamurlfetcher':_video,'cookies':_requests,'exceptions':_requests}
for _name,_module in _aliases.items(): _sys.modules[f'{__name__}.{_name}']=_module

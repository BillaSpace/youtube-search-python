from youtubesearchpython.core.constants import *
from youtubesearchpython.core.search import SearchCore
from youtubesearchpython.core.channelsearch import ChannelSearchCore


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
    
    See Also:
        For usage examples and output structure, see docs/search_examples.md
    '''
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: int = None):
        self.searchMode = (True, False, False)
        super().__init__(query, limit, language, region, SearchMode.videos, timeout)
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
        return self.sync_create()


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
        self._next()

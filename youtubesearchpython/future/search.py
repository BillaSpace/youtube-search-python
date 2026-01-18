from typing import Any, Dict, Optional

from youtubesearchpython.core.channelsearch import ChannelSearchCore
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.search import SearchCore


class Search(SearchCore):
    '''Searches for videos, channels & playlists in YouTube (async version).

    Args:
        query (str): Sets the search query.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Sets the request timeout in seconds.
    
    See Also:
        For usage examples, see docs/earch_examples.md (use await with async methods)
    '''
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (True, True, True)
        super().__init__(query, limit, language, region, None, timeout)

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()


class VideosSearch(SearchCore):
    '''Searches for videos in YouTube (async version).

    Args:
        query (str): Sets the search query.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Sets the request timeout in seconds.
    
    See Also:
        For usage examples, see docs/search_examples.md (use await with async methods)
    '''
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (True, False, False)
        super().__init__(query, limit, language, region, SearchMode.videos, timeout)  # type: ignore

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()


class ChannelsSearch(SearchCore):
    '''Searches for channels in YouTube (async version).

    Args:
        query (str): Sets the search query.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Sets the request timeout in seconds.
    
    See Also:
        For usage examples, see docs/search_examples.md (use await with async methods)
    '''
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (False, True, False)
        super().__init__(query, limit, language, region, SearchMode.channels, timeout)

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()


class PlaylistsSearch(SearchCore):
    '''Searches for playlists in YouTube (async version).

    Args:
        query (str): Sets the search query.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Sets the request timeout in seconds.
    
    See Also:
        For usage examples, see docs/search_examples.md (use await with async methods)
    '''
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (False, False, True)
        super().__init__(query, limit, language, region, SearchMode.playlists, timeout)

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()


class ChannelSearch(ChannelSearchCore):
    '''Searches for videos in specific channel in YouTube (async version).

    Args:
        query (str): Sets the search query.
        browseId (str): Channel ID to search within.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        searchPreferences (str, optional): Custom search preferences parameter.
        timeout (int, optional): Sets the request timeout in seconds.
    
    See Also:
        For usage examples, see docs/search_examples.md (use await with async methods)
    '''
    def __init__(self, query: str, browseId: str, language: str = 'en', region: str = 'US', searchPreferences: str = "EgZzZWFyY2g%3D", timeout: Optional[int] = None):
        super().__init__(query, language, region, searchPreferences, browseId, timeout)

    async def next(self) -> Dict[str, Any]:
        return await self.async_create()


class CustomSearch(SearchCore):
    '''Performs custom search in YouTube with search filters or sorting orders (async version).

    Args:
        query (str): Sets the search query.
        searchPreferences (str): Sets the `sp` query parameter in the YouTube search request.
        limit (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en'.
        region (str, optional): Sets the result region. Defaults to 'US'.
        timeout (int, optional): Sets the request timeout in seconds.
    
    See Also:
        For usage examples and available filters, see docs/search_examples.md (use await with async methods)
    '''
    def __init__(self, query: str, searchPreferences: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (True, True, True)
        super().__init__(query, limit, language, region, searchPreferences, timeout)

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()

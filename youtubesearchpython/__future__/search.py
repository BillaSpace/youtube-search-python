from typing import Any, Dict, Optional

from youtubesearchpython.core.channelsearch import ChannelSearchCore
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.search import SearchCore


class Search(SearchCore):
    def __init__(self, query: str, limit: int = 20, language: str = "en", region: str = "US", timeout: Optional[int] = None):
        self.searchMode = (True, True, True)
        super().__init__(query, limit, language, region, None, timeout)

    async def next(self) -> Dict[str, Any]:
        return await super().next()

    def create(self) -> None:
        self.sync_create()
        self._getComponents(*self.searchMode)


class VideosSearch(SearchCore):
    def __init__(self, query: str, limit: int = 20, language: str = "en", region: str = "US", timeout: Optional[int] = None):
        self.searchMode = (True, False, False)
        super().__init__(query, limit, language, region, SearchMode.videos, timeout)

    async def next(self) -> Dict[str, Any]:
        return await super().next()

    def create(self) -> None:
        self.sync_create()
        self._getComponents(*self.searchMode)


class ChannelsSearch(SearchCore):
    def __init__(self, query: str, limit: int = 20, language: str = "en", region: str = "US", timeout: Optional[int] = None):
        self.searchMode = (False, True, False)
        super().__init__(query, limit, language, region, SearchMode.channels, timeout)

    async def next(self) -> Dict[str, Any]:
        return await super().next()

    def create(self) -> None:
        self.sync_create()
        self._getComponents(*self.searchMode)


class PlaylistsSearch(SearchCore):
    def __init__(self, query: str, limit: int = 20, language: str = "en", region: str = "US", timeout: Optional[int] = None):
        self.searchMode = (False, False, True)
        super().__init__(query, limit, language, region, SearchMode.playlists, timeout)

    async def next(self) -> Dict[str, Any]:
        return await super().next()

    def create(self) -> None:
        self.sync_create()
        self._getComponents(*self.searchMode)


class CustomSearch(SearchCore):
    def __init__(self, query: str, searchPreferences: str, limit: int = 20, language: str = "en", region: str = "US", timeout: Optional[int] = None):
        self.searchMode = (True, True, True)
        super().__init__(query, limit, language, region, searchPreferences, timeout)

    async def next(self) -> Dict[str, Any]:
        return await super().next()

    def create(self) -> None:
        self.sync_create()
        self._getComponents(*self.searchMode)


class ChannelSearch(ChannelSearchCore):
    def __init__(self, query: str, browseId: str, language: str = "en", region: str = "US", searchPreferences: str = "EgZzZWFyY2g%3D", timeout: Optional[int] = None):
        super().__init__(query, language, region, searchPreferences, browseId, timeout)

    async def next(self) -> Dict[str, Any]:
        return await super().next()

    def create(self) -> None:
        self.sync_create()

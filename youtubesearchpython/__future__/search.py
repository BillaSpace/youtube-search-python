# checkout __usage.txt for usage Refrence for your project
from typing import Any, Dict, Optional

from youtubesearchpython.core.channelsearch import ChannelSearchCore
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.search import SearchCore


class Search(SearchCore):
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (True, True, True)
        super().__init__(query, limit, language, region, None, timeout)  # type: ignore

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()  # type: ignore

    def create(self) -> None:
        """Synchronous convenience initializer (keeps old behavior if caller wants it)."""
        self.sync_create()
        self._getComponents(*self.searchMode)


class VideosSearch(SearchCore):
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (True, False, False)
        super().__init__(query, limit, language, region, SearchMode.videos, timeout)  # type: ignore

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()  # type: ignore

    def create(self) -> None:
        self.sync_create()
        self._getComponents(*self.searchMode)


class ChannelsSearch(SearchCore):
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (False, True, False)
        super().__init__(query, limit, language, region, SearchMode.channels, timeout)  # type: ignore

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()  # type: ignore

    def create(self) -> None:
        self.sync_create()
        self._getComponents(*self.searchMode)


class PlaylistsSearch(SearchCore):
    def __init__(self, query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (False, False, True)
        super().__init__(query, limit, language, region, SearchMode.playlists, timeout)  # type: ignore

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()  # type: ignore

    def create(self) -> None:
        self.sync_create()
        self._getComponents(*self.searchMode)


class CustomSearch(SearchCore):
    def __init__(self, query: str, searchPreferences: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: Optional[int] = None):
        self.searchMode = (True, True, True)
        super().__init__(query, limit, language, region, searchPreferences, timeout)  # type: ignore

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()  # type: ignore

    def create(self) -> None:
        self.sync_create()
        self._getComponents(*self.searchMode)


class ChannelSearch(ChannelSearchCore):
    def __init__(self, query: str, browseId: str, language: str = 'en', region: str = 'US', searchPreferences: str = "EgZzZWFyY2g%3D", timeout: Optional[int] = None):
        super().__init__(query, language, region, searchPreferences, browseId, timeout)  # type: ignore

    async def next(self) -> Dict[str, Any]:
        return await self._nextAsync()  # type: ignore

    def create(self) -> None:
        """Synchronous convenience initializer for backward compatibility."""
        self.sync_create()
        # ChannelSearchCore.sync_create already prepares response in most handlers; so i removed duplication

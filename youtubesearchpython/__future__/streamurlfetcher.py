from typing import Union, Optional, Dict, Any
from copy import deepcopy
from youtubesearchpython.core.streamurlfetcher import StreamURLFetcherCore


class StreamURLFetcher(StreamURLFetcherCore):
    def __init__(self) -> None:
        super().__init__()

    async def get(self, videoFormats: Dict[str, Any], itag: int) -> Optional[str]:
        self._getDecipheredURLs(videoFormats, itag)
        for s in self._streams:
            if s.get("itag") == itag and s.get("url"):
                return s.get("url")
        return None

    async def getAll(self, videoFormats: Dict[str, Any]) -> Dict[str, Any]:
        self._getDecipheredURLs(videoFormats)
        return {"streams": deepcopy(self._streams)}

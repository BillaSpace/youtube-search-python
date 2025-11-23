import re
import requests
from typing import Any, Dict, List, Optional

requestPayload: Dict[str, Any] = {
    "context": {
        "client": {
            "clientName": "WEB",
            "clientVersion": "2.20210224.06.00",
            "newVisitorCookie": True,
        },
        "user": {
            "lockedSafetyMode": False,
        },
    }
}

userAgent: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

videoElementKey = "videoRenderer"
channelElementKey = "channelRenderer"
playlistElementKey = "playlistRenderer"
shelfElementKey = "shelfRenderer"
itemSectionKey = "itemSectionRenderer"
continuationItemKey = "continuationItemRenderer"
playerResponseKey = "playerResponse"
richItemKey = "richItemRenderer"
hashtagElementKey = "hashtagTileRenderer"
hashtagBrowseKey = "FEhashtag"
hashtagVideosPath: List[Any] = [
    "contents",
    "twoColumnBrowseResultsRenderer",
    "tabs",
    0,
    "tabRenderer",
    "content",
    "richGridRenderer",
    "contents",
]
hashtagContinuationVideosPath: List[Any] = [
    "onResponseReceivedActions",
    0,
    "appendContinuationItemsAction",
    "continuationItems",
]
contentPath: List[Any] = [
    "contents",
    "twoColumnSearchResultsRenderer",
    "primaryContents",
    "sectionListRenderer",
    "contents",
]
fallbackContentPath: List[Any] = [
    "contents",
    "twoColumnSearchResultsRenderer",
    "primaryContents",
    "richGridRenderer",
    "contents",
]
continuationContentPath: List[Any] = [
    "onResponseReceivedCommands",
    0,
    "appendContinuationItemsAction",
    "continuationItems",
]
continuationKeyPath: List[Any] = [
    "continuationItemRenderer",
    "continuationEndpoint",
    "continuationCommand",
    "token",
]
playlistInfoPath: List[Any] = ["response", "sidebar", "playlistSidebarRenderer", "items"]
playlistVideosPath: List[Any] = [
    "response",
    "contents",
    "twoColumnBrowseResultsRenderer",
    "tabs",
    0,
    "tabRenderer",
    "content",
    "sectionListRenderer",
    "contents",
    0,
    "itemSectionRenderer",
    "contents",
    0,
    "playlistVideoListRenderer",
    "contents",
]
playlistPrimaryInfoKey = "playlistSidebarPrimaryInfoRenderer"
playlistSecondaryInfoKey = "playlistSidebarSecondaryInfoRenderer"
playlistVideoKey = "playlistVideoRenderer"

class ResultMode:
    json = 0
    dict = 1

class SearchMode:
    videos = "EgIQAQ%3D%3D"
    channels = "EgIQAg%3D%3D"
    playlists = "EgIQAw%3D%3D"
    livestreams = "EgJAAQ%3D%3D"

class VideoUploadDateFilter:
    lastHour = "EgQIARAB"
    today = "EgQIAhAB"
    thisWeek = "EgQIAxAB"
    thisMonth = "EgQIBBAB"
    thisYear = "EgQIBRAB"

class VideoDurationFilter:
    short = "EgQQARgB"
    long = "EgQQARgC"

class VideoSortOrder:
    relevance = "CAASAhAB"
    uploadDate = "CAISAhAB"
    viewCount = "CAMSAhAB"
    rating = "CAESAhAB"

class ChannelRequestType:
    info = "EgVhYm91dA%3D%3D"
    playlists = "EglwbGF5bGlzdHMYAyABcAA%3D"

INNERTUBE_API_KEY: Optional[str] = None
INNERTUBE_CLIENT_VERSION: Optional[str] = None
searchKey: Optional[str] = None

def _extract_innertube_values_from_html(html: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    m_key = re.search(r'"INNERTUBE_API_KEY"\s*:\s*"([^"]+)"', html)
    if m_key:
        result["api_key"] = m_key.group(1)
    m_ver = re.search(r'"INNERTUBE_CLIENT_VERSION"\s*:\s*"([^"]+)"', html)
    if m_ver:
        result["client_version"] = m_ver.group(1)
    return result

def update_dynamic_keys(url: str = "https://www.youtube.com", timeout: int = 6) -> None:
    global INNERTUBE_API_KEY, INNERTUBE_CLIENT_VERSION, searchKey, requestPayload
    headers = {"User-Agent": userAgent}
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        if r.status_code == 200 and r.text:
            vals = _extract_innertube_values_from_html(r.text)
            if "api_key" in vals:
                INNERTUBE_API_KEY = vals["api_key"]
            if "client_version" in vals:
                INNERTUBE_CLIENT_VERSION = vals["client_version"]
    except Exception:
        pass
    if INNERTUBE_API_KEY:
        searchKey = INNERTUBE_API_KEY
    if INNERTUBE_CLIENT_VERSION:
        requestPayload["context"]["client"]["clientVersion"] = INNERTUBE_CLIENT_VERSION

try:
    update_dynamic_keys()
except Exception:
    pass

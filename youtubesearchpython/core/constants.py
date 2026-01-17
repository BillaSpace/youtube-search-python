from enum import Enum

requestPayload = {
    "context": {
        "client": {
            "clientName": "WEB",
            # Client Version History:
            # Latest: 2.20250115.01.00 (Jan 2026)
            # Recent: 2.20241210.01.00 (Dec 2024)
            # Legacy: 2.20210621.02.00 (Jun 2021 - stable fallback)
            "clientVersion": "2.20250115.01.00",
        },
        "user": {
            "lockedSafetyMode": False,
        },
    }
}


userAgent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)


videoElementKey = "videoRenderer"
compactVideoElementKey = "compactVideoRenderer"
channelElementKey = "channelRenderer"
playlistElementKey = "playlistRenderer"
shelfElementKey = "shelfRenderer"
itemSectionKey = "itemSectionRenderer"
continuationItemKey = "continuationItemRenderer"
richItemKey = "richItemRenderer"
playerResponseKey = "playerResponse"

hashtagElementKey = "hashtagTileRenderer"
hashtagBrowseKey = "FEhashtag"

searchKey = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"


contentPath = [
    "contents",
    "twoColumnSearchResultsRenderer",
    "primaryContents",
    "sectionListRenderer",
    "contents",
]

fallbackContentPath = [
    "contents",
    "twoColumnSearchResultsRenderer",
    "primaryContents",
    "richGridRenderer",
    "contents",
]

continuationContentPath = [
    "onResponseReceivedCommands",
    0,
    "appendContinuationItemsAction",
    "continuationItems",
]

continuationKeyPath = [
    "continuationItemRenderer",
    "continuationEndpoint",
    "continuationCommand",
    "token",
]


hashtagVideosPath = [
    "contents",
    "twoColumnBrowseResultsRenderer",
    "tabs",
    0,
    "tabRenderer",
    "content",
    "richGridRenderer",
    "contents",
]

hashtagContinuationVideosPath = [
    "onResponseReceivedActions",
    0,
    "appendContinuationItemsAction",
    "continuationItems",
]


playlistInfoPath = [
    "response",
    "sidebar",
    "playlistSidebarRenderer",
    "items",
]

playlistVideosPath = [
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


class ResultMode(int, Enum):
    json = 0
    dict = 1


class SearchMode(str, Enum):
    videos = "EgIQAQ%3D%3D"
    channels = "EgIQAg%3D%3D"
    playlists = "EgIQAw%3D%3D"
    livestreams = "EgJAAQ%3D%3D"


class VideoUploadDateFilter(str, Enum):
    lastHour = "EgQIARAB"
    today = "EgQIAhAB"
    thisWeek = "EgQIAxAB"
    thisMonth = "EgQIBBAB"
    thisYear = "EgQIBRAB"


class VideoDurationFilter(str, Enum):
    short = "EgQQARgB"
    long = "EgQQARgC"


class VideoSortOrder(str, Enum):
    relevance = "CAASAhAB"
    uploadDate = "CAISAhAB"
    viewCount = "CAMSAhAB"
    rating = "CAESAhAB"


class ChannelRequestType(str, Enum):
    info = "EgVhYm91dA%3D%3D"
    playlists = "EglwbGF5bGlzdHMYAyABcAA%3D"

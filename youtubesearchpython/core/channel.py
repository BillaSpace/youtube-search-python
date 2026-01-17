import copy
import json
from typing import Union, List
from urllib.parse import urlencode

from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import getValue, getVideoId


class ChannelCore(RequestCore):
    def __init__(self, channel_id: str, request_params: str):
        super().__init__()
        self.browseId = channel_id
        self.params = request_params
        self.result = {}
        self.continuation = None

    def prepare_request(self):
        self.url = 'https://www.youtube.com/youtubei/v1/browse' + "?" + urlencode({
            'key': searchKey,
            "prettyPrint": "false"
        })
        self.data = copy.deepcopy(requestPayload)
        if not self.continuation:
            self.data["params"] = self.params
            self.data["browseId"] = self.browseId
        else:
            self.data["continuation"] = self.continuation

    def playlist_parse(self, i) -> dict:
        if "lockupViewModel" in i:
            lockup = i["lockupViewModel"]
            contentId = getValue(lockup, ["contentId"])
            return {
                "id": contentId,
                "thumbnails": getValue(lockup, ["contentImage", "collectionThumbnailViewModel", "primaryThumbnail", "thumbnailViewModel", "image", "sources"]),
                "title": getValue(lockup, ["metadata", "lockupMetadataViewModel", "title", "content"]),
                "videoCount": None,
                "lastEdited": None,
                "link": 'https://www.youtube.com/playlist?list=' + contentId if contentId else None
            }
        
        # GridPlaylistRenderer fallback
        target = i.get("gridPlaylistRenderer", i)
        return {
            "id": getValue(target, ["playlistId"]),
            "thumbnails": getValue(target, ["thumbnail", "thumbnails"]),
            "title": getValue(target, ["title", "runs", 0, "text"]),
            "videoCount": getValue(target, ["videoCountShortText", "simpleText"]),
            "lastEdited": getValue(target, ["publishedTimeText", "simpleText"]),
        }

    def parse_response(self):
        response = self.data.json()

        thumbnails = []
        try:
            thumbnails.extend(getValue(response, ["header", "c4TabbedHeaderRenderer", "avatar", "thumbnails"]))
        except (KeyError, AttributeError, TypeError):
            pass
        try:
            thumbnails.extend(getValue(response, ["metadata", "channelMetadataRenderer", "avatar", "thumbnails"]))
        except (KeyError, AttributeError, TypeError):
            pass
        try:
            thumbnails.extend(getValue(response, ["microformat", "microformatDataRenderer", "thumbnail", "thumbnails"]))
        except (KeyError, AttributeError, TypeError):
            pass
        
        tabData: dict = {}
        playlists: list = []

        tabs = getValue(response, ["contents", "twoColumnBrowseResultsRenderer", "tabs"])
        if tabs:
            for tab in tabs:
                tab: dict
                title = getValue(tab, ["tabRenderer", "title"])
                
                # Check for playlists in any tab content (often Home tab has shelves)
                content = getValue(tab, ["tabRenderer", "content", "sectionListRenderer", "contents"])
                if content:
                    for section in content:
                        items = getValue(section, ["itemSectionRenderer", "contents", 0, "gridRenderer", "items"])
                        if not items:
                            items = getValue(section, ["itemSectionRenderer", "contents", 0, "shelfRenderer", "content", "horizontalListRenderer", "items"])
                        
                        if items:
                             for i in items:
                                if getValue(i, ["continuationItemRenderer"]):
                                    self.continuation = getValue(i, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])
                                    continue
                                
                                if "gridPlaylistRenderer" in i or "lockupViewModel" in i:
                                    playlists.append(self.playlist_parse(i))
                
                if title == "About":
                    tabData = tab["tabRenderer"]

        metadata = getValue(tabData,
                            ["content", "sectionListRenderer", "contents", 0, "itemSectionRenderer", "contents", 0,
                             "channelAboutFullMetadataRenderer"])

        self.result = {
            "id": getValue(response, ["metadata", "channelMetadataRenderer", "externalId"]),
            "url": getValue(response, ["metadata", "channelMetadataRenderer", "channelUrl"]),
            "description": getValue(response, ["metadata", "channelMetadataRenderer", "description"]),
            "title": getValue(response, ["metadata", "channelMetadataRenderer", "title"]),
            "banners": getValue(response, ["header", "c4TabbedHeaderRenderer", "banner", "thumbnails"]),
            "subscribers": {
                "simpleText": getValue(response,
                                       ["header", "c4TabbedHeaderRenderer", "subscriberCountText", "simpleText"]),
                "label": getValue(response, ["header", "c4TabbedHeaderRenderer", "subscriberCountText", "accessibility",
                                             "accessibilityData", "label"])
            },
            "thumbnails": thumbnails,
            "availableCountryCodes": getValue(response,
                                              ["metadata", "channelMetadataRenderer", "availableCountryCodes"]),
            "isFamilySafe": getValue(response, ["metadata", "channelMetadataRenderer", "isFamilySafe"]),
            "keywords": getValue(response, ["metadata", "channelMetadataRenderer", "keywords"]),
            "tags": getValue(response, ["microformat", "microformatDataRenderer", "tags"]),
            "views": getValue(metadata, ["viewCountText", "simpleText"]) if metadata else None,
            "joinedDate": getValue(metadata, ["joinedDateText", "runs", -1, "text"]) if metadata else None,
            "country": getValue(metadata, ["country", "simpleText"]) if metadata else None,
            "playlists": playlists,
        }

    def parse_next_response(self):
        response = self.data.json()

        self.continuation = None

        response = getValue(response, ["onResponseReceivedActions", 0, "appendContinuationItemsAction", "continuationItems"])
        if response:
            for i in response:
                if getValue(i, ["continuationItemRenderer"]):
                    self.continuation = getValue(i, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])
                    break
                elif getValue(i, ['gridPlaylistRenderer']):
                    self.result["playlists"].append(self.playlist_parse(getValue(i, ['gridPlaylistRenderer'])))
                elif getValue(i, ['lockupViewModel']):
                    self.result["playlists"].append(self.playlist_parse(i))

    async def async_next(self):
        if not self.continuation:
            return
        self.prepare_request()
        self.data = await self.asyncPostRequest()
        self.parse_next_response()

    def sync_next(self):
        if not self.continuation:
            return
        self.prepare_request()
        self.data = self.syncPostRequest()
        self.parse_next_response()

    def has_more_playlists(self):
        return self.continuation is not None

    async def async_create(self):
        self.prepare_request()
        self.data = await self.asyncPostRequest()
        self.parse_response()
    def sync_create(self):
        self.prepare_request()
        self.data = self.syncPostRequest()
        self.parse_response()

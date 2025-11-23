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
        if not searchKey:
            raise Exception('INNERTUBE API key (searchKey) is not set.')
        self.url = 'https://www.youtube.com/youtubei/v1/browse' + "?" + urlencode({
            'key': searchKey,
            "prettyPrint": "false"
        })
        self.data = copy.deepcopy(requestPayload)
        context = self.data.setdefault('context', {})
        client = context.setdefault('client', {})
        client.setdefault('hl', client.get('hl'))
        client.setdefault('gl', client.get('gl'))
        if not self.continuation:
            self.data["params"] = self.params
            self.data["browseId"] = self.browseId
        else:
            self.data["continuation"] = self.continuation

    def playlist_parse(self, i) -> dict:
        return {
            "id": getValue(i, ["playlistId"]),
            "thumbnails": getValue(i, ["thumbnail", "thumbnails"]),
            "title": getValue(i, ["title", "runs", 0, "text"]),
            "videoCount": getValue(i, ["videoCountShortText", "simpleText"]),
            "lastEdited": getValue(i, ["publishedTimeText", "simpleText"]),
        }

    def _safe_extend_thumbnails(self, resp, path):
        val = getValue(resp, path)
        if val:
            try:
                return list(val)
            except Exception:
                return []
        return []

    def parse_response(self):
        resp = None
        try:
            resp = self.data.json()
        except Exception:
            resp = json.loads(self.data.text) if hasattr(self.data, "text") else {}
        thumbnails = []
        thumbnails.extend(self._safe_extend_thumbnails(resp, ["header", "c4TabbedHeaderRenderer", "avatar", "thumbnails"]))
        thumbnails.extend(self._safe_extend_thumbnails(resp, ["metadata", "channelMetadataRenderer", "avatar", "thumbnails"]))
        thumbnails.extend(self._safe_extend_thumbnails(resp, ["microformat", "microformatDataRenderer", "thumbnail", "thumbnails"]))
        tabData: dict = {}
        playlists: list = []
        tabs = getValue(resp, ["contents", "twoColumnBrowseResultsRenderer", "tabs"]) or []
        for tab in tabs:
            title = getValue(tab, ["tabRenderer", "title"])
            if title == "Playlists":
                playlist = getValue(tab, ["tabRenderer", "content", "sectionListRenderer", "contents", 0, "itemSectionRenderer", "contents", 0, "gridRenderer", "items"])
                if playlist and getValue(playlist, [0, "gridPlaylistRenderer"]):
                    for i in playlist:
                        if getValue(i, ["continuationItemRenderer"]):
                            self.continuation = getValue(i, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])
                            break
                        grid = getValue(i, ["gridPlaylistRenderer"])
                        if grid:
                            playlists.append(self.playlist_parse(grid))
            elif title == "About":
                tabData = getValue(tab, ["tabRenderer"]) or {}

        metadata = getValue(tabData, ["content", "sectionListRenderer", "contents", 0, "itemSectionRenderer", "contents", 0, "channelAboutFullMetadataRenderer"]) or {}

        self.result = {
            "id": getValue(resp, ["metadata", "channelMetadataRenderer", "externalId"]),
            "url": getValue(resp, ["metadata", "channelMetadataRenderer", "channelUrl"]),
            "description": getValue(resp, ["metadata", "channelMetadataRenderer", "description"]),
            "title": getValue(resp, ["metadata", "channelMetadataRenderer", "title"]),
            "banners": getValue(resp, ["header", "c4TabbedHeaderRenderer", "banner", "thumbnails"]),
            "subscribers": {
                "simpleText": getValue(resp, ["header", "c4TabbedHeaderRenderer", "subscriberCountText", "simpleText"]),
                "label": getValue(resp, ["header", "c4TabbedHeaderRenderer", "subscriberCountText", "accessibility", "accessibilityData", "label"])
            },
            "thumbnails": thumbnails,
            "availableCountryCodes": getValue(resp, ["metadata", "channelMetadataRenderer", "availableCountryCodes"]),
            "isFamilySafe": getValue(resp, ["metadata", "channelMetadataRenderer", "isFamilySafe"]),
            "keywords": getValue(resp, ["metadata", "channelMetadataRenderer", "keywords"]),
            "tags": getValue(resp, ["microformat", "microformatDataRenderer", "tags"]),
            "views": getValue(metadata, ["viewCountText", "simpleText"]) if metadata else None,
            "joinedDate": getValue(metadata, ["joinedDateText", "runs", -1, "text"]) if metadata else None,
            "country": getValue(metadata, ["country", "simpleText"]) if metadata else None,
            "playlists": playlists,
        }

    def parse_next_response(self):
        resp = None
        try:
            resp = self.data.json()
        except Exception:
            resp = json.loads(self.data.text) if hasattr(self.data, "text") else {}
        self.continuation = None
        items = getValue(resp, ["onResponseReceivedActions", 0, "appendContinuationItemsAction", "continuationItems"]) or []
        for i in items:
            if getValue(i, ["continuationItemRenderer"]):
                self.continuation = getValue(i, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])
                break
            grid = getValue(i, ['gridPlaylistRenderer']) or getValue(i, ['gridShowRenderer'])
            if grid:
                self.result.setdefault("playlists", []).append(self.playlist_parse(grid))

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

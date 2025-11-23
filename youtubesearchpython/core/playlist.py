import collections
import copy
import itertools
import json
import re
from typing import Iterable, Mapping, Tuple, TypeVar, Union, List
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import RequestCore


K = TypeVar("K")
T = TypeVar("T")


class PlaylistCore(RequestCore):
    playlistComponent = None
    result = None
    continuationKey = None

    def __init__(self, playlistLink: str, componentMode: str, resultMode: int, timeout: int):
        super().__init__()
        self.componentMode = componentMode
        self.resultMode = resultMode
        self.timeout = timeout
        self.url = playlistLink
        self.responseSource = None

    def post_processing(self):
        self.__parseSource()
        self.__getComponents()
        if self.resultMode == ResultMode.json:
            self.result = json.dumps(self.playlistComponent, indent=4)
        else:
            self.result = self.playlistComponent

    def sync_create(self):
        statusCode = self.__makeRequest()
        if statusCode == 200:
            self.post_processing()
        else:
            raise Exception('ERROR: Invalid status code.')

    async def async_create(self):
        statusCode = await self.__makeAsyncRequest()
        if statusCode == 200:
            self.post_processing()
        else:
            raise Exception('ERROR: Invalid status code.')

    def next_post_processing(self):
        self.__parseSource()
        self.__getNextComponents()
        if self.resultMode == ResultMode.json:
            self.result = json.dumps(self.playlistComponent, indent=4)
        else:
            self.result = self.playlistComponent

    def _next(self):
        self.prepare_next_request()
        if self.continuationKey:
            response = self.syncPostRequest()
            self.response = response.text if hasattr(response, "text") else None
            if hasattr(response, "status_code") and response.status_code == 200:
                self.next_post_processing()
            else:
                raise Exception('ERROR: Invalid status code.')

    async def _async_next(self):
        if self.continuationKey:
            self.prepare_next_request()
            response = await self.asyncPostRequest()
            self.response = response.text if hasattr(response, "text") else None
            if hasattr(response, "status_code") and response.status_code == 200:
                self.next_post_processing()
            else:
                raise Exception('ERROR: Invalid status code.')
        else:
            await self.async_create()

    def prepare_first_request(self):
        match = re.search(r"(?:list=)([a-zA-Z0-9\-_+=]+)", self.url or "")
        if not match:
            raise Exception("Could not extract playlist id from url")
        id = match.group(1)
        browseId = "VL" + id if not id.startswith("VL") else id
        if not searchKey:
            raise Exception('INNERTUBE API key (searchKey) is not set.')
        self.url = 'https://www.youtube.com/youtubei/v1/browse' + '?' + urlencode({'key': searchKey})
        self.data = copy.deepcopy(requestPayload)
        ctx = self.data.setdefault('context', {})
        client = ctx.setdefault('client', {})
        client.setdefault('hl', client.get('hl'))
        client.setdefault('gl', client.get('gl'))
        self.data.update({"browseId": browseId})

    def __makeRequest(self) -> int:
        self.prepare_first_request()
        response = self.syncPostRequest()
        self.response = response.text if hasattr(response, "text") else None
        return response.status_code if hasattr(response, "status_code") else 0

    async def __makeAsyncRequest(self) -> int:
        self.prepare_first_request()
        response = await self.asyncPostRequest()
        self.response = response.text if hasattr(response, "text") else None
        return response.status_code if hasattr(response, "status_code") else 0

    def prepare_next_request(self):
        if not searchKey:
            raise Exception('INNERTUBE API key (searchKey) is not set.')
        requestBody = copy.deepcopy(requestPayload)
        ctx = requestBody.setdefault('context', {})
        client = ctx.setdefault('client', {})
        client.setdefault('hl', client.get('hl'))
        client.setdefault('gl', client.get('gl'))
        requestBody['continuation'] = self.continuationKey
        self.data = requestBody
        self.url = 'https://www.youtube.com/youtubei/v1/browse' + '?' + urlencode({'key': searchKey})

    def __makeNextRequest(self) -> int:
        response = self.syncPostRequest()
        try:
            self.response = response.text if hasattr(response, "text") else None
            return response.status_code if hasattr(response, "status_code") else 0
        except Exception:
            raise Exception('ERROR: Could not make request.')

    def __parseSource(self) -> None:
        try:
            if isinstance(self.response, (str, bytes)):
                self.responseSource = json.loads(self.response)
            elif hasattr(self.response, "json"):
                self.responseSource = self.response.json()
            else:
                self.responseSource = {}
        except Exception:
            raise Exception('ERROR: Could not parse YouTube response.')

    def __getComponents(self) -> None:
        try:
            sidebar = self.__getValue(self.responseSource, ["sidebar", "playlistSidebarRenderer", "items"]) or []
            inforenderer = sidebar[0]["playlistSidebarPrimaryInfoRenderer"] if sidebar and "playlistSidebarPrimaryInfoRenderer" in sidebar[0] else {}
            channel_details_available = len(sidebar) > 1 and "playlistSidebarSecondaryInfoRenderer" in sidebar[1]
            channelrenderer = sidebar[1]["playlistSidebarSecondaryInfoRenderer"].get("videoOwner", {}).get("videoOwnerRenderer") if channel_details_available else None
            videorenderer = self.__getFirstValue(self.responseSource, ["contents", "twoColumnBrowseResultsRenderer", "tabs", None, "tabRenderer", "content", "sectionListRenderer", "contents", None, "itemSectionRenderer", "contents", None, "playlistVideoListRenderer", "contents"]) or []
            videos = []
            for video in videorenderer:
                video_data = video.get("playlistVideoRenderer") if isinstance(video, dict) else None
                if not video_data:
                    continue
                try:
                    j = {
                        "id": self.__getValue(video_data, ["videoId"]),
                        "thumbnails": self.__getValue(video_data, ["thumbnail", "thumbnails"]),
                        "title": self.__getValue(video_data, ["title", "runs", 0, "text"]),
                        "channel": {
                            "name": self.__getValue(video_data, ["shortBylineText", "runs", 0, "text"]),
                            "id": self.__getValue(video_data, ["shortBylineText", "runs", 0, "navigationEndpoint", "browseEndpoint", "browseId"]),
                            "link": self.__getValue(video_data, ["shortBylineText", "runs", 0, "navigationEndpoint", "browseEndpoint", "canonicalBaseUrl"]),
                        },
                        "duration": self.__getValue(video_data, ["lengthText", "simpleText"]),
                        "accessibility": {
                            "title": self.__getValue(video_data, ["title", "accessibility", "accessibilityData", "label"]),
                            "duration": self.__getValue(video_data, ["lengthText", "accessibility", "accessibilityData", "label"]),
                        },
                        "link": "https://www.youtube.com" + (self.__getValue(video_data, ["navigationEndpoint", "commandMetadata", "webCommandMetadata", "url"]) or ""),
                        "isPlayable": self.__getValue(video_data, ["isPlayable"]),
                    }
                    videos.append(j)
                except Exception:
                    pass

            playlistElement = {
                'info': {
                    "id": self.__getValue(inforenderer, ["title", "runs", 0, "navigationEndpoint", "watchEndpoint", "playlistId"]),
                    "thumbnails": self.__getValue(inforenderer, ["thumbnailRenderer", "playlistVideoThumbnailRenderer", "thumbnail", "thumbnails"]),
                    "title": self.__getValue(inforenderer, ["title", "runs", 0, "text"]),
                    "videoCount": self.__getValue(inforenderer, ["stats", 0, "runs", 0, "text"]),
                    "viewCount": self.__getValue(inforenderer, ["stats", 1, "simpleText"]),
                    "link": self.__getValue(self.responseSource, ["microformat", "microformatDataRenderer", "urlCanonical"]),
                    "channel": {
                        "id": self.__getValue(channelrenderer, ["title", "runs", 0, "navigationEndpoint", "browseEndpoint", "browseId"]) if channel_details_available else None,
                        "name": self.__getValue(channelrenderer, ["title", "runs", 0, "text"]) if channel_details_available else None,
                        "detailsAvailable": channel_details_available,
                        "link": ("https://www.youtube.com" + (self.__getValue(channelrenderer, ["title", "runs", 0, "navigationEndpoint", "browseEndpoint", "canonicalBaseUrl"]) or "")) if channel_details_available else None,
                        "thumbnails": self.__getValue(channelrenderer, ["thumbnail", "thumbnails"]) if channel_details_available else None,
                    }
                },
                'videos': videos,
            }
            if self.componentMode == "getInfo":
                self.playlistComponent = playlistElement["info"]
            elif self.componentMode == "getVideos":
                self.playlistComponent = {"videos": videos}
            else:
                self.playlistComponent = playlistElement
            self.continuationKey = self.__getValue(videorenderer, [-1, "continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])
        except Exception:
            raise Exception('ERROR: Could not parse YouTube response.')

    def __getNextComponents(self) -> None:
        self.continuationKey = None
        playlistComponent = {'videos': []}
        continuationElements = self.__getValue(self.responseSource, ['onResponseReceivedActions', 0, 'appendContinuationItemsAction', 'continuationItems'])
        if continuationElements is None:
            return
        for videoElement in continuationElements:
            if isinstance(videoElement, dict) and playlistVideoKey in videoElement:
                videoComponent = {
                    'id': self.__getValue(videoElement, [playlistVideoKey, 'videoId']),
                    'title': self.__getValue(videoElement, [playlistVideoKey, 'title', 'runs', 0, 'text']),
                    'thumbnails': self.__getValue(videoElement, [playlistVideoKey, 'thumbnail', 'thumbnails']),
                    'link': "https://www.youtube.com" + (self.__getValue(videoElement, [playlistVideoKey, "navigationEndpoint", "commandMetadata", "webCommandMetadata", "url"]) or ""),
                    'channel': {
                        'name': self.__getValue(videoElement, [playlistVideoKey, 'shortBylineText', 'runs', 0, 'text']),
                        'id': self.__getValue(videoElement, [playlistVideoKey, 'shortBylineText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']),
                        "link": "https://www.youtube.com" + (self.__getValue(videoElement, [playlistVideoKey, "shortBylineText", "runs", 0, "navigationEndpoint", "browseEndpoint", "canonicalBaseUrl"]) or "")
                    },
                    'duration': self.__getValue(videoElement, [playlistVideoKey, 'lengthText', 'simpleText']),
                    'accessibility': {
                        'title': self.__getValue(videoElement, [playlistVideoKey, 'title', 'accessibility', 'accessibilityData', 'label']),
                        'duration': self.__getValue(videoElement, [playlistVideoKey, 'lengthText', 'accessibility', 'accessibilityData', 'label']),
                    },
                }
                playlistComponent['videos'].append(videoComponent)
            self.continuationKey = self.__getValue(videoElement, continuationKeyPath)
        self.playlistComponent["videos"].extend(playlistComponent['videos'])

    def __getPlaylistComponent(self, element: dict, mode: str) -> dict:
        playlistComponent = {}
        if mode in ['getInfo', None]:
            for infoElement in element.get('info', []):
                if playlistPrimaryInfoKey in infoElement:
                    component = {
                        'id': self.__getValue(infoElement, [playlistPrimaryInfoKey, 'title', 'runs', 0, 'navigationEndpoint', 'watchEndpoint', 'playlistId']),
                        'title': self.__getValue(infoElement, [playlistPrimaryInfoKey, 'title', 'runs', 0, 'text']),
                        'videoCount': self.__getValue(infoElement, [playlistPrimaryInfoKey, 'stats', 0, 'runs', 0, 'text']),
                        'viewCount': self.__getValue(infoElement, [playlistPrimaryInfoKey, 'stats', 1, 'simpleText']),
                        'thumbnails': self.__getValue(infoElement, [playlistPrimaryInfoKey, 'thumbnailRenderer', 'playlistVideoThumbnailRenderer', 'thumbnail']),
                    }
                    if not component['thumbnails']:
                        component['thumbnails'] = self.__getValue(infoElement, [playlistPrimaryInfoKey, 'thumbnailRenderer', 'playlistCustomThumbnailRenderer', 'thumbnail', 'thumbnails'])
                    component['link'] = 'https://www.youtube.com/playlist?list=' + (component['id'] or "")
                    playlistComponent.update(component)
                if playlistSecondaryInfoKey in infoElement:
                    component = {
                        'channel': {
                            'name': self.__getValue(infoElement, [playlistSecondaryInfoKey, 'videoOwner', 'videoOwnerRenderer', 'title', 'runs', 0, 'text']),
                            'id': self.__getValue(infoElement, [playlistSecondaryInfoKey, 'videoOwner', 'videoOwnerRenderer', 'title', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']),
                            'thumbnails': self.__getValue(infoElement, [playlistSecondaryInfoKey, 'videoOwner', 'videoOwnerRenderer', 'thumbnail', 'thumbnails']),
                        },
                    }
                    component['channel']['link'] = 'https://www.youtube.com/channel/' + (component['channel']['id'] or "")
                    playlistComponent.update(component)
        if mode in ['getVideos', None]:
            self.continuationKey = None
            playlistComponent['videos'] = []
            for videoElement in element.get('videos', []):
                if playlistVideoKey in videoElement:
                    videoComponent = {
                        'id': self.__getValue(videoElement, [playlistVideoKey, 'videoId']),
                        'title': self.__getValue(videoElement, [playlistVideoKey, 'title', 'runs', 0, 'text']),
                        'thumbnails': self.__getValue(videoElement, [playlistVideoKey, 'thumbnail', 'thumbnails']),
                        'channel': {
                            'name': self.__getValue(videoElement, [playlistVideoKey, 'shortBylineText', 'runs', 0, 'text']),
                            'id': self.__getValue(videoElement, [playlistVideoKey, 'shortBylineText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']),
                        },
                        'duration': self.__getValue(videoElement, [playlistVideoKey, 'lengthText', 'simpleText']),
                        'accessibility': {
                            'title': self.__getValue(videoElement, [playlistVideoKey, 'title', 'accessibility', 'accessibilityData', 'label']),
                            'duration': self.__getValue(videoElement, [playlistVideoKey, 'lengthText', 'accessibility', 'accessibilityData', 'label']),
                        },
                    }
                    videoComponent['link'] = 'https://www.youtube.com/watch?v=' + (videoComponent['id'] or "")
                    videoComponent['channel']['link'] = 'https://www.youtube.com/channel/' + (videoComponent['channel']['id'] or "")
                    playlistComponent['videos'].append(videoComponent)
                if continuationItemKey in videoElement:
                    self.continuationKey = self.__getValue(videoElement, continuationKeyPath)
        return playlistComponent

    def __result(self, mode: int) -> Union[dict, str]:
        if mode == ResultMode.dict:
            return self.playlistComponent
        elif mode == ResultMode.json:
            return json.dumps(self.playlistComponent, indent=4)

    def __getValue(self, source: Union[dict, list, None], path: Iterable[Union[str, int]]) -> Union[str, int, dict, list, None]:
        value = source
        for key in path:
            if value is None:
                return None
            if isinstance(key, str):
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            elif isinstance(key, int):
                if isinstance(value, list) and len(value) > abs(key):
                    value = value[key]
                else:
                    return None
            else:
                return None
        return value

    def __getAllWithKey(self, source: Iterable[Mapping[K, T]], key: K) -> Iterable[T]:
        for item in source or []:
            if key in item:
                yield item[key]

    def __getValueEx(self, source: dict, path: List[Union[str, None]]) -> Iterable[Union[str, int, dict, None]]:
        if len(path) <= 0:
            yield source
            return
        key = path[0]
        upcoming = path[1:]
        if key is None:
            if not upcoming:
                raise Exception("Cannot search for a key twice consecutive or at the end with no key given")
            following_key = upcoming[0]
            upcoming = upcoming[1:]
            for val in self.__getAllWithKey(source or [], following_key):
                yield from self.__getValueEx(val, path=upcoming)
        else:
            val = self.__getValue(source, [key])
            if val is None:
                return
            yield from self.__getValueEx(val, path=upcoming)

    def __getFirstValue(self, source: dict, path: Iterable[Union[str, None]]) -> Union[str, int, dict, list, None]:
        values = self.__getValueEx(source or {}, list(path))
        for val in values:
            if val is not None:
                return val
        return None

from urllib.parse import urlencode

from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import getValue
from youtubesearchpython.core.requests import YouTubeRequestError
from youtubesearchpython.core.utils import normalize_thumbnails


class ChannelCore(RequestCore):
    def __init__(self, channel_id: str, request_params: str, timeout: int = None):
        super().__init__(timeout=timeout)
        self.browseId = channel_id
        self.params = request_params
        self.result = {}
        self.continuation = None

    def prepare_request(self):
        self.url = 'https://www.youtube.com/youtubei/v1/browse' + "?" + urlencode({
            'key': searchKey,
            "prettyPrint": "false"
        })
        if not self.continuation:
            self.data = self.buildInnertubeBody(params=self.params, browseId=self.browseId)
        else:
            self.data = self.buildInnertubeBody(continuation=self.continuation)

    def playlist_parse(self, i) -> dict:
        if "lockupViewModel" in i:
            lockup = i["lockupViewModel"]
            contentId = getValue(lockup, ["contentId"])
            return {
                "id": contentId,
                "thumbnails": normalize_thumbnails(getValue(lockup, ["contentImage", "collectionThumbnailViewModel", "primaryThumbnail", "thumbnailViewModel", "image", "sources"])),
                "title": getValue(lockup, ["metadata", "lockupMetadataViewModel", "title", "content"]),
                "videoCount": None,
                "lastEdited": None,
                "link": 'https://www.youtube.com/playlist?list=' + contentId if contentId else None
            }
        
        # GridPlaylistRenderer fallback
        target = i.get("gridPlaylistRenderer", i)
        return {
            "id": getValue(target, ["playlistId"]),
            "thumbnails": normalize_thumbnails(getValue(target, ["thumbnail", "thumbnails"])),
            "title": getValue(target, ["title", "runs", 0, "text"]),
            "videoCount": getValue(target, ["videoCountShortText", "simpleText"]),
            "lastEdited": getValue(target, ["publishedTimeText", "simpleText"]),
            "link": f"https://www.youtube.com/playlist?list={getValue(target, ['playlistId'])}" if getValue(target, ['playlistId']) else None,
        }

    def parse_response(self, response):

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
        
        tabData = {}
        playlists = []
        seen = set()

        tabs = getValue(response, ["contents", "twoColumnBrowseResultsRenderer", "tabs"])
        if tabs:
            for tab in tabs:
                tab: dict
                title = getValue(tab, ["tabRenderer", "title"])
                
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
                                    item = self.playlist_parse(i)
                                    if item.get("id") and item["id"] not in seen:
                                        seen.add(item["id"])
                                        playlists.append(item)
                
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
            "thumbnails": normalize_thumbnails(thumbnails),
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

    def parse_next_response(self, response):
        self.continuation = None

        response = getValue(response, ["onResponseReceivedActions", 0, "appendContinuationItemsAction", "continuationItems"])
        if response:
            for i in response:
                if getValue(i, ["continuationItemRenderer"]):
                    self.continuation = getValue(i, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])
                    continue
                elif getValue(i, ['gridPlaylistRenderer']) or getValue(i, ['lockupViewModel']):
                    item = self.playlist_parse(getValue(i, ['gridPlaylistRenderer']) or i)
                    if item.get("id") not in {x.get("id") for x in self.result.get("playlists", [])}:
                        self.result.setdefault("playlists", []).append(item)

    def _json(self, response):
        if response.status_code != 200:
            raise YouTubeRequestError(f"Invalid status code {response.status_code} for channel request")
        return response.json()

    async def async_next(self):
        if not self.continuation:
            return
        self.prepare_request()
        self.parse_next_response(self._json(await self.asyncPostRequest()))

    def sync_next(self):
        if not self.continuation:
            return
        self.prepare_request()
        self.parse_next_response(self._json(self.syncPostRequest()))

    def has_more_playlists(self):
        return self.continuation is not None

    async def async_create(self):
        self.prepare_request()
        self.parse_response(self._json(await self.asyncPostRequest()))

    def sync_create(self):
        self.prepare_request()
        self.parse_response(self._json(self.syncPostRequest()))


import json
from typing import Union

from youtubesearchpython.core.componenthandler import getVideoId, getValue
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.requests import YouTubeRequestError


class CommentsCore(RequestCore):
    def __init__(self, videoLink: str, timeout: int = None):
        super().__init__(timeout=timeout)
        self.videoLink = videoLink
        self.commentsComponent = {"result": []}
        self.responseSource = None
        self.continuationKey = None
        self.isNextRequest = False
        self.response = None
        self.entities = {}

    def prepare_continuation_request(self):
        self.data = self.buildInnertubeBody(videoId=getVideoId(self.videoLink), client={"hl": "en", "gl": "US"})
        self.url = f"https://www.youtube.com/youtubei/v1/next?key={searchKey}"

    def prepare_comments_request(self):
        self.data = self.buildInnertubeBody(continuation=self.continuationKey, client={"hl": "en", "gl": "US"})

    def parse_source(self):
        response_json = self.response.json()
        self.responseSource = []
        self.continuationKey = None
        self.entities = {}
        mutations = getValue(response_json, ["frameworkUpdates", "entityBatchUpdate", "mutations"])
        if mutations:
            for m in mutations:
                key = m.get("entityKey")
                payload = m.get("payload")
                if key and payload:
                    self.entities[key] = payload

        endpoints = response_json.get("onResponseReceivedEndpoints", [])
        for ep in endpoints:
            items = getValue(ep, ["appendContinuationItemsAction", "continuationItems"])
            if not items:
                items = getValue(ep, ["reloadContinuationItemsCommand", "continuationItems"])            
            if items:
                for item in items:
                    if "commentThreadRenderer" in item:
                         self.responseSource.append(item)
                    elif "continuationItemRenderer" in item:
                         self.continuationKey = getValue(item, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])

    def parse_continuation_source(self):
        response_json = self.response.json()
        
        paths = [
            [
                "contents",
                "twoColumnWatchNextResults",
                "results",
                "results",
                "contents",
                -1,
                "itemSectionRenderer",
                "contents",
                0,
                "continuationItemRenderer",
                "continuationEndpoint",
                "continuationCommand",
                "token",
            ],
            [
                "contents",
                "twoColumnWatchNextResults",
                "results",
                "results",
                "contents",
                -1,
                "itemSectionRenderer",
                "contents",
                -1,
                "continuationItemRenderer",
                "continuationEndpoint",
                "continuationCommand",
                "token",
            ],
            [
                "onResponseReceivedEndpoints",
                0,
                "reloadContinuationItemsCommand",
                "continuationItems",
                -1,
                "continuationItemRenderer",
                "continuationEndpoint",
                "continuationCommand",
                "token",
            ],
            [
                "onResponseReceivedEndpoints",
                0,
                "appendContinuationItemsAction",
                "continuationItems",
                -1,
                "continuationItemRenderer",
                "continuationEndpoint",
                "continuationCommand",
                "token",
            ],
            [
                "engagementPanels",
            ]
        ]
        
        for path in paths:
            if path == ["engagementPanels"]:
                panels = response_json.get("engagementPanels", [])
                for panel in panels:
                    panel_render = panel.get("engagementPanelSectionListRenderer")
                    if not panel_render:
                        continue
                    if getValue(panel_render, ["targetId"]) == "engagement-panel-comments-section":
                        content = getValue(panel_render, ["content", "sectionListRenderer", "contents"])
                        if content:
                            for item in content:                 
                                token = getValue(item, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])
                                if not token:
                                    token = getValue(item, ["itemSectionRenderer", "contents", 0, "continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])                         
                                if token:
                                    self.continuationKey = token
                                    return
            else:
                continuation = getValue(response_json, path)
                if continuation:
                    self.continuationKey = continuation
                    return
        
        self.continuationKey = None

    def sync_make_comment_request(self):
        self.prepare_comments_request()
        self.response = self.syncPostRequest()
        if self.response.status_code != 200:
            raise YouTubeRequestError(f"Status code is not 200: {self.response.status_code}")
        self.parse_source()

    def sync_make_continuation_request(self):
        self.prepare_continuation_request()
        self.response = self.syncPostRequest()
        if self.response.status_code == 200:
            self.parse_continuation_source()
        else:
            raise YouTubeRequestError(f"Status code is not 200: {self.response.status_code}")

    async def async_make_comment_request(self):
        self.prepare_comments_request()
        self.response = await self.asyncPostRequest()
        if self.response.status_code != 200:
            raise YouTubeRequestError(f"Status code is not 200: {self.response.status_code}")
        self.parse_source()

    async def async_make_continuation_request(self):
        self.prepare_continuation_request()
        self.response = await self.asyncPostRequest()
        if self.response.status_code == 200:
            self.parse_continuation_source()
        else:
            raise YouTubeRequestError(f"Status code is not 200: {self.response.status_code}")

    def sync_create(self):
        self.sync_make_continuation_request()
        if self.continuationKey:
            self.sync_make_comment_request()
            self.__getComponents()
        else:  
            self.commentsComponent = {"result": []}

    def sync_create_next(self):
        if not self.continuationKey:
            return
        self.isNextRequest = True
        self.sync_make_comment_request()
        self.__getComponents()

    async def async_create(self):
        await self.async_make_continuation_request()
        if self.continuationKey:
            await self.async_make_comment_request()
            self.__getComponents()
        else:
            self.commentsComponent = {"result": []}

    async def async_create_next(self):
        if not self.continuationKey:
            return
        self.isNextRequest = True
        await self.async_make_comment_request()
        self.__getComponents()

    def __getComponents(self) -> None:
        comments = []
        if not self.responseSource:
            return
        
        for item in self.responseSource:
            comment_render = getValue(item, ["commentThreadRenderer", "comment", "commentRenderer"])        
            if not comment_render:
                cvm = getValue(item, ["commentThreadRenderer", "commentViewModel", "commentViewModel"])
                if cvm:
                    comment_key = cvm.get("commentKey")
                    if comment_key and comment_key in self.entities:
                        payload = self.entities[comment_key].get("commentEntityPayload")
                        if payload:
                            try:
                                author = payload.get("author", {})
                                properties = payload.get("properties", {})
                                j = {
                                    "id": cvm.get("commentId"),
                                    "author": {
                                        "id": author.get("channelId"),
                                        "name": author.get("displayName"),
                                        "thumbnails": [{"url": author.get("avatarThumbnailUrl")}] if author.get("avatarThumbnailUrl") else []
                                    },
                                    "content": getValue(properties, ["content", "content"]),
                                    "published": properties.get("publishedTime"),
                                    "isLiked": None,
                                    "authorIsChannelOwner": None,
                                    "voteStatus": None,
                                    "votes": {
                                        "simpleText": None,
                                        "label": None
                                    },
                                    "replyCount": None,
                                }
                                comments.append(j)
                                continue
                            except (AttributeError, KeyError, TypeError):
                                pass

            if not comment_render:
                continue
                
            try:
                j = {
                    "id": getValue(comment_render, ["commentId"]),
                    "author": {
                        "id": getValue(comment_render, ["authorEndpoint", "browseEndpoint", "browseId"]),
                        "name": getValue(comment_render, ["authorText", "simpleText"]),
                        "thumbnails": getValue(comment_render, ["authorThumbnail", "thumbnails"])
                    },
                    "content": "".join([r.get("text", "") for r in (getValue(comment_render, ["contentText", "runs"]) or [])]),
                    "published": getValue(comment_render, ["publishedTimeText", "runs", 0, "text"]),
                    "isLiked": getValue(comment_render, ["isLiked"]),
                    "authorIsChannelOwner": getValue(comment_render, ["authorIsChannelOwner"]),
                    "voteStatus": getValue(comment_render, ["voteStatus"]),
                    "votes": {
                        "simpleText": getValue(comment_render, ["voteCount", "simpleText"]),
                        "label": getValue(comment_render, ["voteCount", "accessibility", "accessibilityData", "label"])
                    },
                    "replyCount": getValue(comment_render, ["replyCount"]),
                }
                comments.append(j)
            except (KeyError, AttributeError, IndexError, TypeError):
                pass

        self.commentsComponent["result"].extend(comments)

    def __result(self, mode: int) -> Union[dict, str]:
        if mode == ResultMode.dict:
            return self.commentsComponent
        elif mode == ResultMode.json:
            return json.dumps(self.commentsComponent, indent=4)


import json
from typing import Union

from youtubesearchpython.core.constants import *
from youtubesearchpython.core.componenthandler import ComponentHandler
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.requests import YouTubeRequestError, YouTubeParseError


class HashtagCore(RequestCore, ComponentHandler):
    def __init__(self, hashtag: str, limit: int = 60, language: str = "en", region: str = "US", timeout: int = None):
        RequestCore.__init__(self, timeout=timeout)
        self.hashtag = hashtag
        self.limit = limit
        self.language = language
        self.region = (region or "US").upper()
        self.continuationKey = None
        self.params = None
        self.response = None
        self.resultComponents = []
        self._async_started = False

    def sync_create(self):
        self._getParams()
        self._makeRequest()
        self._getComponents()

    async def async_create(self):
        await self._asyncGetParams()
        await self._asyncMakeRequest()
        self._getComponents()
        self._async_started = True

    async def _nextAsync(self) -> dict:
        if self._async_started and not self.continuationKey:
            self.resultComponents = []
            return {"result": []}
        if self.params is None:
            await self._asyncGetParams()
        await self._asyncMakeRequest()
        self._getComponents()
        self._async_started = True
        return {"result": self.resultComponents}

    def result(self, mode: int = ResultMode.dict) -> Union[str, dict]:
        if mode == ResultMode.json:
            return json.dumps({'result': self.resultComponents}, indent=4)
        elif mode == ResultMode.dict:
            return {'result': self.resultComponents}

    def next(self) -> bool:
        self.response = None
        self.resultComponents = []
        if self.continuationKey:
            self._makeRequest()
            self._getComponents()
        return bool(self.resultComponents)

    def _buildSearchBody(self) -> dict:
        return self.buildInnertubeBody(query="#" + (self.hashtag or ""), client={"hl": self.language, "gl": self.region})

    def _buildBrowseBody(self) -> dict:
        values = {"client": {"hl": self.language, "gl": self.region}}
        if self.continuationKey:
            values["continuation"] = self.continuationKey
        else:
            values.update(browseId=hashtagBrowseKey, params=self.params)
        return self.buildInnertubeBody(**values)

    def _extractParams(self, data: dict) -> None:
        content = self._getValue(data, contentPath) or []
        items = self._getValue(content, [0, 'itemSectionRenderer', 'contents']) or []
        for item in items:
            if hashtagElementKey in item:
                self.params = self._getValue(item[hashtagElementKey], ['onTapCommand', 'browseEndpoint', 'params'])
                return

    def _getParams(self) -> None:
        if not searchKey:
            raise YouTubeRequestError("(searchKey) is not set in library.")
        self.url = 'https://www.youtube.com/youtubei/v1/search?key=' + searchKey
        self.data = self._buildSearchBody()
        try:
            response = self.syncPostRequest()
        except Exception as e:
            raise YouTubeRequestError(f'Failed to make hashtag search request: {str(e)}')
        if response.status_code != 200:
            raise YouTubeRequestError(f'Invalid status code {response.status_code} for hashtag search request')
        self._extractParams(response.json())

    async def _asyncGetParams(self) -> None:
        if not searchKey:
            raise YouTubeRequestError("(searchKey) is not set in library.")
        self.url = 'https://www.youtube.com/youtubei/v1/search?key=' + searchKey
        self.data = self._buildSearchBody()
        try:
            response = await self.asyncPostRequest()
        except Exception as e:
            raise YouTubeRequestError(f'Failed to make hashtag search request: {str(e)}')
        if response.status_code != 200:
            raise YouTubeRequestError(f'Invalid status code {response.status_code} for hashtag search request')
        self._extractParams(response.json())

    def _makeRequest(self) -> None:
        if self.params is None:
            self.response = None
            return
        if not searchKey:
            raise YouTubeRequestError("(searchKey) is not set in library.")
        self.url = 'https://www.youtube.com/youtubei/v1/browse?key=' + searchKey
        self.data = self._buildBrowseBody()
        try:
            response = self.syncPostRequest()
        except Exception as e:
            raise YouTubeRequestError(f'Failed to make hashtag browse request: {str(e)}')
        if response.status_code != 200:
            raise YouTubeRequestError(f'Invalid status code {response.status_code} for hashtag browse request')
        self.response = response.text

    async def _asyncMakeRequest(self) -> None:
        if self.params is None:
            self.response = None
            return
        if not searchKey:
            raise YouTubeRequestError("(searchKey) is not set in library.")
        self.url = 'https://www.youtube.com/youtubei/v1/browse?key=' + searchKey
        self.data = self._buildBrowseBody()
        try:
            response = await self.asyncPostRequest()
        except Exception as e:
            raise YouTubeRequestError(f'Failed to make hashtag browse request: {str(e)}')
        if response.status_code != 200:
            raise YouTubeRequestError(f'Invalid status code {response.status_code} for hashtag browse request')
        self.response = response.text

    def _getComponents(self) -> None:
        if self.response is None:
            return
        self.resultComponents = []
        try:
            data = json.loads(self.response)
        except json.JSONDecodeError as e:
            raise YouTubeParseError(f'Failed to parse JSON response for hashtag: {str(e)}')
        continuing = self.continuationKey is not None
        responseSource = self._getValue(data, hashtagContinuationVideosPath if continuing else hashtagVideosPath) or []
        self.continuationKey = None
        for element in responseSource:
            token = self._getValue(element, continuationKeyPath)
            if token:
                self.continuationKey = token
                continue
            rich = self._getValue(element, [richItemKey, 'content']) or {}
            if videoElementKey in rich:
                videoComponent = self._getVideoComponent(rich)
                self.resultComponents.append(videoComponent)
            elif 'lockupViewModel' in rich:
                lockupComponent = self._getLockupComponent(rich, findVideos=True, findChannels=False, findPlaylists=False)
                if lockupComponent:
                    self.resultComponents.append(lockupComponent)
            elif 'lockupViewModel' in element:
                lockupComponent = self._getLockupComponent(element, findVideos=True, findChannels=False, findPlaylists=False)
                if lockupComponent:
                    self.resultComponents.append(lockupComponent)
            if len(self.resultComponents) >= self.limit:
                break
            


import os
import json
import re
from typing import Union
from urllib.parse import urlencode

from youtubesearchpython.core.constants import ResultMode
from youtubesearchpython.core.requests import YouTubeParseError, YouTubeRequestError
from youtubesearchpython.core.requests import RequestCore


class SuggestionsCore(RequestCore):
    def __init__(self, language: str = 'en', region: str = 'US', timeout: int = None):
        super().__init__(timeout=timeout)
        self.language = language
        self.region = region
        self.proxy = os.environ.get("YTS_PROXY")

    def _post_request_processing(self, mode):
        searchSuggestions = []
        self.__parseSource()
        
        for element in self.responseSource:
            if isinstance(element, list):
                for searchSuggestionElement in element:
                    if isinstance(searchSuggestionElement, list) and len(searchSuggestionElement) > 0:
                        searchSuggestions.append(searchSuggestionElement[0])
                break
        
        if mode == ResultMode.dict:
            return {'result': searchSuggestions}
        elif mode == ResultMode.json:
            return json.dumps({'result': searchSuggestions}, indent=4)

    def _get(self, query: str, mode: int = ResultMode.dict) -> Union[dict, str]:
        self._prepare_url(query)
        self.__makeRequest()
        return self._post_request_processing(mode)

    async def _getAsync(self, query: str, mode: int = ResultMode.dict) -> Union[dict, str]:
        self._prepare_url(query)
        await self.__makeAsyncRequest()
        return self._post_request_processing(mode)

    def _prepare_url(self, query: str):
        self.url = 'https://clients1.google.com/complete/search' + '?' + urlencode({
            'hl': self.language,
            'gl': self.region,
            'q': query,
            'client': 'youtube',
            'gs_ri': 'youtube',
            'ds': 'yt',
        })
        token = os.environ.get("YTS_IDENTITY_TOKEN")
        self.headers = {"x-youtube-identity-token": token} if token else None

    def __parseSource(self) -> None:
        try:
            start_idx = self.response.find('(')
            end_idx = self.response.rfind(')')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = self.response[start_idx + 1:end_idx]
                self.responseSource = json.loads(json_str)
            else:
                try:
                    self.responseSource = json.loads(self.response)
                except (TypeError, ValueError, json.JSONDecodeError):
                    match = re.search(r'\[.*\]', self.response, re.DOTALL)
                    if match:
                        self.responseSource = json.loads(match.group())
                    else:
                        raise YouTubeParseError('Could not find JSON in suggestions response')
        except YouTubeParseError:
            raise
        except Exception as e:
            raise YouTubeParseError(f'Could not parse suggestions response: {e}')

    def __makeRequest(self) -> None:
        request = self.syncGetRequest()
        if request.status_code != 200:
            raise YouTubeRequestError(f"Invalid status code {request.status_code} for suggestions request")
        self.response = request.text

    async def __makeAsyncRequest(self) -> None:
        request = await self.asyncGetRequest()
        if request.status_code != 200:
            raise YouTubeRequestError(f"Invalid status code {request.status_code} for suggestions request")
        self.response = request.text


import re
import json
import asyncio
import xml.etree.ElementTree as ET
from html import unescape
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from typing import Dict, List, Optional

import httpx

from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.constants import userAgent
from youtubesearchpython.core.componenthandler import getVideoId
from youtubesearchpython.core.requests import (
    resolve_cookie_file_ex,
    cleanup_cookie_file,
    apply_cookies_to_client,
)


class TranscriptCore(RequestCore):
    def __init__(self, videoLink: str, key: str = None, timeout: int = None):
        super().__init__(timeout=timeout)
        self.videoLink = videoLink
        self.video_id = getVideoId(videoLink)
        self.key = key
        self.result = {"segments": [], "languages": []}

    def _select_track(self, tracks: List[Dict]) -> Optional[Dict]:
        if not tracks:
            return None
        if self.key:
            key = self.key.lower()
            for track in tracks:
                if (track.get("languageCode") or "").lower() == key:
                    return track
            for track in tracks:
                if (track.get("languageCode") or "").lower().split("-")[0] == key.split("-")[0]:
                    return track
            return None
        for code in ("hi", "en", "ur"):
            for track in tracks:
                if track.get("languageCode") == code:
                    return track
        return tracks[0]

    def _languages(self, tracks: List[Dict]) -> List[Dict]:
        result = []
        for track in tracks:
            name = track.get("name") or {}
            language = name.get("simpleText") or "".join(x.get("text", "") for x in name.get("runs", [])) or track.get("languageCode") or "Unknown"
            url = track.get("baseUrl") or track.get("url") or ""
            generated = track.get("kind") == "asr" or "caps=asr" in url
            result.append({
                "languageCode": track.get("languageCode"),
                "language": language,
                "isGenerated": generated,
                "isTranslatable": track.get("isTranslatable", False),
                "baseUrl": url,
                "params": track.get("languageCode"),
            })
        return result

    def _caption_url(self, url: str) -> str:
        parsed = urlparse(url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query["fmt"] = "json3"
        return urlunparse(parsed._replace(query=urlencode(query)))

    def _parse(self, text: str) -> List[Dict]:
        text = text.strip()
        if not text:
            return []
        segments = []
        if text.startswith("{"):
            for event in json.loads(text).get("events", []):
                value = "".join(x.get("utf8", "") for x in event.get("segs", []))
                value = unescape(value).replace("\n", " ").strip()
                if not value:
                    continue
                start_ms = int(event.get("tStartMs", 0))
                duration_ms = int(event.get("dDurationMs", 0))
                segments.append({
                    "text": value,
                    "start": start_ms / 1000,
                    "duration": duration_ms / 1000,
                    "startMs": str(start_ms),
                    "endMs": str(start_ms + duration_ms),
                })
            return segments
        root = ET.fromstring(text)
        for item in root.findall(".//text"):
            start = float(item.get("start", 0))
            duration = float(item.get("dur", 0))
            value = unescape("".join(item.itertext())).replace("\n", " ").strip()
            if not value:
                continue
            segments.append({
                "text": value,
                "start": start,
                "duration": duration,
                "startMs": str(int(start * 1000)),
                "endMs": str(int((start + duration) * 1000)),
            })
        return segments

    def _client(self, cookie_file: Optional[str]):
        client = httpx.Client(headers={"User-Agent": userAgent}, timeout=self.timeout, follow_redirects=True)
        apply_cookies_to_client(client, cookie_file)
        return client

    def _native(self, cookie_file: Optional[str]):
        with self._client(cookie_file) as client:
            headers = {"Accept-Language": f"{self.key},en;q=0.9" if self.key else "en-US,en;q=0.9"}
            watch = client.get(f"https://www.youtube.com/watch?v={self.video_id}", headers=headers)
            watch.raise_for_status()
            api = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', watch.text)
            version = re.search(r'"INNERTUBE_CLIENT_VERSION":"([^"]+)"', watch.text)
            if not api:
                return
            body = {
                "context": {"client": {
                    "clientName": "WEB",
                    "clientVersion": version.group(1) if version else "2.20250730.01.00",
                    "hl": self.key or "en",
                    "gl": "US",
                }},
                "videoId": self.video_id,
                "contentCheckOk": True,
                "racyCheckOk": True,
            }
            response = client.post(
                f"https://www.youtube.com/youtubei/v1/player?key={api.group(1)}",
                json=body, headers={**headers, "Content-Type": "application/json"},
            )
            response.raise_for_status()
            tracks = response.json().get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])
            languages = self._languages(tracks)
            selected = self._select_track(tracks)
            if not selected:
                self.result = {"segments": [], "languages": languages}
                return
            url = selected.get("baseUrl") or selected.get("url")
            if not url:
                self.result = {"segments": [], "languages": languages}
                return
            caption = client.get(self._caption_url(url), headers=headers)
            caption.raise_for_status()
            self.result = {"segments": self._parse(caption.text), "languages": languages}

    def _ytdlp(self, cookie_file: Optional[str]):
        try:
            from yt_dlp import YoutubeDL
        except ImportError:
            return
        options = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "socket_timeout": 20,
            "retries": 1,
            "extractor_retries": 1,
            "fragment_retries": 1,
            "extractor_args": {"youtube": {"player_client": ["web", "android", "tv"]}},
        }
        if cookie_file:
            options["cookiefile"] = cookie_file
        with YoutubeDL(options) as downloader:
            info = downloader.extract_info(self.videoLink, download=False)
        tracks = []
        for generated, source in ((False, info.get("subtitles") or {}), (True, info.get("automatic_captions") or {})):
            for code, formats in source.items():
                if any(x.get("languageCode") == code for x in tracks):
                    continue
                selected = next((x for x in formats if x.get("ext") == "json3"), next((x for x in formats if x.get("ext") in ("srv1", "srv3", "ttml")), None))
                if not selected:
                    continue
                url = selected.get("url") or ""
                tracks.append({
                    "languageCode": code,
                    "name": {"simpleText": selected.get("name") or code},
                    "kind": "asr" if generated or "caps=asr" in url else None,
                    "isTranslatable": False,
                    "baseUrl": url,
                })
        languages = self._languages(tracks)
        selected = self._select_track(tracks)
        if not selected:
            self.result = {"segments": [], "languages": languages}
            return
        with self._client(cookie_file) as client:
            response = client.get(self._caption_url(selected["baseUrl"]))
            response.raise_for_status()
            self.result = {"segments": self._parse(response.text), "languages": languages}

    def sync_create(self):
        cookie_file, owns_cookie_file = resolve_cookie_file_ex()
        try:
            try:
                self._native(cookie_file)
            except Exception:
                self.result = {"segments": [], "languages": []}
            if not self.result["segments"]:
                try:
                    self._ytdlp(cookie_file)
                except Exception:
                    pass
        finally:
            if owns_cookie_file:
                cleanup_cookie_file(cookie_file)

    async def async_create(self):
        await asyncio.to_thread(self.sync_create)

import collections
import copy
import itertools
import json
from typing import Iterable, Mapping, Tuple, TypeVar, Union, List
from urllib.parse import urlencode, unquote
from urllib.request import Request, urlopen

from youtubesearchpython.core.componenthandler import getVideoId, getValue
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.exceptions import YouTubeRequestError

K = TypeVar("K")
T = TypeVar("T")


class CommentsCore(RequestCore):
    result = None
    continuationKey = None
    isNextRequest = False
    response = None

    def __init__(self, videoLink: str):
        super().__init__()
        self.commentsComponent = {"result": []}
        self.responseSource = None
        self.videoLink = videoLink

    def prepare_continuation_request(self):
        self.data = copy.deepcopy(requestPayload)
        self.data["videoId"] = getVideoId(self.videoLink)
        self.data["client"] = {"hl": "en", "gl": "US"}
        self.url = f"https://www.youtube.com/youtubei/v1/next?key={searchKey}"

    def prepare_comments_request(self):
        self.data = copy.deepcopy(requestPayload)
        self.data["continuation"] = self.continuationKey
        self.data["client"] = {"hl": "en", "gl": "US"}

    def parse_source(self):
        with open('comments_response.json', 'w', encoding='utf-8') as f:
             json.dump(self.response.json(), f, indent=2)
        response_json = self.response.json()
        self.responseSource = []
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
                # Filter out header renderers if we only want comments
                for item in items:
                    if "commentThreadRenderer" in item:
                         self.responseSource.append(item)
                    elif "continuationItemRenderer" in item:
                         self.continuationKey = getValue(item, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])
        
        print(f"DEBUG: Found {len(self.responseSource)} comment items and {len(self.entities)} entities.")

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
                        # Find continuationItemRenderer anywhere in the panel content
                        content = getValue(panel_render, ["content", "sectionListRenderer", "contents"])
                        if content:
                            for item in content:
                                # Look specifically for continuationItemRenderer, potentially nested
                                token = getValue(item, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])
                                if not token:
                                    token = getValue(item, ["itemSectionRenderer", "contents", 0, "continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])
                                
                                if token:
                                    self.continuationKey = token
                                    print(f"DEBUG: Found comment continuation key: {self.continuationKey[:30]}...")
                                    return
            else:
                continuation = getValue(response_json, path)
                if continuation:
                    self.continuationKey = continuation
                    print(f"DEBUG: Found comment continuation key: {self.continuationKey[:30]}...")
                    return
        
        self.continuationKey = None

    def sync_make_comment_request(self):
        self.prepare_comments_request()
        self.response = self.syncPostRequest()
        if self.response.status_code == 200:
            with open('comments_response.json', 'w', encoding='utf-8') as f:
                json.dump(self.response.json(), f, indent=2)
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
        if self.response.status_code == 200:
            self.parse_source()

    async def async_make_continuation_request(self):
        self.prepare_continuation_request()
        self.response = await self.asyncPostRequest()
        if self.response.status_code == 200:
            self.parse_continuation_source()
            # Don't raise error if continuation key is None - video might not have comments
            # The comment request will handle empty results gracefully
        else:
            raise YouTubeRequestError(f"Status code is not 200: {self.response.status_code}")

    def sync_create(self):
        self.sync_make_continuation_request()
        # Only make comment request if we have a continuation key
        if self.continuationKey:
            self.sync_make_comment_request()
            self.__getComponents()
        else:
            # No comments available - set empty result
            self.commentsComponent = {"result": []}

    def sync_create_next(self):
        self.isNextRequest = True
        self.sync_make_comment_request()
        self.__getComponents()

    async def async_create(self):
        await self.async_make_continuation_request()
        # Only make comment request if we have a continuation key
        if self.continuationKey:
            await self.async_make_comment_request()
            self.__getComponents()
        else:
            # No comments available - set empty result
            self.commentsComponent = {"result": []}

    async def async_create_next(self):
        self.isNextRequest = True
        await self.async_make_comment_request()
        self.__getComponents()

    def __getComponents(self) -> None:
        comments = []
        if not self.responseSource:
            return
        
        for item in self.responseSource:
            comment_render = getValue(item, ["commentThreadRenderer", "comment", "commentRenderer"])
            
            # Try newer commentViewModel if commentRenderer is missing
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
                            except:
                                pass

            if not comment_render:
                continue
                
            try:
                # DEBUG: print found comment author
                author_name = getValue(comment_render, ["authorText", "simpleText"])
                # print(f"DEBUG: Processing comment by: {author_name}")
                j = {
                    "id": getValue(comment_render, ["commentId"]),
                    "author": {
                        "id": getValue(comment_render, ["authorEndpoint", "browseEndpoint", "browseId"]),
                        "name": getValue(comment_render, ["authorText", "simpleText"]),
                        "thumbnails": getValue(comment_render, ["authorThumbnail", "thumbnails"])
                    },
                    "content": "".join([r.get("text", "") for r in (getValue(comment, ["contentText", "runs"]) or [])]),
                    "published": getValue(comment, ["publishedTimeText", "runs", 0, "text"]),
                    "isLiked": getValue(comment, ["isLiked"]),
                    "authorIsChannelOwner": getValue(comment, ["authorIsChannelOwner"]),
                    "voteStatus": getValue(comment, ["voteStatus"]),
                    "votes": {
                        "simpleText": getValue(comment, ["voteCount", "simpleText"]),
                        "label": getValue(comment, ["voteCount", "accessibility", "accessibilityData", "label"])
                    },
                    "replyCount": getValue(comment, ["replyCount"]),
                }
                comments.append(j)
            except (KeyError, AttributeError, IndexError, TypeError):
                pass

        self.commentsComponent["result"].extend(comments)
        # continuationKey already updated in parse_source or we can re-check here if needed
        if not self.continuationKey:
             last_item = self.responseSource[-1] if self.responseSource else None
             if last_item and "continuationItemRenderer" in last_item:
                  self.continuationKey = self.__getValue(last_item, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])

    def __result(self, mode: int) -> Union[dict, str]:
        if mode == ResultMode.dict:
            return self.commentsComponent
        elif mode == ResultMode.json:
            return json.dumps(self.commentsComponent, indent=4)

    def __getValue(self, source: dict, path: Iterable[str]) -> Union[str, int, dict, None]:
        value = source
        for key in path:
            if type(key) is str:
                if key in value.keys():
                    value = value[key]
                else:
                    value = None
                    break
            elif type(key) is int:
                if len(value) != 0:
                    value = value[key]
                else:
                    value = None
                    break
        return value

    def __getAllWithKey(self, source: Iterable[Mapping[K, T]], key: K) -> Iterable[T]:
        for item in source:
            if key in item:
                yield item[key]

    def __getValueEx(self, source: dict, path: List[str]) -> Iterable[Union[str, int, dict, None]]:
        if len(path) <= 0:
            yield source
            return
        key = path[0]
        upcoming = path[1:]
        if key is None:
            following_key = upcoming[0]
            upcoming = upcoming[1:]
            if following_key is None:
                raise ValueError("Cannot search for a key twice consecutive or at the end with no key given")
            values = self.__getAllWithKey(source, following_key)
            for val in values:
                yield from self.__getValueEx(val, path=upcoming)
        else:
            val = self.__getValue(source, path=[key])
            yield from self.__getValueEx(val, path=upcoming)

    def __getFirstValue(self, source: dict, path: Iterable[str]) -> Union[str, int, dict, None]:
        values = self.__getValueEx(source, list(path))
        for val in values:
            if val is not None:
                return val
        return None

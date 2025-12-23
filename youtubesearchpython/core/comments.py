import collections
import copy
import itertools
import json
from typing import Iterable, Mapping, Tuple, TypeVar, Union, List
from urllib.parse import urlencode

from youtubesearchpython.core.componenthandler import getVideoId, getValue
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import RequestCore

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
        if not searchKey:
            raise Exception("INNERTUBE API key (searchKey) is not set.")
        self.data = copy.deepcopy(requestPayload)
        ctx = self.data.setdefault("context", {})
        client = ctx.setdefault("client", {})
        client.setdefault("clientName", client.get("clientName", "WEB"))
        client.setdefault("clientVersion", client.get("clientVersion", "2.20210820.01.00"))
        self.data["videoId"] = getVideoId(self.videoLink)
        self.url = f"https://www.youtube.com/youtubei/v1/next?{urlencode({'key': searchKey})}"

    def prepare_comments_request(self):
        if not searchKey:
            raise Exception("INNERTUBE API key (searchKey) is not set.")
        self.data = copy.deepcopy(requestPayload)
        ctx = self.data.setdefault("context", {})
        client = ctx.setdefault("client", {})
        client.setdefault("clientName", client.get("clientName", "WEB"))
        client.setdefault("clientVersion", client.get("clientVersion", "2.20210820.01.00"))
        self.data["continuation"] = self.continuationKey
        self.url = f"https://www.youtube.com/youtubei/v1/next?{urlencode({'key': searchKey})}"

    def parse_source(self):
        data = self._safe_load_response(self.response)
        idx = 0 if self.isNextRequest else 1
        path = [
            "onResponseReceivedEndpoints",
            idx,
            "appendContinuationItemsAction" if self.isNextRequest else "reloadContinuationItemsCommand",
            "continuationItems",
        ]
        self.responseSource = getValue(data, path)

    def parse_continuation_source(self):
        data = self._safe_load_response(self.response)
        self.continuationKey = getValue(
            data,
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
        )

    def sync_make_comment_request(self):
        self.prepare_comments_request()
        self.response = self.syncPostRequest()
        if hasattr(self.response, "status_code") and self.response.status_code == 200:
            self.parse_source()

    def sync_make_continuation_request(self):
        self.prepare_continuation_request()
        self.response = self.syncPostRequest()
        if hasattr(self.response, "status_code") and self.response.status_code == 200:
            self.parse_continuation_source()
            if not self.continuationKey:
                raise Exception("Could not retrieve continuation token")
        else:
            raise Exception("Status code is not 200")

    async def async_make_comment_request(self):
        self.prepare_comments_request()
        self.response = await self.asyncPostRequest()
        if hasattr(self.response, "status_code") and self.response.status_code == 200:
            self.parse_source()

    async def async_make_continuation_request(self):
        self.prepare_continuation_request()
        self.response = await self.asyncPostRequest()
        if hasattr(self.response, "status_code") and self.response.status_code == 200:
            self.parse_continuation_source()
            if not self.continuationKey:
                raise Exception("Could not retrieve continuation token")
        else:
            raise Exception("Status code is not 200")

    def sync_create(self):
        self.sync_make_continuation_request()
        self.sync_make_comment_request()
        self.__getComponents()

    def sync_create_next(self):
        self.isNextRequest = True
        self.sync_make_comment_request()
        self.__getComponents()

    async def async_create(self):
        await self.async_make_continuation_request()
        await self.async_make_comment_request()
        self.__getComponents()

    async def async_create_next(self):
        self.isNextRequest = True
        await self.async_make_comment_request()
        self.__getComponents()

    def __getComponents(self) -> None:
        comments = []
        src = self.responseSource or []
        for comment in src:
            comment = getValue(comment, ["commentThreadRenderer", "comment", "commentRenderer"])
            try:
                j = {
                    "id": self.__getValue(comment, ["commentId"]),
                    "author": {
                        "id": self.__getValue(comment, ["authorEndpoint", "browseEndpoint", "browseId"]),
                        "name": self.__getValue(comment, ["authorText", "simpleText"]),
                        "thumbnails": self.__getValue(comment, ["authorThumbnail", "thumbnails"]),
                    },
                    "content": self.__getValue(comment, ["contentText", "runs", 0, "text"]),
                    "published": self.__getValue(comment, ["publishedTimeText", "runs", 0, "text"]),
                    "isLiked": self.__getValue(comment, ["isLiked"]),
                    "authorIsChannelOwner": self.__getValue(comment, ["authorIsChannelOwner"]),
                    "voteStatus": self.__getValue(comment, ["voteStatus"]),
                    "votes": {
                        "simpleText": self.__getValue(comment, ["voteCount", "simpleText"]),
                        "label": self.__getValue(comment, ["voteCount", "accessibility", "accessibilityData", "label"]),
                    },
                    "replyCount": self.__getValue(comment, ["replyCount"]),
                }
                comments.append(j)
            except Exception:
                pass

        self.commentsComponent["result"].extend(comments)
        self.continuationKey = self.__getValue(
            self.responseSource or [],
            [-1, "continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"],
        )

    def __result(self, mode: int) -> Union[dict, str]:
        if mode == ResultMode.dict:
            return self.commentsComponent
        elif mode == ResultMode.json:
            return json.dumps(self.commentsComponent, indent=4)

    def __getValue(self, source: Union[dict, list, None], path: Iterable[Union[str, int]]) -> Union[str, int, dict, None]:
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
                raise Exception("Invalid path")
            following_key = upcoming[0]
            upcoming = upcoming[1:]
            for val in self.__getAllWithKey(source or [], following_key):
                yield from self.__getValueEx(val, path=upcoming)
        else:
            val = self.__getValue(source, [key])
            if val is None:
                return
            yield from self.__getValueEx(val, path=upcoming)

    def __getFirstValue(self, source: dict, path: Iterable[Union[str, None]]) -> Union[str, int, dict, None]:
        values = self.__getValueEx(source or {}, list(path))
        for val in values:
            if val is not None:
                return val
        return None

    def _safe_load_response(self, response):
        try:
            if hasattr(response, "json"):
                return response.json()
            if hasattr(response, "text"):
                return json.loads(response.text)
            if isinstance(response, (str, bytes)):
                return json.loads(response)
        except Exception:
            return {}

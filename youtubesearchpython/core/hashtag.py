import copy
import json
from typing import Union

from youtubesearchpython.core.constants import *
from youtubesearchpython.core.componenthandler import ComponentHandler
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.exceptions import YouTubeRequestError, YouTubeParseError


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

    def sync_create(self):
        self._getParams()
        self._makeRequest()
        self._getComponents()

    async def async_create(self):
        await self._asyncGetParams()
        await self._asyncMakeRequest()
        self._getComponents()

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
        requestBody = copy.deepcopy(requestPayload)
        requestBody['query'] = "#" + (self.hashtag or "")
        ctx = requestBody.setdefault('context', {})
        client = ctx.setdefault('client', {})
        client.update({
            'hl': self.language or client.get('hl'),
            'gl': self.region or client.get('gl'),
        })
        return requestBody

    def _buildBrowseBody(self) -> dict:
        requestBody = copy.deepcopy(requestPayload)
        requestBody['browseId'] = hashtagBrowseKey
        requestBody['params'] = self.params
        ctx = requestBody.setdefault('context', {})
        client = ctx.setdefault('client', {})
        client.update({
            'hl': self.language or client.get('hl'),
            'gl': self.region or client.get('gl'),
        })
        if self.continuationKey:
            requestBody['continuation'] = self.continuationKey
        return requestBody

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
        if not self.continuationKey:
            responseSource = self._getValue(data, hashtagVideosPath) or []
        else:
            responseSource = self._getValue(data, hashtagContinuationVideosPath) or []
        for element in responseSource:
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
        if responseSource:
            self.continuationKey = self._getValue(responseSource[-1], continuationKeyPath)
            

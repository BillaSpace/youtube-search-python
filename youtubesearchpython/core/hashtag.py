import copy
import json
from typing import Union
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import httpx

from youtubesearchpython.core.constants import *
from youtubesearchpython.handlers.componenthandler import ComponentHandler


class HashtagCore(ComponentHandler):
    response = None
    resultComponents = []

    def __init__(self, hashtag: str, limit: int, language: str, region: str, timeout: int):
        self.hashtag = hashtag
        self.limit = limit
        self.language = language
        self.region = region
        self.timeout = timeout
        self.continuationKey = None
        self.params = None

    def sync_create(self):
        self._getParams()
        self._makeRequest()
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

    def _getParams(self) -> None:
        if not searchKey:
            raise Exception("INNERTUBE API key (searchKey) is not set.")
        requestBody = copy.deepcopy(requestPayload)
        requestBody['query'] = "#" + (self.hashtag or "")
        ctx = requestBody.setdefault('context', {})
        client = ctx.setdefault('client', {})
        client.update({
            'hl': self.language or client.get('hl'),
            'gl': self.region or client.get('gl'),
        })
        requestBodyBytes = json.dumps(requestBody).encode('utf-8')
        url = 'https://www.youtube.com/youtubei/v1/search' + '?' + urlencode({'key': searchKey})
        req = Request(url, data=requestBodyBytes, headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': userAgent})
        try:
            response = urlopen(req, timeout=self.timeout).read().decode('utf-8')
        except Exception:
            raise Exception('ERROR: Could not make request.')
        data = json.loads(response)
        content = self._getValue(data, contentPath) or []
        items = self._getValue(content, [0, 'itemSectionRenderer', 'contents']) or []
        for item in items:
            if hashtagElementKey in item:
                self.params = self._getValue(item[hashtagElementKey], ['onTapCommand', 'browseEndpoint', 'params'])
                return

    async def _asyncGetParams(self) -> None:
        if not searchKey:
            raise Exception("INNERTUBE API key (searchKey) is not set.")
        requestBody = copy.deepcopy(requestPayload)
        requestBody['query'] = "#" + (self.hashtag or "")
        ctx = requestBody.setdefault('context', {})
        client = ctx.setdefault('client', {})
        client.update({
            'hl': self.language or client.get('hl'),
            'gl': self.region or client.get('gl'),
        })
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'https://www.youtube.com/youtubei/v1/search',
                    params={'key': searchKey},
                    headers={'User-Agent': userAgent},
                    json=requestBody,
                    timeout=self.timeout
                )
                data = response.json()
        except Exception:
            raise Exception('ERROR: Could not make request.')
        content = self._getValue(data, contentPath) or []
        items = self._getValue(content, [0, 'itemSectionRenderer', 'contents']) or []
        for item in items:
            if hashtagElementKey in item:
                self.params = self._getValue(item[hashtagElementKey], ['onTapCommand', 'browseEndpoint', 'params'])
                return

    def _makeRequest(self) -> None:
        if self.params is None:
            return
        if not searchKey:
            raise Exception("INNERTUBE API key (searchKey) is not set.")
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
        requestBodyBytes = json.dumps(requestBody).encode('utf-8')
        url = 'https://www.youtube.com/youtubei/v1/browse' + '?' + urlencode({'key': searchKey})
        req = Request(url, data=requestBodyBytes, headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': userAgent})
        try:
            self.response = urlopen(req, timeout=self.timeout).read().decode('utf-8')
        except Exception:
            raise Exception('ERROR: Could not make request.')

    async def _asyncMakeRequest(self) -> None:
        if self.params is None:
            return
        if not searchKey:
            raise Exception("INNERTUBE API key (searchKey) is not set.")
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
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'https://www.youtube.com/youtubei/v1/browse',
                    params={'key': searchKey},
                    headers={'User-Agent': userAgent},
                    json=requestBody,
                    timeout=self.timeout
                )
                self.response = response.text
        except Exception:
            raise Exception('ERROR: Could not make request.')

    def _getComponents(self) -> None:
        if self.response is None:
            return
        self.resultComponents = []
        try:
            data = json.loads(self.response)
            if not self.continuationKey:
                responseSource = self._getValue(data, hashtagVideosPath) or []
            else:
                responseSource = self._getValue(data, hashtagContinuationVideosPath) or []
            for element in responseSource:
                rich = self._getValue(element, [richItemKey, 'content']) or {}
                if videoElementKey in rich:
                    videoComponent = self._getVideoComponent(rich)
                    self.resultComponents.append(videoComponent)
                if len(self.resultComponents) >= self.limit:
                    break
            if responseSource:
                self.continuationKey = self._getValue(responseSource[-1], continuationKeyPath)
        except Exception:
            raise Exception('ERROR: Could not parse YouTube response.')

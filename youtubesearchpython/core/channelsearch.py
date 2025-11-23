import copy
from typing import Union
import json
from urllib.parse import urlencode

from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.handlers.componenthandler import ComponentHandler
from youtubesearchpython.core.constants import *


class ChannelSearchCore(RequestCore, ComponentHandler):
    response = None
    responseSource = None
    resultComponents = []

    def __init__(self, query: str, language: str, region: str, searchPreferences: str, browseId: str, timeout: int):
        super().__init__()
        self.query = query
        self.language = language
        self.region = region
        self.browseId = browseId
        self.searchPreferences = searchPreferences
        self.continuationKey = None
        self.timeout = timeout

    def sync_create(self):
        self._syncRequest()
        self._parseChannelSearchSource()
        self.response = self._getChannelSearchComponent(self.response)

    async def next(self):
        await self._asyncRequest()
        self._parseChannelSearchSource()
        self.response = self._getChannelSearchComponent(self.response)
        return self.response

    def _parseChannelSearchSource(self) -> None:
        try:
            tabs = self.response.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []) or []
            last_tab = tabs[-1] if tabs else {}
            if 'expandableTabRenderer' in last_tab:
                self.response = last_tab["expandableTabRenderer"].get("content", {}).get("sectionListRenderer", {}).get("contents", [])
            else:
                tab_renderer = last_tab.get("tabRenderer", {})
                content = tab_renderer.get("content")
                if content and "sectionListRenderer" in content:
                    self.response = content["sectionListRenderer"].get("contents", [])
                else:
                    self.response = []
        except Exception:
            raise Exception('ERROR: Could not parse YouTube response.')

    def _getRequestBody(self):
        requestBody = copy.deepcopy(requestPayload)
        requestBody['query'] = self.query or ''
        context = requestBody.setdefault('context', {})
        client = context.setdefault('client', {})
        client.update({
            'hl': self.language or client.get('hl'),
            'gl': self.region or client.get('gl'),
        })
        if self.searchPreferences:
            requestBody['params'] = self.searchPreferences
        if self.browseId:
            requestBody['browseId'] = self.browseId
        if self.continuationKey:
            requestBody['continuation'] = self.continuationKey
        if not searchKey:
            raise Exception('INNERTUBE API key (searchKey) is not set.')
        self.url = 'https://www.youtube.com/youtubei/v1/browse' + '?' + urlencode({'key': searchKey})
        self.data = requestBody

    def _syncRequest(self) -> None:
        self._getRequestBody()
        request = self.syncPostRequest()
        try:
            self.response = request.json() if hasattr(request, "json") else json.loads(request.text)
        except Exception:
            raise Exception('ERROR: Could not make request.')

    async def _asyncRequest(self) -> None:
        self._getRequestBody()
        request = await self.asyncPostRequest()
        try:
            self.response = request.json() if hasattr(request, "json") else json.loads(request.text)
        except Exception:
            raise Exception('ERROR: Could not make request.')

    def result(self, mode: int = ResultMode.dict) -> Union[str, dict]:
        if mode == ResultMode.json:
            return json.dumps({'result': self.response}, indent=4)
        elif mode == ResultMode.dict:
            return {'result': self.response}

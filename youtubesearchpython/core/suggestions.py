import os
import json
import re
from typing import Union
from urllib.parse import urlencode

from youtubesearchpython.core.constants import ResultMode
from youtubesearchpython.core.requests import RequestCore


class SuggestionsCore(RequestCore):
    def __init__(self, language: str = 'en', region: str = 'US', timeout: int = None):
        super().__init__()
        self.language = language
        self.region = region
        self.timeout = timeout
        
        proxy = os.environ.get("YTS_PROXY") or os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
        if proxy:
            self.proxies = {"http": proxy, "https": proxy}

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
        if token:
            if not hasattr(self, "headers") or self.headers is None:
                self.headers = {}
            self.headers["x-youtube-identity-token"] = token

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
                except:
                    match = re.search(r'\[.*\]', self.response, re.DOTALL)
                    if match:
                        self.responseSource = json.loads(match.group())
                    else:
                        raise Exception('Could not find JSON in response through this query')
        except Exception as e:
            raise Exception(f'ERROR: Could not parse YouTube response. {str(e)}')

    def __makeRequest(self) -> None:
        request = self.syncGetRequest()
        self.response = request.text if hasattr(request, 'text') else str(request)

    async def __makeAsyncRequest(self) -> None:
        request = await self.asyncGetRequest()
        self.response = request.text if hasattr(request, 'text') else str(request)

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
        
        if isinstance(self.responseSource, list) and len(self.responseSource) >= 2:
            suggestions_block = self.responseSource[1]
            if isinstance(suggestions_block, list):
                for item in suggestions_block:
                    if isinstance(item, list) and len(item) > 0 and isinstance(item[0], str):
                        searchSuggestions.append(item[0])

        if not searchSuggestions:
            def flatten_strings(obj):
                if isinstance(obj, str):
                    searchSuggestions.append(obj)
                elif isinstance(obj, list):
                    for v in obj:
                        flatten_strings(v)
                elif isinstance(obj, dict):
                    for v in obj.values():
                        flatten_strings(v)
            flatten_strings(self.responseSource)

        seen = set()
        searchSuggestions = [x for x in searchSuggestions if x not in seen and not seen.add(x)]

        if mode == ResultMode.dict:
            return {'result': searchSuggestions}
        elif mode == ResultMode.json:
            return json.dumps({'result': searchSuggestions}, indent=4, ensure_ascii=False)

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
        if not self.response or len(self.response.strip()) == 0:
            raise Exception("Empty response from Google Suggest endpoint")

        text = self.response.strip()

        start_idx = text.find('(')
        end_idx = text.rfind(')')

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_candidate = text[start_idx + 1:end_idx].strip()
            try:
                self.responseSource = json.loads(json_candidate)
                return
            except json.JSONDecodeError:
                pass

        try:
            self.responseSource = json.loads(text)
            if isinstance(self.responseSource, list):
                return
        except json.JSONDecodeError:
            pass

        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            try:
                self.responseSource = json.loads(match.group(0))
                return
            except json.JSONDecodeError:
                pass

        preview = text[:300].replace('\n', ' ').replace('\r', '')
        raise Exception(f"Could not extract JSON from Google Suggest response. Response preview: {preview} ...")

    def __makeRequest(self) -> None:
        request = self.syncGetRequest()
        self.response = request.text if hasattr(request, 'text') else str(request)

    async def __makeAsyncRequest(self) -> None:
        request = await self.asyncGetRequest()
        self.response = request.text if hasattr(request, 'text') else str(request)

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
            block = self.responseSource[1]
            if isinstance(block, list):
                for item in block:
                    if isinstance(item, list) and len(item) > 0 and isinstance(item[0], str):
                        searchSuggestions.append(item[0])

        if not searchSuggestions:
            def extract_strings(obj):
                if isinstance(obj, str):
                    searchSuggestions.append(obj)
                elif isinstance(obj, list):
                    for v in obj:
                        extract_strings(v)
                elif isinstance(obj, dict):
                    for v in obj.values():
                        extract_strings(v)
            extract_strings(self.responseSource)

        seen = set()
        searchSuggestions = [x for x in searchSuggestions if not (x in seen or seen.add(x))]

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
            'client': 'youtube',
            'hl': self.language,
            'gl': self.region,
            'q': query,
            'ds': 'yt',
            'gs_ri': 'youtube',
        })

        if not hasattr(self, 'headers') or self.headers is None:
            self.headers = {}

        self.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Referer': 'https://www.youtube.com/',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        })

        token = os.environ.get("YTS_IDENTITY_TOKEN")
        if token:
            self.headers["x-youtube-identity-token"] = token

    def __parseSource(self) -> None:
        if not self.response or not self.response.strip():
            raise Exception("Empty response from Google Suggest endpoint")

        text = self.response.strip()

        if '(' in text and ')' in text:
            start = text.find('(')
            end = text.rfind(')')
            if start < end:
                candidate = text[start + 1:end].strip()
                try:
                    self.responseSource = json.loads(candidate)
                    return
                except json.JSONDecodeError:
                    pass

        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                self.responseSource = parsed
                return
        except json.JSONDecodeError:
            pass

        match = re.search(r'\[.*?\](?=\s|$)', text, re.DOTALL)
        if match:
            try:
                self.responseSource = json.loads(match.group(0))
                return
            except json.JSONDecodeError:
                pass

        preview = text[:400].replace('\n', ' ').replace('\r', '')
        raise Exception(f"Failed to parse Google Suggest response. Preview: {preview} ...")

    def __makeRequest(self) -> None:
        request = self.syncGetRequest()
        self.response = request.text if hasattr(request, 'text') else str(request)

    async def __makeAsyncRequest(self) -> None:
        request = await self.asyncGetRequest()
        self.response = request.text if hasattr(request, 'text') else str(request)

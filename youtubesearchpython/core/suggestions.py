import json
from typing import Union
from urllib.parse import urlencode

from youtubesearchpython.core.constants import ResultMode, userAgent
from youtubesearchpython.core.requests import RequestCore


class SuggestionsCore(RequestCore):
    def __init__(self, language: str = 'en', region: str = 'US', timeout: int = None):
        super().__init__()
        self.language = language
        self.region = region
        self.timeout = timeout
        self.responseSource = None
        self.response = None

    def _post_request_processing(self, mode):
        searchSuggestions = []
        self.__parseSource()
        for element in self.responseSource:
            if isinstance(element, list):
                for searchSuggestionElement in element:
                    if searchSuggestionElement and isinstance(searchSuggestionElement, list):
                        searchSuggestions.append(searchSuggestionElement[0])
                break
        if mode == ResultMode.dict:
            return {'result': searchSuggestions}
        elif mode == ResultMode.json:
            return json.dumps({'result': searchSuggestions}, indent=4)

    def _get(self, query: str, mode: int = ResultMode.dict) -> Union[dict, str]:
        self.url = 'https://clients1.google.com/complete/search' + '?' + urlencode({
            'hl': self.language,
            'gl': self.region,
            'q': query,
            'client': 'youtube',
            'gs_ri': 'youtube',
            'ds': 'yt',
        })
        self.__makeRequest()
        return self._post_request_processing(mode)

    async def _getAsync(self, query: str, mode: int = ResultMode.dict) -> Union[dict, str]:
        self.url = 'https://clients1.google.com/complete/search' + '?' + urlencode({
            'hl': self.language,
            'gl': self.region,
            'q': query,
            'client': 'youtube',
            'gs_ri': 'youtube',
            'ds': 'yt',
        })
        await self.__makeAsyncRequest()
        return self._post_request_processing(mode)

    def __parseSource(self) -> None:
        try:
            raw = (self.response or "").strip()
            try:
                self.responseSource = json.loads(raw)
                if not isinstance(self.responseSource, list):
                    raise ValueError
            except Exception:
                start = raw.find('(')
                end = raw.rfind(')')
                if start != -1 and end != -1 and end > start:
                    payload = raw[start + 1:end]
                    self.responseSource = json.loads(payload)
                else:
                    raise
        except Exception:
            raise Exception('ERROR: Could not parse suggestion response.')

    def __makeRequest(self) -> None:
        request = self.syncGetRequest()
        self.response = request.text

    async def __makeAsyncRequest(self) -> None:
        request = await self.asyncGetRequest()
        self.response = request.text

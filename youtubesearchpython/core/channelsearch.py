import copy
from typing import Union, Optional
import json
from urllib.parse import urlencode

from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import ComponentHandler
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.exceptions import YouTubeRequestError, YouTubeParseError
import httpx


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
        return {'result': self.response}

    def _parseChannelSearchSource(self) -> None:
        try:
            tabs = self.response.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
            if not tabs:
                tabs = self.response.get("contents", {}).get("singleColumnBrowseResultsRenderer", {}).get("tabs", [])
            
            if not tabs:
                self.response = []
                return
            
            last_tab = tabs[-1]
            
            if 'expandableTabRenderer' in last_tab:
                expandable = last_tab["expandableTabRenderer"]
                if 'content' in expandable:
                    content = expandable["content"]
                    if 'sectionListRenderer' in content:
                        self.response = content["sectionListRenderer"].get("contents", [])
                    else:
                        self.response = []
                else:
                    if 'sectionListRenderer' in expandable:
                        self.response = expandable["sectionListRenderer"].get("contents", [])
                    else:
                        self.response = []
            elif 'tabRenderer' in last_tab:
                tab_renderer = last_tab["tabRenderer"]
                if 'content' in tab_renderer:
                    content = tab_renderer["content"]
                    if 'sectionListRenderer' in content:
                        self.response = content["sectionListRenderer"].get("contents", [])
                    else:
                        self.response = []
                else:
                    self.response = []
            else:
                self.response = []
        except (KeyError, AttributeError, IndexError) as e:
            raise YouTubeParseError(f'Failed to parse YouTube response: {str(e)}')
        except Exception as e:
            raise YouTubeParseError(f'Unexpected error parsing response: {str(e)}')

    def _getRequestBody(self):
        ''' Fixes #v2 '''
        requestBody = copy.deepcopy(requestPayload)
        requestBody['query'] = self.query
        requestBody['client'] = {
            'hl': self.language,
            'gl': self.region,
        }
        requestBody['params'] = self.searchPreferences
        requestBody['browseId'] = self.browseId
        self.url = 'https://www.youtube.com/youtubei/v1/browse' + '?' + urlencode({
            'key': searchKey,
        })
        self.data = requestBody

    def _syncRequest(self) -> None:
        ''' Fixes #v2 '''
        self._getRequestBody()

        try:
            request = self.syncPostRequest()
            if request.status_code != 200:
                raise YouTubeRequestError(f'Request failed with status code {request.status_code}. URL: {self.url}')
            self.response = request.json()
        except httpx.RequestError as e:
            raise YouTubeRequestError(f'Failed to make request to {self.url}: {str(e)}')
        except httpx.HTTPStatusError as e:
            raise YouTubeRequestError(f'HTTP error {e.response.status_code} for {self.url}: {str(e)}')
        except json.JSONDecodeError as e:
            raise YouTubeRequestError(f'Failed to decode JSON response: {str(e)}')
        except Exception as e:
            raise YouTubeRequestError(f'Unexpected error making request: {str(e)}')

    async def _asyncRequest(self) -> None:
        ''' Fixes #v2 '''
        self._getRequestBody()

        try:
            request = await self.asyncPostRequest()
            if request.status_code != 200:
                raise YouTubeRequestError(f'Request failed with status code {request.status_code}. URL: {self.url}')
            self.response = request.json()
        except httpx.RequestError as e:
            raise YouTubeRequestError(f'Failed to make request to {self.url}: {str(e)}')
        except httpx.HTTPStatusError as e:
            raise YouTubeRequestError(f'HTTP error {e.response.status_code} for {self.url}: {str(e)}')
        except json.JSONDecodeError as e:
            raise YouTubeRequestError(f'Failed to decode JSON response: {str(e)}')
        except Exception as e:
            raise YouTubeRequestError(f'Unexpected error making request: {str(e)}')

    def result(self, mode: int = ResultMode.dict) -> Union[str, dict]:
        '''Returns the search result.
        Args:
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.
        Returns:
            Union[str, dict]: Returns JSON or dictionary.
        '''
        if mode == ResultMode.json:
            return json.dumps({'result': self.response}, indent=4)
        elif mode == ResultMode.dict:
            return {'result': self.response}

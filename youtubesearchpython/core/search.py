import copy
from typing import Union, Optional
from urllib.parse import urlencode

from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import ComponentHandler
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.exceptions import YouTubeRequestError, YouTubeParseError
import json
import httpx


class SearchCore(RequestCore, ComponentHandler):
    response = None
    responseSource = None
    resultComponents = []

    def __init__(self, query: str, limit: int, language: str, region: str, searchPreferences: str, timeout: Optional[int]):
        super().__init__(timeout=timeout)
        self.query = query
        self.limit = limit
        self.language = language
        self.region = region
        self.searchPreferences = searchPreferences
        self.timeout = timeout
        self.continuationKey = None

    def sync_create(self):
        self._makeRequest()
        self._parseSource()

    def _getRequestBody(self):
        ''' Fixes #47 '''
        requestBody = copy.deepcopy(requestPayload)
        requestBody['query'] = self.query
        requestBody['client'] = {
            'hl': self.language,
            'gl': self.region,
        }
        if self.searchPreferences:
            requestBody['params'] = self.searchPreferences
        if self.continuationKey:
            requestBody['continuation'] = self.continuationKey
        self.url = 'https://www.youtube.com/youtubei/v1/search' + '?' + urlencode({
            'key': searchKey,
        })
        self.data = requestBody

    def _makeRequest(self) -> None:
        self._getRequestBody()
        try:
            request = self.syncPostRequest()
            if request.status_code != 200:
                raise YouTubeRequestError(f'Request failed with status code {request.status_code}. URL: {self.url}')
            self.response = request.text
        except httpx.RequestError as e:
            raise YouTubeRequestError(f'Failed to make request to {self.url}: {str(e)}')
        except httpx.HTTPStatusError as e:
            raise YouTubeRequestError(f'HTTP error {e.response.status_code} for {self.url}: {str(e)}')
        except Exception as e:
            raise YouTubeRequestError(f'Unexpected error making request: {str(e)}')

    async def _makeAsyncRequest(self) -> None:
        self._getRequestBody()
        try:
            request = await self.asyncPostRequest()
            if request.status_code != 200:
                raise YouTubeRequestError(f'Request failed with status code {request.status_code}. URL: {self.url}')
            self.response = request.text
        except httpx.RequestError as e:
            raise YouTubeRequestError(f'Failed to make request to {self.url}: {str(e)}')
        except httpx.HTTPStatusError as e:
            raise YouTubeRequestError(f'HTTP error {e.response.status_code} for {self.url}: {str(e)}')
        except Exception as e:
            raise YouTubeRequestError(f'Unexpected error making request: {str(e)}')

    def _parseSource(self) -> None:
        try:
            if not self.continuationKey:
                responseContent = self._getValue(json.loads(self.response), contentPath)
            else:
                responseContent = self._getValue(json.loads(self.response), continuationContentPath)
            if responseContent:
                for element in responseContent:
                    if itemSectionKey in element.keys():
                        self.responseSource = self._getValue(element, [itemSectionKey, 'contents'])
                    if continuationItemKey in element.keys():
                        self.continuationKey = self._getValue(element, continuationKeyPath)
            else:
                self.responseSource = self._getValue(json.loads(self.response), fallbackContentPath)
                self.continuationKey = self._getValue(self.responseSource[-1], continuationKeyPath)
        except json.JSONDecodeError as e:
            raise YouTubeParseError(f'Failed to parse JSON response: {str(e)}')
        except KeyError as e:
            raise YouTubeParseError(f'Missing expected key in response: {str(e)}')
        except Exception as e:
            raise YouTubeParseError(f'Failed to parse YouTube response: {str(e)}')

    def result(self, mode: int = ResultMode.dict) -> Union[str, dict]:
        '''Returns the search result.

        Args:
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.

        Returns:
            Union[str, dict]: Returns JSON or dictionary.
        '''
        if mode == ResultMode.json:
            return json.dumps({'result': self.resultComponents}, indent=4)
        elif mode == ResultMode.dict:
            return {'result': self.resultComponents}

    def _next(self) -> bool:
        '''Gets the subsequent search result. Call result

        Args:
            mode (int, optional): Sets the type of result. Defaults to ResultMode.dict.

        Returns:
            Union[str, dict]: Returns True if getting more results was successful.
        '''
        if self.continuationKey:
            self.response = None
            self.responseSource = None
            self.resultComponents = []
            self._makeRequest()
            self._parseSource()
            self._getComponents(*self.searchMode)
            return True
        else:
            return False

    async def _nextAsync(self) -> dict:
        self.response = None
        self.responseSource = None
        self.resultComponents = []
        await self._makeAsyncRequest()
        self._parseSource()
        self._getComponents(*self.searchMode)
        return {
            'result': self.resultComponents,
        }

    def _getComponents(self, findVideos: bool, findChannels: bool, findPlaylists: bool) -> None:
        self.resultComponents = []
        for element in self.responseSource:
            if videoElementKey in element.keys() and findVideos:
                self.resultComponents.append(self._getVideoComponent(element))
            if channelElementKey in element.keys() and findChannels:
                self.resultComponents.append(self._getChannelComponent(element))
            if playlistElementKey in element.keys() and findPlaylists:
                self.resultComponents.append(self._getPlaylistComponent(element))
            if shelfElementKey in element.keys() and findVideos:
                for shelfElement in self._getShelfComponent(element)['elements']:
                    self.resultComponents.append(
                        self._getVideoComponent(shelfElement, shelfTitle=self._getShelfComponent(element)['title']))
            if richItemKey in element.keys():
                richItemElement = self._getValue(element, [richItemKey, 'content'])
                if videoElementKey in richItemElement.keys() and findVideos:
                    videoComponent = self._getVideoComponent(richItemElement)
                    self.resultComponents.append(videoComponent)
                if channelElementKey in richItemElement.keys() and findChannels:
                    channelComponent = self._getChannelComponent(richItemElement)
                    self.resultComponents.append(channelComponent)
                if playlistElementKey in richItemElement.keys() and findPlaylists:
                    playlistComponent = self._getPlaylistComponent(richItemElement)
                    self.resultComponents.append(playlistComponent)
                if "lockupViewModel" in richItemElement.keys():
                    lockupComponent = self._getLockupComponent(richItemElement, findVideos, findChannels, findPlaylists)
                    if lockupComponent:
                        self.resultComponents.append(lockupComponent)

            if "lockupViewModel" in element.keys():
                lockupComponent = self._getLockupComponent(element, findVideos, findChannels, findPlaylists)
                if lockupComponent:
                    self.resultComponents.append(lockupComponent)
            if len(self.resultComponents) >= self.limit:
                break

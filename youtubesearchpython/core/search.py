from typing import Union, Optional
from urllib.parse import urlencode

from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import ComponentHandler
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import YouTubeRequestError, YouTubeParseError
import json
import httpx


class SearchCore(RequestCore, ComponentHandler):
    def __init__(self, query: str, limit: int, language: str, region: str, searchPreferences: str, timeout: Optional[int]):
        super().__init__(timeout=timeout)
        self.query = query
        self.limit = limit
        self.language = language
        self.region = region
        self.searchPreferences = searchPreferences
        self.continuationKey = None
        self.response = None
        self.responseSource = []
        self.resultComponents = []
        self._async_started = False

    def sync_create(self):
        self._makeRequest()
        self._parseSource()

    def _getRequestBody(self):
        overrides = {'client': {'hl': self.language, 'gl': self.region}}
        if self.continuationKey:
            overrides['continuation'] = self.continuationKey
        else:
            overrides['query'] = self.query
            if self.searchPreferences:
                overrides['params'] = self.searchPreferences
        self.url = 'https://www.youtube.com/youtubei/v1/search' + '?' + urlencode({
            'key': searchKey,
        })
        self.data = self.buildInnertubeBody(**overrides)

    def _makeRequest(self) -> None:
        self._getRequestBody()
        try:
            request = self.syncPostRequest()
            if request.status_code != 200:
                raise YouTubeRequestError(f'Request failed with status code {request.status_code}. URL: {self.url}')
            self.response = request.text
        except YouTubeRequestError:
            raise
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
        except YouTubeRequestError:
            raise
        except httpx.RequestError as e:
            raise YouTubeRequestError(f'Failed to make request to {self.url}: {str(e)}')
        except httpx.HTTPStatusError as e:
            raise YouTubeRequestError(f'HTTP error {e.response.status_code} for {self.url}: {str(e)}')
        except Exception as e:
            raise YouTubeRequestError(f'Unexpected error making request: {str(e)}')

    def _parseSource(self) -> None:
        try:
            data = json.loads(self.response)
            continuing = self.continuationKey is not None
            self.continuationKey = None
            self.responseSource = []
            if continuing:
                responseContent = self._getValue(data, continuationContentPath)
                if responseContent is None:
                    responseContent = self._getValue(data, ["onResponseReceivedActions", 0, "appendContinuationItemsAction", "continuationItems"])
                if responseContent is None:
                    responseContent = self._getValue(data, ["onResponseReceivedEndpoints", 0, "appendContinuationItemsAction", "continuationItems"])
            else:
                responseContent = self._getValue(data, contentPath)
            if responseContent:
                for element in responseContent:
                    if not isinstance(element, dict):
                        continue
                    if itemSectionKey in element:
                        self.responseSource.extend(self._getValue(element, [itemSectionKey, "contents"]) or [])
                    elif richItemKey in element or videoElementKey in element or channelElementKey in element or playlistElementKey in element or "lockupViewModel" in element:
                        self.responseSource.append(element)
                    if continuationItemKey in element:
                        self.continuationKey = self._getValue(element, continuationKeyPath)
            elif not continuing:
                self.responseSource = self._getValue(data, fallbackContentPath) or []
                if self.responseSource:
                    self.continuationKey = self._getValue(self.responseSource[-1], continuationKeyPath)
        except json.JSONDecodeError as e:
            raise YouTubeParseError(f'Failed to parse JSON response: {str(e)}')
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
        if self._async_started and not self.continuationKey:
            self.resultComponents = []
            return {'result': []}
        self.response = None
        self.responseSource = None
        self.resultComponents = []
        await self._makeAsyncRequest()
        self._parseSource()
        self._getComponents(*self.searchMode)
        self._async_started = True
        return {'result': self.resultComponents}

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
                shelf = self._getShelfComponent(element)
                for shelfElement in shelf['elements']:
                    if videoElementKey in shelfElement.keys():
                        self.resultComponents.append(
                            self._getVideoComponent(shelfElement, shelfTitle=shelf['title']))
            if richItemKey in element.keys():
                richItemElement = self._getValue(element, [richItemKey, 'content'])
                if not isinstance(richItemElement, dict):
                    continue
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


import json
from typing import Union, Optional
from urllib.parse import urlencode

import httpx

from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import ComponentHandler
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import YouTubeRequestError, YouTubeParseError


class ChannelSearchCore(RequestCore, ComponentHandler):
    def __init__(self, query: str, language: str, region: str, searchPreferences: str, browseId: str, timeout: Optional[int]):
        super().__init__(timeout=timeout)
        self.query = query
        self.language = language
        self.region = region
        self.browseId = browseId
        self.searchPreferences = searchPreferences
        self.continuationKey = None
        self.response = None
        self.responseSource = None
        self.resultComponents = []

    @staticmethod
    def _find_continuation(value):
        if isinstance(value, dict):
            command = value.get("continuationCommand")
            if isinstance(command, dict) and command.get("token"):
                return command["token"]
            for child in value.values():
                token = ChannelSearchCore._find_continuation(child)
                if token:
                    return token
        elif isinstance(value, list):
            for child in value:
                token = ChannelSearchCore._find_continuation(child)
                if token:
                    return token
        return None

    @staticmethod
    def _continuation_items(value):
        if isinstance(value, dict):
            action = value.get("appendContinuationItemsAction")
            if isinstance(action, dict) and isinstance(action.get("continuationItems"), list):
                return action["continuationItems"]
            for child in value.values():
                items = ChannelSearchCore._continuation_items(child)
                if items is not None:
                    return items
        elif isinstance(value, list):
            for child in value:
                items = ChannelSearchCore._continuation_items(child)
                if items is not None:
                    return items
        return None

    def sync_create(self):
        self._syncRequest()
        source = self.response
        self.continuationKey = self._find_continuation(source)
        self._parseChannelSearchSource()
        self.response = self._getChannelSearchComponent(self.response)
        return {'result': self.response}

    async def async_create(self):
        await self._asyncRequest()
        source = self.response
        self.continuationKey = self._find_continuation(source)
        self._parseChannelSearchSource()
        self.response = self._getChannelSearchComponent(self.response)
        return {'result': self.response}

    def sync_next(self):
        if not self.continuationKey:
            return {'result': self.response}
        self._syncRequest(self.continuationKey)
        source = self.response
        self.continuationKey = self._find_continuation(source)
        self._parseChannelSearchSource()
        self.response = self._getChannelSearchComponent(self.response)
        return {'result': self.response}

    async def async_next(self):
        if not self.continuationKey:
            return {'result': self.response}
        await self._asyncRequest(self.continuationKey)
        source = self.response
        self.continuationKey = self._find_continuation(source)
        self._parseChannelSearchSource()
        self.response = self._getChannelSearchComponent(self.response)
        return {'result': self.response}

    def _parseChannelSearchSource(self) -> None:
        try:
            continuation_items = self._continuation_items(self.response)
            if continuation_items is not None:
                self.response = continuation_items
                return
            tabs = self.response.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
            if not tabs:
                tabs = self.response.get("contents", {}).get("singleColumnBrowseResultsRenderer", {}).get("tabs", [])
            if not tabs:
                self.response = []
                return
            last_tab = tabs[-1]
            if "expandableTabRenderer" in last_tab:
                expandable = last_tab["expandableTabRenderer"]
                if "content" in expandable:
                    content = expandable["content"]
                    if "sectionListRenderer" in content:
                        self.response = content["sectionListRenderer"].get("contents", [])
                    else:
                        self.response = []
                elif "sectionListRenderer" in expandable:
                    self.response = expandable["sectionListRenderer"].get("contents", [])
                else:
                    self.response = []
            elif "tabRenderer" in last_tab:
                tab_renderer = last_tab["tabRenderer"]
                if "content" in tab_renderer:
                    content = tab_renderer["content"]
                    if "sectionListRenderer" in content:
                        self.response = content["sectionListRenderer"].get("contents", [])
                    else:
                        self.response = []
                else:
                    self.response = []
            else:
                self.response = []
        except (KeyError, AttributeError, IndexError) as error:
            raise YouTubeParseError(f"Failed to parse YouTube response: {error}")
        except Exception as error:
            raise YouTubeParseError(f"Unexpected error parsing response: {error}")

    def _getRequestBody(self, continuation: str = None):
        if continuation:
            self.data = self.buildInnertubeBody(client={'hl': self.language, 'gl': self.region}, continuation=continuation)
        else:
            self.data = self.buildInnertubeBody(
                query=self.query,
                client={'hl': self.language, 'gl': self.region},
                params=self.searchPreferences,
                browseId=self.browseId
            )
        self.url = "https://www.youtube.com/youtubei/v1/browse?" + urlencode({
            "key": searchKey
        })

    def _syncRequest(self, continuation: str = None) -> None:
        self._getRequestBody(continuation)
        try:
            request = self.syncPostRequest()
            if request.status_code != 200:
                raise YouTubeRequestError(
                    f"Request failed with status code {request.status_code}. URL: {self.url}"
                )
            self.response = request.json()
        except httpx.RequestError as error:
            raise YouTubeRequestError(f"Failed to make request to {self.url}: {error}")
        except httpx.HTTPStatusError as error:
            raise YouTubeRequestError(
                f"HTTP error {error.response.status_code} for {self.url}: {error}"
            )
        except json.JSONDecodeError as error:
            raise YouTubeRequestError(f"Failed to decode JSON response: {error}")
        except YouTubeRequestError:
            raise
        except Exception as error:
            raise YouTubeRequestError(f"Unexpected error making request: {error}")

    async def _asyncRequest(self, continuation: str = None) -> None:
        self._getRequestBody(continuation)
        try:
            request = await self.asyncPostRequest()
            if request.status_code != 200:
                raise YouTubeRequestError(
                    f"Request failed with status code {request.status_code}. URL: {self.url}"
                )
            self.response = request.json()
        except httpx.RequestError as error:
            raise YouTubeRequestError(f"Failed to make request to {self.url}: {error}")
        except httpx.HTTPStatusError as error:
            raise YouTubeRequestError(
                f"HTTP error {error.response.status_code} for {self.url}: {error}"
            )
        except json.JSONDecodeError as error:
            raise YouTubeRequestError(f"Failed to decode JSON response: {error}")
        except YouTubeRequestError:
            raise
        except Exception as error:
            raise YouTubeRequestError(f"Unexpected error making request: {error}")

    def result(self, mode: int = ResultMode.dict) -> Union[str, dict]:
        if mode == ResultMode.json:
            return json.dumps({'result': self.response}, indent=4)
        if mode == ResultMode.dict:
            return {'result': self.response}

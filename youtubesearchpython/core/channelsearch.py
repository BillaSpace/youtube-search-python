import json
from typing import Union, Optional
from urllib.parse import urlencode

import httpx

from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import ComponentHandler
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.exceptions import YouTubeRequestError, YouTubeParseError


class ChannelSearchCore(RequestCore, ComponentHandler):
    def __init__(self, query: str, language: str, region: str, searchPreferences: str, browseId: str, timeout: Optional[int]):
        super().__init__(timeout=timeout)
        self.query = query
        self.language = language
        self.region = region
        self.browseId = browseId
        self.searchPreferences = searchPreferences
        self.timeout = timeout
        self.continuationKey = None
        self.response = None
        self.responseSource = None
        self.resultComponents = []

    def sync_create(self):
        self._syncRequest()
        self._parseChannelSearchSource()
        self.response = self._getChannelSearchComponent(self.response)

    async def async_create(self):
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

    def _getRequestBody(self):
        self.data = self.buildInnertubeBody(
            query=self.query,
            client={'hl': self.language, 'gl': self.region},
            params=self.searchPreferences,
            browseId=self.browseId
        )
        self.url = "https://www.youtube.com/youtubei/v1/browse?" + urlencode({
            "key": searchKey
        })

    def _syncRequest(self) -> None:
        self._getRequestBody()
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

    async def _asyncRequest(self) -> None:
        self._getRequestBody()
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

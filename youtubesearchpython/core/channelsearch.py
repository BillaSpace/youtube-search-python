import copy
from typing import Union
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
        return {"result": self.response}

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
                content = expandable.get("content", expandable)
                self.response = content.get("sectionListRenderer", {}).get("contents", []) or []
            elif "tabRenderer" in last_tab:
                tab_renderer = last_tab["tabRenderer"]
                content = tab_renderer.get("content", {})
                self.response = content.get("sectionListRenderer", {}).get("contents", []) or []
            else:
                self.response = []
        except (KeyError, AttributeError, IndexError) as e:
            raise YouTubeParseError(f"Failed to parse YouTube response: {str(e)}")
        except Exception as e:
            raise YouTubeParseError(f"Unexpected error parsing response: {str(e)}")

    def _getRequestBody(self):
        # IMPORTANT: keep the youtubei "context" structure intact.
        requestBody = copy.deepcopy(requestPayload)

        # Ensure context/client exists
        if "context" not in requestBody or not isinstance(requestBody["context"], dict):
            requestBody["context"] = {}
        if "client" not in requestBody["context"] or not isinstance(requestBody["context"]["client"], dict):
            requestBody["context"]["client"] = {}

        # Set language/region in the correct place (NOT top-level "client")
        requestBody["context"]["client"]["hl"] = self.language
        requestBody["context"]["client"]["gl"] = self.region

        # Channel browse search fields
        if self.query is not None:
            requestBody["query"] = self.query

        if self.searchPreferences:
            requestBody["params"] = self.searchPreferences

        if self.browseId:
            requestBody["browseId"] = self.browseId

        # URL for browse endpoint
        self.url = "https://www.youtube.com/youtubei/v1/browse?" + urlencode({"key": searchKey})
        self.data = requestBody

    def _syncRequest(self) -> None:
        self._getRequestBody()
        try:
            request = self.syncPostRequest()
            if request.status_code != 200:
                raise YouTubeRequestError(f"Request failed with status code {request.status_code}. URL: {self.url}")
            self.response = request.json()
        except httpx.RequestError as e:
            raise YouTubeRequestError(f"Failed to make request to {self.url}: {str(e)}")
        except json.JSONDecodeError as e:
            raise YouTubeRequestError(f"Failed to decode JSON response: {str(e)}")
        except Exception as e:
            raise YouTubeRequestError(f"Unexpected error making request: {str(e)}")

    async def _asyncRequest(self) -> None:
        self._getRequestBody()
        try:
            request = await self.asyncPostRequest()
            if request.status_code != 200:
                raise YouTubeRequestError(f"Request failed with status code {request.status_code}. URL: {self.url}")
            self.response = request.json()
        except httpx.RequestError as e:
            raise YouTubeRequestError(f"Failed to make request to {self.url}: {str(e)}")
        except json.JSONDecodeError as e:
            raise YouTubeRequestError(f"Failed to decode JSON response: {str(e)}")
        except Exception as e:
            raise YouTubeRequestError(f"Unexpected error making request: {str(e)}")

    def result(self, mode: int = ResultMode.dict) -> Union[str, dict]:
        if mode == ResultMode.json:
            return json.dumps({"result": self.response}, indent=4)
        return {"result": self.response}

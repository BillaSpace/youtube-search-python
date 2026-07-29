"""
DEPRECATED transport used only by `youtubesearchpython.legacy` (SearchVideos /
SearchPlaylists). This used to be a third, independent copy of the same
"post an innertube search request, then walk contentPath" logic already
implemented in `core/search.py`, but built on raw `urllib.request` instead of
the shared httpx-based `RequestCore` - a different transport stack with the
same `hl`/`gl` top-level-key bug the rest of the library had. It now reuses
the single canonical implementation (pooled httpx client, correctly nested
request body) instead of maintaining its own copy.
"""
import json

from youtubesearchpython.core.componenthandler import ComponentHandler
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.exceptions import YouTubeRequestError, YouTubeParseError
from youtubesearchpython.core.requests import RequestCore


class RequestHandler(RequestCore, ComponentHandler):
    def _getRequestBody(self) -> dict:
        overrides = {'query': self.query, 'client': {'hl': self.language, 'gl': self.region}}
        if getattr(self, 'searchPreferences', None):
            overrides['params'] = self.searchPreferences
        if getattr(self, 'continuationKey', None):
            overrides['continuation'] = self.continuationKey
        return overrides

    def _makeRequest(self) -> None:
        self.url = 'https://www.youtube.com/youtubei/v1/search?key=' + searchKey
        self.data = self.buildInnertubeBody(**self._getRequestBody())
        # `timeout` may not be set by every legacy caller
        if not hasattr(self, 'timeout'):
            self.timeout = None
        try:
            response = self.syncPostRequest()
            if response.status_code != 200:
                raise YouTubeRequestError(f'Request failed with status code {response.status_code}. URL: {self.url}')
            self.response = response.text
        except YouTubeRequestError:
            raise
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
                self.responseSource = self._getValue(json.loads(self.response), fallbackContentPath) or []
                if self.responseSource:
                    self.continuationKey = self._getValue(self.responseSource[-1], continuationKeyPath)
        except json.JSONDecodeError as e:
            raise YouTubeParseError(f'Failed to parse JSON response: {str(e)}')
        except KeyError as e:
            raise YouTubeParseError(f'Missing expected continuity key in response: {str(e)}')
        except Exception as e:
            raise YouTubeParseError(f'Failed to parse YouTube response: {str(e)}')
            

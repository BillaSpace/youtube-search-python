import json

from youtubesearchpython.core.componenthandler import ComponentHandler
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import YouTubeRequestError, YouTubeParseError
from youtubesearchpython.core.requests import RequestCore


class RequestHandler(RequestCore, ComponentHandler):
    def _getRequestBody(self) -> dict:
        overrides = {'client': {'hl': self.language, 'gl': self.region}}
        if getattr(self, 'continuationKey', None):
            overrides['continuation'] = self.continuationKey
        else:
            overrides['query'] = self.query
            if getattr(self, 'searchPreferences', None):
                overrides['params'] = self.searchPreferences
        return overrides

    def _makeRequest(self) -> None:
        self.url = 'https://www.youtube.com/youtubei/v1/search?key=' + searchKey
        self.data = self.buildInnertubeBody(**self._getRequestBody())
        if not hasattr(self, 'timeout'):
            self.timeout = 10
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
            continuing = self.continuationKey is not None
            self.continuationKey = None
            if not continuing:
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
            


from youtubesearchpython.core.componenthandler import ComponentHandler, getValue, getVideoId
import sys as _sys
from youtubesearchpython.core import componenthandler as _componenthandler
_sys.modules[f'{__name__}.componenthandler']=_componenthandler
_sys.modules[f'{__name__}.requesthandler']=_sys.modules[__name__]

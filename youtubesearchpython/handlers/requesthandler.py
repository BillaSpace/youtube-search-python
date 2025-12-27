from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
import json
import copy
from youtubesearchpython.core.componenthandler import ComponentHandler
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.exceptions import YouTubeRequestError, YouTubeParseError


class RequestHandler(ComponentHandler):
    def _makeRequest(self) -> None:
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
        requestBodyBytes = json.dumps(requestBody).encode('utf_8')
        request = Request(
            'https://www.youtube.com/youtubei/v1/search' + '?' + urlencode({
                'key': searchKey,
            }),
            data = requestBodyBytes,
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'Content-Length': len(requestBodyBytes),
                'User-Agent': userAgent,
            }
        )
        try:
            self.response = urlopen(request, timeout=self.timeout).read().decode('utf_8')
        except (URLError, HTTPError, TimeoutError) as e:
            raise YouTubeRequestError(f'Failed to make request: {str(e)}')
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

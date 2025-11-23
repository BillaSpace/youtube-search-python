from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json
import copy
from youtubesearchpython.handlers.componenthandler import ComponentHandler
from youtubesearchpython.core.constants import *


class RequestHandler(ComponentHandler):
    def _makeRequest(self) -> None:
        requestBody = copy.deepcopy(requestPayload)
        requestBody['query'] = self.query or ''
        context = requestBody.setdefault('context', {})
        client = context.setdefault('client', {})
        client.update({
            'hl': self.language or client.get('hl'),
            'gl': self.region or client.get('gl'),
        })
        if self.searchPreferences:
            requestBody['params'] = self.searchPreferences
        if self.continuationKey:
            requestBody['continuation'] = self.continuationKey

        if not searchKey:
            raise Exception('INNERTUBE API key (searchKey) is not set.')

        requestBodyBytes = json.dumps(requestBody).encode('utf-8')
        url = 'https://www.youtube.com/youtubei/v1/search' + '?' + urlencode({'key': searchKey})
        request = Request(
            url,
            data=requestBodyBytes,
            headers={
                'Content-Type': 'application/json; charset=utf-8',
                'User-Agent': userAgent,
            }
        )
        try:
            self.response = urlopen(request, timeout=self.timeout).read().decode('utf-8')
        except Exception as e:
            raise Exception('ERROR: Could not make request.') from e

    def _parseSource(self) -> None:
        try:
            data = json.loads(self.response)
            if not self.continuationKey:
                responseContent = self._getValue(data, contentPath)
            else:
                responseContent = self._getValue(data, continuationContentPath)

            if responseContent:
                for element in responseContent:
                    if itemSectionKey in element:
                        self.responseSource = self._getValue(element, [itemSectionKey, 'contents'])
                    if continuationItemKey in element:
                        self.continuationKey = self._getValue(element, continuationKeyPath)
            else:
                fallback = self._getValue(data, fallbackContentPath)
                if fallback:
                    self.responseSource = fallback
                    # attempt to set continuationKey from the last element if present there was url failing like for tracks like pal pal afusic
                    try:
                        last = self.responseSource[-1]
                        self.continuationKey = self._getValue(last, continuationKeyPath)
                    except Exception:
                        self.continuationKey = None
                else:
                    self.responseSource = []
                    self.continuationKey = None
        except Exception as e:
            raise Exception('ERROR: Could not parse YouTube response.') from e

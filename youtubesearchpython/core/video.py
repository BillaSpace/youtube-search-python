import os
import copy
import json
from typing import Union, List
from urllib.parse import urlencode

from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import getValue, getVideoId


CLIENTS = {
    "MWEB": {"clientName": "MWEB", "clientVersion": None},
    "ANDROID": {"clientName": "ANDROID", "clientVersion": None},
    "ANDROID_EMBED": {"clientName": "ANDROID", "clientVersion": None, "clientScreen": "EMBED"},
    "TV_EMBED": {"clientName": "TVHTML5_SIMPLY_EMBEDDED_PLAYER", "clientVersion": None}
}


class VideoCore(RequestCore):
    def __init__(self, videoLink: str, componentMode: str, resultMode: int, timeout: int, enableHTML: bool, overridedClient: str = "ANDROID"):
        super().__init__()
        self.timeout = timeout
        self.resultMode = resultMode
        self.componentMode = componentMode
        self.videoLink = videoLink
        self.enableHTML = enableHTML
        self.overridedClient = overridedClient
        self.response = None
        self.responseSource = None
        self.HTMLresponseSource = None
        self.__videoComponent = None

    def post_request_only_html_processing(self):
        self.__getVideoComponent(self.componentMode)
        self.result = self.__videoComponent

    def post_request_processing(self):
        self.__parseSource()
        self.__getVideoComponent(self.componentMode)
        self.result = self.__videoComponent

    def prepare_innertube_request(self):
        if not searchKey:
            raise Exception('INNERTUBE API key (searchKey) is not set.')
        params = {
            'key': searchKey,
            'contentCheckOk': True,
            'racyCheckOk': True,
            'videoId': getVideoId(self.videoLink)
        }
        self.url = 'https://www.youtube.com/youtubei/v1/player' + "?" + urlencode(params)
        data = copy.deepcopy(requestPayload)
        ctx = data.setdefault('context', {})
        client = ctx.setdefault('client', {})
        override = CLIENTS.get(self.overridedClient, {})
        client['clientName'] = override.get('clientName', client.get('clientName'))
        if override.get('clientVersion'):
            client['clientVersion'] = override['clientVersion']
        else:
            client['clientVersion'] = client.get('clientVersion', client.get('clientVersion'))
        self.data = data

    async def async_create(self):
        self.prepare_innertube_request()
        response = await self.asyncPostRequest()
        self.response = response.text if hasattr(response, "text") else (response.content.decode() if hasattr(response, "content") else None)
        if hasattr(response, "status_code") and response.status_code == 200:
            self.post_request_processing()
        else:
            raise Exception('ERROR: Invalid status code.')

    def sync_create(self):
        self.prepare_innertube_request()
        response = self.syncPostRequest()
        self.response = response.text if hasattr(response, "text") else None
        if hasattr(response, "status_code") and response.status_code == 200:
            self.post_request_processing()
        else:
            raise Exception('ERROR: Invalid status code.')

    def prepare_html_request(self):
        if not searchKey:
            raise Exception('INNERTUBE API key (searchKey) is not set.')
        params = {
            'key': searchKey,
            'contentCheckOk': True,
            'racyCheckOk': True,
            'videoId': getVideoId(self.videoLink)
        }
        self.url = 'https://www.youtube.com/youtubei/v1/player' + "?" + urlencode(params)
        data = copy.deepcopy(requestPayload)
        ctx = data.setdefault('context', {})
        client = ctx.setdefault('client', {})
        override = CLIENTS.get("MWEB", {})
        client['clientName'] = override.get('clientName', client.get('clientName'))
        self.data = data

    def sync_html_create(self):
        self.prepare_html_request()
        response = self.syncPostRequest()
        try:
            self.HTMLresponseSource = response.json() if hasattr(response, "json") else json.loads(response.text)
        except Exception:
            self.HTMLresponseSource = {}

    async def async_html_create(self):
        self.prepare_html_request()
        response = await self.asyncPostRequest()
        try:
            self.HTMLresponseSource = response.json() if hasattr(response, "json") else json.loads(response.text)
        except Exception:
            self.HTMLresponseSource = {}

    def __parseSource(self) -> None:
        try:
            if isinstance(self.response, (str, bytes)):
                self.responseSource = json.loads(self.response)
            elif hasattr(self.response, "json"):
                self.responseSource = self.response.json()
            else:
                self.responseSource = {}
        except Exception:
            raise Exception('ERROR: Could not parse YouTube response.')

    def __result(self, mode: int) -> Union[dict, str]:
        if mode == ResultMode.dict:
            return self.__videoComponent
        elif mode == ResultMode.json:
            return json.dumps(self.__videoComponent, indent=4)

    def __getVideoComponent(self, mode: str) -> None:
        videoComponent = {}
        if mode in ['getInfo', None]:
            responseSource = self.responseSource if not self.enableHTML else self.HTMLresponseSource
            component = {
                'id': getValue(responseSource, ['videoDetails', 'videoId']),
                'title': getValue(responseSource, ['videoDetails', 'title']),
                'duration': {
                    'secondsText': getValue(responseSource, ['videoDetails', 'lengthSeconds']),
                },
                'viewCount': {
                    'text': getValue(responseSource, ['videoDetails', 'viewCount'])
                },
                'thumbnails': getValue(responseSource, ['videoDetails', 'thumbnail', 'thumbnails']),
                'description': getValue(responseSource, ['videoDetails', 'shortDescription']),
                'channel': {
                    'name': getValue(responseSource, ['videoDetails', 'author']),
                    'id': getValue(responseSource, ['videoDetails', 'channelId']),
                },
                'allowRatings': getValue(responseSource, ['videoDetails', 'allowRatings']),
                'averageRating': getValue(responseSource, ['videoDetails', 'averageRating']),
                'keywords': getValue(responseSource, ['videoDetails', 'keywords']),
                'isLiveContent': getValue(responseSource, ['videoDetails', 'isLiveContent']),
                'publishDate': getValue(responseSource, ['microformat', 'playerMicroformatRenderer', 'publishDate']),
                'uploadDate': getValue(responseSource, ['microformat', 'playerMicroformatRenderer', 'uploadDate']),
                'isFamilySafe': getValue(responseSource, ['microformat', 'playerMicroformatRenderer', 'isFamilySafe']),
                'category': getValue(responseSource, ['microformat', 'playerMicroformatRenderer', 'category']),
            }
            component['isLiveNow'] = bool(component.get('isLiveContent')) and component.get('duration', {}).get('secondsText') == "0"
            component['link'] = 'https://www.youtube.com/watch?v=' + (component.get('id') or "")
            channel_id = component.get('channel', {}).get('id')
            component['channel']['link'] = ('https://www.youtube.com/channel/' + channel_id) if channel_id else None
            videoComponent.update(component)
        if mode in ['getFormats', None]:
            videoComponent.update({"streamingData": getValue(self.responseSource, ["streamingData"])})
        if self.enableHTML:
            videoComponent["publishDate"] = getValue(self.HTMLresponseSource, ['microformat', 'playerMicroformatRenderer', 'publishDate'])
            videoComponent["uploadDate"] = getValue(self.HTMLresponseSource, ['microformat', 'playerMicroformatRenderer', 'uploadDate'])
        self.__videoComponent = videoComponent

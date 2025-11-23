import os
import copy
import json
import re
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
    ANDROID_USER_AGENT = "Mozilla/5.0 (Linux; Android 12; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    DEFAULT_ANDROID_CLIENT_VERSION = "16.20.35"

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
            client['clientVersion'] = client.get('clientVersion', client.get('clientVersion') or (self.DEFAULT_ANDROID_CLIENT_VERSION if self.overridedClient == "ANDROID" else None))
        self.data = data

    async def async_create(self):
        self.prepare_innertube_request()
        response = await self.asyncPostRequest_override()
        self.response = response.text if hasattr(response, "text") else (response.content.decode() if hasattr(response, "content") else None)
        if hasattr(response, "status_code") and response.status_code == 200:
            self.post_request_processing()
            return
        scraped = await self.__deep_scrape_watch_page_async()
        if scraped:
            self.post_request_processing()
            return
        # try innertube again with android-specific headers/context
        try:
            self.overridedClient = "ANDROID"
            self.prepare_innertube_request()
            response = await self.asyncPostRequest_override()
            self.response = response.text if hasattr(response, "text") else (response.content.decode() if hasattr(response, "content") else None)
            if hasattr(response, "status_code") and response.status_code == 200:
                self.post_request_processing()
                return
        except Exception:
            pass
        raise Exception('ERROR: Invalid status code.')

    def sync_create(self):
        self.prepare_innertube_request()
        response = self.syncPostRequest_override()
        self.response = response.text if hasattr(response, "text") else None
        if hasattr(response, "status_code") and response.status_code == 200:
            self.post_request_processing()
            return
        scraped = self.__deep_scrape_watch_page_sync()
        if scraped:
            self.post_request_processing()
            return
        try:
            self.overridedClient = "ANDROID"
            self.prepare_innertube_request()
            response = self.syncPostRequest_override()
            self.response = response.text if hasattr(response, "text") else None
            if hasattr(response, "status_code") and response.status_code == 200:
                self.post_request_processing()
                return
        except Exception:
            pass
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
        response = self.syncPostRequest_override()
        try:
            self.HTMLresponseSource = response.json() if hasattr(response, "json") else json.loads(response.text)
        except Exception:
            self.HTMLresponseSource = {}

    async def async_html_create(self):
        self.prepare_html_request()
        response = await self.asyncPostRequest_override()
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

    async def __deep_scrape_watch_page_async(self) -> bool:
        try:
            watch_url = 'https://www.youtube.com/watch?v=' + (getVideoId(self.videoLink) or "")
            resp = await self.asyncGetRequest_override(watch_url)
            html = resp.text if hasattr(resp, "text") else (resp.content.decode() if hasattr(resp, "content") else "")
            j = self.__extract_initial_player_response(html)
            if j:
                self.response = json.dumps(j)
                self.responseSource = j
                if self.enableHTML:
                    try:
                        self.HTMLresponseSource = json.loads(j.get('microformat', {}).get('playerMicroformatRenderer', {}) or "{}")
                    except Exception:
                        self.HTMLresponseSource = {}
                return True
        except Exception:
            pass
        return False

    def __deep_scrape_watch_page_sync(self) -> bool:
        try:
            watch_url = 'https://www.youtube.com/watch?v=' + (getVideoId(self.videoLink) or "")
            resp = self.syncGetRequest_override(watch_url)
            html = resp.text if hasattr(resp, "text") else ""
            j = self.__extract_initial_player_response(html)
            if j:
                self.response = json.dumps(j)
                self.responseSource = j
                if self.enableHTML:
                    try:
                        self.HTMLresponseSource = json.loads(j.get('microformat', {}).get('playerMicroformatRenderer', {}) or "{}")
                    except Exception:
                        self.HTMLresponseSource = {}
                return True
        except Exception:
            pass
        return False

    def __extract_initial_player_response(self, html: str) -> dict:
        try:
            m = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', html, re.DOTALL)
            if not m:
                m = re.search(r'var\s+ytInitialPlayerResponse\s*=\s*({.+?});', html, re.DOTALL)
            if not m:
                m = re.search(r'window\["ytInitialPlayerResponse"\]\s*=\s*({.+?});', html, re.DOTALL)
            if not m:
                m = re.search(r'({"responseContext".+?"videoDetails".+?})\s*;</script>', html, re.DOTALL)
            if not m:
                return {}
            json_text = m.group(1)
            try:
                return json.loads(json_text)
            except Exception:
                json_text = re.sub(r'(\n|\r|\t)', '', json_text)
                json_text = re.sub(r',\s*([}\]])', r'\1', json_text)
                return json.loads(json_text)
        except Exception:
            return {}

    async def asyncGetRequest_override(self, url: str):
        try:
            self.url = url
            return await self.asyncGetRequest()
        except Exception:
            try:
                rc = RequestCore()
                rc.url = url
                rc.headers = self._build_spoof_headers()
                rc.timeout = getattr(self, "timeout", None)
                proxy = os.environ.get("YTS_PROXY") or os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
                if proxy:
                    rc.proxies = {"http": proxy, "https": proxy}
                return await rc.asyncGetRequest()
            except Exception:
                raise

    def syncGetRequest_override(self, url: str):
        try:
            self.url = url
            return self.syncGetRequest()
        except Exception:
            try:
                rc = RequestCore()
                rc.url = url
                rc.headers = self._build_spoof_headers()
                rc.timeout = getattr(self, "timeout", None)
                proxy = os.environ.get("YTS_PROXY") or os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
                if proxy:
                    rc.proxies = {"http": proxy, "https": proxy}
                return rc.syncGetRequest()
            except Exception:
                raise

    async def asyncPostRequest_override(self):
        try:
            return await self.asyncPostRequest()
        except Exception:
            try:
                rc = RequestCore()
                rc.url = getattr(self, "url", None)
                rc.data = getattr(self, "data", None)
                rc.headers = self._build_spoof_headers(include_innertube=True)
                rc.timeout = getattr(self, "timeout", None)
                proxy = os.environ.get("YTS_PROXY") or os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
                if proxy:
                    rc.proxies = {"http": proxy, "https": proxy}
                return await rc.asyncPostRequest()
            except Exception:
                raise

    def syncPostRequest_override(self):
        try:
            return self.syncPostRequest()
        except Exception:
            try:
                rc = RequestCore()
                rc.url = getattr(self, "url", None)
                rc.data = getattr(self, "data", None)
                rc.headers = self._build_spoof_headers(include_innertube=True)
                rc.timeout = getattr(self, "timeout", None)
                proxy = os.environ.get("YTS_PROXY") or os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
                if proxy:
                    rc.proxies = {"http": proxy, "https": proxy}
                return rc.syncPostRequest()
            except Exception:
                raise

    def _build_spoof_headers(self, include_innertube: bool = False) -> dict:
        headers = {
            "User-Agent": self.ANDROID_USER_AGENT,
            "Accept-Language": os.environ.get("YTS_ACCEPT_LANGUAGE", "en-US,en;q=0.9"),
            "Referer": "https://www.youtube.com/",
            "Origin": "https://www.youtube.com",
        }
        client_ctx = (self.data.get("context", {}).get("client", {}) if isinstance(getattr(self, "data", None), dict) else {}) or {}
        client_name = client_ctx.get("clientName", "ANDROID")
        client_version = client_ctx.get("clientVersion", self.DEFAULT_ANDROID_CLIENT_VERSION)
        if include_innertube:
            headers["x-youtube-client-name"] = str(ANDROID_CLIENT_NAME if 'ANDROID' in CLIENTS else client_name)
            headers["x-youtube-client-version"] = str(client_version)
            # identity token if provided via env direct access for yt contents
            identity = os.environ.get("YTS_IDENTITY_TOKEN")
            if identity:
                headers["x-youtube-identity-token"] = identity
        return headers

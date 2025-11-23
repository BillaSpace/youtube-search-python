import copy
import urllib.request
import urllib.parse
import re

from youtubesearchpython.core.constants import ResultMode
from youtubesearchpython.core.video import VideoCore
from youtubesearchpython.core.componenthandler import getValue
from youtubesearchpython.core.requests import RequestCore

isYtDLPinstalled = False

try:
    from yt_dlp.extractor.youtube import YoutubeIE
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import url_or_none, try_get, update_url_query, ExtractorError
    isYtDLPinstalled = True
except Exception:
    pass


class StreamURLFetcherCore(RequestCore):
    def __init__(self):
        if not isYtDLPinstalled:
            raise Exception('ERROR: yt-dlp is not installed. To use this functionality of youtube-search-python, yt-dlp must be installed.')
        super().__init__()
        self._js_url = None
        self._js = None
        self.ytie = YoutubeIE()
        self.ytie.set_downloader(YoutubeDL())
        self._streams = []
        self.video_id = None
        self._player_response = None
        self.format_id = None

    def _getDecipheredURLs(self, videoFormats: dict, formatId: int = None) -> None:
        self._streams = []
        self.video_id = videoFormats.get("id")
        if not videoFormats.get("streamingData"):
            vc = VideoCore(self.video_id, None, ResultMode.dict, None, False, overridedClient="TV_EMBED")
            vc.sync_create()
            videoFormats = vc.result
            if not videoFormats.get("streamingData"):
                raise Exception("streamingData is not present in Video.get. This is most likely an age-restricted video")
        self._player_response = copy.deepcopy(videoFormats["streamingData"].get("formats", []))
        self._player_response.extend(videoFormats["streamingData"].get("adaptiveFormats", []))
        self.format_id = formatId
        self._decipher()

    def extract_js_url(self, res: str):
        if not res:
            raise Exception("Failed to retrieve JavaScript for this video")
        m = re.search(r'"jsUrl"\s*:\s*"([^"]+)"', res)
        if m:
            js = m.group(1)
            if js.startswith("http"):
                self._js_url = js
                return
            self._js_url = urllib.parse.urljoin("https://www.youtube.com", js)
            return
        m = re.search(r'"PLAYER_JS_URL"\s*:\s*"([^"]+)"', res)
        if m:
            js = m.group(1)
            if js.startswith("http"):
                self._js_url = js
                return
            self._js_url = urllib.parse.urljoin("https://www.youtube.com", js)
            return
        m = re.search(r'src="([^"]*player(?:_ias|_vflset)[^"]*\.js[^"]*)"', res)
        if m:
            js = m.group(1)
            self._js_url = urllib.parse.urljoin("https://www.youtube.com", js)
            return
        m = re.search(r'player\/([0-9a-fA-F]{8})\/player', res)
        if m:
            token = m.group(1)
            self._js_url = f'https://www.youtube.com/s/player/{token}/player_ias.vflset/en_US/base.js'
            return
        raise Exception("Failed to retrieve JavaScript for this video")

    def _getJS(self) -> None:
        if not self.video_id:
            raise Exception("video id not set")
        self.url = f'https://www.youtube.com/watch?v={self.video_id}'
        res = self.syncGetRequest()
        if not res or not getattr(res, "text", None):
            raise Exception("Failed to download player page")
        self.extract_js_url(res.text)

    async def getJavaScript(self):
        if not self.video_id:
            raise Exception("video id not set")
        self.url = f'https://www.youtube.com/watch?v={self.video_id}'
        res = await self.asyncGetRequest()
        if not res or not getattr(res, "text", None):
            raise Exception("Failed to download player page")
        self.extract_js_url(res.text)

    def _decipher(self, retry: bool = False):
        if not self._js_url or retry:
            self._js_url = None
            self._js = None
            self._getJS()
        try:
            for yt_format in self._player_response:
                if self.format_id is not None and self.format_id != yt_format.get("itag"):
                    continue
                if getValue(yt_format, ["url"]):
                    yt_format["throttled"] = False
                    self._streams.append(yt_format)
                    continue
                cipher = yt_format.get("signatureCipher") or yt_format.get("cipher")
                if not cipher:
                    yt_format["throttled"] = False
                    self._streams.append(yt_format)
                    continue
                sc = urllib.parse.parse_qs(cipher)
                fmt_url = url_or_none(try_get(sc, lambda x: x.get('url', [None])[0]))
                encrypted_sig = try_get(sc, lambda x: x.get('s', [None])[0])
                if not (sc and fmt_url and encrypted_sig):
                    yt_format["throttled"] = False
                    self._streams.append(yt_format)
                    continue
                signature = self.ytie._decrypt_signature(sc.get('s', [None])[0], self.video_id, self._js_url)
                sp = try_get(sc, lambda x: x.get('sp', [None])[0]) or 'signature'
                fmt_url = fmt_url + '&' + sp + '=' + signature
                query = urllib.parse.parse_qs(fmt_url)
                throttled = False
                if query.get('n'):
                    try:
                        fmt_url = update_url_query(fmt_url, {
                            'n': self.ytie._decrypt_nsig(query['n'][0], self.video_id, self._js_url)})
                    except ExtractorError:
                        throttled = True
                yt_format["url"] = fmt_url
                yt_format["throttled"] = throttled
                self._streams.append(yt_format)
        except Exception:
            if retry:
                raise
            self._decipher(retry=True)

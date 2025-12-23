import re
import copy
import urllib.parse
import os

from youtubesearchpython.core.constants import ResultMode
from youtubesearchpython.core.componenthandler import getValue
from youtubesearchpython.core.requests import RequestCore

isYtDLPinstalled = False

try:
    from yt_dlp.extractor.youtube import YoutubeIE
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import url_or_none, try_get, update_url_query, ExtractorError

    isYtDLPinstalled = True
except ImportError:
    pass


class StreamURLFetcherCore(RequestCore):
    def __init__(self, proxy: str = None, cookies_file: str = None):
        if not isYtDLPinstalled:
            raise Exception('ERROR: yt-dlp is not installed. Install with: pip install yt-dlp')

        super().__init__()

        self._js_url = None
        self._js = None
        self.video_id = None
        self._streams = []

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        if proxy:
            ydl_opts['proxy'] = proxy
        if cookies_file and os.path.exists(cookies_file):
            ydl_opts['cookiefile'] = cookies_file

        self.downloader = YoutubeDL(ydl_opts)
        self.ytie = YoutubeIE()
        self.ytie.set_downloader(self.downloader)

    def _getDecipheredURLs(self, videoFormats: dict, formatId: int = None) -> None:
        self._streams = []
        self.video_id = videoFormats.get("id")
        if not self.video_id:
            return

        streaming_data = videoFormats.get("streamingData")
        if not streaming_data or not streaming_data.get("formats") and not streaming_data.get("adaptiveFormats"):
            return

        self._streaming_data = copy.deepcopy(streaming_data)

        self._player_response = copy.deepcopy(streaming_data.get("formats", []))
        self._player_response.extend(streaming_data.get("adaptiveFormats", []))

        self.format_id = formatId
        self._decipher()

    def extract_js_url(self, res: str):
        self._js_url = None
        if not res:
            return
        player_version = re.search(r'([0-9a-fA-F]{8})\\?', res)
        if player_version:
            player_version = player_version.group().replace("\\", "")
            self._js_url = f'https://www.youtube.com/s/player/{player_version}/player_ias.vflset/en_US/base.js'

    def _getJS(self) -> None:
        if not self.video_id:
            return
        self.url = 'https://www.youtube.com/iframe_api'
        res = self.syncGetRequest()
        if res and res.text:
            self.extract_js_url(res.text)

    async def getJavaScript(self):
        if not self.video_id:
            return
        self.url = 'https://www.youtube.com/iframe_api'
        res = await self.asyncGetRequest()
        if res and res.text:
            self.extract_js_url(res.text)

    def _decipher(self, retry: bool = False):
        if not self.video_id:
            return

        if not self._js_url or retry:
            self._js_url = None
            self._js = None
            self._getJS()

        if not self._js_url:
            return

        try:
            server_abr_url = getValue(self._streaming_data, ["serverAbrStreamingUrl"])

            for yt_format in self._player_response:
                if self.format_id is not None and yt_format.get("itag") != self.format_id:
                    continue

                if getValue(yt_format, ["url"]):
                    yt_format["throttled"] = False
                    self._streams.append(yt_format)
                    if self.format_id is not None:
                        return
                    continue

                if server_abr_url and not getValue(yt_format, ["signatureCipher"]):
                    yt_format["url"] = server_abr_url
                    yt_format["throttled"] = False
                    self._streams.append(yt_format)
                    if self.format_id is not None:
                        return
                    continue

                cipher = getValue(yt_format, ["signatureCipher"])
                if not cipher:
                    continue

                sc = urllib.parse.parse_qs(cipher)
                fmt_url = url_or_none(try_get(sc, lambda x: x['url'][0]))
                encrypted_sig = try_get(sc, lambda x: x['s'][0])

                if not (fmt_url and encrypted_sig):
                    yt_format["throttled"] = False
                    self._streams.append(yt_format)
                    continue

                try:
                    signature = self.ytie._decrypt_signature(encrypted_sig, self.video_id, self._js_url)
                except:
                    continue

                sp = try_get(sc, lambda x: x['sp'][0]) or 'signature'
                fmt_url += '&' + sp + '=' + signature

                query = urllib.parse.parse_qs(fmt_url)
                throttled = False
                if query.get('n'):
                    try:
                        n_code = query['n'][0]
                        new_n = self.ytie._decrypt_nsig(n_code, self.video_id, self._js_url)
                        fmt_url = update_url_query(fmt_url, {'n': new_n})
                    except ExtractorError:
                        throttled = True

                yt_format["url"] = fmt_url
                yt_format["throttled"] = throttled
                self._streams.append(yt_format)

                if self.format_id is not None:
                    return

        except Exception:
            if retry:
                return
            self._decipher(retry=True)

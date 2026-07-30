import re
import copy
import urllib.parse
import os

from youtubesearchpython.core.constants import ResultMode
from youtubesearchpython.core.componenthandler import getValue
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.cookies import resolve_cookie_file_ex, cleanup_cookie_file

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
            raise Exception('ERROR: yt-dlp is not installed in your system. Install with: pip3 install yt-dlp & try again')

        super().__init__()
        self._js_url = None
        self._js = None
        self.video_id = None
        self._streams = []

        # Resolution order: an explicit cookies_file argument (if it's a
        # real, existing path) takes priority; otherwise fall back to the
        # same shared resolver Transcript uses - a local path via
        # YOUTUBE_COOKIES_FILE/cookies.txt, or a COOKIE_URL to download from.
        # Ownership of the resulting file (i.e. whether we downloaded it and
        # are therefore responsible for deleting it) is tracked explicitly,
        # not guessed from where the path happens to live on disk - a real
        # user-supplied cookies file could itself sit in /tmp.
        self._owns_temp_cookie_file = False
        resolved_cookies_file = None
        if cookies_file and os.path.exists(cookies_file):
            resolved_cookies_file = cookies_file
        else:
            resolved_cookies_file, self._owns_temp_cookie_file = resolve_cookie_file_ex()
        self._cookies_file = resolved_cookies_file
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        if proxy:
            ydl_opts['proxy'] = proxy
        if resolved_cookies_file:
            ydl_opts['cookiefile'] = resolved_cookies_file
        self.downloader = YoutubeDL(ydl_opts)
        self.ytie = YoutubeIE()
        self.ytie.set_downloader(self.downloader)

    def close(self) -> None:
        '''Releases the yt-dlp downloader and removes the temp cookie file
        (if one was downloaded via COOKIE_URL rather than passed in as a
        real path) so it doesn't accumulate on disk across many instances.
        Safe to call more than once.
        '''
        try:
            self.downloader.close()
        except Exception:
            pass
        if self._owns_temp_cookie_file:
            cleanup_cookie_file(self._cookies_file)
            self._owns_temp_cookie_file = False

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def _getDecipheredURLs(self, videoFormats: dict, formatId: int = None) -> None:
        self._streams = []
        self.video_id = videoFormats.get("id")
        if not self.video_id:
            return

        streaming_data = videoFormats.get("streamingData")
        if not streaming_data:
            return
        if not streaming_data.get("formats") and not streaming_data.get("adaptiveFormats"):
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
        if res and getattr(res, "text", None):
            self.extract_js_url(res.text)

    async def getJavaScript(self):
        if not self.video_id:
            return
        self.url = 'https://www.youtube.com/iframe_api'
        res = await self.asyncGetRequest()
        if res and getattr(res, "text", None):
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
                except Exception:
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
                    except Exception:
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

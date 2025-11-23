from __future__ import annotations

import copy
import logging
import re
import urllib.parse
from typing import Any, Dict, List, Optional

from youtubesearchpython.core.constants import ResultMode
from youtubesearchpython.core.video import VideoCore
from youtubesearchpython.core.componenthandler import getValue
from youtubesearchpython.core.requests import RequestCore

isYtDLPinstalled = False
_ytdl_extras = {}

try:
    from yt_dlp.extractor.youtube import YoutubeIE
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import url_or_none, try_get, update_url_query, ExtractorError

    isYtDLPinstalled = True
    _ytdl_extras.update(
        {
            "YoutubeIE": YoutubeIE,
            "YoutubeDL": YoutubeDL,
            "url_or_none": url_or_none,
            "try_get": try_get,
            "update_url_query": update_url_query,
            "ExtractorError": ExtractorError,
        }
    )
except Exception:
    pass

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class StreamURLFetcherCore(RequestCore):
    def __init__(self) -> None:
        try:
            super().__init__()
        except Exception:
            pass
        self._initialized = False
        self.init()

    def init(self) -> None:
        self._js_url = None
        self._js = None
        self._streams = []
        self.video_id = None
        self._player_response = None
        self.format_id = None
        self._initialized = True
        if isYtDLPinstalled:
            try:
                self.ytie = _ytdl_extras["YoutubeIE"]()
                self.ytie.set_downloader(_ytdl_extras["YoutubeDL"]())
            except Exception:
                self.ytie = None
        else:
            self.ytie = None

    def get_streams(self) -> List[Dict[str, Any]]:
        return copy.deepcopy(self._streams)

    def get_player_response(self) -> Optional[List[Dict[str, Any]]]:
        return copy.deepcopy(self._player_response)

    def _getDecipheredURLs(self, videoFormats: Dict[str, Any], formatId: Optional[int] = None) -> None:
        if not self._initialized:
            self.init()

        self._streams = []
        self.video_id = videoFormats.get("id")

        if not videoFormats.get("streamingData"):
            vc = VideoCore(self.video_id, None, ResultMode.dict, None, False, overridedClient="TV_EMBED")
            vc.sync_create()
            videoFormats = vc.result
            if not videoFormats.get("streamingData"):
                raise Exception("streamingData is not present in Video.get. This is most likely an age-restricted video")

        sd = videoFormats["streamingData"]
        formats_list = []
        formats_list.extend(sd.get("formats", []) or [])
        formats_list.extend(sd.get("adaptiveFormats", []) or [])
        self._player_response = formats_list
        self.format_id = formatId

        try:
            self._decipher()
        except Exception:
            self._decipher(retry=True)

    def extract_js_url(self, res: str) -> None:
        if not res:
            raise Exception("Failed to retrieve JavaScript for this video")

        patterns = [
            r'"jsUrl"\s*:\s*"([^"]+)"',
            r'"PLAYER_JS_URL"\s*:\s*"([^"]+)"',
            r'src="([^"]*player(?:_ias|_vflset|_vfl)[^"]*\.js[^"]*)"',
            r'"/s/player/([0-9a-fA-F]{8})/player(?:_ias|_vflset)?/[^"]*\.js"',
            r'player\/([0-9a-fA-F]{8})\/player',
        ]

        for patt in patterns:
            m = re.search(patt, res)
            if not m:
                continue
            js = m.group(1)
            if js.startswith("http"):
                self._js_url = js
                return
            if re.fullmatch(r"[0-9a-fA-F]{8}", js):
                token = js
                self._js_url = f"https://www.youtube.com/s/player/{token}/player_ias.vflset/en_US/base.js"
                return
            self._js_url = urllib.parse.urljoin("https://www.youtube.com", js)
            return

        m = re.search(r'(["\'])PLAYER_JS_URL\1\s*:\s*["\']?([^"\'}]+)', res)
        if m:
            js = m.group(2)
            self._js_url = urllib.parse.urljoin("https://www.youtube.com", js) if not js.startswith("http") else js
            return

        raise Exception("Failed to retrieve JavaScript for this video")

    def _getJS(self) -> None:
        if not self.video_id:
            raise Exception("video id not set")

        self.url = f"https://www.youtube.com/watch?v={self.video_id}"
        last_exc = None

        for _ in range(3):
            try:
                res = self.syncGetRequest()
                if not res or not getattr(res, "text", None):
                    raise Exception("Failed to download player page (no response text)")
                self.extract_js_url(res.text)
                return
            except Exception as e:
                last_exc = e
        raise Exception(f"Failed to download player page after retries: {last_exc}")

    async def getJavaScript(self, video_or_id: Optional[Any] = None) -> None:
        def _extract_id(x: Any) -> Optional[str]:
            try:
                if isinstance(x, dict) and x.get("id"):
                    return x.get("id")
                if hasattr(x, "get") and callable(getattr(x, "get")) and x.get("id"):
                    return x.get("id")
            except Exception:
                pass
            if not x:
                return None
            s = str(x)
            m = re.search(r"(?:v=|/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{6,})", s)
            if m:
                return m.group(1)
            if re.fullmatch(r"[A-Za-z0-9_-]{6,}", s):
                return s
            return None

        if video_or_id:
            vid = _extract_id(video_or_id)
            if vid:
                self.video_id = vid

        if not self.video_id:
            raise Exception("video id not set")

        self.url = f"https://www.youtube.com/watch?v={self.video_id}"
        last_exc = None

        for _ in range(3):
            try:
                res = await self.asyncGetRequest()
                if not res or not getattr(res, "text", None):
                    raise Exception("Failed to download player page (no response text)")
                self.extract_js_url(res.text)
                return
            except Exception as e:
                last_exc = e

        raise Exception(f"Failed to download player page after retries: {last_exc}")

    def _decipher(self, retry: bool = False) -> None:
        if not self._player_response:
            raise Exception("player response not loaded")

        if not self._js_url or retry:
            self._js_url = None
            self._js = None
            self._getJS()

        url_or_none = _ytdl_extras.get("url_or_none")
        try_get = _ytdl_extras.get("try_get")
        update_url_query = _ytdl_extras.get("update_url_query")

        for yt_format in self._player_response:
            try:
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

                if try_get and url_or_none:
                    fmt_url = url_or_none(try_get(sc, lambda x: x.get("url", [None])[0]))
                    encrypted_sig = try_get(sc, lambda x: x.get("s", [None])[0])
                else:
                    fmt_url = sc.get("url", [None])[0]
                    encrypted_sig = sc.get("s", [None])[0]

                if not (sc and fmt_url and encrypted_sig and self.ytie and hasattr(self.ytie, "_decrypt_signature")):
                    if fmt_url:
                        yt_format["url"] = fmt_url
                        yt_format["throttled"] = False
                        self._streams.append(yt_format)
                        continue
                    yt_format["throttled"] = True
                    self._streams.append(yt_format)
                    continue

                signature = self.ytie._decrypt_signature(sc.get("s", [None])[0], self.video_id, self._js_url)
                sp = try_get(sc, lambda x: x.get("sp", [None])[0]) if try_get else None
                sp = sp or "signature"

                fmt_url = fmt_url + "&" + sp + "=" + signature

                throttled = False
                if update_url_query and sc.get("n"):
                    try:
                        fmt_url = update_url_query(fmt_url, {"n": self.ytie._decrypt_nsig(sc.get("n", [None])[0], self.video_id, self._js_url)})
                    except Exception:
                        throttled = True

                yt_format["url"] = fmt_url
                yt_format["throttled"] = throttled
                self._streams.append(yt_format)

            except Exception:
                try:
                    yt_format["throttled"] = True
                    self._streams.append(yt_format)
                except Exception:
                    pass

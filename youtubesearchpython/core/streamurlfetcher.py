import re
import copy
import urllib.parse
import urllib.request


from youtubesearchpython.core.constants import ResultMode
from youtubesearchpython.core.video import VideoCore
from youtubesearchpython.core.componenthandler import getValue
from youtubesearchpython.core.requests import RequestCore

isYtDLPinstalled = False

try:
    from yt_dlp.extractor.youtube import YoutubeBaseInfoExtractor, YoutubeIE
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import url_or_none, try_get, update_url_query, ExtractorError

    isYtDLPinstalled = True
except:
    pass


class StreamURLFetcherCore(RequestCore):
    def __init__(self):
        if isYtDLPinstalled:
            super().__init__()
            self._js_url = None
            self._js = None
            self.ytie = YoutubeIE()
            self.ytie.set_downloader(YoutubeDL())
            self._streams = []
        else:
            raise Exception('ERROR: yt-dlp is not installed. To use this functionality of youtube-search-python, yt-dlp must be installed.')

    def _getDecipheredURLs(self, videoFormats: dict, formatId: int = None) -> None:
        self._streams = []

        self.video_id = videoFormats["id"]
        if not videoFormats["streamingData"]:
            try:
                vc = VideoCore(self.video_id, None, ResultMode.dict, None, False, overridedClient="ANDROID")
                vc.sync_create()
                videoFormats = vc.result
            except:
                vc = VideoCore(self.video_id, None, ResultMode.dict, None, False, overridedClient="TV_EMBED")
                vc.sync_create()
                videoFormats = vc.result
            if not videoFormats["streamingData"]:
                raise Exception("streamingData is not present in Video.get. This is most likely a age-restricted video")
        
        self._streaming_data = copy.deepcopy(videoFormats["streamingData"])
        self._player_response = copy.deepcopy(videoFormats["streamingData"]["formats"])
        self._player_response.extend(videoFormats["streamingData"]["adaptiveFormats"])
        self.format_id = formatId
        self._decipher()

    def extract_js_url(self, res: str):
        if res:
            # Source: https://github.com/yt-dlp/yt-dlp/blob/e600a5c90817f4caac221679f6639211bba1f3a2/yt_dlp/extractor/youtube.py#L2258
            player_version = re.search(
                r'([0-9a-fA-F]{8})\\?', res)
            player_version = player_version.group().replace("\\", "")
            self._js_url = f'https://www.youtube.com/s/player/{player_version}/player_ias.vflset/en_US/base.js'
        else:
            raise Exception("Failed to retrieve JavaScript for this video")

    def _getJS(self) -> None:
        self.url = 'https://www.youtube.com/iframe_api'
        res = self.syncGetRequest()
        self.extract_js_url(res.text)

    async def getJavaScript(self):
        self.url = 'https://www.youtube.com/iframe_api'
        res = await self.asyncGetRequest()
        self.extract_js_url(res.text)

    def _decipher(self, retry: bool = False):
        if not self._js_url or retry:
            self._js_url = None
            self._js = None
            self._getJS()
        try:
            server_abr_url = getValue(self._streaming_data, ["serverAbrStreamingUrl"])
            if server_abr_url:
                for yt_format in self._player_response:
                    if self.format_id == yt_format["itag"] or self.format_id is None:
                        if not getValue(yt_format, ["url"]) and not getValue(yt_format, ["signatureCipher"]):
                            yt_format["url"] = server_abr_url
                            yt_format["throttled"] = False
                            self._streams.append(yt_format)
                            if self.format_id is not None:
                                return
            
            for yt_format in self._player_response:
                if self.format_id == yt_format["itag"] or self.format_id is None:
                    if getValue(yt_format, ["url"]):
                        yt_format["throttled"] = False
                        self._streams.append(yt_format)
                        continue
                    cipher = getValue(yt_format, ["signatureCipher"])
                    if not cipher:
                        continue
                    # Source: https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/youtube.py#L2972-L2981
                    sc = urllib.parse.parse_qs(cipher)
                    fmt_url = url_or_none(try_get(sc, lambda x: x['url'][0]))
                    encrypted_sig = try_get(sc, lambda x: x['s'][0])
                    if not (sc and fmt_url and encrypted_sig):
                        yt_format["throttled"] = False
                        self._streams.append(yt_format)
                        continue
                    if not cipher:
                        continue
                    signature = self.ytie._decrypt_signature(sc['s'][0], self.video_id, self._js_url)
                    sp = try_get(sc, lambda x: x['sp'][0]) or 'signature'
                    fmt_url += '&' + sp + '=' + signature

                    # Source: https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/youtube.py#L2983-L2993
                    query = urllib.parse.parse_qs(fmt_url)
                    throttled = False
                    if query.get('n'):
                        try:
                            fmt_url = update_url_query(fmt_url, {
                                'n': self.ytie._decrypt_nsig(query['n'][0], self.video_id, self._js_url)})
                        except ExtractorError as e:
                            throttled = True
                    yt_format["url"] = fmt_url
                    yt_format["throttled"] = throttled
                    self._streams.append(yt_format)
        except Exception as e:
            if retry:
                raise e
            self._decipher(retry=True)

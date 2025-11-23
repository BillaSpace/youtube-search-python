import copy
import json
from typing import Union, List
from urllib.parse import urlencode

from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import getValue, getVideoId


class TranscriptCore(RequestCore):
    def __init__(self, videoLink: str, key: str):
        super().__init__()
        self.videoLink = videoLink
        self.key = key
        self.data = None
        self.result = None

    def prepare_params_request(self):
        if not searchKey:
            raise Exception("INNERTUBE API key (searchKey) is not set.")
        self.url = 'https://www.youtube.com/youtubei/v1/next' + "?" + urlencode({
            'key': searchKey,
            "prettyPrint": "false"
        })
        self.data = copy.deepcopy(requestPayload)
        ctx = self.data.setdefault('context', {})
        client = ctx.setdefault('client', {})
        client.update({
            'clientName': client.get('clientName', 'WEB'),
            'clientVersion': client.get('clientVersion', requestPayload.get('context', {}).get('client', {}).get('clientVersion', '2.20210820.01.00'))
        })
        self.data["videoId"] = getVideoId(self.videoLink)

    def extract_continuation_key(self, r):
        data = self._safe_load_response(r)
        panels = getValue(data, ["engagementPanels"]) or []
        if not panels:
            self.result = {"segments": [], "languages": []}
            return True
        key = ""
        for panel in panels:
            panel_renderer = getValue(panel, ["engagementPanelSectionListRenderer"]) or {}
            target = getValue(panel_renderer, ["targetId"])
            if target == "engagement-panel-searchable-transcript":
                key = getValue(panel_renderer, ["content", "continuationItemRenderer", "continuationEndpoint", "getTranscriptEndpoint", "params"])
                break
        if not key:
            self.result = {"segments": [], "languages": []}
            return True
        self.key = key
        return False

    def prepare_transcript_request(self):
        if not searchKey:
            raise Exception("INNERTUBE API key (searchKey) is not set.")
        self.url = 'https://www.youtube.com/youtubei/v1/get_transcript' + "?" + urlencode({
            'key': searchKey,
            "prettyPrint": "false"
        })
        self.data = copy.deepcopy(requestPayload)
        ctx = self.data.setdefault('context', {})
        client = ctx.setdefault('client', {})
        client.update({
            'clientName': client.get('clientName', 'WEB'),
            'clientVersion': '2.20220318.00.00'
        })
        self.data["params"] = self.key

    def extract_transcript(self):
        data = self._safe_load_response(self.data)
        transcripts = getValue(data, ["actions", 0, "updateEngagementPanelAction", "content", "transcriptRenderer", "content", "transcriptSearchPanelRenderer", "body", "transcriptSegmentListRenderer", "initialSegments"]) or []
        segments = []
        languages = []
        for segment in transcripts:
            seg = getValue(segment, ["transcriptSegmentRenderer"]) or {}
            j = {
                "startMs": getValue(seg, ["startMs"]),
                "endMs": getValue(seg, ["endMs"]),
                "text": getValue(seg, ["snippet", "runs", 0, "text"]),
                "startTime": getValue(seg, ["startTimeText", "simpleText"])
            }
            segments.append(j)
        langs = getValue(data, ["actions", 0, "updateEngagementPanelAction", "content", "transcriptRenderer", "content", "transcriptSearchPanelRenderer", "footer", "transcriptFooterRenderer", "languageMenu", "sortFilterSubMenuRenderer", "subMenuItems"]) or []
        for language in langs:
            j = {
                "params": getValue(language, ["continuation", "reloadContinuationData", "continuation"]),
                "selected": getValue(language, ["selected"]),
                "title": getValue(language, ["title"])
            }
            languages.append(j)
        self.result = {
            "segments": segments,
            "languages": languages
        }

    async def async_create(self):
        if not self.key:
            self.prepare_params_request()
            r = await self.asyncPostRequest()
            end = self.extract_continuation_key(r)
            if end:
                return
        self.prepare_transcript_request()
        self.data = await self.asyncPostRequest()
        self.extract_transcript()

    def sync_create(self):
        if not self.key:
            self.prepare_params_request()
            r = self.syncPostRequest()
            end = self.extract_continuation_key(r)
            if end:
                return
        self.prepare_transcript_request()
        self.data = self.syncPostRequest()
        self.extract_transcript()

    def _safe_load_response(self, response):
        try:
            if hasattr(response, "json"):
                return response.json()
            if hasattr(response, "text"):
                return json.loads(response.text)
            if isinstance(response, (str, bytes)):
                return json.loads(response)
        except Exception:
            return {}

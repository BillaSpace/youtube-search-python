import copy
import json
from typing import Union, List, Optional
from urllib.parse import urlencode

from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import ComponentHandler, getValue


class RecommendationsCore(RequestCore, ComponentHandler):
    def __init__(self, videoId: str, timeout: Optional[int] = None):
        super().__init__(timeout=timeout)
        self.videoId = videoId
        self.resultComponents = []

    def prepare_request(self):
        self.url = 'https://www.youtube.com/youtubei/v1/next' + "?" + urlencode({
            'key': searchKey,
            "prettyPrint": "false"
        })
        self.data = copy.deepcopy(requestPayload)
        self.data["videoId"] = self.videoId
        self.data["client"] = {"hl": "en", "gl": "US"}

    def parse_response(self, response_json: dict):
        self.resultComponents = []
        watch_results = getValue(response_json, ["contents", "twoColumnWatchNextResults"])
        secondary_results = getValue(watch_results, ["secondaryResults", "secondaryResults", "results"])
        
        if not secondary_results:
             secondary_results = getValue(watch_results, ["secondaryResults", "results"])
        
        if not secondary_results:
             secondary_results = getValue(response_json, ["onResponseReceivedEndpoints", 0, "appendContinuationItemsAction", "continuationItems"])

        if secondary_results:
            for item in secondary_results:
                # Try lockupViewModel first as it's the escape way 
                if "lockupViewModel" in item:
                    component = self._getLockupComponent(item, findVideos=True, findChannels=False, findPlaylists=False)
                    if component:
                        self.resultComponents.append(component)
                    continue

                if compactVideoElementKey in item:
                    self.resultComponents.append(self._getRecommendationsComponent(item[compactVideoElementKey]))
                elif videoElementKey in item:
                    self.resultComponents.append(self._getRecommendationsComponent(item[videoElementKey]))
                elif itemSectionKey in item:
                    section_items = getValue(item, [itemSectionKey, "contents"])
                    if section_items:
                        for s_item in section_items:
                            if "lockupViewModel" in s_item:
                                component = self._getLockupComponent(s_item, findVideos=True, findChannels=False, findPlaylists=False)
                                if component:
                                    self.resultComponents.append(component)
                            elif compactVideoElementKey in s_item:
                                self.resultComponents.append(self._getRecommendationsComponent(s_item[compactVideoElementKey]))
                            elif videoElementKey in s_item:
                                self.resultComponents.append(self._getRecommendationsComponent(s_item[videoElementKey]))

    def _getRecommendationsComponent(self, video: dict) -> dict:
        component = {
            'type':                           'video',
            'id':                              self._getValue(video, ['videoId']),
            'title':                           self._getValue(video, ['title', 'simpleText']) or self._getValue(video, ['title', 'runs', 0, 'text']),
            'publishedTime':                   self._getValue(video, ['publishedTimeText', 'simpleText']),
            'duration':                        self._getValue(video, ['lengthText', 'simpleText']),
            'viewCount': {
                'text':                        self._getValue(video, ['viewCountText', 'simpleText']),
                'short':                       self._getValue(video, ['shortViewCountText', 'simpleText']),
            },
            'thumbnails':                      self._getValue(video, ['thumbnail', 'thumbnails']),
            'channel': {
                'name':                        self._getValue(video, ['longBylineText', 'runs', 0, 'text']) or self._getValue(video, ['shortBylineText', 'runs', 0, 'text']),
                'id':                          self._getValue(video, ['longBylineText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']) or self._getValue(video, ['shortBylineText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']),
            },
            'accessibility': {
                'title':                       self._getValue(video, ['title', 'accessibility', 'accessibilityData', 'label']),
                'duration':                    self._getValue(video, ['lengthText', 'accessibility', 'accessibilityData', 'label']),
            },
        }
        component['link'] = 'https://www.youtube.com/watch?v=' + (component['id'] or "")
        if component['channel']['id']:
            component['channel']['link'] = 'https://www.youtube.com/channel/' + component['channel']['id']
        return component

    async def async_create(self):
        self.prepare_request()
        response = await self.asyncPostRequest()
        self.parse_response(response.json())

    def sync_create(self):
        self.prepare_request()
        response = self.syncPostRequest()
        self.parse_response(response.json())

import copy
import json
from typing import Union, List, Optional
from urllib.parse import urlencode

from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import RequestCore, get_env_auth
from youtubesearchpython.core.componenthandler import getValue, getVideoId
from youtubesearchpython.core.requests import YouTubeRequestError, YouTubeParseError
from youtubesearchpython.core.utils import (
    get_cleaned_url,
    format_view_count,
    format_duration,
    format_published_time,
    normalize_thumbnails
)

CLIENTS = {
    "MWEB": {
        "context": {
            "client": {"clientName": "MWEB", "clientVersion": "2.20240425.01.00"}
        },
        "api_key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
    },
    "WEB": {
        'context': {
            'client': {
                'clientName': 'WEB',
                'clientVersion': '2.20240502.07.00',
                'newVisitorCookie': True
            },
            'user': {
                'lockedSafetyMode': False
            }
        },
        'api_key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'
    },
    "ANDROID": {
        "context": {"client": {"clientName": "ANDROID", "clientVersion": "19.02.39"}},
        "api_key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
    },
    "ANDROID_EMBED": {
        "context": {
            "client": {
                "clientName": "ANDROID",
                "clientVersion": "19.02.39",
                "clientScreen": "EMBED",
            }
        },
        "api_key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
    },
    "TV_EMBED": {
        "context": {
            "client": {
                "clientName": "TVHTML5_SIMPLY_EMBEDDED_PLAYER",
                "clientVersion": "2.0",
            },
            "thirdParty": {
                "embedUrl": "https://www.youtube.com/",
            },
        },
        "api_key": "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
    },
}

class VideoCore(RequestCore):
    def __init__(self, videoLink: str, componentMode: str, resultMode: int, timeout: Optional[int], enableHTML: bool, overridedClient: str = "ANDROID", po_token: str = None, visitor_data: str = None, proxy: str = None):
        super().__init__(timeout=timeout)
        self.resultMode = resultMode
        self.componentMode = componentMode
        self.videoLink = get_cleaned_url(videoLink)
        self.enableHTML = enableHTML
        self.overridedClient = overridedClient
        self.po_token, self.visitor_data = get_env_auth(po_token, visitor_data)
        self.proxy = proxy
        self.HTMLresponseSource = {}

    def post_request_only_html_processing(self):
        self.__getVideoComponent(self.componentMode)
        self.result = self.__result(self.resultMode)

    def post_request_processing(self):
        self.__parseSource()
        self.__getVideoComponent(self.componentMode)
        self.result = self.__result(self.resultMode)

    async def async_post_request_processing(self):
        self.__parseSource()
        await self.__getVideoComponentAsync(self.componentMode)
        self.result = self.__result(self.resultMode)

    def prepare_innertube_request(self):
        self.url = 'https://www.youtube.com/youtubei/v1/player' + "?" + urlencode({
            'key': searchKey,
            'contentCheckOk': 1,
            'racyCheckOk': 1,
            "videoId": getVideoId(self.videoLink)
        })
        self.data = copy.deepcopy(CLIENTS[self.overridedClient])
        client = self.data.setdefault("context", {}).setdefault("client", {})
        if self.visitor_data:
            client["visitorData"] = self.visitor_data
        if self.po_token:
            self.data["serviceIntegrityDimensions"] = {"poToken": self.po_token}

    @staticmethod
    def _streaming_score(source: dict) -> int:
        data = (source or {}).get("streamingData") or {}
        formats = list(data.get("formats") or []) + list(data.get("adaptiveFormats") or [])
        direct = sum(1 for item in formats if item.get("url"))
        usable_cipher = sum(1 for item in formats if (item.get("signatureCipher") or item.get("cipher")) and "s=" not in (item.get("signatureCipher") or item.get("cipher") or ""))
        return direct * 1000 + usable_cipher * 100 + len(formats)

    async def async_create(self):
        best_response = None
        best_source = None
        best_score = -1
        for client in ["ANDROID", "WEB", "MWEB", "TV_EMBED"]:
            self.overridedClient = client
            self.prepare_innertube_request()
            response = await self.asyncPostRequest()
            if response is None or response.status_code != 200:
                continue
            try:
                source = response.json()
            except Exception:
                continue
            if "videoDetails" not in source:
                continue
            if self.componentMode == "getInfo":
                self.response = response.text
                self.responseSource = source
                await self.__getVideoComponentAsync(self.componentMode)
                self.result = self.__result(self.resultMode)
                return
            score = self._streaming_score(source)
            if score > best_score:
                best_response, best_source, best_score = response.text, source, score
            if score >= 1000:
                break
        if best_source is not None and (self.componentMode != "getFormats" or best_score > 0):
            self.response = best_response
            self.responseSource = best_source
            await self.__getVideoComponentAsync(self.componentMode)
            self.result = self.__result(self.resultMode)
            return
        if self.componentMode == "getFormats":
            raise YouTubeRequestError(f"Could not fetch streaming formats for {self.videoLink}.")
        try:
            search_data = await self.__getVideoDataFromSearchAsync(getVideoId(self.videoLink))
            if search_data.get("title"):
                self.resultComponents = search_data
                self.__videoComponent = search_data
                self.result = self.__result(self.resultMode)
                return
        except Exception:
            pass
        raise YouTubeRequestError(f"Could not fetch video details for {self.videoLink} after trying multiple clients.")

    def sync_create(self):
        best_response = None
        best_source = None
        best_score = -1
        for client in ["ANDROID", "WEB", "MWEB", "TV_EMBED"]:
            self.overridedClient = client
            self.prepare_innertube_request()
            response = self.syncPostRequest()
            if response is None or response.status_code != 200:
                continue
            try:
                source = response.json()
            except Exception:
                continue
            if "videoDetails" not in source:
                continue
            if self.componentMode == "getInfo":
                self.response = response.text
                self.responseSource = source
                self.__getVideoComponent(self.componentMode)
                self.result = self.__result(self.resultMode)
                return
            score = self._streaming_score(source)
            if score > best_score:
                best_response, best_source, best_score = response.text, source, score
            if score >= 1000:
                break
        if best_source is not None and (self.componentMode != "getFormats" or best_score > 0):
            self.response = best_response
            self.responseSource = best_source
            self.__getVideoComponent(self.componentMode)
            self.result = self.__result(self.resultMode)
            return
        if self.componentMode == "getFormats":
            raise YouTubeRequestError(f"Could not fetch streaming formats for {self.videoLink}.")
        try:
            search_data = self.__getVideoDataFromSearch(getVideoId(self.videoLink))
            if search_data.get("title"):
                self.resultComponents = search_data
                self.__videoComponent = search_data
                self.result = self.__result(self.resultMode)
                return
        except Exception:
            pass
        raise YouTubeRequestError(f"Could not fetch video details for {self.videoLink} after trying multiple clients.")

    def prepare_html_request(self):
        self.url = 'https://www.youtube.com/youtubei/v1/player' + "?" + urlencode({
            'key': searchKey,
            'contentCheckOk': True,
            'racyCheckOk': True,
            "videoId": getVideoId(self.videoLink)
        })
        self.data = copy.deepcopy(CLIENTS["MWEB"])
        client = self.data.setdefault("context", {}).setdefault("client", {})
        if self.visitor_data:
            client["visitorData"] = self.visitor_data
        if self.po_token:
            self.data["serviceIntegrityDimensions"] = {"poToken": self.po_token}

    def sync_html_create(self):
        self.prepare_html_request()
        try:
            response = self.syncPostRequest()
            self.HTMLresponseSource = response.json() if response is not None and response.status_code == 200 else {}
        except Exception:
            self.HTMLresponseSource = {}

    async def async_html_create(self):
        self.prepare_html_request()
        try:
            response = await self.asyncPostRequest()
            self.HTMLresponseSource = response.json() if response is not None and response.status_code == 200 else {}
        except Exception:
            self.HTMLresponseSource = {}

    def __parseSource(self) -> None:
        try:
            self.responseSource = json.loads(self.response)
        except json.JSONDecodeError as e:
            raise YouTubeParseError(f'Failed to parse JSON response for video {self.videoLink}: {str(e)}')
        except Exception as e:
            raise YouTubeParseError(f'Failed to parse YouTube response: {str(e)}')

    def __result(self, mode: int) -> Union[dict, str]:
        if mode == ResultMode.dict:
            return self.__videoComponent
        elif mode == ResultMode.json:
            return json.dumps(self.__videoComponent, indent=4)

    def __findVideoDataInSearchResults(self,search_contents:List[dict],video_id:str)->Optional[dict]:
        if not search_contents:return None
        stack=list(search_contents)
        while stack:
            item=stack.pop()
            if not isinstance(item,dict):
                if isinstance(item,list):stack.extend(item)
                continue
            if item.get("id")==video_id:
                channel_id=getValue(item,["channel","id"])
                return {
                    "videoId":video_id,
                    "title":{"runs":[{"text":item.get("title")}]},
                    "lengthText":{"simpleText":item.get("duration")},
                    "viewCountText":{"simpleText":getValue(item,["viewCount","text"])},
                    "shortViewCountText":{"simpleText":getValue(item,["viewCount","short"])},
                    "publishedTimeText":{"simpleText":item.get("publishedTime")},
                    "thumbnail":{"thumbnails":item.get("thumbnails") or []},
                    "ownerText":{"runs":[{"text":getValue(item,["channel","name"]),"navigationEndpoint":{"browseEndpoint":{"browseId":channel_id}}}]}
                }
            video_data=None
            if videoElementKey in item:video_data=item[videoElementKey]
            elif item.get("videoId")==video_id:video_data=item
            elif richItemKey in item:
                rich=getValue(item,[richItemKey,"content"])
                if isinstance(rich,dict):
                    if videoElementKey in rich:video_data=rich[videoElementKey]
                    elif "lockupViewModel" in rich:item=rich["lockupViewModel"]
            if isinstance(video_data,dict):
                found_id=getValue(video_data,["videoId"]) or getValue(video_data,["navigationEndpoint","watchEndpoint","videoId"])
                if found_id==video_id:return video_data
            lockup=item.get("lockupViewModel") if isinstance(item.get("lockupViewModel"),dict) else item if "contentId" in item else None
            if isinstance(lockup,dict) and getValue(lockup,["contentId"])==video_id:
                metadata=getValue(lockup,["metadata","lockupMetadataViewModel"]) or {}
                title=getValue(metadata,["title","content"]) or getValue(metadata,["title","runs",0,"text"])
                thumbnails=getValue(lockup,["contentImage","thumbnailViewModel","image","sources"]) or getValue(lockup,["contentImage","thumbnailViewModel","thumbnail","thumbnails"]) or []
                owner_name=None
                owner_id=None
                rows=getValue(metadata,["metadata","contentMetadataViewModel","metadataRows"]) or []
                for row in rows:
                    for part in getValue(row,["metadataParts"]) or []:
                        text_value=getValue(part,["text","content"])
                        browse_id=getValue(part,["text","commandRuns",0,"onTap","innertubeCommand","browseEndpoint","browseId"])
                        if browse_id:
                            owner_id=browse_id
                            owner_name=text_value
                            break
                    if owner_id:break
                return {
                    "videoId":video_id,
                    "title":{"runs":[{"text":title}]},
                    "lengthText":{"simpleText":None},
                    "viewCountText":{"simpleText":None},
                    "shortViewCountText":{"simpleText":None},
                    "publishedTimeText":{"simpleText":None},
                    "thumbnail":{"thumbnails":thumbnails},
                    "ownerText":{"runs":[{"text":owner_name,"navigationEndpoint":{"browseEndpoint":{"browseId":owner_id}}}]}
                }
            for value in item.values():
                if isinstance(value,(dict,list)):stack.append(value)
        return None

    def __searchQueries(self, video_id: str, video_title: Optional[str] = None) -> list:
        queries = [f"https://www.youtube.com/watch?v={video_id}", video_id]
        if video_title:
            queries.insert(0, video_title)
        return queries

    def __searchResult(self, data: dict, video_id: str) -> Optional[dict]:
        search_contents = getValue(data, contentPath) or getValue(data, fallbackContentPath)
        video_data = self.__findVideoDataInSearchResults(search_contents, video_id)
        if not video_data:
            return None
        channel_id = getValue(video_data, ['ownerText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId'])
        return {
            'id': video_id,
            'title': getValue(video_data, ['title', 'runs', 0, 'text']),
            'publishedTime': getValue(video_data, ['publishedTimeText', 'simpleText']) or getValue(video_data, ['publishedTimeText', 'runs', 0, 'text']),
            'duration': format_duration(getValue(video_data, ['lengthText', 'simpleText'])),
            'viewCount': {
                'text': getValue(video_data, ['viewCountText', 'simpleText']),
                'short': getValue(video_data, ['shortViewCountText', 'simpleText']),
            },
            'thumbnails': normalize_thumbnails(getValue(video_data, ['thumbnail', 'thumbnails']), video_id),
            'channel': {
                'name': getValue(video_data, ['ownerText', 'runs', 0, 'text']),
                'id': channel_id,
                'link': f"https://www.youtube.com/channel/{channel_id}" if channel_id else None,
            },
            'link': f"https://www.youtube.com/watch?v={video_id}",
        }

    def __emptySearchResult(self, video_id: str) -> dict:
        return {
            'id': video_id, 'title': None, 'publishedTime': None, 'duration': None,
            'viewCount': {'text': None, 'short': None}, 'thumbnails': None,
            'channel': {'name': None, 'id': None, 'link': None},
            'link': f"https://www.youtube.com/watch?v={video_id}",
        }

    def __prepareSearchRequest(self, query: str) -> None:
        self.url = 'https://www.youtube.com/youtubei/v1/search?' + urlencode({'key': searchKey})
        self.data = self.buildInnertubeBody(query=query, client={'hl': 'en', 'gl': 'US'})

    def __getVideoDataFromSearch(self, video_id: str, video_title: Optional[str] = None) -> dict:
        for query in self.__searchQueries(video_id, video_title):
            try:
                self.__prepareSearchRequest(query)
                response = self.syncPostRequest()
                if response.status_code == 200:
                    result = self.__searchResult(response.json(), video_id)
                    if result and result.get('title'):
                        return result
            except Exception:
                continue
        return self.__emptySearchResult(video_id)

    async def __getVideoDataFromSearchAsync(self, video_id: str, video_title: Optional[str] = None) -> dict:
        for query in self.__searchQueries(video_id, video_title):
            try:
                self.__prepareSearchRequest(query)
                response = await self.asyncPostRequest()
                if response.status_code == 200:
                    result = self.__searchResult(response.json(), video_id)
                    if result and result.get('title'):
                        return result
            except Exception:
                continue
        return self.__emptySearchResult(video_id)

    def __enhanceThumbnails(self, thumbnails: List[dict], video_id: str, search_api_data: Optional[dict] = None) -> List[dict]:
        return normalize_thumbnails(thumbnails, video_id)

    async def __enhanceThumbnailsAsync(self, thumbnails: List[dict], video_id: str, search_api_data: Optional[dict] = None) -> List[dict]:
        return normalize_thumbnails(thumbnails, video_id)

    def __getVideoComponent(self, mode: str) -> None:
        videoComponent = {}
        if mode in ["getInfo", None]:
            responseSource = getattr(self, "responseSource", None)
            raw_view_count = getValue(responseSource, ["videoDetails", "viewCount"])
            raw_duration = getValue(responseSource, ["videoDetails", "lengthSeconds"])
            publish_date = getValue(
                responseSource,
                ["microformat", "playerMicroformatRenderer", "publishDate"],
            )
            component = {
                "id": getValue(responseSource, ["videoDetails", "videoId"]),
                "title": getValue(responseSource, ["videoDetails", "title"]),
                "duration": format_duration(raw_duration),
                "viewCount": format_view_count(raw_view_count),
                "thumbnails": getValue(
                    responseSource, ["videoDetails", "thumbnail", "thumbnails"]
                ),
                "description": getValue(
                    responseSource, ["videoDetails", "shortDescription"]
                ),
                "channel": {
                    "name": getValue(responseSource, ["videoDetails", "author"]),
                    "id": getValue(responseSource, ["videoDetails", "channelId"]),
                },
                "allowRatings": getValue(
                    responseSource, ["videoDetails", "allowRatings"]
                ),
                "averageRating": getValue(
                    responseSource, ["videoDetails", "averageRating"]
                ),
                "keywords": getValue(responseSource, ["videoDetails", "keywords"]),
                "isLiveContent": getValue(
                    responseSource, ["videoDetails", "isLiveContent"]
                ),
                "isFamilySafe": getValue(
                    responseSource,
                    ["microformat", "playerMicroformatRenderer", "isFamilySafe"],
                ),
                "category": getValue(
                    responseSource,
                    ["microformat", "playerMicroformatRenderer", "category"],
                ),
            }

            upload_date = getValue(
                responseSource,
                ["microformat", "playerMicroformatRenderer", "uploadDate"],
            )
            live_broadcast_date = getValue(
                responseSource,
                ["videoDetails", "liveBroadcastDetails", "startTimestamp"],
            )
            scheduled_start_time = getValue(
                responseSource,
                ["videoDetails", "liveBroadcastDetails", "scheduledStartTime"],
            )

            if not publish_date and upload_date:
                publish_date = upload_date
            if not publish_date and live_broadcast_date:
                publish_date = live_broadcast_date
            if not publish_date and scheduled_start_time:
                publish_date = scheduled_start_time

            component["publishedTime"] = format_published_time(publish_date)
            if not component["publishedTime"] and upload_date:
                component["publishedTime"] = format_published_time(upload_date)
            if not component["publishedTime"] and live_broadcast_date:
                component["publishedTime"] = format_published_time(live_broadcast_date)

            search_api_data = None
            if component.get("id"):
                needs_search_data = not component["publishedTime"]
                if needs_search_data:
                    search_api_data = self.__getVideoDataFromSearch(component["id"], component.get("title"))
                    if not component["publishedTime"] and search_api_data.get("publishedTime"):
                        component["publishedTime"] = search_api_data["publishedTime"]

            if not component["publishedTime"]:
                if component.get("isLiveContent") or component.get("isLiveNow"):
                    component["publishedTime"] = "Live"

            if "publishDate" in component:
                del component["publishDate"]
            if "uploadDate" in component:
                del component["uploadDate"]
            live_broadcast_details = getValue(
                responseSource,
                ["videoDetails", "liveBroadcastDetails"],
            )
            is_live_broadcast = live_broadcast_details is not None
            duration_seconds = component["duration"].get("seconds")
            is_zero_duration = duration_seconds == 0 or duration_seconds is None

            component["isLiveNow"] = (
                component.get("isLiveContent") is True
                and (is_zero_duration or is_live_broadcast)
            )

            if component["id"]:
                component["link"] = "https://www.youtube.com/watch?v=" + component["id"]
            else:
                component["link"] = None
            if component["channel"]["id"]:
                component["channel"]["link"] = (
                    "https://www.youtube.com/channel/" + component["channel"]["id"]
                )
            else:
                component["channel"]["link"] = None

            if component.get("id"):
                component["thumbnails"] = self.__enhanceThumbnails(component.get("thumbnails") or [], component["id"], search_api_data)

            videoComponent.update(component)
        if mode in ["getFormats", None]:
            videoComponent.update(
                {"streamingData": getValue(self.responseSource, ["streamingData"])}
            )
        if self.enableHTML:
            html_publish_date = getValue(
                self.HTMLresponseSource,
                ["microformat", "playerMicroformatRenderer", "publishDate"],
            )
            html_upload_date = getValue(
                self.HTMLresponseSource,
                ["microformat", "playerMicroformatRenderer", "uploadDate"],
            )
            if not videoComponent.get("publishedTime") and html_publish_date:
                videoComponent["publishedTime"] = format_published_time(html_publish_date)
            if not videoComponent.get("publishedTime") and html_upload_date:
                videoComponent["publishedTime"] = format_published_time(html_upload_date)

        if "publishDate" in videoComponent:
            del videoComponent["publishDate"]
        if "uploadDate" in videoComponent:
            del videoComponent["uploadDate"]
        self.__videoComponent = videoComponent

    async def __getVideoComponentAsync(self, mode: str) -> None:
        videoComponent = {}
        if mode in ["getInfo", None]:
            responseSource = getattr(self, "responseSource", None)
            raw_view_count = getValue(responseSource, ["videoDetails", "viewCount"])
            raw_duration = getValue(responseSource, ["videoDetails", "lengthSeconds"])
            publish_date = getValue(
                responseSource,
                ["microformat", "playerMicroformatRenderer", "publishDate"],
            )

            component = {
                "id": getValue(responseSource, ["videoDetails", "videoId"]),
                "title": getValue(responseSource, ["videoDetails", "title"]),
                "duration": format_duration(raw_duration),
                "viewCount": format_view_count(raw_view_count),
                "thumbnails": getValue(
                    responseSource, ["videoDetails", "thumbnail", "thumbnails"]
                ),
                "description": getValue(
                    responseSource, ["videoDetails", "shortDescription"]
                ),
                "channel": {
                    "name": getValue(responseSource, ["videoDetails", "author"]),
                    "id": getValue(responseSource, ["videoDetails", "channelId"]),
                },
                "allowRatings": getValue(
                    responseSource, ["videoDetails", "allowRatings"]
                ),
                "averageRating": getValue(
                    responseSource, ["videoDetails", "averageRating"]
                ),
                "keywords": getValue(responseSource, ["videoDetails", "keywords"]),
                "isLiveContent": getValue(
                    responseSource, ["videoDetails", "isLiveContent"]
                ),
                "isFamilySafe": getValue(
                    responseSource,
                    ["microformat", "playerMicroformatRenderer", "isFamilySafe"],
                ),
                "category": getValue(
                    responseSource,
                    ["microformat", "playerMicroformatRenderer", "category"],
                ),
            }

            upload_date = getValue(
                responseSource,
                ["microformat", "playerMicroformatRenderer", "uploadDate"],
            )
            live_broadcast_date = getValue(
                responseSource,
                ["videoDetails", "liveBroadcastDetails", "startTimestamp"],
            )
            scheduled_start_time = getValue(
                responseSource,
                ["videoDetails", "liveBroadcastDetails", "scheduledStartTime"],
            )

            if not publish_date and upload_date:
                publish_date = upload_date
            if not publish_date and live_broadcast_date:
                publish_date = live_broadcast_date
            if not publish_date and scheduled_start_time:
                publish_date = scheduled_start_time

            component["publishedTime"] = format_published_time(publish_date)
            if not component["publishedTime"] and upload_date:
                component["publishedTime"] = format_published_time(upload_date)
            if not component["publishedTime"] and live_broadcast_date:
                component["publishedTime"] = format_published_time(live_broadcast_date)

            search_api_data = None
            if component.get("id"):
                needs_search_data = not component["publishedTime"]
                if needs_search_data:
                    search_api_data = await self.__getVideoDataFromSearchAsync(component["id"], component.get("title"))
                    if not component["publishedTime"] and search_api_data.get("publishedTime"):
                        component["publishedTime"] = search_api_data["publishedTime"]

            if not component["publishedTime"]:
                if component.get("isLiveContent") or component.get("isLiveNow"):
                    component["publishedTime"] = "Live"

            if "publishDate" in component:
                del component["publishDate"]
            if "uploadDate" in component:
                del component["uploadDate"]
            live_broadcast_details = getValue(
                responseSource,
                ["videoDetails", "liveBroadcastDetails"],
            )
            is_live_broadcast = live_broadcast_details is not None
            duration_seconds = component["duration"].get("seconds")
            is_zero_duration = duration_seconds == 0 or duration_seconds is None

            component["isLiveNow"] = (
                component.get("isLiveContent") is True
                and (is_zero_duration or is_live_broadcast)
            )

            if component["id"]:
                component["link"] = "https://www.youtube.com/watch?v=" + component["id"]
            else:
                component["link"] = None
            if component["channel"]["id"]:
                component["channel"]["link"] = (
                    "https://www.youtube.com/channel/" + component["channel"]["id"]
                )
            else:
                component["channel"]["link"] = None

            if component.get("id"):
                component["thumbnails"] = await self.__enhanceThumbnailsAsync(component.get("thumbnails") or [], component["id"], search_api_data)

            videoComponent.update(component)
        if mode in ["getFormats", None]:
            videoComponent.update(
                {"streamingData": getValue(self.responseSource, ["streamingData"])}
            )
        if self.enableHTML:
            html_publish_date = getValue(
                self.HTMLresponseSource,
                ["microformat", "playerMicroformatRenderer", "publishDate"],
            )
            html_upload_date = getValue(
                self.HTMLresponseSource,
                ["microformat", "playerMicroformatRenderer", "uploadDate"],
            )
            if not videoComponent.get("publishedTime") and html_publish_date:
                videoComponent["publishedTime"] = format_published_time(html_publish_date)
            if not videoComponent.get("publishedTime") and html_upload_date:
                videoComponent["publishedTime"] = format_published_time(html_upload_date)

        if "publishDate" in videoComponent:
            del videoComponent["publishDate"]
        if "uploadDate" in videoComponent:
            del videoComponent["uploadDate"]
        self.__videoComponent = videoComponent


from typing import Optional
from urllib.parse import urlencode

from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import ComponentHandler, getValue
from youtubesearchpython.core.requests import YouTubeRequestError
from youtubesearchpython.core.utils import normalize_thumbnails


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
        self.data = self.buildInnertubeBody(videoId=self.videoId, client={"hl": "en", "gl": "US"})

    def parse_response(self, response_json: dict):
        self.resultComponents = []
        seen = {self.videoId}
        watch_results = getValue(response_json, ["contents", "twoColumnWatchNextResults"])
        secondary_results = getValue(watch_results, ["secondaryResults", "secondaryResults", "results"]) or getValue(watch_results, ["secondaryResults", "results"]) or getValue(response_json, ["onResponseReceivedEndpoints", 0, "appendContinuationItemsAction", "continuationItems"]) or []

        def append(component):
            video_id = component.get("id") if isinstance(component, dict) else None
            if not video_id or video_id in seen:
                return
            seen.add(video_id)
            self.resultComponents.append(component)

        for item in secondary_results:
            if "lockupViewModel" in item:
                append(self._getLockupComponent(item, findVideos=True, findChannels=False, findPlaylists=False))
            elif compactVideoElementKey in item:
                append(self._getRecommendationsComponent(item[compactVideoElementKey]))
            elif videoElementKey in item:
                append(self._getRecommendationsComponent(item[videoElementKey]))
            elif itemSectionKey in item:
                for s_item in getValue(item, [itemSectionKey, "contents"]) or []:
                    if "lockupViewModel" in s_item:
                        append(self._getLockupComponent(s_item, findVideos=True, findChannels=False, findPlaylists=False))
                    elif compactVideoElementKey in s_item:
                        append(self._getRecommendationsComponent(s_item[compactVideoElementKey]))
                    elif videoElementKey in s_item:
                        append(self._getRecommendationsComponent(s_item[videoElementKey]))

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
            'thumbnails':                      normalize_thumbnails(self._getValue(video, ['thumbnail', 'thumbnails']), self._getValue(video, ['videoId'])),
            'channel': {
                'name':                        self._getValue(video, ['longBylineText', 'runs', 0, 'text']) or self._getValue(video, ['shortBylineText', 'runs', 0, 'text']),
                'id':                          self._getValue(video, ['longBylineText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']) or self._getValue(video, ['shortBylineText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']),
            },
            'isLive':                          self._isLiveVideo(video),
            'accessibility': {
                'title':                       self._getValue(video, ['title', 'accessibility', 'accessibilityData', 'label']),
                'duration':                    self._getValue(video, ['lengthText', 'accessibility', 'accessibilityData', 'label']),
            },
        }
        component['link'] = 'https://www.youtube.com/watch?v=' + (component['id'] or "")
        if component['channel']['id']:
            component['channel']['link'] = 'https://www.youtube.com/channel/' + component['channel']['id']
        return component

    def _parse_http_response(self, response):
        if response.status_code != 200:
            raise YouTubeRequestError(f"Invalid status code {response.status_code} for recommendations request")
        self.parse_response(response.json())

    async def async_create(self):
        self.prepare_request()
        self._parse_http_response(await self.asyncPostRequest())

    def sync_create(self):
        self.prepare_request()
        self._parse_http_response(self.syncPostRequest())


import copy
import urllib.parse
from typing import Optional

from youtubesearchpython.core.componenthandler import getValue
from youtubesearchpython.core.requests import RequestCore, get_env_auth


class StreamURLFetcherCore(RequestCore):
    def __init__(self, proxy: str = None, cookies_file: str = None, po_token: str = None, visitor_data: str = None):
        super().__init__()
        self.proxy = proxy
        self.cookies_file = cookies_file
        self.po_token, self.visitor_data = get_env_auth(po_token, visitor_data)
        self.video_id = None
        self._streams = []
        self._unresolved = []

    def close(self) -> None:
        return None

    async def aclose(self) -> None:
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.aclose()

    def set_po_token(self, po_token: Optional[str]) -> None:
        self.po_token = po_token

    def _with_po_token(self, url: str) -> str:
        if not url or not self.po_token:
            return url
        parsed = urllib.parse.urlsplit(url)
        query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        if not any(key == "pot" for key, _ in query):
            query.append(("pot", self.po_token))
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), parsed.fragment))

    def _from_cipher(self, yt_format: dict) -> Optional[str]:
        cipher = getValue(yt_format, ["signatureCipher"]) or getValue(yt_format, ["cipher"])
        if not cipher:
            return None
        values = urllib.parse.parse_qs(cipher)
        url = getValue(values, ["url", 0])
        if not url:
            return None
        signature = getValue(values, ["sig", 0]) or getValue(values, ["signature", 0])
        encrypted = getValue(values, ["s", 0])
        if encrypted and not signature:
            return None
        if signature:
            key = getValue(values, ["sp", 0]) or "signature"
            parsed = urllib.parse.urlsplit(url)
            query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
            query.append((key, signature))
            url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), parsed.fragment))
        return url

    def _getDecipheredURLs(self, videoFormats: dict, formatId: int = None) -> None:
        self._streams = []
        self._unresolved = []
        self.video_id = videoFormats.get("id") or videoFormats.get("videoId")
        streaming_data = videoFormats.get("streamingData") or {}
        formats = list(streaming_data.get("formats") or []) + list(streaming_data.get("adaptiveFormats") or [])
        for source in formats:
            if formatId is not None and source.get("itag") != formatId:
                continue
            yt_format = copy.deepcopy(source)
            url = yt_format.get("url") or self._from_cipher(yt_format)
            if not url:
                unresolved = copy.deepcopy(yt_format)
                unresolved["requiresDecipher"] = bool(yt_format.get("signatureCipher") or yt_format.get("cipher"))
                self._unresolved.append(unresolved)
                continue
            yt_format["url"] = self._with_po_token(url)
            yt_format["throttled"] = "n=" in urllib.parse.urlsplit(url).query
            self._streams.append(yt_format)
            if formatId is not None:
                return

    def unresolved(self):
        return copy.deepcopy(self._unresolved)

    def _getJS(self) -> None:
        return None

    async def getJavaScript(self):
        return None

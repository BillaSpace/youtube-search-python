import copy
import json
from typing import Union, List, Optional
from urllib.parse import urlencode
import httpx

from youtubesearchpython.core.constants import *
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import getValue, getVideoId
from youtubesearchpython.core.exceptions import YouTubeRequestError, YouTubeParseError
from youtubesearchpython.core.utils import (
    get_cleaned_url,
    format_view_count,
    format_duration,
    format_published_time
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
    def __init__(self, videoLink: str, componentMode: str, resultMode: int, timeout: Optional[int], enableHTML: bool, overridedClient: str = "ANDROID"):
        super().__init__(timeout=timeout)
        self.timeout = timeout
        self.resultMode = resultMode
        self.componentMode = componentMode
        self.videoLink = get_cleaned_url(videoLink)
        self.enableHTML = enableHTML
        self.overridedClient = overridedClient
    
    def post_request_only_html_processing(self):
        self.__getVideoComponent(self.componentMode)
        self.result = self.__videoComponent

    def post_request_processing(self):
        self.__parseSource()
        self.__getVideoComponent(self.componentMode)
        self.result = self.__videoComponent

    async def async_post_request_processing(self):
        self.__parseSource()
        await self.__getVideoComponentAsync(self.componentMode)
        self.result = self.__videoComponent

    def prepare_innertube_request(self):
        self.url = 'https://www.youtube.com/youtubei/v1/player' + "?" + urlencode({
            'key': searchKey,
            'contentCheckOk': 1,
            'racyCheckOk': 1,
            "videoId": getVideoId(self.videoLink)
        })
        self.data = copy.deepcopy(CLIENTS[self.overridedClient])

    async def async_create(self):
        for client in ["ANDROID", "WEB", "MWEB", "TV_EMBED"]:
            self.overridedClient = client
            self.prepare_innertube_request()
            response = await self.asyncPostRequest()
            if response is not None and response.status_code == 200:
                self.response = response.text
                self.__parseSource()
                if self.responseSource and 'videoDetails' in self.responseSource:
                    await self.async_post_request_processing()
                    return
        
        try:
            search_data = await self.__getVideoDataFromSearchAsync(getVideoId(self.videoLink))
            if search_data.get("title"):
                self.resultComponents = search_data
                self.result = search_data
                self.__videoComponent = search_data
                return
        except Exception:
            pass
        
        raise YouTubeRequestError(f"Could not fetch video details for {self.videoLink} after trying multiple clients.")

    def sync_create(self):
        for client in ["ANDROID", "WEB", "MWEB", "TV_EMBED"]:
            self.overridedClient = client
            self.prepare_innertube_request()
            response = self.syncPostRequest()
            if response is not None and response.status_code == 200:
                self.response = response.text
                self.__parseSource()
                if self.responseSource and 'videoDetails' in self.responseSource:
                    self.post_request_processing()
                    return
        
        try:
            search_data = self.__getVideoDataFromSearch(getVideoId(self.videoLink))
            if search_data.get("title"):
                self.resultComponents = search_data
                self.result = search_data
                self.__videoComponent = search_data
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
        self.data = CLIENTS["MWEB"]

    def sync_html_create(self):
        self.prepare_html_request()
        response = self.syncPostRequest()
        self.HTMLresponseSource = response.json()

    async def async_html_create(self):
        self.prepare_html_request()
        response = await self.asyncPostRequest()
        self.HTMLresponseSource = response.json()

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

    def __checkThumbnailExists(self, url: str) -> bool:
        try:
            response = httpx.head(url, headers={"User-Agent": userAgent}, timeout=2, follow_redirects=True)
            return response.status_code == 200
        except (httpx.RequestError, httpx.HTTPStatusError, Exception):
            return False

    async def __checkThumbnailExistsAsync(self, url: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(url, headers={"User-Agent": userAgent}, timeout=2, follow_redirects=True)
                return response.status_code == 200
        except (httpx.RequestError, httpx.HTTPStatusError, Exception):
            return False

    def __getBestHq720FromThumbnails(self, thumbnails: List[dict]) -> Union[dict, None]:
        best_thumb = None
        best_resolution = 0
        for thumb in thumbnails:
            url_value = thumb.get('url', '')
            if 'hq720.jpg' in url_value:
                width = thumb.get('width', 0)
                height = thumb.get('height', 0)
                resolution = width * height
                if resolution > best_resolution:
                    best_resolution = resolution
                    full_url = url_value if url_value.startswith('http') else 'https:' + url_value
                    best_thumb = {
                        "url": full_url,
                        "width": width,
                        "height": height
                    }
        return best_thumb

    def __findVideoDataInSearchResults(self, search_contents: List[dict], video_id: str) -> Optional[dict]:
        """
        Helper method to find video data in search API response.
        Eliminates code duplication across multiple methods.
        """
        if not search_contents:
            return None
        
        for item in search_contents:
            video_data = None
            if itemSectionKey in item:
                section_contents = getValue(item, [itemSectionKey, 'contents'])
                if section_contents:
                    for section_item in section_contents:
                        if videoElementKey in section_item:
                            v_data = section_item[videoElementKey]
                            if getValue(v_data, ['videoId']) == video_id:
                                return v_data
            elif videoElementKey in item:
                video_data = item[videoElementKey]
            elif richItemKey in item:
                rich_content = getValue(item, [richItemKey, 'content'])
                if rich_content and videoElementKey in rich_content:
                    video_data = rich_content[videoElementKey]
                elif rich_content and "lockupViewModel" in rich_content:
                    lockup = rich_content["lockupViewModel"]
                    if getValue(lockup, ["contentId"]) == video_id:
                        return {
                            "videoId": video_id,
                            "title": {"runs": [{"text": getValue(lockup, ["metadata", "lockupMetadataViewModel", "title", "content"])}]},
                            "lengthText": {"simpleText": "0:00"},
                            "viewCountText": {"simpleText": "0 views"},
                            "publishedTimeText": {"simpleText": "Unknown"},
                            "ownerText": {"runs": [{"text": "Unknown"}]}
                        }
            
            if video_data:
                found_video_id = getValue(video_data, ['videoId'])
                if found_video_id == video_id:
                    return video_data
                nav_video_id = getValue(video_data, ['navigationEndpoint', 'watchEndpoint', 'videoId'])
                if nav_video_id == video_id:
                    return video_data
        return None

    def __getVideoDataFromSearch(self, video_id: str, video_title: Optional[str] = None) -> dict:
        result = {
            'id': video_id,
            'title': None,
            'publishedTime': None, 
            'duration': None,
            'viewCount': {'text': None, 'short': None},
            'thumbnails': None,
            'channel': {'name': None, 'id': None, 'link': None},
            'link': f"https://www.youtube.com/watch?v={video_id}"
        }
        
        search_queries = []
        if video_title:
            search_queries.append(video_title)
        search_queries.append(f"https://www.youtube.com/watch?v={video_id}")
        search_queries.append(video_id)
        
        for query in search_queries:
            try:
                request_body = copy.deepcopy(requestPayload)
                request_body['query'] = query
                request_body['client'] = {
                    'hl': 'en',
                    'gl': 'US',
                }
                
                url = 'https://www.youtube.com/youtubei/v1/search' + '?' + urlencode({'key': searchKey})
                response = httpx.post(
                    url,
                    headers={"User-Agent": userAgent, "Content-Type": "application/json"},
                    json=request_body,
                    timeout=self.timeout if self.timeout else 5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    contents = getValue(data, contentPath)
                    fallback_contents = getValue(data, fallbackContentPath)
                    
                    search_contents = contents if contents else fallback_contents
                    video_data = self.__findVideoDataInSearchResults(search_contents, video_id)
                    
                    if video_data:
                        result['title'] = getValue(video_data, ['title', 'runs', 0, 'text'])
                        result['publishedTime'] = getValue(video_data, ['publishedTimeText', 'simpleText']) or getValue(video_data, ['publishedTimeText', 'runs', 0, 'text'])
                        result['duration'] = format_duration(getValue(video_data, ['lengthText', 'simpleText']))
                        result['viewCount'] = {
                            'text': getValue(video_data, ['viewCountText', 'simpleText']),
                            'short': getValue(video_data, ['shortViewCountText', 'simpleText'])
                        }
                        result['thumbnails'] = getValue(video_data, ['thumbnail', 'thumbnails'])
                        result['channel'] = {
                            'name': getValue(video_data, ['ownerText', 'runs', 0, 'text']),
                            'id': getValue(video_data, ['ownerText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']),
                            'link': 'https://www.youtube.com/channel/' + (getValue(video_data, ['ownerText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']) or "")
                        }
                        
                        if result['thumbnails']:
                            best_thumb = self.__getBestHq720FromThumbnails(result['thumbnails'])
                            if best_thumb:
                                result['hq720Thumbnail'] = best_thumb
                        
                        if result['title']:
                            break
            except Exception:
                continue
        
        return result

    async def __getVideoDataFromSearchAsync(self, video_id: str, video_title: Optional[str] = None) -> dict:
        result = {
            'id': video_id,
            'title': None,
            'publishedTime': None, 
            'duration': None,
            'viewCount': {'text': None, 'short': None},
            'thumbnails': None,
            'channel': {'name': None, 'id': None, 'link': None},
            'link': f"https://www.youtube.com/watch?v={video_id}"
        }
        
        search_queries = []
        if video_title:
            search_queries.append(video_title)
        search_queries.append(f"https://www.youtube.com/watch?v={video_id}")
        search_queries.append(video_id)
        
        for query in search_queries:
            try:
                request_body = copy.deepcopy(requestPayload)
                request_body['query'] = query
                request_body['client'] = {
                    'hl': 'en',
                    'gl': 'US',
                }
                
                url = 'https://www.youtube.com/youtubei/v1/search' + '?' + urlencode({'key': searchKey})
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        headers={"User-Agent": userAgent, "Content-Type": "application/json"},
                        json=request_body,
                        timeout=self.timeout if self.timeout else 5
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    contents = getValue(data, contentPath)
                    fallback_contents = getValue(data, fallbackContentPath)
                    
                    search_contents = contents if contents else fallback_contents
                    video_data = self.__findVideoDataInSearchResults(search_contents, video_id)
                    
                    if video_data:
                        result['title'] = getValue(video_data, ['title', 'runs', 0, 'text'])
                        result['publishedTime'] = getValue(video_data, ['publishedTimeText', 'simpleText']) or getValue(video_data, ['publishedTimeText', 'runs', 0, 'text'])
                        result['duration'] = format_duration(getValue(video_data, ['lengthText', 'simpleText']))
                        result['viewCount'] = {
                            'text': getValue(video_data, ['viewCountText', 'simpleText']),
                            'short': getValue(video_data, ['shortViewCountText', 'simpleText'])
                        }
                        result['thumbnails'] = getValue(video_data, ['thumbnail', 'thumbnails'])
                        result['channel'] = {
                            'name': getValue(video_data, ['ownerText', 'runs', 0, 'text']),
                            'id': getValue(video_data, ['ownerText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']),
                            'link': 'https://www.youtube.com/channel/' + (getValue(video_data, ['ownerText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']) or "")
                        }
                        
                        # Extract hq720 thumbnail
                        if result['thumbnails']:
                            best_thumb = self.__getBestHq720FromThumbnails(result['thumbnails'])
                            if best_thumb:
                                result['hq720Thumbnail'] = best_thumb
                        
                        if result['title']:
                            break
            except Exception:
                continue
        
        return result


    def __enhanceThumbnails(self, thumbnails: List[dict], video_id: str, search_api_data: Optional[dict] = None) -> List[dict]:
        if not thumbnails or not video_id:
            return thumbnails
        
        enhanced = list(thumbnails)
        existing_urls = {thumb.get("url", "") for thumb in enhanced if isinstance(thumb, dict)}
        existing_base_urls = {url.split('?')[0] if '?' in url else url for url in existing_urls}
        
        standard_thumbnails = [
            {"url": f"https://i.ytimg.com/vi/{video_id}/default.jpg", "width": 120, "height": 90},
            {"url": f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg", "width": 320, "height": 180},
            {"url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg", "width": 480, "height": 360},
            {"url": f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg", "width": 640, "height": 480},
            {"url": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg", "width": 1920, "height": 1080},
            {"url": f"https://i.ytimg.com/vi/{video_id}/hq720.jpg", "width": 1280, "height": 720},
        ]
        
        for thumb in standard_thumbnails:
            base_url = thumb["url"]
            if base_url not in existing_base_urls:
                if self.__checkThumbnailExists(base_url):
                    enhanced.append(thumb)
        
        if search_api_data and search_api_data.get('hq720Thumbnail'):
            optimized_hq720 = search_api_data['hq720Thumbnail']
        else:
            search_data = self.__getVideoDataFromSearch(video_id)
            optimized_hq720 = search_data.get('hq720Thumbnail')
        
        if optimized_hq720:
            optimized_url = optimized_hq720["url"]
            if optimized_url not in existing_urls and optimized_url.split('?')[0] not in existing_base_urls:
                enhanced.append(optimized_hq720)
        
        return enhanced



    async def __enhanceThumbnailsAsync(self, thumbnails: List[dict], video_id: str, search_api_data: Optional[dict] = None) -> List[dict]:
        if not thumbnails or not video_id:
            return thumbnails
        
        enhanced = list(thumbnails)
        existing_urls = {thumb.get("url", "") for thumb in enhanced if isinstance(thumb, dict)}
        existing_base_urls = {url.split('?')[0] if '?' in url else url for url in existing_urls}
        
        standard_thumbnails = [
            {"url": f"https://i.ytimg.com/vi/{video_id}/default.jpg", "width": 120, "height": 90},
            {"url": f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg", "width": 320, "height": 180},
            {"url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg", "width": 480, "height": 360},
            {"url": f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg", "width": 640, "height": 480},
            {"url": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg", "width": 1920, "height": 1080},
            {"url": f"https://i.ytimg.com/vi/{video_id}/hq720.jpg", "width": 1280, "height": 720},
        ]
        
        for thumb in standard_thumbnails:
            base_url = thumb["url"]
            if base_url not in existing_base_urls:
                if await self.__checkThumbnailExistsAsync(base_url):
                    enhanced.append(thumb)
        
        # Use search API data if already fetched in same call to avoid multiple reqs , otherwise fetch separately
        if search_api_data and search_api_data.get('hq720Thumbnail'):
            optimized_hq720 = search_api_data['hq720Thumbnail']
        else:
            search_data = await self.__getVideoDataFromSearchAsync(video_id)
            optimized_hq720 = search_data.get('hq720Thumbnail')
        
        if optimized_hq720:
            optimized_url = optimized_hq720["url"]
            if optimized_url not in existing_urls and optimized_url.split('?')[0] not in existing_base_urls:
                enhanced.append(optimized_hq720)
        
        return enhanced

    def __getVideoComponent(self, mode: str) -> None:
        videoComponent = {}
        if mode in ["getInfo", None]:
            responseSource = getattr(self, "responseSource", None)
            if self.enableHTML:
                responseSource = self.HTMLresponseSource
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
                needs_search_data = not component["publishedTime"] or (component.get("thumbnails") and component.get("id"))
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
            
            if component.get("thumbnails") and component.get("id"):
                component["thumbnails"] = self.__enhanceThumbnails(component["thumbnails"], component["id"], search_api_data)
            
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
            if self.enableHTML:
                responseSource = self.HTMLresponseSource
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
                needs_search_data = not component["publishedTime"] or (component.get("thumbnails") and component.get("id"))
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
            
            if component.get("thumbnails") and component.get("id"):
                component["thumbnails"] = await self.__enhanceThumbnailsAsync(component["thumbnails"], component["id"], search_api_data)
            
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

import copy
import json
import re
from typing import Iterable, Mapping, TypeVar, Union, List, Optional
from urllib.parse import urlencode

import httpx

from youtubesearchpython.core.constants import *
from youtubesearchpython.core.exceptions import YouTubeParseError, YouTubeRequestError
from youtubesearchpython.core.requests import RequestCore

K=TypeVar("K")
T=TypeVar("T")

class PlaylistCore(RequestCore):
    playlistComponent=None
    result=None
    continuationKey=None

    def __init__(self,playlistLink:str,componentMode:str,resultMode:int,timeout:Optional[int]):
        super().__init__(timeout=timeout)
        self.componentMode=componentMode
        self.resultMode=resultMode
        self.timeout=timeout
        self.url=playlistLink

    def post_processing(self):
        self.__parseSource()
        self.__getComponents()
        self.result=json.dumps(self.playlistComponent,indent=4) if self.resultMode==ResultMode.json else self.playlistComponent

    def sync_create(self):
        statusCode=self.__makeRequest()
        if statusCode==200:self.post_processing()
        else:raise YouTubeRequestError(f"Invalid status code {statusCode} for playlist request")

    async def async_create(self):
        statusCode=await self.__makeAsyncRequest()
        if statusCode==200:self.post_processing()
        else:raise YouTubeRequestError(f"Invalid status code {statusCode} for playlist async request")

    def next_post_processing(self):
        self.__parseSource()
        self.__getNextComponents()
        self.result=json.dumps(self.playlistComponent,indent=4) if self.resultMode==ResultMode.json else self.playlistComponent

    def _next(self):
        self.prepare_next_request()
        if self.continuationKey:
            response=self.syncPostRequest()
            self.response=response.text
            if response.status_code==200:self.next_post_processing()
            else:raise YouTubeRequestError(f"Invalid status code {response.status_code} for playlist next request")

    async def _async_next(self):
        if self.continuationKey:
            self.prepare_next_request()
            response=await self.asyncPostRequest()
            self.response=response.text
            if response.status_code==200:self.next_post_processing()
            else:raise YouTubeRequestError(f"Invalid status code {response.status_code} for playlist async next request")
        else:await self.async_create()

    def prepare_first_request(self):
        self.url=self.url.strip("/")
        if "youtube.com" in self.url or "youtu.be" in self.url:
            match=re.search(r"(?<=list=)([a-zA-Z0-9+/=_-]+)",self.url)
            playlist_id=match.group() if match else self.url
        else:playlist_id=self.url
        browseId="VL"+playlist_id if not playlist_id.startswith("VL") else playlist_id
        self.playlistId=playlist_id
        self.url="https://www.youtube.com/youtubei/v1/browse?"+urlencode({"key":searchKey})
        self.data={"browseId":browseId}
        self.data.update(copy.deepcopy(requestPayload))

    def __makeRequest(self)->int:
        self.prepare_first_request()
        request=self.syncPostRequest()
        self.response=request.text
        return request.status_code

    async def __makeAsyncRequest(self)->int:
        self.prepare_first_request()
        request=await self.asyncPostRequest()
        self.response=request.text
        return request.status_code

    def prepare_next_request(self):
        requestBody=copy.deepcopy(requestPayload)
        requestBody["continuation"]=self.continuationKey
        self.data=requestBody
        self.url="https://www.youtube.com/youtubei/v1/browse?"+urlencode({"key":searchKey})

    def __makeNextRequest(self)->int:
        response=self.syncPostRequest()
        try:
            self.response=response.text
            return response.status_code
        except (AttributeError,httpx.RequestError) as e:
            raise YouTubeRequestError(f"Failed to make playlist request: {e}")
        except Exception as e:
            raise YouTubeRequestError(f"Unexpected error making playlist request: {e}")

    def __parseSource(self)->None:
        try:self.responseSource=json.loads(self.response)
        except json.JSONDecodeError as e:raise YouTubeParseError(f"Failed to parse JSON response for playlist: {e}")
        except Exception as e:raise YouTubeParseError(f"Failed to parse YouTube playlist response: {e}")


    def __getComponents(self)->None:
        has_sidebar="sidebar" in self.responseSource
        if has_sidebar:
            sidebar=self.responseSource["sidebar"]["playlistSidebarRenderer"]["items"]
            inforenderer=sidebar[0]["playlistSidebarPrimaryInfoRenderer"]
            channel_details_available=len(sidebar)>1
            channelrenderer=sidebar[1]["playlistSidebarSecondaryInfoRenderer"]["videoOwner"]["videoOwnerRenderer"] if channel_details_available else None
        else:
            inforenderer={}
            channelrenderer=None
            channel_details_available=False
        videorenderer=[]
        stack=[self.responseSource]
        while stack:
            current=stack.pop()
            if isinstance(current,dict):
                renderer=current.get("playlistVideoListRenderer")
                if isinstance(renderer,dict):
                    contents=renderer.get("contents")
                    if isinstance(contents,list) and contents:
                        videorenderer=contents
                        break
                stack.extend(current.values())
            elif isinstance(current,list):stack.extend(current)
        videos=[]
        seen=set()
        for item in videorenderer:
            try:
                video=item.get("playlistVideoRenderer")
                if not isinstance(video,dict):continue
                video_id=self.__getValue(video,["videoId"])
                if not video_id or video_id in seen:continue
                seen.add(video_id)
                relative_url=self.__getValue(video,["navigationEndpoint","commandMetadata","webCommandMetadata","url"])
                channel_base=["shortBylineText","runs",0,"navigationEndpoint","browseEndpoint"]
                videos.append({
                    "id":video_id,
                    "thumbnails":self.__getValue(video,["thumbnail","thumbnails"]),
                    "title":self.__getValue(video,["title","runs",0,"text"]),
                    "channel":{
                        "name":self.__getValue(video,["shortBylineText","runs",0,"text"]),
                        "id":self.__getValue(video,channel_base+["browseId"]),
                        "link":self.__getValue(video,channel_base+["canonicalBaseUrl"])
                    },
                    "duration":self.__getValue(video,["lengthText","simpleText"]),
                    "accessibility":{
                        "title":self.__getValue(video,["title","accessibility","accessibilityData","label"]),
                        "duration":self.__getValue(video,["lengthText","accessibility","accessibilityData","label"])
                    },
                    "link":"https://www.youtube.com"+relative_url if relative_url else "https://www.youtube.com/watch?v="+video_id,
                    "isPlayable":self.__getValue(video,["isPlayable"])
                })
            except (KeyError,AttributeError,IndexError,TypeError):continue
        stack=[self.responseSource]
        while stack:
            current=stack.pop()
            if isinstance(current,dict):
                lockup=current.get("lockupViewModel")
                if isinstance(lockup,dict):
                    video_id=lockup.get("contentId")
                    if not isinstance(video_id,str) or len(video_id)!=11:
                        video_id=None
                        inner=[lockup]
                        while inner and not video_id:
                            node=inner.pop()
                            if isinstance(node,dict):
                                candidate=node.get("videoId")
                                if isinstance(candidate,str) and len(candidate)==11:
                                    video_id=candidate
                                    break
                                inner.extend(node.values())
                            elif isinstance(node,list):inner.extend(node)
                    if video_id and video_id not in seen:
                        seen.add(video_id)
                        metadata=self.__getValue(lockup,["metadata","lockupMetadataViewModel"]) or {}
                        title=self.__getValue(metadata,["title","content"])
                        if not title:title=self.__getValue(metadata,["title","runs",0,"text"])
                        thumbnails=self.__getValue(lockup,["contentImage","thumbnailViewModel","image","sources"])
                        if not thumbnails:thumbnails=self.__getValue(lockup,["contentImage","thumbnailViewModel","thumbnail","thumbnails"])
                        duration=None
                        metadata_rows=self.__getValue(metadata,["metadata","contentMetadataViewModel","metadataRows"]) or []
                        for row in metadata_rows:
                            parts=self.__getValue(row,["metadataParts"]) or []
                            for part in parts:
                                text=self.__getValue(part,["text","content"])
                                if isinstance(text,str) and re.fullmatch(r"\d{1,2}:\d{2}(?::\d{2})?",text):
                                    duration=text
                                    break
                            if duration:break
                        videos.append({
                            "id":video_id,
                            "thumbnails":thumbnails,
                            "title":title,
                            "channel":{"name":None,"id":None,"link":None},
                            "duration":duration,
                            "accessibility":{"title":title,"duration":duration},
                            "link":"https://www.youtube.com/watch?v="+video_id,
                            "isPlayable":True
                        })
                stack.extend(current.values())
            elif isinstance(current,list):stack.extend(current)
        if not has_sidebar and not videos:
            if getattr(self,"playlistId","").upper().startswith("RD"):
                raise YouTubeParseError("Could not parse this playlist: auto-generated Mix/Radio playlists are not supported.")
            raise YouTubeParseError("Could not parse this playlist: no sidebar and no video list found.")
        playlistElement={
            "info":{
                "id":self.__getValue(inforenderer,["title","runs",0,"navigationEndpoint","watchEndpoint","playlistId"]) or getattr(self,"playlistId",None),
                "thumbnails":self.__getValue(inforenderer,["thumbnailRenderer","playlistVideoThumbnailRenderer","thumbnail","thumbnails"]),
                "title":self.__getValue(inforenderer,["title","runs",0,"text"]),
                "videoCount":self.__getValue(inforenderer,["stats",0,"runs",0,"text"]),
                "viewCount":self.__getValue(inforenderer,["stats",1,"simpleText"]),
                "link":self.__getValue(self.responseSource,["microformat","microformatDataRenderer","urlCanonical"]),
                "channel":{
                    "id":self.__getValue(channelrenderer,["title","runs",0,"navigationEndpoint","browseEndpoint","browseId"]) if channel_details_available else None,
                    "name":self.__getValue(channelrenderer,["title","runs",0,"text"]) if channel_details_available else None,
                    "detailsAvailable":channel_details_available,
                    "link":"https://www.youtube.com"+self.__getValue(channelrenderer,["title","runs",0,"navigationEndpoint","browseEndpoint","canonicalBaseUrl"]) if channel_details_available and self.__getValue(channelrenderer,["title","runs",0,"navigationEndpoint","browseEndpoint","canonicalBaseUrl"]) else None,
                    "thumbnails":self.__getValue(channelrenderer,["thumbnail","thumbnails"]) if channel_details_available else None
                }
            },
            "videos":videos
        }
        if self.componentMode=="getInfo":self.playlistComponent=playlistElement["info"]
        elif self.componentMode=="getVideos":self.playlistComponent={"videos":videos}
        else:self.playlistComponent=playlistElement
        self.continuationKey=self.__getValue(videorenderer,[-1,"continuationItemRenderer","continuationEndpoint","continuationCommand","token"]) if videorenderer else None

    def __getNextComponents(self)->None:
        self.continuationKey=None
        playlistComponent={"videos":[]}
        continuationElements=self.__getValue(self.responseSource,["onResponseReceivedActions",0,"appendContinuationItemsAction","continuationItems"])
        if continuationElements is None:return
        for videoElement in continuationElements:
            if playlistVideoKey in videoElement:
                videoComponent={
                    "id":self.__getValue(videoElement,[playlistVideoKey,"videoId"]),
                    "title":self.__getValue(videoElement,[playlistVideoKey,"title","runs",0,"text"]),
                    "thumbnails":self.__getValue(videoElement,[playlistVideoKey,"thumbnail","thumbnails"]),
                    "link":"https://www.youtube.com"+self.__getValue(videoElement,[playlistVideoKey,"navigationEndpoint","commandMetadata","webCommandMetadata","url"]),
                    "channel":{
                        "name":self.__getValue(videoElement,[playlistVideoKey,"shortBylineText","runs",0,"text"]),
                        "id":self.__getValue(videoElement,[playlistVideoKey,"shortBylineText","runs",0,"navigationEndpoint","browseEndpoint","browseId"]),
                        "link":"https://www.youtube.com"+self.__getValue(videoElement,[playlistVideoKey,"shortBylineText","runs",0,"navigationEndpoint","browseEndpoint","canonicalBaseUrl"])
                    },
                    "duration":self.__getValue(videoElement,[playlistVideoKey,"lengthText","simpleText"]),
                    "accessibility":{
                        "title":self.__getValue(videoElement,[playlistVideoKey,"title","accessibility","accessibilityData","label"]),
                        "duration":self.__getValue(videoElement,[playlistVideoKey,"lengthText","accessibility","accessibilityData","label"])
                    }
                }
                playlistComponent["videos"].append(videoComponent)
            self.continuationKey=self.__getValue(videoElement,continuationKeyPath)
        self.playlistComponent["videos"].extend(playlistComponent["videos"])

    def __getPlaylistComponent(self,element:dict,mode:str)->dict:
        playlistComponent={}
        if mode in ["getInfo",None]:
            for infoElement in element["info"]:
                if playlistPrimaryInfoKey in infoElement:
                    component={
                        "id":self.__getValue(infoElement,[playlistPrimaryInfoKey,"title","runs",0,"navigationEndpoint","watchEndpoint","playlistId"]),
                        "title":self.__getValue(infoElement,[playlistPrimaryInfoKey,"title","runs",0,"text"]),
                        "videoCount":self.__getValue(infoElement,[playlistPrimaryInfoKey,"stats",0,"runs",0,"text"]),
                        "viewCount":self.__getValue(infoElement,[playlistPrimaryInfoKey,"stats",1,"simpleText"]),
                        "thumbnails":self.__getValue(infoElement,[playlistPrimaryInfoKey,"thumbnailRenderer","playlistVideoThumbnailRenderer","thumbnail"])
                    }
                    if not component["thumbnails"]:
                        component["thumbnails"]=self.__getValue(infoElement,[playlistPrimaryInfoKey,"thumbnailRenderer","playlistCustomThumbnailRenderer","thumbnail","thumbnails"])
                    component["link"]="https://www.youtube.com/playlist?list="+component["id"]
                    playlistComponent.update(component)
                if playlistSecondaryInfoKey in infoElement:
                    component={"channel":{
                        "name":self.__getValue(infoElement,[playlistSecondaryInfoKey,"videoOwner","videoOwnerRenderer","title","runs",0,"text"]),
                        "id":self.__getValue(infoElement,[playlistSecondaryInfoKey,"videoOwner","videoOwnerRenderer","title","runs",0,"navigationEndpoint","browseEndpoint","browseId"]),
                        "thumbnails":self.__getValue(infoElement,[playlistSecondaryInfoKey,"videoOwner","videoOwnerRenderer","thumbnail","thumbnails"])
                    }}
                    component["channel"]["link"]="https://www.youtube.com/channel/"+component["channel"]["id"]
                    playlistComponent.update(component)
        if mode in ["getVideos",None]:
            self.continuationKey=None
            playlistComponent["videos"]=[]
            for videoElement in element["videos"]:
                if playlistVideoKey in videoElement:
                    videoComponent={
                        "id":self.__getValue(videoElement,[playlistVideoKey,"videoId"]),
                        "title":self.__getValue(videoElement,[playlistVideoKey,"title","runs",0,"text"]),
                        "thumbnails":self.__getValue(videoElement,[playlistVideoKey,"thumbnail","thumbnails"]),
                        "channel":{
                            "name":self.__getValue(videoElement,[playlistVideoKey,"shortBylineText","runs",0,"text"]),
                            "id":self.__getValue(videoElement,[playlistVideoKey,"shortBylineText","runs",0,"navigationEndpoint","browseEndpoint","browseId"])
                        },
                        "duration":self.__getValue(videoElement,[playlistVideoKey,"lengthText","simpleText"]),
                        "accessibility":{
                            "title":self.__getValue(videoElement,[playlistVideoKey,"title","accessibility","accessibilityData","label"]),
                            "duration":self.__getValue(videoElement,[playlistVideoKey,"lengthText","accessibility","accessibilityData","label"])
                        }
                    }
                    videoComponent["link"]="https://www.youtube.com/watch?v="+videoComponent["id"]
                    videoComponent["channel"]["link"]="https://www.youtube.com/channel/"+videoComponent["channel"]["id"]
                    playlistComponent["videos"].append(videoComponent)
                if continuationItemKey in videoElement:self.continuationKey=self.__getValue(videoElement,continuationKeyPath)
        return playlistComponent

    def __result(self,mode:int)->Union[dict,str]:
        if mode==ResultMode.dict:return self.playlistComponent
        if mode==ResultMode.json:return json.dumps(self.playlistComponent,indent=4)

    def __getValue(self,source:dict,path:Iterable[str])->Union[str,int,dict,None]:
        value=source
        for key in path:
            if value is None:return None
            if isinstance(key,str):
                if isinstance(value,dict) and key in value:value=value[key]
                else:return None
            elif isinstance(key,int):
                if isinstance(value,(list,tuple)) and value:
                    try:value=value[key]
                    except IndexError:return None
                else:return None
        return value

    def __getAllWithKey(self,source:Iterable[Mapping[K,T]],key:K)->Iterable[T]:
        if not source:return
        for item in source:
            if item and key in item:yield item[key]

    def __getValueEx(self,source:dict,path:List[str])->Iterable[Union[str,int,dict,None]]:
        if not path:
            yield source
            return
        key=path[0]
        upcoming=path[1:]
        if key is None:
            following_key=upcoming[0]
            upcoming=upcoming[1:]
            if following_key is None:raise ValueError("Cannot search for a key twice consecutive or at the end with no key given")
            values=self.__getAllWithKey(source,following_key)
            for val in values:yield from self.__getValueEx(val,path=upcoming)
        else:
            val=self.__getValue(source,path=[key])
            yield from self.__getValueEx(val,path=upcoming)

    def __getFirstValue(self,source:dict,path:Iterable[str])->Union[str,int,dict,list,None]:
        for val in self.__getValueEx(source,list(path)):
            if val is not None:return val
        return None

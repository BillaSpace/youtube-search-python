import re
from typing import Union, List
from youtubesearchpython.core.constants import *
from urllib.parse import urlparse, parse_qs


def getValue(source: dict, path: List[Union[str, int]]) -> Union[str, int, dict, None]:
    value = source

    for key in path:
        if value is None:
            return None

        if isinstance(key, str):
            if not isinstance(value, dict):
                return None
            value = value.get(key)
            if value is None:
                return None

        elif isinstance(key, int):
            if not isinstance(value, (list, tuple)):
                return None
            if key < 0 or key >= len(value):
                return None
            value = value[key]

        else:
            return None
            
    return value


def getVideoId(videoLink: str) -> str:
    try:
        parsed = urlparse(videoLink)
        host = (parsed.netloc or "").lower()

        if "youtu.be" in host:
            path = parsed.path.rstrip("/")
            if path:
                return path.split("/")[-1]

        if "youtube" in host or "youtube-nocookie" in host:
            qs = parse_qs(parsed.query)

            if "v" in qs and qs["v"]:
                return qs["v"][0]

            parts = [p for p in parsed.path.split("/") if p]

            for i, p in enumerate(parts):
                if p in ("embed", "v", "live") and i + 1 < len(parts):
                    return parts[i + 1]

            if parts:
                return parts[-1]
        core = videoLink.split("?")[0].split("#")[0].rstrip("/")
        if "/" in core:
            return core.split("/")[-1]
        return core

    except Exception:
        return videoLink


class ComponentHandler:
    def _getVideoComponent(self, element: dict, shelfTitle: str = None) -> dict:
        video = element[videoElementKey]
        component = {
            'type':                           'video',
            'id':                              self._getValue(video, ['videoId']),
            'title':                           self._getValue(video, ['title', 'runs', 0, 'text']),
            'publishedTime':                   self._getValue(video, ['publishedTimeText', 'simpleText']),
            'duration':                        self._getValue(video, ['lengthText', 'simpleText']),
            'viewCount': {
                'text':                        self._getValue(video, ['viewCountText', 'simpleText']),
                'short':                       self._getValue(video, ['shortViewCountText', 'simpleText']),
            },
            'thumbnails':                      self._getValue(video, ['thumbnail', 'thumbnails']),
            'richThumbnail':                   self._getValue(video, ['richThumbnail', 'movingThumbnailRenderer', 'movingThumbnailDetails', 'thumbnails', 0]),
            'descriptionSnippet':              self._getValue(video, ['detailedMetadataSnippets', 0, 'snippetText', 'runs']),
            'channel': {
                'name':                        self._getValue(video, ['ownerText', 'runs', 0, 'text']),
                'id':                          self._getValue(video, ['ownerText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']),
                'thumbnails':                  self._getValue(video, ['channelThumbnailSupportedRenderers', 'channelThumbnailWithLinkRenderer', 'thumbnail', 'thumbnails']),
            },
            'accessibility': {
                'title':                       self._getValue(video, ['title', 'accessibility', 'accessibilityData', 'label']),
                'duration':                    self._getValue(video, ['lengthText', 'accessibility', 'accessibilityData', 'label']),
            },
        }
        component['link'] = 'https://www.youtube.com/watch?v=' + component['id']

        if component['channel']['id']:
            component['channel']['link'] = 'https://www.youtube.com/channel/' + component['channel']['id']

        component['shelfTitle'] = shelfTitle
        return component

    def _getChannelComponent(self, element: dict) -> dict:
        channel = element[channelElementKey]
        component = {
            'type':                           'channel',
            'id':                              self._getValue(channel, ['channelId']),
            'title':                           self._getValue(channel, ['title', 'simpleText']),
            'thumbnails':                      self._getValue(channel, ['thumbnail', 'thumbnails']),
            'videoCount':                      self._getValue(channel, ['videoCountText', 'runs', 0, 'text']),
            'descriptionSnippet':              self._getValue(channel, ['descriptionSnippet', 'runs']),
            'subscribers':                     self._getValue(channel, ['subscriberCountText', 'simpleText']),
        }
        component['link'] = 'https://www.youtube.com/channel/' + component['id']
        return component

    def _getPlaylistComponent(self, element: dict) -> dict:
        playlist = element[playlistElementKey]
        component = {
            'type':                           'playlist',
            'id':                             self._getValue(playlist, ['playlistId']),
            'title':                          self._getValue(playlist, ['title', 'simpleText']),
            'videoCount':                     self._getValue(playlist, ['videoCount']),
            'channel': {
                'name':                       self._getValue(playlist, ['shortBylineText', 'runs', 0, 'text']),
                'id':                         self._getValue(playlist, ['shortBylineText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']),
            },
            'thumbnails':                     self._getValue(playlist, ['thumbnailRenderer', 'playlistVideoThumbnailRenderer', 'thumbnail', 'thumbnails']),
        }
        component['link'] = 'https://www.youtube.com/playlist?list=' + component['id']

        if component['channel']['id']:
            component['channel']['link'] = 'https://www.youtube.com/channel/' + component['channel']['id']

        return component

    def _getLockupComponent(self, element: dict, findVideos: bool, findChannels: bool, findPlaylists: bool) -> dict:
        lockup = self._getValue(element, ["lockupViewModel"])
        if not lockup:
            return None
            
        contentType = self._getValue(lockup, ["contentType"])
        contentId = self._getValue(lockup, ["contentId"])
        
        if contentType == "LOCKUP_CONTENT_TYPE_VIDEO" and findVideos:
            component = {
                'type':                           'video',
                'id':                              contentId,
                'title':                           self._getValue(lockup, ['metadata', 'lockupMetadataViewModel', 'title', 'content']),
                'thumbnails':                      self._getValue(lockup, ['contentImage', 'thumbnailViewModel', 'image', 'sources']),
            }
            component['link'] = 'https://www.youtube.com/watch?v=' + contentId
            return component
            
        if contentType == "LOCKUP_CONTENT_TYPE_PLAYLIST" and findPlaylists:
            component = {
                'type':                           'playlist',
                'id':                             contentId,
                'title':                          self._getValue(lockup, ['metadata', 'lockupMetadataViewModel', 'title', 'content']),
                'thumbnails':                     self._getValue(lockup, ['contentImage', 'collectionThumbnailViewModel', 'primaryThumbnail', 'thumbnailViewModel', 'image', 'sources']),
            }
            component['link'] = 'https://www.youtube.com/playlist?list=' + contentId
            return component
            
        if contentType == "LOCKUP_CONTENT_TYPE_CHANNEL" and findChannels:
            component = {
                'type':                           'channel',
                'id':                             contentId,
                'title':                          self._getValue(lockup, ['metadata', 'lockupMetadataViewModel', 'title', 'content']),
                'thumbnails':                     self._getValue(lockup, ['contentImage', 'thumbnailViewModel', 'image', 'sources']),
            }
            component['link'] = 'https://www.youtube.com/channel/' + contentId
            return component
            
        return None
    
    def _getVideoFromChannelSearch(self, elements: list) -> list:
        channelsearch = []
        for element in elements:
            element = self._getValue(element, ["childVideoRenderer"])
            json = {
                "id":                                    self._getValue(element, ["videoId"]),
                "title":                                 self._getValue(element, ["title", "simpleText"]),
                "uri":                                   self._getValue(element, ["navigationEndpoint", "commandMetadata", "webCommandMetadata", "url"]),
                "duration": {
                    "simpleText":                        self._getValue(element, ["lengthText", "simpleText"]),
                    "text":                              self._getValue(element, ["lengthText", "accessibility", "accessibilityData", "label"])
                }
            }
            channelsearch.append(json)
        return channelsearch
    
    def _getChannelSearchComponent(self, elements: list) -> list:
        channelsearch = []
        for element in elements:
            responsetype = None

            if 'gridPlaylistRenderer' in element:
                element = element['gridPlaylistRenderer']
                responsetype = 'gridplaylist'
            elif 'itemSectionRenderer' in element:
                first_content = element["itemSectionRenderer"]["contents"][0]
                if 'videoRenderer' in first_content:
                    element = first_content['videoRenderer']
                    responsetype = "video"
                elif 'playlistRenderer' in first_content:
                    element = first_content["playlistRenderer"]
                    responsetype = "playlist"
                else:
                    raise ValueError(f'Unexpected first_content {first_content}')
            elif 'continuationItemRenderer' in element:
                continue
            else:
                raise ValueError(f'Unexpected element {element}')
            
            if responsetype == "video":
                json = {
                    "id":                                    self._getValue(element, ["videoId"]),
                    "thumbnails": {
                        "normal":                            self._getValue(element, ["thumbnail", "thumbnails"]),
                        "rich":                              self._getValue(element, ["richThumbnail", "movingThumbnailRenderer", "movingThumbnailDetails", "thumbnails"])
                    },
                    "title":                                 self._getValue(element, ["title", "runs", 0, "text"]),
                    "descriptionSnippet":                    self._getValue(element, ["descriptionSnippet", "runs", 0, "text"]),
                    "uri":                                   self._getValue(element, ["navigationEndpoint", "commandMetadata", "webCommandMetadata", "url"]),
                    "views": {
                        "precise":                           self._getValue(element, ["viewCountText", "simpleText"]),
                        "simple":                            self._getValue(element, ["shortViewCountText", "simpleText"]),
                        "approximate":                       self._getValue(element, ["shortViewCountText", "accessibility", "accessibilityData", "label"])
                    },
                    "duration": {
                        "simpleText":                        self._getValue(element, ["lengthText", "simpleText"]),
                        "text":                              self._getValue(element, ["lengthText", "accessibility", "accessibilityData", "label"])
                    },
                    "published":                             self._getValue(element, ["publishedTimeText", "simpleText"]),
                    "channel": {
                        "name":                              self._getValue(element, ["ownerText", "runs", 0, "text"]),
                        "thumbnails":                        self._getValue(element, ["channelThumbnailSupportedRenderers", "channelThumbnailWithLinkRenderer", "thumbnail", "thumbnails"])
                    },
                    "type":                                  responsetype
                }
            elif responsetype == 'playlist':
                json = {
                    "id":                                    self._getValue(element, ["playlistId"]),
                    "videos":                                self._getVideoFromChannelSearch(self._getValue(element, ["videos"])),
                    "thumbnails": {
                        "normal":                            self._getValue(element, ["thumbnails"]),
                    },
                    "title":                                 self._getValue(element, ["title", "simpleText"]),
                    "uri":                                   self._getValue(element, ["navigationEndpoint", "commandMetadata", "webCommandMetadata", "url"]),
                    "channel": {
                        "name":                              self._getValue(element, ["longBylineText", "runs", 0, "text"]),
                    },
                    "type":                                  responsetype
                }
            else:
                json = {
                    "id":                                    self._getValue(element, ["playlistId"]),
                    "thumbnails": {
                        "normal":                            self._getValue(element, ["thumbnail", "thumbnails", 0]),
                    },
                    "title":                                 self._getValue(element, ["title", "runs", 0, "text"]),
                    "uri":                                   self._getValue(element, ["navigationEndpoint", "commandMetadata", "webCommandMetadata", "url"]),
                    "type":                                  'playlist'
                }
            channelsearch.append(json)
        return channelsearch

    def _getShelfComponent(self, element: dict) -> dict:
        shelf = element[shelfElementKey]
        return {
            'title':                           self._getValue(shelf, ['title', 'simpleText']),
            'elements':                        self._getValue(shelf, ['content', 'verticalListRenderer', 'items']),
        }

    def _getValue(self, source: dict, path: List[str]) -> Union[str, int, dict, None]:
        value = source
        if value is None:
            return None
        for key in path:
            if type(key) is str:
                if isinstance(value, dict) and key in value.keys():
                    value = value[key]
                else:
                    value = None
                    break
            elif type(key) is int:
                if isinstance(value, (list, tuple)) and len(value) > key:
                    value = value[key]
                else:
                    value = None
                    break
        return value

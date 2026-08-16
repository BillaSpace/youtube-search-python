from typing import Union, List
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.utils import get_video_id, normalize_thumbnails


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
            if not isinstance(value, (list, tuple)) or not (-len(value) <= key < len(value)):
                return None
            value = value[key]

        else:
            return None
            
    return value


def getVideoId(videoLink: str) -> str:
    return get_video_id(videoLink)

class ComponentHandler:
    _getValue = staticmethod(getValue)

    def _isLiveVideo(self, video: dict) -> bool:
        for badge in self._getValue(video, ["badges"]) or []:
            style = self._getValue(badge, ["metadataBadgeRenderer", "style"])
            if style == "BADGE_STYLE_TYPE_LIVE_NOW":
                return True
        for overlay in self._getValue(video, ["thumbnailOverlays"]) or []:
            if self._getValue(overlay, ["thumbnailOverlayTimeStatusRenderer", "style"]) == "LIVE":
                return True
        return False

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
            'thumbnails':                      normalize_thumbnails(self._getValue(video, ['thumbnail', 'thumbnails']), self._getValue(video, ['videoId'])),
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
            'isLive':                          self._isLiveVideo(video),
        }
        component['link'] = 'https://www.youtube.com/watch?v=' + component['id'] if component['id'] else None
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
        component['link'] = 'https://www.youtube.com/channel/' + component['id'] if component['id'] else None
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
            'thumbnails':                     normalize_thumbnails(self._getValue(playlist, ['thumbnailRenderer', 'playlistVideoThumbnailRenderer', 'thumbnail', 'thumbnails'])),
        }
        component['link'] = 'https://www.youtube.com/playlist?list=' + component['id'] if component['id'] else None

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
                'thumbnails':                      normalize_thumbnails(self._getValue(lockup, ['contentImage', 'thumbnailViewModel', 'image', 'sources']), contentId),
            }
            component['link'] = 'https://www.youtube.com/watch?v=' + contentId if contentId else None
            return component
            
        if contentType == "LOCKUP_CONTENT_TYPE_PLAYLIST" and findPlaylists:
            component = {
                'type':                           'playlist',
                'id':                             contentId,
                'title':                          self._getValue(lockup, ['metadata', 'lockupMetadataViewModel', 'title', 'content']),
                'thumbnails':                     self._getValue(lockup, ['contentImage', 'collectionThumbnailViewModel', 'primaryThumbnail', 'thumbnailViewModel', 'image', 'sources']),
            }
            component['link'] = 'https://www.youtube.com/playlist?list=' + contentId if contentId else None
            return component
            
        if contentType == "LOCKUP_CONTENT_TYPE_CHANNEL" and findChannels:
            component = {
                'type':                           'channel',
                'id':                             contentId,
                'title':                          self._getValue(lockup, ['metadata', 'lockupMetadataViewModel', 'title', 'content']),
                'thumbnails':                     self._getValue(lockup, ['contentImage', 'thumbnailViewModel', 'image', 'sources']),
            }
            component['link'] = 'https://www.youtube.com/channel/' + contentId if contentId else None
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
        pending = list(elements or [])
        index = 0
        while index < len(pending):
            element = pending[index]
            index += 1
            if not isinstance(element, dict):
                continue
            if "itemSectionRenderer" in element:
                contents = self._getValue(element, ["itemSectionRenderer", "contents"]) or []
                pending[index:index] = contents
                continue
            if "continuationItemRenderer" in element:
                continue
            if "lockupViewModel" in element:
                component = self._getLockupComponent(element, True, False, True)
                if component:
                    channelsearch.append(component)
                continue
            if "videoRenderer" in element:
                video = element["videoRenderer"]
                video_id = self._getValue(video, ["videoId"])
                channelsearch.append({
                    "id": video_id,
                    "thumbnails": {
                        "normal": normalize_thumbnails(self._getValue(video, ["thumbnail", "thumbnails"]), video_id),
                        "rich": self._getValue(video, ["richThumbnail", "movingThumbnailRenderer", "movingThumbnailDetails", "thumbnails"]),
                    },
                    "title": self._getValue(video, ["title", "runs", 0, "text"]),
                    "descriptionSnippet": self._getValue(video, ["descriptionSnippet", "runs", 0, "text"]),
                    "uri": self._getValue(video, ["navigationEndpoint", "commandMetadata", "webCommandMetadata", "url"]),
                    "views": {
                        "precise": self._getValue(video, ["viewCountText", "simpleText"]),
                        "simple": self._getValue(video, ["shortViewCountText", "simpleText"]),
                        "approximate": self._getValue(video, ["shortViewCountText", "accessibility", "accessibilityData", "label"]),
                    },
                    "duration": {
                        "simpleText": self._getValue(video, ["lengthText", "simpleText"]),
                        "text": self._getValue(video, ["lengthText", "accessibility", "accessibilityData", "label"]),
                    },
                    "published": self._getValue(video, ["publishedTimeText", "simpleText"]),
                    "channel": {
                        "name": self._getValue(video, ["ownerText", "runs", 0, "text"]),
                        "thumbnails": self._getValue(video, ["channelThumbnailSupportedRenderers", "channelThumbnailWithLinkRenderer", "thumbnail", "thumbnails"]),
                    },
                    "type": "video",
                })
                continue
            if "playlistRenderer" in element:
                playlist = element["playlistRenderer"]
                channelsearch.append({
                    "id": self._getValue(playlist, ["playlistId"]),
                    "videos": self._getVideoFromChannelSearch(self._getValue(playlist, ["videos"]) or []),
                    "thumbnails": {"normal": self._getValue(playlist, ["thumbnails"])},
                    "title": self._getValue(playlist, ["title", "simpleText"]) or self._getValue(playlist, ["title", "runs", 0, "text"]),
                    "uri": self._getValue(playlist, ["navigationEndpoint", "commandMetadata", "webCommandMetadata", "url"]),
                    "channel": {"name": self._getValue(playlist, ["longBylineText", "runs", 0, "text"])},
                    "type": "playlist",
                })
                continue
            if "gridPlaylistRenderer" in element:
                playlist = element["gridPlaylistRenderer"]
                channelsearch.append({
                    "id": self._getValue(playlist, ["playlistId"]),
                    "thumbnails": {"normal": self._getValue(playlist, ["thumbnail", "thumbnails", 0])},
                    "title": self._getValue(playlist, ["title", "runs", 0, "text"]),
                    "uri": self._getValue(playlist, ["navigationEndpoint", "commandMetadata", "webCommandMetadata", "url"]),
                    "type": "playlist",
                })
        return channelsearch

    def _getShelfComponent(self, element: dict) -> dict:
        shelf = element[shelfElementKey]
        title = self._getValue(shelf, ['title', 'simpleText'])
        if title is None:
            title = self._getValue(shelf, ['title', 'runs', 0, 'text'])
        elements = self._getValue(shelf, ['content', 'verticalListRenderer', 'items'])
        if elements is None:
            elements = self._getValue(shelf, ['content', 'horizontalListRenderer', 'items'])
        return {
            'title':                           title,
            'elements':                        elements or [],
        }


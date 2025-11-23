from typing import List, Union
import json
from youtubesearchpython.handlers.componenthandler import ComponentHandler
from youtubesearchpython.handlers.requesthandler import RequestHandler
from youtubesearchpython.core.constants import *


def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider


class LegacyComponentHandler(RequestHandler, ComponentHandler):
    index = 0

    @overrides(ComponentHandler)
    def _getVideoComponent(self, element: dict, shelfTitle: str = None) -> dict:
        video = element.get(videoElementKey, {}) or {}
        videoId = self.__getValue(video, ['videoId'])
        viewCount = 0
        vc_text = self.__getValue(video, ['viewCountText', 'simpleText']) or ""
        for character in str(vc_text):
            if character.isnumeric():
                viewCount = viewCount * 10 + int(character)
        thumbnails = []
        if videoId:
            modes = ['default', 'hqdefault', 'mqdefault', 'sddefault', 'maxresdefault']
            for mode in modes:
                thumbnails.append('https://img.youtube.com/vi/' + videoId + '/' + mode + '.jpg')
        component = {
            'index':                          self.index,
            'id':                             videoId,
            'link':                           'https://www.youtube.com/watch?v=' + (videoId or ""),
            'title':                          self.__getValue(video, ['title', 'runs', 0, 'text']),
            'channel':                        self.__getValue(video, ['ownerText', 'runs', 0, 'text']),
            'duration':                       self.__getValue(video, ['lengthText', 'simpleText']),
            'views':                          viewCount,
            'thumbnails':                     thumbnails,
            'channeId':                       self.__getValue(video, ['ownerText', 'runs', 0, 'navigationEndpoint', 'browseEndpoint', 'browseId']),
            'publishTime':                    self.__getValue(video, ['publishedTimeText', 'simpleText']),
        }
        self.index += 1
        return component

    @overrides(ComponentHandler)
    def _getPlaylistComponent(self, element: dict) -> dict:
        playlist = element.get(playlistElementKey, {}) or {}
        playlistId = self.__getValue(playlist, ['playlistId'])
        thumbnailVideoId = self.__getValue(playlist, ['navigationEndpoint', 'watchEndpoint', 'videoId'])
        thumbnails = []
        if thumbnailVideoId:
            modes = ['default', 'hqdefault', 'mqdefault', 'sddefault', 'maxresdefault']
            for mode in modes:
                thumbnails.append('https://img.youtube.com/vi/' + thumbnailVideoId + '/' + mode + '.jpg')
        component = {
            'index':                          self.index,
            'id':                             playlistId,
            'link':                           'https://www.youtube.com/playlist?list=' + (playlistId or ""),
            'title':                          self.__getValue(playlist, ['title', 'simpleText']),
            'thumbnails':                     thumbnails,
            'count':                          self.__getValue(playlist, ['videoCount']),
            'channel':                        self.__getValue(playlist, ['shortBylineText', 'runs', 0, 'text']),
        }
        self.index += 1
        return component

    @overrides(ComponentHandler)
    def _getShelfComponent(self, element: dict) -> dict:
        shelf = element.get(shelfElementKey, {}) or {}
        return {
            'title':                          self.__getValue(shelf, ['title', 'simpleText']),
            'elements':                       self.__getValue(shelf, ['content', 'verticalListRenderer', 'items']),
        }

    def __getValue(self, component: Union[dict, list, None], path: List[Union[str, int]]) -> Union[str, int, dict, list, None]:
        # Preserve original behavior of returning 'LIVE' for missing values,
        # but guard against None and wrong types so it won't raise.
        value = component
        for key in path:
            if value is None:
                return 'LIVE'
            if isinstance(key, str):
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return 'LIVE'
            elif isinstance(key, int):
                if isinstance(value, list) and len(value) > abs(key):
                    try:
                        value = value[key]
                    except Exception:
                        return 'LIVE'
                else:
                    return 'LIVE'
            else:
                return 'LIVE'
        return value


class LegacySearchInternal(LegacyComponentHandler):
    exception = False
    resultComponents = []
    responseSource = []

    def __init__(self, keyword, offset, mode, max_results, language, region):
        self.page = offset
        self.query = keyword
        self.mode = mode
        self.limit = max_results
        self.language = language
        self.region = region
        self.continuationKey = None
        self.timeout = None

    def result(self) -> Union[str, dict, list, None]:
        '''Returns the search result.

        Returns:
            Union[str, dict, list, None]: Returns JSON, list or dictionary & None in case of any exception.
        '''
        if self.exception or len(self.resultComponents) == 0:
            return None
        else:
            if self.mode == 'dict':
                return {'search_result': self.resultComponents}
            elif self.mode == 'json':
                return json.dumps({'search_result': self.resultComponents}, indent = 4)
            elif self.mode == 'list':
                result = []
                for component in self.resultComponents:
                    listComponent = []
                    for key in component.keys():
                        listComponent.append(component[key])
                    result.append(listComponent)
                return result


class SearchVideos(LegacySearchInternal):
    '''
    DEPRECATED
    ----------
    Use `VideosSearch` instead.

    Searches for playlists in YouTube.

    Args:
        keyword (str): Sets the search query.
        offset (int, optional): Sets the search result page number. Defaults to 1.
        mode (str, optional): Sets the result type, can be 'json', 'dict' or 'list'. Defaults to 'json'. 
        max_results (int, optional): Sets limit to the number of results. Defaults to 20.
        language (str, optional): Sets the result language. Defaults to 'en-US'.
        region (str, optional): Sets the result region. Defaults to 'US'.

    Examples:
        Calling `result` method gives the search result.
    '''
    def __init__(self, keyword, offset = 1, mode = 'json', max_results = 20, language = 'en', region = 'US'):
        super().__init__(keyword, offset, mode, max_results, language, region)
        self.searchPreferences = 'EgIQAQ%3D%3D'
        self._makeRequest()
        self._parseSource()
        self.__makeComponents()

    def __makeComponents(self) -> None:
        self.resultComponents = []
        for element in self.responseSource or []:
            if videoElementKey in element.keys():
                self.resultComponents.append(self._getVideoComponent(element))
            if shelfElementKey in element.keys():
                elements = self._getShelfComponent(element).get('elements') if isinstance(self._getShelfComponent(element), dict) else None
                for shelfElement in elements or []:
                    self.resultComponents.append(self._getVideoComponent(shelfElement))
            if len(self.resultComponents) >= self.limit:
                break


class SearchPlaylists(LegacySearchInternal):
    '''
    DEPRECATED
    ----------
    Use `PlaylistsSearch` instead.
    '''
    def __init__(self, keyword, offset = 1, mode = 'json', max_results = 20, language = 'en', region = 'US'):
        super().__init__(keyword, offset, mode, max_results, language, region)
        self.searchPreferences = 'EgIQAw%3D%3D'
        self._makeRequest()
        self._parseSource()
        self.__makeComponents()

    def __makeComponents(self) -> None:
        self.resultComponents = []
        for element in self.responseSource or []:
            if playlistElementKey in element.keys():
                self.resultComponents.append(self._getPlaylistComponent(element))
            if len(self.resultComponents) >= self.limit:
                break

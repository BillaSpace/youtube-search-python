import json
from typing import Optional
from urllib.parse import urlencode

from youtubesearchpython.core.componenthandler import getValue
from youtubesearchpython.core.constants import ResultMode, searchKey
from youtubesearchpython.core.requests import YouTubeParseError, YouTubeRequestError
from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.utils import get_playlist_id, normalize_thumbnails


class PlaylistCore(RequestCore):
    def __init__(self, playlistLink: str, componentMode: str, resultMode: int, timeout: Optional[int]):
        super().__init__(timeout=timeout)
        self.playlistLink = playlistLink
        self.componentMode = componentMode
        self.resultMode = resultMode
        self.playlistId = get_playlist_id(playlistLink)
        self.continuationKey = None
        self.response = None
        self.responseSource = None
        self.playlistComponent = None
        self.result = None
        self._endpoint = "browse"

    def _body(self, **values) -> dict:
        body = self.buildInnertubeBody()
        body.update(values)
        return body

    def prepare_first_request(self) -> None:
        if not self.playlistId:
            raise YouTubeRequestError("Playlist ID is empty")
        is_mix = self.playlistId.startswith("RD")
        self._endpoint = "next" if is_mix else "browse"
        self.url = f"https://www.youtube.com/youtubei/v1/{self._endpoint}?" + urlencode({"key": searchKey})
        if is_mix:
            seed = self.playlistId[2:]
            payload = {"playlistId": self.playlistId}
            if len(seed) == 11:
                payload["videoId"] = seed
            self.data = self._body(**payload)
        else:
            browse_id = self.playlistId if self.playlistId.startswith("VL") else "VL" + self.playlistId
            self.data = self._body(browseId=browse_id)

    def prepare_next_request(self) -> None:
        self.url = f"https://www.youtube.com/youtubei/v1/{self._endpoint}?" + urlencode({"key": searchKey})
        self.data = self._body(continuation=self.continuationKey)

    def _decode(self, response) -> dict:
        if response.status_code != 200:
            raise YouTubeRequestError(f"Invalid status code {response.status_code} for playlist request")
        try:
            return response.json()
        except (ValueError, json.JSONDecodeError) as exc:
            raise YouTubeParseError(f"Failed to parse JSON response for playlist: {exc}") from exc

    def sync_create(self):
        self.prepare_first_request()
        self.responseSource = self._decode(self.syncPostRequest())
        self._process(first=True)

    async def async_create(self):
        self.prepare_first_request()
        self.responseSource = self._decode(await self.asyncPostRequest())
        self._process(first=True)

    def _next(self):
        if not self.continuationKey:
            return self.result
        self.prepare_next_request()
        self.responseSource = self._decode(self.syncPostRequest())
        self._process(first=False)
        return self.result

    async def _async_next(self):
        if not self.continuationKey:
            return self.result
        self.prepare_next_request()
        self.responseSource = self._decode(await self.asyncPostRequest())
        self._process(first=False)
        return self.result

    @staticmethod
    def _walk(source):
        stack = [source]
        while stack:
            node = stack.pop()
            yield node
            if isinstance(node, dict):
                stack.extend(reversed(list(node.values())))
            elif isinstance(node, list):
                stack.extend(reversed(node))

    @classmethod
    def _find_first(cls, source, key):
        for node in cls._walk(source):
            if isinstance(node, dict) and isinstance(node.get(key), dict):
                return node[key]
        return None

    @staticmethod
    def _channel(video: dict) -> dict:
        base = ["shortBylineText", "runs", 0, "navigationEndpoint", "browseEndpoint"]
        channel_id = getValue(video, base + ["browseId"])
        base_url = getValue(video, base + ["canonicalBaseUrl"])
        return {
            "name": getValue(video, ["shortBylineText", "runs", 0, "text"]),
            "id": channel_id,
            "link": "https://www.youtube.com" + base_url if base_url else (f"https://www.youtube.com/channel/{channel_id}" if channel_id else None),
        }

    @classmethod
    def _video_from_playlist_renderer(cls, video: dict) -> Optional[dict]:
        video_id = getValue(video, ["videoId"])
        if not video_id:
            return None
        relative_url = getValue(video, ["navigationEndpoint", "commandMetadata", "webCommandMetadata", "url"])
        return {
            "id": video_id,
            "thumbnails": normalize_thumbnails(getValue(video, ["thumbnail", "thumbnails"]), video_id),
            "title": getValue(video, ["title", "runs", 0, "text"]) or getValue(video, ["title", "simpleText"]),
            "channel": cls._channel(video),
            "duration": getValue(video, ["lengthText", "simpleText"]),
            "accessibility": {
                "title": getValue(video, ["title", "accessibility", "accessibilityData", "label"]),
                "duration": getValue(video, ["lengthText", "accessibility", "accessibilityData", "label"]),
            },
            "link": "https://www.youtube.com" + relative_url if relative_url else f"https://www.youtube.com/watch?v={video_id}",
            "isPlayable": getValue(video, ["isPlayable"]),
        }

    @classmethod
    def _video_from_panel_renderer(cls, video: dict) -> Optional[dict]:
        video_id = getValue(video, ["videoId"])
        if not video_id:
            return None
        byline = getValue(video, ["longBylineText", "runs", 0]) or getValue(video, ["shortBylineText", "runs", 0]) or {}
        channel_id = getValue(byline, ["navigationEndpoint", "browseEndpoint", "browseId"])
        return {
            "id": video_id,
            "thumbnails": normalize_thumbnails(getValue(video, ["thumbnail", "thumbnails"]), video_id),
            "title": getValue(video, ["title", "simpleText"]) or getValue(video, ["title", "runs", 0, "text"]),
            "channel": {
                "name": getValue(byline, ["text"]),
                "id": channel_id,
                "link": f"https://www.youtube.com/channel/{channel_id}" if channel_id else None,
            },
            "duration": getValue(video, ["lengthText", "simpleText"]),
            "accessibility": {
                "title": getValue(video, ["title", "accessibility", "accessibilityData", "label"]),
                "duration": getValue(video, ["lengthText", "accessibility", "accessibilityData", "label"]),
            },
            "link": f"https://www.youtube.com/watch?v={video_id}",
            "isPlayable": getValue(video, ["isPlayable"]) if getValue(video, ["isPlayable"]) is not None else not bool(getValue(video, ["unplayableText"])),
        }

    def _extract_videos(self) -> list:
        videos = []
        seen = set()
        for node in self._walk(self.responseSource):
            if not isinstance(node, dict):
                continue
            renderer = node.get("playlistVideoRenderer")
            if isinstance(renderer, dict):
                component = self._video_from_playlist_renderer(renderer)
            else:
                renderer = node.get("playlistPanelVideoRenderer")
                component = self._video_from_panel_renderer(renderer) if isinstance(renderer, dict) else None
            if component and component["id"] not in seen:
                seen.add(component["id"])
                videos.append(component)
        return videos

    def _extract_continuation(self) -> Optional[str]:
        panel = self._find_first(self.responseSource, "playlistPanelRenderer")
        for continuation in (panel or {}).get("continuations") or []:
            token = getValue(continuation, ["nextRadioContinuationData", "continuation"]) or getValue(continuation, ["nextContinuationData", "continuation"])
            if token:
                return token
        if self.playlistId.startswith("RD"):
            for node in self._walk(self.responseSource):
                if not isinstance(node, dict):
                    continue
                radio = node.get("nextRadioContinuationData")
                if isinstance(radio, dict) and radio.get("continuation"):
                    return radio["continuation"]
            return None
        video_list = self._find_first(self.responseSource, "playlistVideoListRenderer")
        for item in (video_list or {}).get("contents") or []:
            token = getValue(item, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])
            if token:
                return token
        for node in self._walk(self.responseSource):
            if isinstance(node, dict):
                token = getValue(node, ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"])
                if token:
                    return token
        return None

    def _extract_info(self, videos: list) -> dict:
        sidebar = self._find_first(self.responseSource, "playlistSidebarRenderer")
        primary = secondary = None
        if sidebar:
            items = sidebar.get("items") or []
            primary = getValue(items, [0, "playlistSidebarPrimaryInfoRenderer"])
            secondary = getValue(items, [1, "playlistSidebarSecondaryInfoRenderer", "videoOwner", "videoOwnerRenderer"])
        panel = self._find_first(self.responseSource, "playlistPanelRenderer")
        title = getValue(primary, ["title", "runs", 0, "text"]) if primary else None
        if not title and panel:
            panel_title = panel.get("title")
            title = panel_title if isinstance(panel_title, str) else getValue(panel, ["title", "simpleText"]) or getValue(panel, ["title", "runs", 0, "text"])
        channel_id = getValue(secondary, ["title", "runs", 0, "navigationEndpoint", "browseEndpoint", "browseId"]) if secondary else None
        channel_name = getValue(secondary, ["title", "runs", 0, "text"]) if secondary else None
        thumbnails = getValue(primary, ["thumbnailRenderer", "playlistVideoThumbnailRenderer", "thumbnail", "thumbnails"]) if primary else None
        if not thumbnails and videos:
            thumbnails = videos[0].get("thumbnails")
        canonical = getValue(self.responseSource, ["microformat", "microformatDataRenderer", "urlCanonical"])
        return {
            "id": self.playlistId,
            "thumbnails": normalize_thumbnails(thumbnails),
            "title": title,
            "videoCount": getValue(primary, ["stats", 0, "runs", 0, "text"]) if primary else (str(len(videos)) if videos else None),
            "viewCount": getValue(primary, ["stats", 1, "simpleText"]) if primary else None,
            "link": canonical or f"https://www.youtube.com/playlist?list={self.playlistId}",
            "channel": {
                "id": channel_id,
                "name": channel_name,
                "detailsAvailable": bool(secondary),
                "link": f"https://www.youtube.com/channel/{channel_id}" if channel_id else None,
                "thumbnails": getValue(secondary, ["thumbnail", "thumbnails"]) if secondary else None,
            },
        }

    def _process(self, first: bool) -> None:
        videos = self._extract_videos()
        self.continuationKey = self._extract_continuation()
        if first:
            if not videos and not self._find_first(self.responseSource, "playlistSidebarRenderer") and not self._find_first(self.responseSource, "playlistPanelRenderer"):
                raise YouTubeParseError("Could not parse playlist response")
            info = self._extract_info(videos)
            if self.componentMode == "getInfo":
                self.playlistComponent = info
            elif self.componentMode == "getVideos":
                self.playlistComponent = {"videos": videos}
            else:
                self.playlistComponent = {"info": info, "videos": videos}
        else:
            if self.componentMode == "getInfo":
                return
            if self.playlistComponent is None:
                self.playlistComponent = {"videos": videos}
            elif isinstance(self.playlistComponent, dict):
                current = self.playlistComponent.setdefault("videos", [])
                seen = {item.get("id") for item in current if isinstance(item, dict)}
                current.extend(item for item in videos if item.get("id") not in seen)
        self.result = json.dumps(self.playlistComponent, indent=4) if self.resultMode == ResultMode.json else self.playlistComponent

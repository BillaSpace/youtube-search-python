import re
import json
import asyncio
import xml.etree.ElementTree as ET
from html import unescape
from pathlib import Path
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from typing import Dict, List, Optional

from youtubesearchpython.core.requests import RequestCore, _get_sync_client
from youtubesearchpython.core.componenthandler import getVideoId
from youtubesearchpython.core.cookies import (
    resolve_cookie_file,
    cleanup_cookie_file,
    apply_cookies_to_client,
)


class TranscriptCore(RequestCore):
    def __init__(self, videoLink: str, key: str = None):
        super().__init__()
        self.videoLink = videoLink
        self.video_id = getVideoId(videoLink)
        self.key = key
        self.result = {"segments": [], "languages": []}

    def _select_track(self, tracks: List[Dict]) -> Optional[Dict]:
        if not tracks:
            return None
        if self.key:
            key = self.key.lower()
            for track in tracks:
                if (track.get("languageCode") or "").lower() == key:
                    return track
            for track in tracks:
                if (track.get("languageCode") or "").lower().split("-")[0] == key.split("-")[0]:
                    return track
            return None
        for code in ("hi", "en", "ur"):
            for track in tracks:
                if track.get("languageCode") == code:
                    return track
        return tracks[0]

    def _languages(self, tracks: List[Dict]) -> List[Dict]:
        result = []
        for track in tracks:
            name = track.get("name") or {}
            language = name.get("simpleText") or "".join(x.get("text", "") for x in name.get("runs", [])) or track.get("languageCode") or "Unknown"
            url = track.get("baseUrl") or track.get("url") or ""
            generated = track.get("kind") == "asr" or "caps=asr" in url
            result.append({
                "languageCode": track.get("languageCode"),
                "language": language,
                "isGenerated": generated,
                "isTranslatable": track.get("isTranslatable", False),
                "baseUrl": url,
                "params": track.get("languageCode"),
            })
        return result

    def _caption_url(self, url: str) -> str:
        parsed = urlparse(url)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query["fmt"] = "json3"
        return urlunparse(parsed._replace(query=urlencode(query)))

    def _parse(self, text: str) -> List[Dict]:
        text = text.strip()
        if not text:
            return []
        segments = []
        if text.startswith("{"):
            for event in json.loads(text).get("events", []):
                value = "".join(x.get("utf8", "") for x in event.get("segs", []))
                value = unescape(value).replace("\n", " ").strip()
                if not value:
                    continue
                start_ms = int(event.get("tStartMs", 0))
                duration_ms = int(event.get("dDurationMs", 0))
                segments.append({
                    "text": value,
                    "start": start_ms / 1000,
                    "duration": duration_ms / 1000,
                    "startMs": str(start_ms),
                    "endMs": str(start_ms + duration_ms),
                })
            return segments
        root = ET.fromstring(text)
        for item in root.findall(".//text"):
            start = float(item.get("start", 0))
            duration = float(item.get("dur", 0))
            value = unescape("".join(item.itertext())).replace("\n", " ").strip()
            if not value:
                continue
            segments.append({
                "text": value,
                "start": start,
                "duration": duration,
                "startMs": str(int(start * 1000)),
                "endMs": str(int((start + duration) * 1000)),
            })
        return segments

    def _native(self, cookie_file: Optional[str]):
        # Reuses the shared pooled client - no ephemeral client per call.
        client = _get_sync_client()
        apply_cookies_to_client(client, cookie_file)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
            "Accept-Language": f"{self.key},en;q=0.9" if self.key else "en-US,en;q=0.9",
        }
        watch = client.get(f"https://www.youtube.com/watch?v={self.video_id}", headers=headers, timeout=20, follow_redirects=True)
        watch.raise_for_status()
        api = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', watch.text)
        version = re.search(r'"INNERTUBE_CLIENT_VERSION":"([^"]+)"', watch.text)
        if not api:
            return
        body = {
            "context": {"client": {
                "clientName": "WEB",
                "clientVersion": version.group(1) if version else "2.20250730.01.00",
                "hl": self.key or "en",
                "gl": "US",
            }},
            "videoId": self.video_id,
            "contentCheckOk": True,
            "racyCheckOk": True,
        }
        response = client.post(
            f"https://www.youtube.com/youtubei/v1/player?key={api.group(1)}",
            json=body,
            headers={**headers, "Content-Type": "application/json"},
            timeout=20,
            follow_redirects=True,
        )
        response.raise_for_status()
        tracks = response.json().get("captions", {}).get("playerCaptionsTracklistRenderer", {}).get("captionTracks", [])
        languages = self._languages(tracks)
        selected = self._select_track(tracks)
        if not selected:
            self.result = {"segments": [], "languages": languages}
            return
        url = selected.get("baseUrl") or selected.get("url")
        if not url:
            self.result = {"segments": [], "languages": languages}
            return
        caption = client.get(self._caption_url(url), headers=headers, timeout=20, follow_redirects=True)
        caption.raise_for_status()
        self.result = {"segments": self._parse(caption.text), "languages": languages}

    def _ytdlp(self, cookie_file: Optional[str]):
        try:
            from yt_dlp import YoutubeDL
        except ImportError:
            return
        options = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "socket_timeout": 20,
            "retries": 1,
            "extractor_retries": 1,
            "fragment_retries": 1,
            "extractor_args": {"youtube": {"player_client": ["web", "android", "tv"]}},
        }
        if cookie_file:
            options["cookiefile"] = cookie_file
        with YoutubeDL(options) as downloader:
            info = downloader.extract_info(self.videoLink, download=False)
        tracks = []
        for generated, source in ((False, info.get("subtitles") or {}), (True, info.get("automatic_captions") or {})):
            for code, formats in source.items():
                if any(x.get("languageCode") == code for x in tracks):
                    continue
                selected = next((x for x in formats if x.get("ext") == "json3"), next((x for x in formats if x.get("ext") in ("srv1", "srv3", "ttml")), None))
                if not selected:
                    continue
                url = selected.get("url") or ""
                tracks.append({
                    "languageCode": code,
                    "name": {"simpleText": selected.get("name") or code},
                    "kind": "asr" if generated or "caps=asr" in url else None,
                    "isTranslatable": False,
                    "baseUrl": url,
                })
        languages = self._languages(tracks)
        selected = self._select_track(tracks)
        if not selected:
            self.result = {"segments": [], "languages": languages}
            return
        client = _get_sync_client()
        apply_cookies_to_client(client, cookie_file)
        response = client.get(self._caption_url(selected["baseUrl"]), timeout=20, follow_redirects=True)
        response.raise_for_status()
        self.result = {"segments": self._parse(response.text), "languages": languages}

    def sync_create(self):
        cookie_file = resolve_cookie_file()
        try:
            try:
                self._native(cookie_file)
            except Exception:
                self.result = {"segments": [], "languages": []}
            if not self.result["segments"]:
                try:
                    self._ytdlp(cookie_file)
                except Exception:
                    pass
        finally:
            cleanup_cookie_file(cookie_file)

    async def async_create(self):
        await asyncio.to_thread(self.sync_create)

import re
import json
import xml.etree.ElementTree as ET
from html import unescape
from typing import Union, Dict, List, Optional
import httpx

from youtubesearchpython.core.requests import RequestCore, _get_sync_client, _get_async_client
from youtubesearchpython.core.componenthandler import getVideoId
from youtubesearchpython.core.exceptions import YouTubeRequestError


class TranscriptCore(RequestCore):
    """
    Fetches transcripts by parsing the video page HTML to extract captions data.
    Based on youtube-transcript-api approach.
    """
    def __init__(self, videoLink: str, key: str = None):
        super().__init__()
        self.videoLink = videoLink
        self.video_id = getVideoId(videoLink)
        self.key = key
        self.result = {"segments": [], "languages": []}
    
    def _extract_player_response(self, html: str) -> Optional[Dict]:
        """Extract ytInitialPlayerResponse JSON from video page HTML"""
        patterns = [
            r'var ytInitialPlayerResponse\s*=\s*({.+?});var',
            r'ytInitialPlayerResponse\s*=\s*({.+?});',
            r'ytInitialPlayerResponse"\s*:\s*({.+?}),"',
        ]        
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1)
                    brace_count = 0
                    end_pos = 0
                    for i, char in enumerate(json_str):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_pos = i + 1
                                break                    
                    if end_pos > 0:
                        json_str = json_str[:end_pos]                    
                    player_response = json.loads(json_str)
                    return player_response
                except (json.JSONDecodeError, ValueError) as e:
                    continue        
        return None
    
    def _select_track(self, caption_tracks: List[Dict]) -> Dict:
        if self.key:
            for track in caption_tracks:
                if track.get("languageCode") == self.key:
                    return track
        return caption_tracks[0]

    def _fetch_transcript_xml(self, url: str) -> List[Dict]:
        """Fetch and parse transcript XML from caption URL"""
        try:
            response = _get_sync_client().get(url, timeout=10)
            response.raise_for_status()
            root = ET.fromstring(response.text)            
            segments = []
            for text_elem in root.findall('.//text'):
                start = float(text_elem.get('start', 0))
                duration = float(text_elem.get('dur', 0))
                text = text_elem.text or ""
                text = unescape(text)             
                segments.append({
                    "text": text,
                    "start": start,
                    "duration": duration,
                    "startMs": str(int(start * 1000)),
                    "endMs": str(int((start + duration) * 1000))
                })            
            return segments
        except Exception as e:
            return []
    
    async def _fetch_transcript_xml_async(self, url: str) -> List[Dict]:
        """Async version of transcript XML fetching"""
        try:
            response = await _get_async_client().get(url, timeout=10)
            response.raise_for_status()
            root = ET.fromstring(response.text)
            segments = []
            for text_elem in root.findall('.//text'):
                start = float(text_elem.get('start', 0))
                duration = float(text_elem.get('dur', 0))
                text = text_elem.text or ""
                text = unescape(text)
                segments.append({
                    "text": text,
                    "start": start,
                    "duration": duration,
                    "startMs": str(int(start * 1000)),
                    "endMs": str(int((start + duration) * 1000))
                })
            return segments
        except Exception as e:
            return []
    
    def sync_create(self):
        """Fetch transcript by parsing video page HTML"""
        try:
            watch_url = f"https://www.youtube.com/watch?v={self.video_id}"
            response = _get_sync_client().get(watch_url, timeout=10, follow_redirects=True)
            response.raise_for_status()
            player_response = self._extract_player_response(response.text)
            if not player_response:
                self.result = {"segments": [], "languages": []}
                return
            
            captions = player_response.get("captions")
            if not captions:
                self.result = {"segments": [], "languages": []}
                return
            
            renderer = captions.get("playerCaptionsTracklistRenderer")
            if not renderer:
                self.result = {"segments": [], "languages": []}
                return
            
            caption_tracks = renderer.get("captionTracks", [])
            if not caption_tracks:
                self.result = {"segments": [], "languages": []}
                return
            
            languages = []
            for track in caption_tracks:
                name = track.get("name", {})
                lang_name = name.get("simpleText") or (name.get("runs", [{}])[0].get("text") if name.get("runs") else "Unknown")
                
                lang_info = {
                    "languageCode": track.get("languageCode"),
                    "language": lang_name,
                    "isGenerated": track.get("kind") == "asr",
                    "baseUrl": track.get("baseUrl"),
                    "params": track.get("languageCode"),
                }
                languages.append(lang_info)
            
            if caption_tracks:
                selected_track = self._select_track(caption_tracks)
                base_url = selected_track.get("baseUrl", "")
                if base_url:
                    base_url = base_url.replace("&fmt=srv3", "")
                    segments = self._fetch_transcript_xml(base_url)                    
                    self.result = {
                        "segments": segments,
                        "languages": languages
                    }
                else:
                    self.result = {"segments": [], "languages": languages}
            else:
                self.result = {"segments": [], "languages": []}
                
        except Exception as e:
            self.result = {"segments": [], "languages": []}
    
    async def async_create(self):
        """Async version of transcript fetching"""
        try:
            watch_url = f"https://www.youtube.com/watch?v={self.video_id}"
            client = _get_async_client()
            response = await client.get(watch_url, timeout=30, follow_redirects=True)
            response.raise_for_status()

            player_response = self._extract_player_response(response.text)
            if not player_response:
                self.result = {"segments": [], "languages": []}
                return

            captions = player_response.get("captions")
            if not captions:
                self.result = {"segments": [], "languages": []}
                return

            renderer = captions.get("playerCaptionsTracklistRenderer")
            if not renderer:
                self.result = {"segments": [], "languages": []}
                return

            caption_tracks = renderer.get("captionTracks", [])
            if not caption_tracks:
                self.result = {"segments": [], "languages": []}
                return

            languages = []
            for track in caption_tracks:
                name = track.get("name", {})
                lang_name = name.get("simpleText") or (name.get("runs", [{}])[0].get("text") if name.get("runs") else "Unknown")
                lang_info = {
                    "languageCode": track.get("languageCode"),
                    "language": lang_name,
                    "isGenerated": track.get("kind") == "asr",
                    "baseUrl": track.get("baseUrl"),
                    "params": track.get("languageCode"),
                }
                languages.append(lang_info)

            if caption_tracks:
                selected_track = self._select_track(caption_tracks)
                base_url = selected_track.get("baseUrl", "")
                if base_url:
                    base_url = base_url.replace("&fmt=srv3", "")
                    segments = await self._fetch_transcript_xml_async(base_url)
                    self.result = {
                        "segments": segments,
                        "languages": languages
                    }
                else:
                    self.result = {"segments": [], "languages": languages}
            else:
                self.result = {"segments": [], "languages": []}
        except Exception as e:
            self.result = {"segments": [], "languages": []}           

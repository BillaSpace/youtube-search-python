import re
import json
import xml.etree.ElementTree as ET
from html import unescape
from typing import Union, Dict, List, Optional
import httpx

from youtubesearchpython.core.requests import RequestCore
from youtubesearchpython.core.componenthandler import getVideoId
from youtubesearchpython.core.exceptions import YouTubeRequestError


class TranscriptCore(RequestCore):
    """
    Fetches transcripts by parsing the video page HTML to extract captions data.
    Based on youtube-transcript-api approach but implemented directly.
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
    
    def _fetch_transcript_xml(self, url: str) -> List[Dict]:
        """Fetch and parse transcript XML from caption URL"""
        try:
            response = httpx.get(url, timeout=10)
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
            print(f"DEBUG: Error fetching transcript XML: {e}")
            return []
    
    async def _fetch_transcript_xml_async(self, url: str) -> List[Dict]:
        """Async version of transcript XML fetching"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
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
            print(f"DEBUG: Error fetching transcript XML (async): {e}")
            return []
    
    def sync_create(self):
        """Fetch transcript by parsing video page HTML"""
        try:
            watch_url = f"https://www.youtube.com/watch?v={self.video_id}"
            response = httpx.get(watch_url, timeout=10, follow_redirects=True)
            response.raise_for_status()
            player_response = self._extract_player_response(response.text)
            if not player_response:
                print("DEBUG: Could not extract player response from page")
                self.result = {"segments": [], "languages": []}
                return
            
            captions = player_response.get("captions")
            if not captions:
                print("DEBUG: No captions in player response")
                self.result = {"segments": [], "languages": []}
                return
            
            renderer = captions.get("playerCaptionsTracklistRenderer")
            if not renderer:
                print("DEBUG: No playerCaptionsTracklistRenderer found")
                self.result = {"segments": [], "languages": []}
                return
            
            caption_tracks = renderer.get("captionTracks", [])
            if not caption_tracks:
                print("DEBUG: No caption tracks available")
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
                    "baseUrl": track.get("baseUrl")
                }
                languages.append(lang_info)
            
            if caption_tracks:
                base_url = caption_tracks[0].get("baseUrl", "")
                if base_url:
                    # Remove fmt=srv3 for better compatibility to push for cleaner segement 
                    base_url = base_url.replace("&fmt=srv3", "")
                    segments = self._fetch_transcript_xml(base_url)
                    
                    self.result = {
                        "segments": segments,
                        "languages": languages
                    }
                    print(f"DEBUG: Successfully fetched {len(segments)} transcript segments")
                else:
                    self.result = {"segments": [], "languages": languages}
            else:
                self.result = {"segments": [], "languages": []}
                
        except Exception as e:
            print(f"DEBUG: Transcript fetch error: {type(e).__name__}: {e}")
            self.result = {"segments": [], "languages": []}
    
    async def async_create(self):
        """Async version of transcript fetching"""
        try:
            watch_url = f"https://www.youtube.com/watch?v={self.video_id}"
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(watch_url, timeout=10)
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
                        "baseUrl": track.get("baseUrl")
                    }
                    languages.append(lang_info)
                
                if caption_tracks:
                    base_url = caption_tracks[0].get("baseUrl", "")
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
            print(f"DEBUG: Async transcript fetch error: {type(e).__name__}: {e}")
            self.result = {"segments": [], "languages": []}

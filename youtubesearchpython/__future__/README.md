# youtube-search-python (__future__) – Async Usage Guide

**⚠️ Experimental:**  
This library extracts YouTube data **without YouTube Data API v3**.  
It depends on public YouTube endpoints and may break anytime due to internal changes.  
Maintainer: **[Prakhar Shukla](https://github.com/BillaSpace)**

---

# 🔍 Async Search Usage

## Search – videos + channels + playlists
```python
from youtubesearchpython.__future__ import Search

search = Search("lofi music", limit=5)
result = await search.next()
print(result)
```

## VideosSearch – only videos
```python
from youtubesearchpython.__future__ import VideosSearch

search = VideosSearch("anime edits", limit=10)
result = await search.next()
print(result)
```

## ChannelsSearch – only channels
```python
from youtubesearchpython.__future__ import ChannelsSearch

search = ChannelsSearch("MrBeast", limit=3)
result = await search.next()
print(result)
```

## PlaylistsSearch – only playlists
```python
from youtubesearchpython.__future__ import PlaylistsSearch

search = PlaylistsSearch("best english songs", limit=3)
result = await search.next()
print(result)
```

## CustomSearch – filtered search via `searchPreferences`
```python
from youtubesearchpython.__future__ import CustomSearch

sp = "EgQQARgB"  # example filter: uploaded last hour
search = CustomSearch("gaming", searchPreferences=sp, limit=5)
result = await search.next()
print(result)
```

## ChannelSearch – search inside a channel
```python
from youtubesearchpython.__future__ import ChannelSearch

channel_id = "UCZFWPqqPkFlNwIxcpsLOwew"
search = ChannelSearch("watermelon", browseId=channel_id)
result = await search.next()
print(result)
```

---

# 🎬 StreamURLFetcher – Direct YouTube Stream URLs (Experimental)

## Requirements
- Call `await fetcher.getJavaScript()` **once** before any extraction.
- Works with results from `Video.get()` or `Video.getFormats()`.

## Example: Get stream URLs
```python
from youtubesearchpython.__future__ import StreamURLFetcher, Video

# 1. Create fetcher
fetcher = StreamURLFetcher()

# 2. Load player JavaScript only once
await fetcher.getJavaScript()

# 3. Get video formats
video = await Video.get("https://www.youtube.com/watch?v=aqz-KE-bpKQ")

# 4. Get a direct URL using itag
url_251 = await fetcher.get(video, 251)
print(url_251)

# 5. Get all available direct URLs
all_streams = await fetcher.getAll(video)
print(all_streams)
```

## Example output structure (`getAll`)
```json
{
  "streams": [
    {
      "url": "...",
      "itag": 251,
      "type": "audio/webm; codecs=\"opus\"",
      "quality": "tiny",
      "bitrate": 57976,
      "is_otf": false
    },
    {
      "url": "...",
      "itag": 22,
      "type": "video/mp4; codecs=\"avc1.64001F, mp4a.40.2\"",
      "quality": "hd720",
      "bitrate": 1340380,
      "is_otf": false
    }
  ]
}
```

---

# 📝 Fixation Notes
- Reuse a single `StreamURLFetcher()` instance for multiple URLs.
- Avoid calling `getJavaScript()` more than once.
- Extraction speed is fast because **no extra network calls** are made when deciphering.

---

# 👤 Maintainer
**Prakhar Shukla**  
GitHub: https://github.com/BillaSpace

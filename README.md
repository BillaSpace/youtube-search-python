# 🎥 YouTube Search Python v2.0.0

<div align="center">

![YouTube Search Python](https://files.catbox.moe/rbt2je.jpg)

[![GitHub Stars](https://img.shields.io/github/stars/BillaSpace/youtube-search-python?style=for-the-badge&logo=github)](https://github.com/BillaSpace/youtube-search-python/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/BillaSpace/youtube-search-python?style=for-the-badge&logo=github)](https://github.com/BillaSpace/youtube-search-python/network)
[![Python Version](https://img.shields.io/badge/python-3.7-10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/BillaSpace/youtube-search-python?style=for-the-badge)](https://github.com/BillaSpace/youtube-search-python/blob/main/LICENSE)

**Search YouTube without the YouTube Data API v3**

A professional, actively maintained Python library for searching YouTube content—completely free and without API quotas.

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Examples](#-examples) • [Documentation](#-documentation)

</div>

---

## ✨ Features

- 🚀 **No API Key Required** - Search YouTube without quotas or rate limits
- ⚡ **Fast & Reliable** - Optimized for performance
- 🔄 **Sync & Async Support** - Use synchronous or asynchronous methods
- 📦 **Rich Metadata** - Get videos, channels, playlists, comments, transcripts & more
- 🎯 **Advanced Filtering** - Sort by date, views, duration, and more
- 🌐 **Multi-Region** - Search with language and region preferences
- 🔧 **Modern** - Compatible with Python 3.7+ and httpx 0.28+
- 💪 **Type Hints** - Full type annotations for better IDE support

---

## 📦 Installation

### Via Git (Recommended)

```bash
pip install git+https://github.com/BillaSpace/youtube-search-python.git
```

### Via requirements.txt

```text
git+https://github.com/BillaSpace/youtube-search-python.git
```

Then:
```bash
pip install -r requirements.txt
```

### Clone & Install

```bash
git clone https://github.com/BillaSpace/youtube-search-python.git
cd youtube-search-python
pip install -e .
```

---

## 🚀 Quick Start

### Synchronous Search

```python
from youtubesearchpython import VideosSearch

# Search for videos
videos = VideosSearch('Kesariya song', limit=5)
results = videos.result()

for video in results['result']:
    print(f"{video['title']} - {video['link']}")
```

### Asynchronous Search

```python
import asyncio
from youtubesearchpython.future import VideosSearch

async def search():
    videos = VideosSearch('Hindi songs', limit=5)
    results = await videos.next()
    
    for video in results['result']:
        print(f"{video['title']} - {video['link']}")

asyncio.run(search())
```

### Get Video Information

```python
from youtubesearchpython import Video

# Get complete video details
video = Video.get('https://youtu.be/7bj_2x-IoRE')
print(f"Title: {video['title']}")
print(f"Views: {video['viewCount']['text']}")
print(f"Duration: {video['duration']['text']}")
```

---

## 📚 Examples

### 1. Search for Videos

#### Synchronous
```python
from youtubesearchpython import VideosSearch

# Basic search
search = VideosSearch('Bollywood songs 2024', limit=10)
print(search.result())

# With language and region
search = VideosSearch('Myanmar music', limit=5, language='en', region='MM')
results = search.result()
```

#### Asynchronous
```python
import asyncio
from youtubesearchpython.future import VideosSearch

async def search_videos():
    search = VideosSearch('Arijit Singh songs', limit=10)
    results = await search.next()
    
    for video in results['result']:
        print(f"{video['title']}")
        print(f"Views: {video['viewCount']['text']}")
        print(f"Link: {video['link']}\n")

asyncio.run(search_videos())
```

---

### 2. Search for Channels

```python
from youtubesearchpython import ChannelsSearch

# Search for channels
channels = ChannelsSearch('T-Series', limit=5)
results = channels.result()

for channel in results['result']:
    print(f"{channel['title']} - {channel['subscribers']}")
```

---

### 3. Search for Playlists

```python
from youtubesearchpython import PlaylistsSearch

# Search for playlists
playlists = PlaylistsSearch('Best of Arijit Singh', limit=5)
results = playlists.result()

for playlist in results['result']:
    print(f"{playlist['title']} - {playlist['videoCount']} videos")
```

---

### 4. Get Video Details

```python
from youtubesearchpython import Video

# Using URL
video = Video.get('https://www.youtube.com/watch?v=7bj_2x-IoRE')

# Using video ID
video = Video.get('7bj_2x-IoRE')

# Get only metadata (faster)
info = Video.getInfo('7bj_2x-IoRE')

# Get only stream formats
formats = Video.getFormats('7bj_2x-IoRE')
```

---

### 5. Get Playlist Videos

```python
from youtubesearchpython import Playlist

playlist = Playlist('https://www.youtube.com/playlist?list=PLAYLIST_ID')

print(f'Videos: {len(playlist.videos)}')

# Get all videos (pagination)
while playlist.hasMoreVideos:
    playlist.getNextVideos()
    print(f'Total videos: {len(playlist.videos)}')
```

---

### 6. Advanced Search with Filters

```python
from youtubesearchpython import CustomSearch, VideoSortOrder, VideoUploadDateFilter

# Sort by view count
search = CustomSearch('Indian music', VideoSortOrder.viewCount, limit=10)

# Filter by upload date
search = CustomSearch('Latest songs', VideoUploadDateFilter.thisWeek, limit=5)

results = search.result()
```

**Available Filters:**

| Filter | Options |
|--------|---------|
| **Sort Order** | `relevance`, `uploadDate`, `viewCount`, `rating` |
| **Upload Date** | `lastHour`, `today`, `thisWeek`, `thisMonth`, `thisYear` |
| **Duration** | `short` (<4min), `long` (>20min) |

---

### 7. Search Pagination

```python
from youtubesearchpython import VideosSearch

search = VideosSearch('Kesariya song', limit=5)

# Page 1
page1 = search.result()
print(f"Page 1: {len(page1['result'])} videos")

# Next page
search.next()
page2 = search.result()
print(f"Page 2: {len(page2['result'])} videos")
```

---

### 8. Get Comments

```python
from youtubesearchpython import Comments

comments = Comments('VIDEO_ID')
print(f"Comments: {len(comments.comments['result'])}")

# Get more comments
while comments.hasMoreComments:
    comments.getNextComments()
    print(f"Total: {len(comments.comments['result'])}")
```

---

### 9. Get Transcripts

```python
from youtubesearchpython import Transcript

# Get transcript
transcript = Transcript.get('VIDEO_URL')

# Get in different language
if transcript and 'languages' in transcript:
    transcript_hindi = Transcript.get('VIDEO_URL', transcript['languages'][1]['params'])
```

---

### 10. Search Suggestions

```python
from youtubesearchpython import Suggestions

suggestions = Suggestions(language='en', region='IN')
results = suggestions.get('Arijit Singh')
print(results)
```

---

## 🔄 Async vs Sync

### When to Use Async?

✅ **Use Async (`youtubesearchpython.future`) when:**
- Building web apps (FastAPI, aiohttp)
- Making multiple concurrent searches
- Integrating with async frameworks
- Need maximum performance

✅ **Use Sync (`youtubesearchpython`) when:**
- Simple scripts
- Learning/prototyping
- Don't need concurrency
- Simpler code is priority

### Import Comparison

```python
# Synchronous
from youtubesearchpython import VideosSearch, Video, Playlist

# Asynchronous
from youtubesearchpython.future import VideosSearch, Video, Playlist
```

---

## 🌍 Regional Search Examples

### Search Indian Content

```python
from youtubesearchpython import VideosSearch

# Hindi songs
search = VideosSearch('Kesariya', limit=5, language='hi', region='IN')

# Bollywood music
search = VideosSearch('Bollywood hits 2024', limit=10, region='IN')
```

### Search unicode languages Content

```python
from youtubesearchpython import VideosSearch

# Myanmar music
search = VideosSearch('myanmar love song', limit=5, region='MM')

# Burmese content
search = VideosSearch('burmese music', limit=10, language='my', region='MM')
```

---

## 🎯 Tested With

✅ **Indian Content**
- Kesariya (Brahmastra)
- Arijit Singh songs
- T-Series channel
- Bollywood playlists

✅ **Regional Content**  
- works on any server ip 
- supports almost all languages
- Regional artists

✅ **Global Content**
- International music
- Multi-language videos
- Various regions

---

## 🛠️ Advanced Usage

### Custom Timeout

```python
from youtubesearchpython import VideosSearch

# Set 30 second timeout
search = VideosSearch('query', limit=10, timeout=30)
```

###Result Modes

```python
from youtubesearchpython import ResultMode, VideosSearch

# Dictionary (default)
results = search.result(mode=ResultMode.dict)

# JSON string
results_json = search.result(mode=ResultMode.json)
```

### Channel-Specific Search

```python
from youtubesearchpython import ChannelSearch

# Search within a specific channel
search = ChannelSearch('song name', 'CHANNEL_ID')
results = search.result()
```

---

## 🐛 Troubleshooting

### Common Issues

**1. No results found**
- Try different search terms
- Check region/language settings
- Verify internet connection

**2. Timeout errors**
```python
# Increase timeout
search = VideosSearch('query', timeout=60)
```

**3. Import errors**
```bash
# Reinstall
pip install --force-reinstall git+https://github.com/BillaSpace/youtube-search-python.git
```

---

## 📝 Changelog

### Version 2.0.0 (Latest)
- ✨ Renamed async module to `future` for clarity from `__future__`
- 🐛 Fixed duplicate method in youtubesearchpython/core/video.py
- 🧪 Comprehensive testing made for all regions 
- 📚 Completely rewritten classes with its pageRendrers
- ⚡ Improved stability and performance
- 📱 ANDROID client as default
- 🔄 Enhanced stream URL handling
- ⚙️ httpx 0.28+ compatibility
- 🐛 Multiple bug fixes specially async v/s sync messups

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Credits

- **Original Author:** [Hitesh Kumar Saini](https://github.com/alexmercerind)
- **Maintainer:** [Prakhar](https://github.com/BillaSpace)
- **Contributors:** Community contributors

---

## ⭐ Support

If this project helped you, please ⭐ star it on [GitHub](https://github.com/BillaSpace/youtube-search-python)!

---

## 📧 Contact

- **Issues:** [GitHub Issues](https://github.com/BillaSpace/youtube-search-python/issues)
- **Email:** srvopus@gmail.com
- **Once i feel there is support my work is usable for everyone i'll release this library in pypi live as** :
-  ```yt-search-python```
---

<div align="center">

**Made with ❤️ for the YouTube community**

[⬆ Back to Top](#-youtube-search-python)

</div>

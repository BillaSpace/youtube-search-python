# 📮 YouTube Search Python v2.0.0 
- now known as :-
`yt-search-python`

<div align="center">

![yt-search-python](https://files.catbox.moe/m25e74.jpg)

[![GitHub Stars](https://img.shields.io/github/stars/BillaSpace/youtube-search-python?style=for-the-badge&logo=github)](https://github.com/BillaSpace/youtube-search-python/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/BillaSpace/youtube-search-python?style=for-the-badge&logo=github)](https://github.com/BillaSpace/youtube-search-python/network)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/BillaSpace/youtube-search-python?style=for-the-badge)](https://github.com/BillaSpace/youtube-search-python/blob/main/LICENSE)

**Search YouTube without the YouTube Data API v3**

A professional, Modern & actively maintained Python library for searching YouTube content—completely free and without youtube data API quotas.

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples) • [Testing](#-testing)

</div>

---

## ✨ Features

- 🚀 **No API Key Required** - Search YouTube without quotas or rate limits
- ⚡ **Fast & Reliable** - Optimized for performance with modern httpx
- 🔄 **Sync & Async Support** - Use synchronous or asynchronous methods
- 📦 **Rich Metadata** - Get videos, channels, playlists, comments, transcripts & more
- 🎯 **Advanced Filtering** - Sort by date, views, duration, and more
- 🌐 **Multi-Region** - Search with language and region preferences
- 🔧 **Modern** - Compatible with Python 3.7+ to current and httpx 0.28+
- 💪 **Type Hints** - Full type annotations for better IDE support

---

## Old youtube-search-python User? 
- if your are old user of this library & confused while migration to this library don't be confused just remove _ _ future _ _  imports to `youtube-search-python.future` only

## 📦 Installation

### Via Pip
```bash
pip3 install yt-search-python
```

### Via Git

```bash
pip install git+https://github.com/BillaSpace/youtube-search-python.git
```

### Via git requirements.txt

```text
git+https://github.com/BillaSpace/youtube-search-python.git
```

---

## 🚀 Quick Start

### Search for Videos

```python
from youtubesearchpython import VideosSearch

search = VideosSearch('NoCopyrightSounds', limit=10)
print(search.result())
```

### Get Video Information

```python
from youtubesearchpython import Video

video = Video.get('https://www.youtube.com/watch?v=aqz-KE-bpKQ')
print(video['title'])
print(video['viewCount'])
```

### Async Support

```python
import asyncio
from youtubesearchpython.future import VideosSearch, Video

async def main():
    search = VideosSearch('Python Tutorial', limit=5)
    result = await search.next()
    print(result)
    
    video = await Video.get('video_id_here')
    print(video)

asyncio.run(main())
```

---

## 📚 Documentation

### Core Documentation
- **[API Reference](docs.md)** - Complete API documentation with all classes and methods
- **[Usage Examples](docs/)** - Comprehensive examples for all features:
  - [Search Examples](docs/search_examples.md) - All search classes with filters
  - [Video & Extras Examples](docs/extras_examples.md) - Video, Playlist, Comments, etc.
  - [Stream URL Examples](docs/stream_examples.md) - Direct stream URL fetching
  - for stream url fetching services you must have `yt-dlp` already installed in your system

### Key Classes

#### Search Classes
- `VideosSearch` - Search for videos
- `ChannelsSearch` - Search for channels
- `PlaylistsSearch` - Search for playlists
- `CustomSearch` - Search with custom filters
- `ChannelSearch` - Search within a specific channel

#### Content Classes
- `Video` - Get video information and formats
- `Playlist` - Get playlist information and videos
- `Channel` - Get channel information
- `Comments` - Get video comments
- `Transcript` - Get video transcripts/captions
- `Suggestions` - Get search suggestions
- `Recommendations` - Get video recommendations
- `Hashtag` - Get videos by hashtag

#### Utility Classes
- `StreamURLFetcher` - Get direct stream URLs with multiple formats
- `ResultMode` - Control output format (dict/json)

---

## 💡 Examples

### Advanced Search with Filters

```python
from youtubesearchpython import CustomSearch, VideoSortOrder

# Search videos sorted by view count
search = CustomSearch('Python', VideoSortOrder.viewCount, limit=10)
print(search.result())
```

### Get Playlist Videos

```python
from youtubesearchpython import Playlist

# Works with both URLs and IDs
playlist = Playlist.get('PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK')
print(f"Playlist: {playlist['title']}")
print(f"Videos: {len(playlist['videos'])}")
```

### Fetch Comments

```python
from youtubesearchpython import Comments

comments = Comments.get('https://www.youtube.com/watch?v=aqz-KE-bpKQ')
for comment in comments['result'][:5]:
    print(f"{comment['author']}: {comment['content']}")
```

### Get Search Suggestions

```python
from youtubesearchpython import Suggestions

suggestions = Suggestions.get('Arijit Singh', language='en', region='US')
print(suggestions['result'])
```

For more examples, see the [examples directory](docs/examples/).

---

## 🧪 Testing

### Wanna Quick Test ?

```bash
cd tests
python3 full_execution.py
```

This comprehensive test suite covers:
- ✅ All search classes (Videos, Channels, Playlists, Custom)
- ✅ Content retrieval (Video, Playlist, Channel)
- ✅ Social features (Comments, Recommendations, Suggestions)
- ✅ Advanced features (StreamURLFetcher, Transcript)
- ✅ Both synchronous and asynchronous methods

### Test Documentation
See [tests/README.md](tests/README.md) for detailed testing information.

---

## 🔧 Advanced Features

### Pagination

```python
search = VideosSearch('Python', limit=10)
print(search.result())

# Get next page
search.next()
print(search.result())
```

### 🌎 Language & Region

```python
search = VideosSearch('Music', limit=10, language='es', region='ES')
```

### Custom Filters

Available filters:
- **Upload Date**: `VideoUploadDateFilter.lastHour`, `.today`, `.thisWeek`, `.thisMonth`, `.thisYear`
- **Duration**: `VideoDurationFilter.short`, `.long`
- **Sort Order**: `VideoSortOrder.relevance`, `.uploadDate`, `.viewCount`, `.rating`

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer 

This library is not affiliated with YouTube or Google Inc. It uses YouTube's internal API which may change without notice. Use responsibly and in accordance with YouTube's Terms of Content usage and distribution Services.

---
## 🔁 Credits

- **Current Developer:** [Prakhar](https://github.com/BillaSpace)
- **Old Author:** [Hitesh Kumar Saini](https://github.com/alexmercerind) 

---


## 🌟 Support & Future of the Library 

- If you find this library useful, please consider to support the developer by giving a fork & ✳️ star on [GitHub](https://github.com/BillaSpace/youtube-search-python) , 

- if i found this library is really useful n necessary for everyone i'll keep maintaining on [pypi](https://pypi.org/project/yt-search-python) as -;
`yt-search-python`

---

<div align="center">

**Made with ❤️ for the community**

[Report Bug](https://github.com/BillaSpace/youtube-search-python/issues) • [Request Feature](https://github.com/BillaSpace/youtube-search-python/issues)

</div>

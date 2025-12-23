<!-- ========================= -->
<!-- youtube-search-python Revamped -->
<!-- ========================= -->

<p align="center">
  <img src="https://files.catbox.moe/rbt2je.jpg" alt="youtube-search-python" style="border-radius: 18px; max-width: 100%; height: auto;" />
</p>

<h1 align="center">youtube-search-python v2.0 (Revamped)</h1>

<p align="center">
  A revived and improved fork of <code>youtube-search-python</code> focused on better reliability, compatibility, and maintained fixes.
</p>

<p align="center">
  <a href="https://github.com/BillaSpace/youtube-search-python">Repository</a> •
  <a href="https://github.com/BillaSpace">GitHub Profile</a>
</p>

---

## About

This project is a **revamped** version of the original `youtube-search-python` library that helps you search YouTube and fetch video/channel/playlist metadata **without** using YouTube Data API v3. [web:2]

The original upstream project `alexmercerind/youtube-search-python` is archived and read-only. [page:0]

---

## Installation

### edit your requirements.txt & replace with
```git+https://github.com/BillaSpace/youtube-search-python.git```

### locally clone this repository under your project
``` git clone https://github.com/BillaSpace/youtube-search-python```

### Using pip ( old version )
```pip install youtube-search-python```

This installs the published PyPI package name. [web:2]

> If you are using features like `StreamURLFetcher`, you may need extra dependencies (e.g., `yt-dlp`) depending on the library version you’re running. [web:2]

```pip install yt-dlp```

## Quick Start (Examples)

All example outputs may differ depending on YouTube changes, region, and time.  
For “Example Result”, prefer running `tests/sync` or `tests/async` files to get real outputs in your environment.

---

## Sync Usage

### Search for only videos (Sync)
```from youtubesearchpython import VideosSearchvideosSearch = VideosSearch('Habibi', limit = 2)print(videosSearch.result())```

---

## Async Usage (Revamped)

### Search for only videos (Async)
```from youtubesearchpython.future import VideosSearchvideosSearch = VideosSearch('Challa', limit = 2)videosResult = await videosSearch.next()print(videosResult)```


### Async documentation
Read more about usage & examples of newer asynchronous version of this library:  
https://github.com/BillaSpace/youtube-search-python/blob/main/youtubesearchpython/future/README.md

---

## More Examples

### Search for only channels
```from youtubesearchpython import ChannelsSearchchannelsSearch = ChannelsSearch('NoCopyrightSounds', limit = 10, region = 'US')print(channelsSearch.result())```

### Search for only playlists
```from youtubesearchpython import PlaylistsSearchplaylistsSearch = PlaylistsSearch('NoCopyrightSounds', limit = 1)print(playlistsSearch.result())```


### Search with a filter or sort
```from youtubesearchpython import *customSearch = CustomSearch('NoCopyrightSounds', VideoSortOrder.uploadDate, limit = 1)print(customSearch.result())```


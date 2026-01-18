## Quick Documentations ✳️

### This is the updated and complete documentation for yt-search-python, highlighting modern async-first design.
 For full usage guides and examples, [visit the Docs:](https://github.com/BillaSpace/yt-search-python/docs/)


---

## 🚀 Modern Async API [future] — New in v2.0.0

### yt-search-python introduces a fully modern asynchronous API under the youtubesearchpython.future module with modern Features that Not Even One Single Library offers in the world that is recommendations & Search Suggestions.

- Async Advantages

- Faster requests using httpx

- Cleaner parallel querying

- More consistent results

- Fully non-blocking I/O


### All major features support async:

VideosSearch

ChannelsSearch

PlaylistsSearch

CustomSearch

ChannelSearch

Video / Channel / Playlist

Comments

Suggestions

Recommendations

StreamURLFetcher

Transcript


Example:

`from youtubesearchpython.future import VideosSearch
results = await VideosSearch("Arijit Singh", limit=10).next()`

Sync API (Legacy-Compatible)

The original synchronous API remains unchanged for backward compatibility.

Example:

`from youtubesearchpython import VideosSearch
search = VideosSearch("Arijit Singh", limit=10)
print(search.result())`


---

## Core Search Classes

**VideosSearch**

Searches for videos via query or video_id.

Sync Constructor:

`VideosSearch(query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: int = None)`

Sync Methods:

`result(mode) — returns current results`

`next() — fetch next page`


Async Version:

`await VideosSearch(...).next()`

Returns the next page directly as a dict.


---

**ChannelsSearch**

Search YouTube channels via channel_id.

Sync:

`result(mode)`

`next()`


Async:

`await next()`



---

**PlaylistsSearch**

Search playlists both url or  id.

Sync & Async parity:

`.result() / await .next()`



---

**CustomSearch**

Custom filtered search eg: regional biased or filter specifics.

Supports sync + async.

`CustomSearch(query, searchPreferences, limit, language, region, timeout)`


---

**ChannelSearch**

Search within a specific channel via query.

Supports sync + async.

`ChannelSearch(query, browseId, language, region, searchPreferences, timeout)`


---

## Content Retrieval Classes

**Video**

Retrieves video metadata and streaming formats via url.

Sync:

`get(video_id)`

`getFormats(video_id)`


Async:

`await Video.get(video_id)`

`await Video.getInfo(video_id)`

`await Video.getFormats(video_id)`



---

**Channel**

Retrieve channel info + playlists via channel_id.

Sync:

`get(channelId)`


Async:

`await Channel.get(channel_id)`

Instance-based async navigation with .init() and .next() [ experimental]



---

**Youtube / Music Playlists**

Fetch playlist info and videos via playlist urls or playlist_id.

Sync:

`get(playlistUrl)`

`Instance .getNextVideos()`


Async:

`await Playlist.get(playlistUrl)`

Instance .init() and await getNextVideos()



---

**Video Comments**

Fetch comments from a video via url or video_id.

Sync:

`get(videoUrl)`

`.getNextComments()`


Async:

`await Comments.get(videoUrl)`

Instance .init() and await getNextComments()



---

**Search Suggestions**

Retrieve search suggestions via query.

Sync:

`get(query)` (static)

instance .get(query)


Async:

`await Suggestions.get(query)`

instance await get(query)



---

**Song Recommendations**

Get related videos via video_id.

Sync:

`get(videoId)` → list


Async:

`await Recommendations.get(videoId)` → list



---

**Transcript**

Retrieve video transcripts.

Sync:

`get(video_url)`


Async:

`await Transcript.get(video_url)`


Note: Transcript availability may vary due to YouTube restrictions Use cookies.


---

**StreamURLFetcher**

Directly fetch streaming URLs.

Sync:

`get(video_data, itag)`

`getAll(video_data)`


Async:

`await get(...)`

`await getAll(...)`

`await getJavaScript()`



---

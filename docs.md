# Quick Documentations

Detailed documentation for `yt-search-python`.

> **Note:** For complete usage examples with sample outputs, Checkout  full [Docs](https://github.com/BillaSpace/youtube-search-python/docs/)

## Core Classes

### VideosSearch

Searches for videos.

**Constructor:**
`VideosSearch(query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: int = None)`
- `query`: The search term (e.g., "Arijit Singh", "New Song").
- `limit`: Max results to fetch (default: 20).
- `language`: Code (e.g., 'en', 'hi').
- `region`: Code (e.g., 'US', 'IN').
- `timeout`: Time in seconds to wait for response.

**Methods:**
- `result(mode: int = ResultMode.dict) -> dict | str`: Returns the current search results.
- `next() -> bool`: Fetches the next page of results. Returns `True` if successful, `False` otherwise.

**Async (`future.VideosSearch`):**
- `await next() -> dict`: Fetches and returns the next page of results directly.

---

### ChannelsSearch

Searches for channels.

**Constructor:**
`ChannelsSearch(query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: int = None)`
- `query`: The search term (e.g., "T-Series").
- `limit`: Max results to fetch (default: 20).
- `language`: Language code (e.g., 'en', 'hi').
- `region`: Region code (e.g., 'US', 'IN').
- `timeout`: Request timeout in seconds.

**Methods:**
- `result(mode: int = ResultMode.dict) -> dict | str`
- `next() -> bool`

**Async:**
- `await next() -> dict`

---

### PlaylistsSearch

Searches for playlists.

**Constructor:**
`PlaylistsSearch(query: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: int = None)`
- `query`: The search term (e.g., "Bollywood Hits").
- `limit`: Max results to fetch (default: 20).
- `language`: Language code.
- `region`: Region code.
- `timeout`: Request timeout in seconds.

**Methods:**
- `result(mode: int = ResultMode.dict) -> dict | str`
- `next() -> bool`

**Async:**
- `await next() -> dict`

---

### CustomSearch

Search with custom filters.

**Constructor:**
`CustomSearch(query: str, searchPreferences: str, limit: int = 20, language: str = 'en', region: str = 'US', timeout: int = None)`
- `query`: The search term.
- `searchPreferences`: Filter string (e.g., `VideoSortOrder.viewCount`).
- `limit`: Max results.
- `language`: Language code.
- `region`: Region code.
- `timeout`: Request timeout.

**Methods:**
- `result(mode: int = ResultMode.dict) -> dict | str`
- `next() -> bool`

**Async:**
- `await next() -> dict`

---

### ChannelSearch

Search within a specific channel.

**Constructor:**
`ChannelSearch(query: str, browseId: str, language: str = 'en', region: str = 'US', searchPreferences: str, timeout: int = None)`
- `query`: Search term to find *within* the channel.
- `browseId`: The Channel ID (must start with `UC...`, e.g., `UC_aEa8K-EOJ3D6gOs7HcyNg`).
- `searchPreferences`: Filter string (optional).

**Methods:**
- `result(mode: int = ResultMode.dict) -> dict | str`
- `next() -> bool`

**Async:**
- `await next() -> dict`

---

## Content Retrieval Classes

### Video

Retrieves video information and formats.

**Methods:**
- `get(video_id: str, mode: int = ResultMode.dict, timeout: int = None) -> dict | str`: Gets full video info. Accepts video ID or full URL.
- `getFormats(video_id: str, mode: int = ResultMode.dict, timeout: int = None) -> dict | str`: Gets streaming formats only. Accepts ID or URL.

**Async (`future.Video`):**
- `await Video.get(video_id: str, resultMode: int = ResultMode.dict, timeout: int = 2, get_upload_date: bool = False) -> dict`: Gets full video info.
- `await Video.getInfo(video_id: str, resultMode: int = ResultMode.dict, timeout: int = 2) -> dict`: Gets metadata only (faster).
- `await Video.getFormats(video_id: str, resultMode: int = ResultMode.dict, timeout: int = 2) -> dict`: Gets streaming formats only.

---

### Channel

Retrieves channel information and content (playlists).

**Methods:**
- `get(channelId: str, mode: int = ResultMode.dict, timeout: int = None) -> dict | str`: Gets channel info.

**Async (`future.Channel`):**
- `await Channel.get(channel_id: str, request_type: str = ChannelRequestType.playlists) -> dict`: Static method to fetch and return channel info.
- `Channel(channel_id: str, request_type: str = ChannelRequestType.playlists)`: Constructor for instance-based browsing.
- `await init()`: Initialize instance.
- `await next()`: Fetch next page of content (playlists).

---

### Playlist

Retrieves playlist information and videos.

**Methods:**
- `get(playlistLink: str, mode: int = ResultMode.dict, timeout: int = None) -> dict | str`: Static method to fetch playlist info and videos.
- `Playlist(playlistLink: str, timeout: int = None)`: Constructor for instance-based pagination.
- `getNextVideos() -> dict`: Fetches next batch of videos.
- `hasMoreVideos: bool`: Property indicating if more videos are available.

**Async (`future.Playlist`):**
- `await Playlist.get(playlistLink: str) -> dict`: Static method to fetch info.
- `await Playlist.getInfo(playlistLink: str) -> dict`: Static method to fetch metadata.
- `await Playlist.getVideos(playlistLink: str) -> dict`: Static method to fetch videos.
- `Playlist(playlistLink: str)`: Constructor.
- `await init()`: Initialize instance.
- `await getNextVideos()`: Instance method to fetch more.
- `hasMoreVideos: bool`: Property.

---

### Comments

Retrieves comments for a video.

**Methods:**
- `get(videoLink: str, mode: int = ResultMode.dict, timeout: int = None) -> dict | str`: Static method.
- `Comments(videoLink: str, timeout: int = None)`: Constructor.
- `getNextComments() -> dict`: Fetches next batch of comments.
- `hasMoreComments: bool`

**Async (`future.Comments`):**
- `await Comments.get(videoLink: str) -> dict`: Static method.
- `Comments(videoLink: str, timeout: int = None)`: Constructor.
- `await init()`: Initialize instance.
- `await getNextComments()`: Instance method.
- `hasMoreComments: bool`

---

### Suggestions

Retrieves search suggestions.

**Methods:**
- `get(query: str, language: str = 'en', region: str = 'US', timeout: int = None) -> dict | str`: Static method.
- `Suggestions(language: str = 'en', region: str = 'US', timeout: int = None)`: Constructor.
- `get(query: str, mode: int = ResultMode.dict) -> dict | str`: Instance method.

**Async (`future.Suggestions`):**
- `await Suggestions.get(query: str, language: str = 'en', region: str = 'US', mode: int = ResultMode.dict) -> dict`: Static method.
- `Suggestions(language: str = 'en', region: str = 'US')`: Constructor.
- `await get(query: str, mode: int = ResultMode.dict) -> dict`: Instance method.

---

### Recommendations

Retrieves video recommendations (related videos).

**Methods:**
- `get(videoId: str, timeout: int = None) -> list`: Static method.

**Async (`future.Recommendations`):**
- `await Recommendations.get(videoId: str, timeout: int = 2) -> list`: Static method.

---

### Transcript

Retrieves video transcripts.

**Methods:**
- `get(video_url: str) -> dict`: Returns transcript data. Requires full YouTube URL.
- **Note**: Currently returns 400 error due to YouTube's IP/Auth blocking. Use cookies or proxies.

**Async (`future.Transcript`):**
- `await Transcript.get(video_url)`

### StreamURLFetcher

Fetches direct media URLs.

**Constructor:**
`StreamURLFetcher(proxy: str = None, cookies_file: str = None)`
- `proxy`: HTTP/HTTPS proxy URL (e.g., `http://user:pass@host:port`).
- `cookies_file`: Path to cookies.txt file for authenticated requests.

**Methods:**
- `get(video_data: dict, itag: int) -> str`: Returns direct stream URL for specific itag.
- `getAll(video_data: dict) -> dict`: Returns all direct stream URLs in a dictionary.
- `getJavaScript()`: Fetches necessary deciphering JavaScript from YouTube (sync or async).

**Async (`future.StreamURLFetcher`):**
- `await get(video_data, itag)`
- `await getAll(video_data)`
- `await getJavaScript()`

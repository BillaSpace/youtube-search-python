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
- `get(video_id: str, mode: int = ResultMode.dict, timeout: int = 2) -> dict | str`: Gets full video info. Accepts video ID or full URL.
- `getInfo(video_id: str, mode: int = ResultMode.dict, timeout: int = 2) -> dict | str`: Gets metadata only (faster). Accepts ID or URL.
- `getFormats(video_id: str, mode: int = ResultMode.dict, timeout: int = 2) -> dict | str`: Gets streaming formats only. Accepts ID or URL.

**Async (`future.Video`):**
- methods are `await Video.get(...)`, `await Video.getInfo(...)`, etc.

---

### Channel

Retrieves channel information.

**Constructor:**
`Channel(channel_id: str, request_type: str)`
- `channel_id`: The Channel ID (must start with `UC...`).
- `request_type`: Type of content to fetch (e.g., `ChannelRequestType.playlists`).

**Methods:**
- `result(mode: int = ResultMode.dict) -> dict | str`: Returns channel info.

**Async (`future.Channel`):**
- `await Channel.get(channel_id)`: Static method to fetch and return channel info.
- `await init()`: Initialize instance.
- `await next()`: Fetch next page of content (if browsing videos/playlists).

---

### Playlist

Retrieves playlist information and videos.

**Constructor:**
`Playlist(playlist_link: str)`
- `playlist_link`: Full YouTube playlist URL OR just the playlist ID (e.g., `PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK`).

**Methods:**
- `hasMoreVideos: bool`: Property indicating if more videos are available.
- `getNextVideos()`: Fetches next batch of videos.

**Async (`future.Playlist`):**
- `await Playlist.get(link)`: Static method to fetch info.
- `await getNextVideos()`: Instance method to fetch more.

---

### Comments

Retrieves comments for a video.

**Constructor:**
`Comments(video_id: str)`
- `video_id`: The video ID (not full URL).

**Methods:**
- `hasMoreComments: bool`
- `getNextComments()`: Fetches next batch of comments.

**Async (`future.Comments`):**
- `await Comments.get(video_id)`: Static method.
- `await getNextComments()`: Instance method.

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
- `get(video_data: dict, itag: int) -> str`: Returns URL for specific itag.
- `getAll(video_data: dict) -> dict`: Returns all stream URLs.
- `getJavaScript()`: Fetches necessary JS (run once i suggesst install deno for proper working).

**Async (`future.StreamURLFetcher`):**
- All methods are awaitable.

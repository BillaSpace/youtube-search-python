<p align="center">
  <img src="https://raw.githubusercontent.com/BillaSpace/yt-search-python/legacy/assets/yt-search-python-banner.jpg" alt="yt-search-python" width="100%">
</p>

<p align="center">
  <a href="https://pypi.org/project/yt-search-python/">
    <img src="https://img.shields.io/pypi/v/yt-search-python?label=PyPI&cacheSeconds=60" alt="PyPI">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/yt-search-python?cacheSeconds=60" alt="Python versions">
  <a href="https://github.com/BillaSpace/yt-search-python/blob/legacy/LICENSE">
    <img src="https://img.shields.io/github/license/BillaSpace/yt-search-python?branch=legacy" alt="License">
  </a>
  <a href="https://github.com/BillaSpace/yt-search-python/tree/legacy">
    <img src="https://img.shields.io/badge/API-Sync%20%2B%20Async-blue" alt="Sync and Async">
  </a>
</p>

# yt-search-python v2.2.1

Search YouTube videos, playlists, channels, comments, transcripts, recommendations, suggestions, and stream metadata without the YouTube Data API v3.

- Python 3.9+
- Sync API: `youtubesearchpython`
- Async API: `youtubesearchpython.future`
- `httpx>=0.28.1`
- No YouTube Data API key or quota

## Installation

```bash
pip install yt-search-python
```

## Search

```python
from youtubesearchpython import VideosSearch

search = VideosSearch("Arijit Singh", limit=10)
print(search.result())
search.next()
print(search.result())
```

Live-only search is optional and backward compatible:

```python
live = VideosSearch("news", limit=10, is_live=True)
print(live.result())
```

Async search loads its first page on the first `await next()` call:

```python
import asyncio
from youtubesearchpython.future import VideosSearch

async def main():
    search = VideosSearch("Arijit Singh", limit=10)
    first = await search.next()
    print(first)
    second = await search.next()
    print(second)

asyncio.run(main())
```

## Video

```python
from youtubesearchpython import Video

info = Video.getInfo("pnxL4OOzPEc")
formats = Video.getFormats("pnxL4OOzPEc")
```

PO token and visitor data can be supplied when required by the selected YouTube client/session:

```python
formats = Video.getFormats(
    "pnxL4OOzPEc",
    po_token="YOUR_PO_TOKEN",
    visitor_data="YOUR_VISITOR_DATA",
)
```

`ResultMode.dict` and `ResultMode.json` are supported by video APIs.

## StreamURLFetcher

`StreamURLFetcher` no longer uses yt-dlp. It can process a `Video.getFormats()` result or fetch the format data from a video ID/link itself. PO-token generation and session-aware token caching can be handled separately through the [`ytsp-po-token-provider`](https://github.com/BillaSpace/ytsp-po-token-provider).

```python
from youtubesearchpython import StreamURLFetcher

fetcher = StreamURLFetcher(po_token="YOUR_PO_TOKEN", visitor_data="YOUR_VISITOR_DATA")
url = fetcher.get("pnxL4OOzPEc", 18)
all_streams = fetcher.getAll("pnxL4OOzPEc")
```

Existing dictionary input remains supported:

```python
from youtubesearchpython import Video, StreamURLFetcher

formats = Video.getFormats("pnxL4OOzPEc")
result = StreamURLFetcher().getAll(formats)
print(result["streams"])
print(result["unresolved"])
```

Direct URLs and cipher entries that already contain a usable signature are returned without yt-dlp. Formats that still require YouTube's encrypted player-JavaScript signature deciphering are returned under `unresolved` instead of being presented as working URLs. URLs that still contain an `n` parameter are marked with `throttled=True` so callers can make an informed choice rather than silently receiving a falsely-deciphered URL.

## Playlists

Regular playlists and YouTube Mix/Radio playlists (`RD...`) use YouTube's native Innertube endpoints.

```python
from youtubesearchpython import Playlist

normal = Playlist.get("PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK")
mix = Playlist.get("https://youtube.com/playlist?list=RDpnxL4OOzPEc&playnext=1")
```

Mix results preserve YouTube's returned song order. Duplicate video IDs are removed without re-sorting the result. Generic comment/engagement continuation tokens from `/next` responses are not treated as playlist continuations.

For regular playlists, instantiate `Playlist(link)` and call `getNextVideos()` for continuation pages.

## Recommendations

```python
from youtubesearchpython import Recommendations

related = Recommendations.get("pnxL4OOzPEc")
```

Recommendation results preserve YouTube's response order, skip the source video, remove duplicate video IDs stably, and normalize thumbnails against each video's ID.

## Suggestions

```python
from youtubesearchpython import Suggestions

print(Suggestions.get("Guru Randhawa"))
```

`YTS_PROXY` and `YTS_IDENTITY_TOKEN` environment variables are supported by the suggestions transport.

## Comments, transcripts, channels and hashtags

```python
from youtubesearchpython import Comments, Transcript, Channel, Hashtag

comments = Comments.get("pnxL4OOzPEc")
transcript = Transcript.get("pnxL4OOzPEc", params="en")
channel = Channel.get("UC_x5XG1OV2P6uZZ5FSM9Ttw")
hashtag = Hashtag.get("music", limit=10)
```

Transcript retrieval first uses YouTube's native caption/player flow. The optional `transcript` extra keeps the legacy yt-dlp caption fallback available:

```bash
pip install 'yt-search-python[transcript]'
```

## HTTP lifecycle

The library uses one canonical `httpx` transport layer. Idle keep-alive retention is disabled to avoid stale pooled sockets in long-running bots/services.

Sync shutdown:

```python
# Optional forced teardown only
from youtubesearchpython import close_clients
close_clients()
```

Async shutdown:

```python
# Optional forced teardown only
from youtubesearchpython.future import aclose_clients
await aclose_clients()
```

Proxy requests use scoped clients that are closed after each request. Temporary downloaded cookie files are also ownership-tracked and cleaned without deleting user-owned cookie files.

## Main API

Search:
- `Search`
- `VideosSearch`
- `ChannelsSearch`
- `PlaylistsSearch`
- `CustomSearch`
- `ChannelSearch`

Content:
- `Video`
- `Playlist`
- `Channel`
- `Comments`
- `Transcript`
- `Hashtag`
- `Suggestions`
- `Recommendations`

Streaming:
- `StreamURLFetcher`

Utilities:
- `ResultMode`
- `SearchMode`
- `VideoUploadDateFilter`
- `VideoDurationFilter`
- `VideoSortOrder`
- `ChannelRequestType`

## Compatibility notes

- `youtubesearchpython.future` is the supported async namespace.
- Legacy `SearchVideos` and `SearchPlaylists` imports remain available.
- YouTube's internal response structures and anti-abuse requirements can change without notice.
- A PO token does not replace player JavaScript signature or `n`-challenge transformation when YouTube requires those for a format.

## License

MIT. See `LICENSE`.

Current maintainer: Prakhar Shukla / BillaSpace. Original project by Hitesh Kumar Saini (alexmercerind).

### Optional PO token environment variables

`Video` and `StreamURLFetcher` keep their existing arguments, but can also read credentials from the environment when explicit values are not passed:

```bash
export YT_PO_TOKEN="..."
export YT_VISITOR_DATA="..."
```

Aliases `YOUTUBE_PO_TOKEN` and `YOUTUBE_VISITOR_DATA` are also supported. Explicit function/class arguments always take precedence over environment values.


## Python compatibility

- Python 3.9+
- Runtime-tested on Python 3.13.5
- Audited against Python 3.14 asyncio removals/deprecations; the library uses `asyncio.get_running_loop()` and does not depend on the deprecated event-loop policy APIs.
- HTTP transport uses the tested `httpx>=0.28.1,<1.0` range.

HTTP clients are managed internally. Normal sync applications require no explicit shutdown call, and async clients are closed automatically when their owning event loop shuts down gracefully (including `asyncio.run()`). `close_clients()` and `aclose_clients()` remain available only for optional forced teardown, tests, or unusual lifecycle control.

## Related project

For PO-token generation, refresh, session-aware caching, and external provider integration, see [`BillaSpace/ytsp-po-token-provider`](https://github.com/BillaSpace/ytsp-po-token-provider).

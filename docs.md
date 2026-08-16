# yt-search-python 2.2.1 API notes

The canonical project overview and current examples live in `README.md` and the files under `docs/`.

## Sync search

```python
from youtubesearchpython import VideosSearch

search = VideosSearch("Arijit Singh", limit=10)
print(search.result())
search.next()
print(search.result())
```

Live-only search:

```python
search = VideosSearch("news", is_live=True)
```

## Async search

```python
from youtubesearchpython.future import VideosSearch

search = VideosSearch("Arijit Singh", limit=10)
first = await search.next()
second = await search.next()
```

## Video and formats

```python
from youtubesearchpython import Video

info = Video.getInfo("pnxL4OOzPEc")
formats = Video.getFormats("pnxL4OOzPEc", po_token="TOKEN", visitor_data="VISITOR_DATA")
```

## StreamURLFetcher

```python
from youtubesearchpython import StreamURLFetcher

fetcher = StreamURLFetcher(po_token="TOKEN", visitor_data="VISITOR_DATA")
result = fetcher.getAll("pnxL4OOzPEc")
```

The stream fetcher does not depend on yt-dlp. It returns direct/already-signed formats and reports encrypted player-JavaScript formats under `unresolved` instead of fabricating a working URL.

## Playlists

```python
from youtubesearchpython import Playlist

regular = Playlist.get("PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK")
mix = Playlist.get("https://youtube.com/playlist?list=RDpnxL4OOzPEc&playnext=1")
```

Regular playlist pagination uses `Playlist(link).getNextVideos()`. Mix/Radio results use the native `/next` response and preserve YouTube's returned order.

## Recommendations

```python
from youtubesearchpython import Recommendations

videos = Recommendations.get("pnxL4OOzPEc")
```

Results preserve backend order, skip the source ID and remove duplicate video IDs stably.

## Shutdown

```python
# Optional forced teardown only
from youtubesearchpython import close_clients
close_clients()
```

Async:

```python
# Optional forced teardown only
from youtubesearchpython.future import aclose_clients
await aclose_clients()
```

# Async API

```python
from youtubesearchpython.future import VideosSearch

search = VideosSearch("lofi music", limit=5)
first = await search.next()
second = await search.next()
```

Available async APIs include `Search`, `VideosSearch`, `ChannelsSearch`, `PlaylistsSearch`, `CustomSearch`, `ChannelSearch`, `Video`, `Playlist`, `Channel`, `Comments`, `Transcript`, `Hashtag`, `Suggestions`, `Recommendations`, and `StreamURLFetcher`.

Live-only video search:

```python
search = VideosSearch("news", is_live=True)
print(await search.next())
```

Stream URLs without yt-dlp:

```python
from youtubesearchpython.future import StreamURLFetcher

fetcher = StreamURLFetcher(po_token="TOKEN", visitor_data="VISITOR_DATA")
result = await fetcher.getAll("pnxL4OOzPEc")
print(result["streams"])
print(result["unresolved"])
```

For deterministic shutdown of the shared async HTTP transport:

```python
# Optional forced teardown only
from youtubesearchpython.future import aclose_clients
await aclose_clients()
```

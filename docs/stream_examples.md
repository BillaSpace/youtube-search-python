# StreamURLFetcher

## From a video ID or URL

```python
from youtubesearchpython import StreamURLFetcher

fetcher = StreamURLFetcher()
print(fetcher.get("pnxL4OOzPEc", 18))
print(fetcher.getAll("pnxL4OOzPEc"))
```

## From `Video.getFormats`

```python
from youtubesearchpython import Video, StreamURLFetcher

formats = Video.getFormats("pnxL4OOzPEc")
result = StreamURLFetcher().getAll(formats)
print(result["streams"])
print(result["unresolved"])
```

## PO token

```python
fetcher = StreamURLFetcher(po_token="TOKEN", visitor_data="VISITOR_DATA")
result = fetcher.getAll("pnxL4OOzPEc")
```

The stream fetcher does not use yt-dlp. Direct URLs and already-signed cipher URLs are returned. Encrypted signature entries that still require YouTube player-JavaScript deciphering are exposed under `unresolved`. URLs containing an `n` query parameter are marked with `throttled=True`.

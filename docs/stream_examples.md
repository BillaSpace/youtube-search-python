# StreamURLFetcher Examples

## StreamURLFetcher.get()

### Basic Usage
```python
from youtubesearchpython import *

fetcher = StreamURLFetcher()
video = Video.get("https://www.youtube.com/watch?v=aqz-KE-bpKQ")
url = fetcher.get(video, 251)
print(url)
```

### Example Output
Returns a direct stream URL string like:
```
"https://r6---sn-gwpa-5bgk.googlevideo.com/videoplayback?expire=1610798125&ei=zX8CYITXEIGKz7sP9MWL0AE&ip=..."
```

## StreamURLFetcher.getAll()

### Basic Usage
```python
from youtubesearchpython import *

fetcher = StreamURLFetcher()
video = Video.get("https://www.youtube.com/watch?v=aqz-KE-bpKQ")
allUrls = fetcher.getAll(video)
print(allUrls)
```

### Example Output Structure
```json
{
    "streams": [
        {
            "url": "https://...",
            "type": "video/mp4; codecs=\"avc1.42001E, mp4a.40.2\"",
            "quality": "medium",
            "itag": 18,
            "bitrate": 599167,
            "is_otf": false
        },
        {
            "url": "https://...",
            "type": "video/mp4; codecs=\"avc1.64001F, mp4a.40.2\"",
            "quality": "hd720",
            "itag": 22,
            "bitrate": 1340380,
            "is_otf": false
        }
    ]
}
```

### Available Quality Levels
- `hd2160` - 4K resolution
- `hd1440` - 2K resolution  
- `hd720` - 720p HD
- `medium` - 360p
- `tiny` - Audio only

### Common ITags
- **Video+Audio**: 18 (360p), 22 (720p)
- **Video Only**: 134 (360p), 135 (480p), 136 (720p), 137 (1080p)
- **Audio Only**: 249 (opus 50kbps), 250 (opus 70kbps), 251 (opus
-  160kbps)

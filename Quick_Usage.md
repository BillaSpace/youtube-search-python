# Quick  Usage Examples for youtube-search-python

This file contains example outputs for all library methods. These examples were extracted from the codebase docstrings.

## VideosSearch

### Example 1: Basic Search
```python
from youtubesearchpython import VideosSearch

search = VideosSearch('Watermelon Sugar', limit=1)
result = search.result()
```
**Output:**
```json
{
    "result": [
        {
            "type": "video",
            "id": "E07s5ZYygMg",
            "title": "Harry Styles - Watermelon Sugar (Official Video)",
            "publishedTime": "6 months ago",
            "duration": "3:09",
            "viewCount": {
                "text": "162,235,006 views",
                "short": "162M views"
            },
            "thumbnails": [
                {
                    "url": "https://i.ytimg.com/vi/E07s5ZYygMg/hq720.jpg",
                    "width": 360,
                    "height": 202
                }
            ],
            "channel": {
                "name": "Harry Styles",
                "id": "UCZFWPqqPkFlNwIxcpsLOwew",
                "link": "https://www.youtube.com/channel/UCZFWPqqPkFlNwIxcpsLOwew"
            },
            "link": "https://www.youtube.com/watch?v=E07s5ZYygMg"
        }
    ]
}
```

## ChannelsSearch

### Example 1: Search Channels
```python
from youtubesearchpython import ChannelsSearch

search = ChannelsSearch('Harry Styles', limit=1)
result = search.result()
```

**Output:**
```json
{
    "result": [
        {
            "type": "channel",
            "id": "UCZFWPqqPkFlNwIxcpsLOwew",
            "title": "Harry Styles",
            "thumbnails": [
                {
                    "url": "https://yt3.ggpht.com/ytc/AAUvwnhR81ocC_KalYEk5ItnJcfMBqaiIpuM1B0lJyg4Rw=s88-c-k-c0x00ffffff-no-rj-mo",
                    "width": 88,
                    "height": 88
                }
            ],
            "videoCount": "7",
            "subscribers": "9.25M subscribers",
            "link": "https://www.youtube.com/channel/UCZFWPqqPkFlNwIxcpsLOwew"
        }
    ]
}
```

## PlaylistsSearch

### Example 1: Search Playlists
```python
from youtubesearchpython import PlaylistsSearch

search = PlaylistsSearch('Harry Styles', limit=1)
result = search.result()
```

**Output:**
```json
{
    "result": [
        {
            "type": "playlist",
            "id": "PL-Rt4gIwHnyvxpEl-9Le0ePztR7WxGDGV",
            "title": "fine line harry styles full album lyrics",
            "videoCount": "12",
            "channel": {
                "name": "ourmemoriestonight",
                "id": "UCZCmb5a8LE9LMxW9I3-BFjA",
                "link": "https://www.youtube.com/channel/UCZCmb5a8LE9LMxW9I3-BFjA"
            },
            "link": "https://www.youtube.com/playlist?list=PL-Rt4gIwHnyvxpEl-9Le0ePztR7WxGDGV"
        }
    ]
}
```

## Suggestions

### Example 1: Get Suggestions
```python
from youtubesearchpython import Suggestions

sug = Suggestions(language='en', region='US')
result = sug.get('Harry Styles')
```

**Output:**
```json
{
    "result": [
        "harry styles",
        "harry styles treat people with kindness",
        "harry styles golden music video",
        "harry styles interview",
        "harry styles adore you",
        "harry styles watermelon sugar"
    ]
}
```

## Video

### Example 1: Get Video Details
```python
from youtubesearchpython import Video

video = Video.get('https://youtu.be/8of5w7RgcTc?si=_jCtUd2DkVMn06Zm ko')
```

**Output:** Returns complete video information including title, description, views, formats, etc.

## Playlist

### Example 1: Get Playlist Details
```python
from youtubesearchpython import Playlist

playlist = Playlist.get('https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK')
```

**Output:** Returns playlist information including title, video count, channel details, and list of videos.

## Comments

### Example 1: Get Comments
```python
from youtubesearchpython import Comments
# video_id 
comments = Comments.get('8of5w7RgcTc')
```

**Output:** Returns list of comments with author information, content, likes, and reply counts.

## StreamURLFetcher

### Example 1: Get Stream URL
```python
from youtubesearchpython import StreamURLFetcher, Video

fetcher = StreamURLFetcher()
fetcher.getJavaScript()
video = Video.get('https://www.youtube.com/watch?v=aqz-KE-bpKQ')
url = fetcher.get(video, 251)
```

**Output:** Returns direct stream URL for the specified itag.

---

**Note:** All example outputs are representative. Actual data will vary based on current YouTube content.

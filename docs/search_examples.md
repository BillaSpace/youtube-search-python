# Search Classes Examples

## VideosSearch

### Basic Usage
```python
from youtubesearchpython import VideosSearch

search = VideosSearch('Watermelon Sugar', limit=1)
print(search.result())
```

### Example Output Structure
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
            "thumbnails": [...],
            "descriptionSnippet": [...],
            "channel": {
                "name": "Harry Styles",
                "id": "UCZFWPqqPkFlNwIxcpsLOwew",
                "thumbnails": [...],
                "link": "https://www.youtube.com/channel/..."
            },
            "link": "https://www.youtube.com/watch?v=E07s5ZYygMg"
        }
    ]
}
```

## ChannelsSearch

### Basic Usage
```python
from youtubesearchpython import ChannelsSearch

search = ChannelsSearch('Harry Styles', limit=1)
print(search.result())
```

### Example Output Structure
```json
{
    "result": [
        {
            "type": "channel",
            "id": "UCZFWPqqPkFlNwIxcpsLOwew",
            "title": "Harry Styles",
            "thumbnails": [...],
            "videoCount": "7",
            "descriptionSnippet": null,
            "subscribers": "9.25M subscribers",
            "link": "https://www.youtube.com/channel/..."
        }
    ]
}
```

## PlaylistsSearch

### Basic Usage
```python
from youtubesearchpython import PlaylistsSearch

search = PlaylistsSearch('Harry Styles', limit=1)
print(search.result())
```

### Example Output Structure
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
                "link": "https://www.youtube.com/channel/..."
            },
            "thumbnails": [...],
            "link": "https://www.youtube.com/playlist?list=..."
        }
    ]
}
```

## ChannelSearch

### Basic Usage
```python
from youtubesearchpython import ChannelSearch

# Search within a specific channel
search = ChannelSearch('Watermelon Sugar', "UCZFWPqqPkFlNwIxcpsLOwew")
print(search.result())
```

### Example Output Structure
```json
{
    "result": [
        {
            "id": "WMcIfZuRuU8",
            "thumbnails": {...},
            "title": "Harry Styles – Watermelon Sugar (Lost Tour Visual)",
            "descriptionSnippet": "This video is dedicated to touching...",
            "uri": "/watch?v=WMcIfZuRuU8",
            "views": {
                "precise": "3,888,287 views",
                "simple": "3.8M views",
                "approximate": "3.8 million views"
            },
            "duration": {
                "simpleText": "2:55",
                "text": "2 minutes, 55 seconds"
            },
            "published": "10 months ago",
            "channel": {...},
            "type": "video"
        }
    ]
}
```

## CustomSearch

### Basic Usage with Filters
```python
from youtubesearchpython import CustomSearch, VideoSortOrder

# Search with custom sort order
search = CustomSearch('Harry Styles', VideoSortOrder.viewCount, limit=1)
print(search.result())
```

### Available Filters
- `SearchMode.videos` - Only videos
- `SearchMode.channels` - Only channels
- `SearchMode.playlists` - Only playlists
- `SearchMode.livestreams` - Only live streams

### Upload Date Filters
- `VideoUploadDateFilter.lastHour`
- `VideoUploadDateFilter.today`
- `VideoUploadDateFilter.thisWeek`
- `VideoUploadDateFilter.thisMonth`
- `VideoUploadDateFilter.thisYear`

### Duration Filters
- `VideoDurationFilter.short` - Under 4 minutes
- `VideoDurationFilter.long` - Over 20 minutes

### Sort Orders
- `VideoSortOrder.relevance` - Most relevant (default)
- `VideoSortOrder.uploadDate` - Recently uploaded
- `VideoSortOrder.viewCount` - Most viewed
- `VideoSortOrder.rating` - Highest rated

## Search (Combined)

### Basic Usage
```python
from youtubesearchpython import Search

# Searches for videos, channels, and playlists
search = Search('Watermelon Sugar', limit=20)
print(search.result())
```

Returns mixed results containing videos, channels, and playlists.

## Pagination

All search classes support pagination with the `next()` method:

```python
search = VideosSearch('NoCopyrightSounds', limit=10)
print(search.result())

# Get next page
search.next()
print(search.result())
```

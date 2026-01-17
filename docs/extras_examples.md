# Video, Playlist, and Other Extras Examples

## Video.get()

### Basic Usage
```python
from youtubesearchpython import Video, ResultMode

# Get video information
video = Video.get("E07s5ZYygMg", mode=ResultMode.dict)
print(video)
```

### Example Output Structure
```json
{
    "id": "E07s5ZYygMg",
    "title": "Harry Styles - Watermelon Sugar (Official Video)",
    "viewCount": {"text": "170389228"},
    "thumbnails": [...],
    "description": "Full video description...",
    "channel": {
        "name": "HarryStylesVEVO",
        "id": "UCbOCbp5gXL8jigIBZLqMPrw",
        "link": "https://www.youtube.com/channel/..."
    },
    "averageRating": 4.9043722,
    "keywords": [...],
    "publishDate": "2020-05-18",
    "uploadDate": "2020-05-18",
    "link": "https://www.youtube.com/watch?v=E07s5ZYygMg",
    "streamingData": {
        "expiresInSeconds": "21540",
        "formats": [...],
        "adaptiveFormats": [...]
    }
}
```

### Key Fields
- `id` - Video ID
- `title` - Video title
- `viewCount` - View count information
- `thumbnails` - Array of thumbnail objects with different sizes
- `description` - Full video description
- `channel` - Channel information (name, id, link)
- `keywords` - Array of video keywords/tags
- `publishDate` / `uploadDate` - Publication dates
- `streamingData` - Contains formats and adaptiveFormats for streaming

## Video.getFormats()

### Basic Usage
```python
from youtubesearchpython import Video

# Get only streaming formats
formats = Video.getFormats("E07s5ZYygMg")
print(formats)
```

Returns only the `streamingData` portion with formats and adaptiveFormats.

## Playlist.get()

### Basic Usage
```python
from youtubesearchpython import Playlist

# Get playlist information
playlist = Playlist.get("https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK")
print(playlist)
```

### Example Output Structure
```json
{
    "id": "PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK",
    "title": "NCS : The Best Of House",
    "videoCount": "86",
    "viewCount": "168,723,680 views",
    "thumbnails": [...],
    "channel": {
        "name": "NoCopyrightSounds",
        "id": "UC_aEa8K-EOJ3D6gOs7HcyNg",
        "link": "https://www.youtube.com/channel/..."
    },
    "videos": [
        {
            "id": "K4DyBUG242c",
            "title": "Janji - Heroes Tonight (feat. Johnning)",
            "thumbnails": [...],
            "channel": {...},
            "duration": "3:29",
            "link": "https://www.youtube.com/watch?v=..."
        },
        ...
    ]
}
```

### Pagination
```python
playlist = Playlist.get("playlist_url_or_id")
print(playlist)

# Get more videos
playlist_obj = Playlist("playlist_url_or_id")
while playlist_obj.hasMoreVideos:
    playlist_obj.getNextVideos()
    print(playlist_obj.result())
```

## Suggestions.get()

### Basic Usage
```python
from youtubesearchpython import Suggestions

# Get search suggestions
suggestions = Suggestions.get("Arijit Singh", language='en', region='US')
print(suggestions)
```

### Example Output
```json
{
    "result": [
        "arijit singh",
        "arijit singh songs",
        "arijit singh new song",
        "arijit singh live",
        "arijit singh interview",
        ...
    ]
}
```

## Hashtag.get()

### Basic Usage
```python
from youtubesearchpython import Hashtag

# Get videos for a hashtag
hashtag = Hashtag.get("#python")
print(hashtag)
```

Returns videos associated with the specified hashtag.

## Comments.get()

### Basic Usage
```python
from youtubesearchpython import Comments

# Get comments for a video
comments = Comments.get("https://www.youtube.com/watch?v=aqz-KE-bpKQ")
print(comments)
```

### Example Output Structure
```json
{
    "result": [
        {
            "author": "@username",
            "likes": "1.2K",
            "content": "Comment text...",
            "published": "2 months ago",
            "isLiked": false
        },
        ...
    ]
}
```

## Transcript.get()

### Basic Usage
```python
from youtubesearchpython import Transcript

# Get transcript/captions
transcript = Transcript.get("https://www.youtube.com/watch?v=aqz-KE-bpKQ")
print(transcript)
```

### Example Output Structure
```json
{
    "segments": [
        {
            "text": "Transcript text",
            "start": 0.0,
            "duration": 2.5,
            "startMs": "0",
            "endMs": "2500"
        },
        ...
    ],
    "languages": [
        {
            "languageCode": "en",
            "language": "English",
            "isGenerated": false
        },
        ...
    ]
}
```

## Channel.get()

### Basic Usage
```python
from youtubesearchpython import Channel

# Get channel information
channel = Channel.get("UCZFWPqqPkFlNwIxcpsLOwew")
print(channel)
```

### Example Output Structure
```json
{
    "id": "UCZFWPqqPkFlNwIxcpsLOwew",
    "title": "Harry Styles",
    "description": "Channel description...",
    "thumbnails": [...],
    "subscriberCount": "9.25M subscribers",
    "videoCount": "7",
    "views": "Total views",
    "link": "https://www.youtube.com/channel/..."
}
```

## ResultMode Options

- `ResultMode.dict` - Returns Python dictionary (default)
- `ResultMode.json` - Returns JSON string

```python
from youtubesearchpython import Video, ResultMode

# Get as JSON string
video_json = Video.get("video_id", mode=ResultMode.json)

# Get as dictionary
video_dict = Video.get("video_id", mode=ResultMode.dict)
```

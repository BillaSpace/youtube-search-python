<!-- ========================= -->
<!-- youtube-search-python Revamped -->
<!-- ========================= -->

<p align="center">
  <img src="https://files.catbox.moe/rbt2je.jpg" alt="youtube-search-python" style="border-radius: 18px; max-width: 100%; height: auto;" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/BillaSpace/youtube-search-python?style=for-the-badge" />
  <img src="https://img.shields.io/github/forks/BillaSpace/youtube-search-python?style=for-the-badge" />
  <img src="https://img.shields.io/github/watchers/BillaSpace/youtube-search-python?style=for-the-badge" />
</p>

<h1 align="center">youtube-search-python v2.0 [Revamped]</h1>

<p align="center">
  A revived and improved fork of <code>youtube-search-python</code> focused on better reliability, compatibility, and maintained fixes.
</p>

<p align="center">
  <a href="https://github.com/BillaSpace/youtube-search-python">Repository</a> •
  <a href="https://github.com/BillaSpace">GitHub Profile</a>
</p>

---

## About

This project is a **revamped** version of the original `youtube-search-python` library that lets you search YouTube (sync / async) and fetch video, channel, and playlist metadata **without** using YouTube Data API v3.

The original upstream project `alexmercerind/youtube-search-python` is archived and read-only.

⭐ Star the repo • 🍴 Fork it • 📢 Share it  
If real usage is observed, this revamped project will be officially released on **PyPI** as: 
```yt-search-python```

## What is Fixed ✳️ or Updated ? 

- 📱 **ANDROID client default** - Video classes now use ANDROID client by default for better compatibility and direct URL access
- 🔄 **Stream URL improvements** - Enhanced age-restricted video handling with ANDROID fallback and serverAbrStreamingUrl support
- 🧹 **URL cleaning** - Automatic URL parameter cleaning for proper video ID extraction
- 🔢 **Updated client versions** - Bumped ANDROID to 19.02.39 and MWEB to 2.20241210.01.00
- 🐛 **Bug fixes** - Fixed Video ID extraction, Transcript null handling, ChannelSearch parsing, Comments continuation, and Suggestions JSON parsing
- ⚡ **Async improvements** - Fixed Playlist async initialization and removed conflicting async methods from sync module
- 🔧 **Error handling** - Improved error messages and fallback mechanisms
- ⚙️ **httpx 0.28+ compatibility** - Removed deprecated `proxies` parameter usage, now fully compatible with httpx >= 0.28.0
- ✨ **Async Video methods** - Added async methods for `Video.get()`, `Video.getInfo()`, and `Video.getFormats()`
- 🔧 **API fixes** - Fixed YouTube API 400 errors with proper request format
- 📝 **Documentation updates** - Updated README and marked as actively maintained fork


## Installation

### edit your requirements.txt & replace with
```git+https://github.com/BillaSpace/youtube-search-python.git```

### locally clone this repository under your project
``` git clone https://github.com/BillaSpace/youtube-search-python```

### Using pip [ Revamped Version ]
### don't use this for now as I'll release pypi v. later there
```yt-search-python```

### Using pip [ old version ]
```pip install youtube-search-python```

This installs the published PyPI package name. [web:2]

> If you are using features like `StreamURLFetcher`, you may need extra dependencies (e.g., `yt-dlp`) depending on the library version you’re running. [web:2]

```pip install yt-dlp```


### Requirements

- Python 3.10 or higher 
- `httpx>=0.28.1` (installed automatically)
  

#### Search for only videos [SYNC]

```python
from youtubesearchpython import VideosSearch

videosSearch = VideosSearch('NoCopyrightSounds', limit = 2)

print(videosSearch.result())
```

<details>
 <summary> Example Result</summary>

```json
{
    "result": [
        {
            "type": "video",
            "id": "K4DyBUG242c",
            "title": "Cartoon - On & On (feat. Daniel Levi) [NCS Release]",
            "publishedTime": "5 years ago",
            "duration": "3:28",
            "viewCount": {
                "text": "389,673,774 views",
                "short": "389M views"
            },
            "thumbnails": [
                {
                    "url": "https://i.ytimg.com/vi/K4DyBUG242c/hqdefault.jpg?sqp=-oaymwEjCOADEI4CSFryq4qpAxUIARUAAAAAGAElAADIQj0AgKJDeAE=&rs=AOn4CLBkTusCwcZQlmVAaRQ5rH-mvBuA1g",
                    "width": 480,
                    "height": 270
                }
            ],
            "richThumbnail": {
                "url": "https://i.ytimg.com/an_webp/K4DyBUG242c/mqdefault_6s.webp?du=3000&sqp=COCn64IG&rs=AOn4CLBeYxeJ_5lME4jXbFQlv7kIN37kmw",
                "width": 320,
                "height": 180
            },
            "descriptionSnippet": [
                {
                    "text": "NCS: Music Without Limitations NCS Spotify: http://spoti.fi/NCS Free Download / Stream: http://ncs.io/onandon \u25bd Connect with\u00a0..."
                }
            ],
            "channel": {
                "name": "NoCopyrightSounds",
                "id": "UC_aEa8K-EOJ3D6gOs7HcyNg",
                "thumbnails": [
                    {
                        "url": "https://yt3.ggpht.com/a-/AOh14GhS0G5FwV8rMhVCUWSDp36vWEvnNs5Vl97Zww=s68-c-k-c0x00ffffff-no-rj-mo",
                        "width": 68,
                        "height": 68
                    }
                ],
                "link": "https://www.youtube.com/channel/UC_aEa8K-EOJ3D6gOs7HcyNg"
            },
            "accessibility": {
                "title": "Cartoon - On & On (feat. Daniel Levi) [NCS Release] by NoCopyrightSounds 5 years ago 3 minutes, 28 seconds 389,673,774 views",
                "duration": "3 minutes, 28 seconds"
            },
            "link": "https://www.youtube.com/watch?v=K4DyBUG242c",
            "shelfTitle": null
        },
        {
            "type": "video",
            "id": "yJg-Y5byMMw",
            "title": "Warriyo - Mortals (feat. Laura Brehm) [NCS Release]",
            "publishedTime": "3 years ago",
            "duration": "3:50",
            "viewCount": {
                "text": "153,353,801 views",
                "short": "153M views"
            },
            "thumbnails": [
                {
                    "url": "https://i.ytimg.com/vi/yJg-Y5byMMw/hqdefault.jpg?sqp=-oaymwEjCOADEI4CSFryq4qpAxUIARUAAAAAGAElAADIQj0AgKJDeAE=&rs=AOn4CLDY-mve79IweErMo-71AsKEIB1m0A",
                    "width": 480,
                    "height": 270
                }
            ],
            "richThumbnail": {
                "url": "https://i.ytimg.com/an_webp/K4DyBUG242c/mqdefault_6s.webp?du=3000&sqp=COCn64IG&rs=AOn4CLBeYxeJ_5lME4jXbFQlv7kIN37kmw",
                "width": 320,
                "height": 180
            },
            "descriptionSnippet": [
                {
                    "text": "NCS: Music Without Limitations NCS Spotify: http://spoti.fi/NCS Free Download / Stream: http://ncs.io/mortals Connect with NCS:\u00a0..."
                }
            ],
            "channel": {
                "name": "NoCopyrightSounds",
                "id": "UC_aEa8K-EOJ3D6gOs7HcyNg",
                "thumbnails": [
                    {
                        "url": "https://yt3.ggpht.com/a-/AOh14GhS0G5FwV8rMhVCUWSDp36vWEvnNs5Vl97Zww=s68-c-k-c0x00ffffff-no-rj-mo",
                        "width": 68,
                        "height": 68
                    }
                ],
                "link": "https://www.youtube.com/channel/UC_aEa8K-EOJ3D6gOs7HcyNg"
            },
            "accessibility": {
                "title": "Warriyo - Mortals (feat. Laura Brehm) [NCS Release] by NoCopyrightSounds 3 years ago 3 minutes, 50 seconds 153,353,801 views",
                "duration": "3 minutes, 50 seconds"
            },
            "link": "https://www.youtube.com/watch?v=yJg-Y5byMMw",
            "shelfTitle": null
        }
    ]
}
```

</details>

#### Search for only videos [ASYNC]

```python
from youtubesearchpython.__future__ import VideosSearch

videosSearch = VideosSearch('Khamosiyan', limit = 2)
videosResult = await videosSearch.next()
print(videosResult)
```

Read more about usage & examples of Future & newer asynchronous version of this library [HERE](https://github.com/BillSpace/youtube-search-python/tree/main/youtubesearchpython/__future__).


## More Examples

#### Search for only channels

```python
from youtubesearchpython import ChannelsSearch

channelsSearch = ChannelsSearch('NoCopyrightSounds', limit = 10, region = 'US')

print(channelsSearch.result())
```

<details>
 <summary> Example Result</summary>

```json
{
    "result": [
        {
            "type": "channel",
            "id": "UC_aEa8K-EOJ3D6gOs7HcyNg",
            "title": "NoCopyrightSounds",
            "thumbnails": [
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwngbenDpBxHNZlecDGyccHeVyQB22dPZnPuhbW8LHw=s88-c-k-c0x00ffffff-no-rj-mo",
                    "width": 88,
                    "height": 88
                },
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwngbenDpBxHNZlecDGyccHeVyQB22dPZnPuhbW8LHw=s176-c-k-c0x00ffffff-no-rj-mo",
                    "width": 176,
                    "height": 176
                }
            ],
            "videoCount": "850",
            "descriptionSnippet": [
                {
                    "text": "NoCopyrightSounds",
                    "bold": true
                },
                {
                    "text": " is a copyright free / stream safe record label, providing free to use music to the content creator community."
                }
            ],
            "subscribers": "28.7M subscribers",
            "link": "https://www.youtube.com/channel/UC_aEa8K-EOJ3D6gOs7HcyNg"
        },
        {
            "type": "channel",
            "id": "UCg-vlcyvOyNVPV6Neogmubg",
            "title": "NoCopyrightSounds Hindi",
            "thumbnails": [
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwnjDHXULXSvX7u71Rmb2f-Cqly0ron2F1N3szu8Y=s88-c-k-c0x00ffffff-no-rj-mo",
                    "width": 88,
                    "height": 88
                },
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwnjDHXULXSvX7u71Rmb2f-Cqly0ron2F1N3szu8Y=s176-c-k-c0x00ffffff-no-rj-mo",
                    "width": 176,
                    "height": 176
                }
            ],
            "videoCount": "56",
            "descriptionSnippet": [
                {
                    "text": "The Official NCS HINDI Songs Channel for Nocopyright hindi audios."
                }
            ],
            "subscribers": "13.7K subscribers",
            "link": "https://www.youtube.com/channel/UCg-vlcyvOyNVPV6Neogmubg"
        },
        {
            "type": "channel",
            "id": "UCrL9x8LllOU2LOVgTo951kA",
            "title": "NoCopyrightSounds",
            "thumbnails": [
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwnhXShCsmo9VwL4KC8j3GNHgHyBBJ0RCmbAUKrwg=s88-c-k-c0x00ffffff-no-rj-mo",
                    "width": 88,
                    "height": 88
                },
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwnhXShCsmo9VwL4KC8j3GNHgHyBBJ0RCmbAUKrwg=s176-c-k-c0x00ffffff-no-rj-mo",
                    "width": 176,
                    "height": 176
                }
            ],
            "videoCount": "2",
            "descriptionSnippet": [
                {
                    "text": "NCS [NopCopyrightSounds] is a channel dedicated to promoting the best FREE DOWNLOAD music on the net. Every track\u00a0..."
                }
            ],
            "subscribers": "1.71K subscribers",
            "link": "https://www.youtube.com/channel/UCrL9x8LllOU2LOVgTo951kA"
        },
        {
            "type": "channel",
            "id": "UCYZvaL6G3m4-UbvWGlyFeLg",
            "title": "NoCopyrightSounds",
            "thumbnails": [
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwnisxA4V_U0Ffh0K-cdnqwGZjs62hKv2-IAfzIqc=s88-c-k-c0x00ffffff-no-rj-mo",
                    "width": 88,
                    "height": 88
                },
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwnisxA4V_U0Ffh0K-cdnqwGZjs62hKv2-IAfzIqc=s176-c-k-c0x00ffffff-no-rj-mo",
                    "width": 176,
                    "height": 176
                }
            ],
            "videoCount": "33",
            "descriptionSnippet": null,
            "subscribers": null,
            "link": "https://www.youtube.com/channel/UCYZvaL6G3m4-UbvWGlyFeLg"
        },
        {
            "type": "channel",
            "id": "UCi7xVhyWWf2eTc0GO0Ty9HQ",
            "title": "NoCopyrightSounds",
            "thumbnails": [
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwngOJ2zbLEkNs96PNp0g9h27l64mwRFhR1vZ9W7u=s88-c-k-c0x00ffffff-no-rj-mo",
                    "width": 88,
                    "height": 88
                },
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwngOJ2zbLEkNs96PNp0g9h27l64mwRFhR1vZ9W7u=s176-c-k-c0x00ffffff-no-rj-mo",
                    "width": 176,
                    "height": 176
                }
            ],
            "videoCount": "1 video",
            "descriptionSnippet": null,
            "subscribers": "2 subscribers",
            "link": "https://www.youtube.com/channel/UCi7xVhyWWf2eTc0GO0Ty9HQ"
        },
        {
            "type": "channel",
            "id": "UCOSiFTIAReRzkPBXaQAuXCQ",
            "title": "NoCopyrightSounds",
            "thumbnails": [
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwng1UBDlLdYyqTofL6x_5hqPMTFnMXxAN9C9_t8Y=s88-c-k-c0x00ffffff-no-rj-mo",
                    "width": 88,
                    "height": 88
                },
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwng1UBDlLdYyqTofL6x_5hqPMTFnMXxAN9C9_t8Y=s176-c-k-c0x00ffffff-no-rj-mo",
                    "width": 176,
                    "height": 176
                }
            ],
            "videoCount": "8",
            "descriptionSnippet": [
                {
                    "text": "YGW MEDIA GROUP 04."
                }
            ],
            "subscribers": "11 subscribers",
            "link": "https://www.youtube.com/channel/UCOSiFTIAReRzkPBXaQAuXCQ"
        },
        {
            "type": "channel",
            "id": "UCSFpIv5SZlg4ub_IWgGKkIA",
            "title": "NoCopyrightSounds Lyrics",
            "thumbnails": [
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwng_J1igSuKFWowZ8OFpT1dPCPgzqEvVkGImwM3Dpg=s88-c-k-c0x00ffffff-no-rj-mo",
                    "width": 88,
                    "height": 88
                },
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwng_J1igSuKFWowZ8OFpT1dPCPgzqEvVkGImwM3Dpg=s176-c-k-c0x00ffffff-no-rj-mo",
                    "width": 176,
                    "height": 176
                }
            ],
            "videoCount": "82",
            "descriptionSnippet": [
                {
                    "text": "Welcome To "
                },
                {
                    "text": "NoCopyrightSounds",
                    "bold": true
                },
                {
                    "text": " Lyrics "
                },
                {
                    "text": "NoCopyrightSounds",
                    "bold": true
                },
                {
                    "text": " lyrics provides music from a variety of licenses that are certainly\u00a0..."
                }
            ],
            "subscribers": null,
            "link": "https://www.youtube.com/channel/UCSFpIv5SZlg4ub_IWgGKkIA"
        },
        {
            "type": "channel",
            "id": "UCcE-Gvu5j55MdREM1a4_EqA",
            "title": "NoCopyrightSounds",
            "thumbnails": [
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwnhbzZwQIVabdGA1SteO2BCtmrG3uT_cpzmJvtBY=s88-c-k-c0x00ffffff-no-rj-mo",
                    "width": 88,
                    "height": 88
                },
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwnhbzZwQIVabdGA1SteO2BCtmrG3uT_cpzmJvtBY=s176-c-k-c0x00ffffff-no-rj-mo",
                    "width": 176,
                    "height": 176
                }
            ],
            "videoCount": "6",
            "descriptionSnippet": null,
            "subscribers": "166 subscribers",
            "link": "https://www.youtube.com/channel/UCcE-Gvu5j55MdREM1a4_EqA"
        },
        {
            "type": "channel",
            "id": "UCCOWDgeFmwW--woYtCYws8Q",
            "title": "NoCopyrightSounds 1 HOUR",
            "thumbnails": [
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwnipj6lV7p6i8Mq7uAlDj5qHsQkiwgwdtPs_vCKy=s88-c-k-c0x00ffffff-no-rj-mo",
                    "width": 88,
                    "height": 88
                },
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwnipj6lV7p6i8Mq7uAlDj5qHsQkiwgwdtPs_vCKy=s176-c-k-c0x00ffffff-no-rj-mo",
                    "width": 176,
                    "height": 176
                }
            ],
            "videoCount": "689",
            "descriptionSnippet": [
                {
                    "text": "NoCopyrightSounds",
                    "bold": true
                },
                {
                    "text": " is a record label dedicated to releasing FREE music for the sole purpose of providing creators with the finest\u00a0..."
                }
            ],
            "subscribers": null,
            "link": "https://www.youtube.com/channel/UCCOWDgeFmwW--woYtCYws8Q"
        },
        {
            "type": "channel",
            "id": "UCSI5zGuirscirQc6UOy_yww",
            "title": "NoCopyrightSounds",
            "thumbnails": [
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwni92w-CAOUnlNfyIVxdCmvMoQmENZbw1wjFOQKjug=s88-c-k-c0x00ffffff-no-rj-mo",
                    "width": 88,
                    "height": 88
                },
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwni92w-CAOUnlNfyIVxdCmvMoQmENZbw1wjFOQKjug=s176-c-k-c0x00ffffff-no-rj-mo",
                    "width": 176,
                    "height": 176
                }
            ],
            "videoCount": "29",
            "descriptionSnippet": [
                {
                    "text": "NoCopyrightSounds",
                    "bold": true
                },
                {
                    "text": " is a Record Label dedicated to giving a platform to the next generation of Artists in Electronic Music,\u00a0..."
                }
            ],
            "subscribers": null,
            "link": "https://www.youtube.com/channel/UCSI5zGuirscirQc6UOy_yww"
        }
    ]
}
```

</details>

#### Search for only playlists

```python
from youtubesearchpython import PlaylistsSearch

playlistsSearch = PlaylistsSearch('NoCopyrightSounds', limit = 1)

print(playlistsSearch.result())
```

<details>
 <summary> Example Result</summary>

```json
{
    "result": [
        {
            "type": "playlist",
            "id": "PLGde6kPURikrUszpUgafLZiOgr5o7pBF0",
            "title": "NoCopyrightSounds",
            "videoCount": "6",
            "channel": {
                "name": "Bruno Neves",
                "id": "UCtqpCV2HkMCSi5InFNBNv0g",
                "link": "https://www.youtube.com/channel/UCtqpCV2HkMCSi5InFNBNv0g"
            },
            "thumbnails": [
                {
                    "url": "https://i.ytimg.com/vi/K4DyBUG242c/hqdefault.jpg?sqp=-oaymwEWCKgBEF5IWvKriqkDCQgBFQAAiEIYAQ==&rs=AOn4CLBw6Bf7J9COwl1LxqhmGbSQgdFj3w",
                    "width": 168,
                    "height": 94
                },
                {
                    "url": "https://i.ytimg.com/vi/K4DyBUG242c/hqdefault.jpg?sqp=-oaymwEWCMQBEG5IWvKriqkDCQgBFQAAiEIYAQ==&rs=AOn4CLBjJCIZlrSGSPjc-7yKc0QQuWRdhg",
                    "width": 196,
                    "height": 110
                },
                {
                    "url": "https://i.ytimg.com/vi/K4DyBUG242c/hqdefault.jpg?sqp=-oaymwEXCPYBEIoBSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLCRIQ0IochteE0KM2tlK2PVVAQKhA",
                    "width": 246,
                    "height": 138
                },
                {
                    "url": "https://i.ytimg.com/vi/K4DyBUG242c/hqdefault.jpg?sqp=-oaymwEXCNACELwBSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLAQYBDz8gWKw_q4Zyb_H6J_DdZCaA",
                    "width": 336,
                    "height": 188
                }
            ],
            "link": "https://www.youtube.com/playlist?list=PLGde6kPURikrUszpUgafLZiOgr5o7pBF0"
        }
    ]
}
```

</details>

#### Search with a filter or sort

```python
from youtubesearchpython import *

customSearch = CustomSearch('NoCopyrightSounds', VideoSortOrder.uploadDate, limit = 1)

print(customSearch.result())
```

<details>
 <summary> Example Result</summary>

```json
{
    "result": [
        {
            "type": "video",
            "id": "k8-drvf4Ruo",
            "title": "Ambient Music 2020 \ud83c\udfb5 voices \ud83c\udfb5 NoCopyrightSounds",
            "publishedTime": "30 minutes ago",
            "duration": "2:29",
            "viewCount": {
                "text": "4 views",
                "short": "4 views"
            },
            "thumbnails": [
                {
                    "url": "https://i.ytimg.com/vi/k8-drvf4Ruo/hq720.jpg?sqp=-oaymwEjCOgCEMoBSFryq4qpAxUIARUAAAAAGAElAADIQj0AgKJDeAE=&rs=AOn4CLDomB-9ivVHpwci6STdNAqQBMBzJA",
                    "width": 360,
                    "height": 202
                },
                {
                    "url": "https://i.ytimg.com/vi/k8-drvf4Ruo/hq720.jpg?sqp=-oaymwEXCNAFEJQDSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLCPrVwYygJ3627h8F-oU3khKehm4g",
                    "width": 720,
                    "height": 404
                }
            ],
            "richThumbnail": {
                "url": "https://i.ytimg.com/an_webp/K4DyBUG242c/mqdefault_6s.webp?du=3000&sqp=COCn64IG&rs=AOn4CLBeYxeJ_5lME4jXbFQlv7kIN37kmw",
                "width": 320,
                "height": 180
            },
            "descriptionSnippet": [
                {
                    "text": "Don't forget to like & share if you enjoy it."
                }
            ],
            "channel": {
                "name": "Sky Sound",
                "id": "UCQT8W5qZn7TCZBW39dVoaBw",
                "thumbnails": [
                    {
                        "url": "https://yt3.ggpht.com/a-/AOh14GhxrkkF27iL3sLTKzWLu3rrO-qtQ7uMPg4SqA=s68-c-k-c0x00ffffff-no-rj-mo",
                        "width": 68,
                        "height": 68
                    }
                ],
                "link": "https://www.youtube.com/channel/UCQT8W5qZn7TCZBW39dVoaBw"
            },
            "accessibility": {
                "title": "Ambient Music 2020 \ud83c\udfb5 voices \ud83c\udfb5 NoCopyrightSounds by Sky Sound 30 minutes ago 2 minutes, 29 seconds 4 views",
                "duration": "2 minutes, 29 seconds"
            },
            "link": "https://www.youtube.com/watch?v=k8-drvf4Ruo",
            "shelfTitle": null
        }
    ]
}
```

</details>

#### Search for everything

```python
from youtubesearchpython import Search

allSearch = Search('NoCopyrightSounds', limit = 1)

print(allSearch.result())
```

<details>
 <summary> Example Result</summary>

```json
{
    "result": [
        {
            "type": "channel",
            "id": "UC_aEa8K-EOJ3D6gOs7HcyNg",
            "title": "NoCopyrightSounds",
            "thumbnails": [
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwngbenDpBxHNZlecDGyccHeVyQB22dPZnPuhbW8LHw=s88-c-k-c0x00ffffff-no-rj-mo",
                    "width": 88,
                    "height": 88
                },
                {
                    "url": "//yt3.ggpht.com/ytc/AAUvwngbenDpBxHNZlecDGyccHeVyQB22dPZnPuhbW8LHw=s176-c-k-c0x00ffffff-no-rj-mo",
                    "width": 176,
                    "height": 176
                }
            ],
            "videoCount": "850",
            "descriptionSnippet": [
                {
                    "text": "NoCopyrightSounds",
                    "bold": true
                },
                {
                    "text": " is a copyright free / stream safe record label, providing free to use music to the content creator community."
                }
            ],
            "subscribers": "28.7M subscribers",
            "link": "https://www.youtube.com/channel/UC_aEa8K-EOJ3D6gOs7HcyNg"
        },
    ]
}
```

</details>

You may see the [older but identical examples](https://github.com/alexmercerind/youtube-search-python/blob/main/syncExample.py) for more information.



</details>

#### Get all videos of a channel
You can use a Playlist class for that, alongside some helpful functions.
```python
from youtubesearchpython import *

channel_id = "UC_aEa8K-EOJ3D6gOs7HcyNg"
playlist = Playlist(playlist_from_channel_id(channel_id))

print(f'Videos Retrieved: {len(playlist.videos)}')

while playlist.hasMoreVideos:
    print('Getting more videos...')
    playlist.getNextVideos()
    print(f'Videos Retrieved: {len(playlist.videos)}')

print('Found all the videos.')
```

<details>
 <summary> Example Result</summary>

```bash
Videos Retrieved: 100
Getting more videos...
Videos Retrieved: 200
Getting more videos...
Videos Retrieved: 300
Getting more videos...
Videos Retrieved: 400
Getting more videos...
Videos Retrieved: 500
Getting more videos...
Videos Retrieved: 600
Getting more videos...
Videos Retrieved: 700
Getting more videos...
Videos Retrieved: 800
Getting more videos...
Videos Retrieved: 900
Getting more videos...
Videos Retrieved: 1000
Getting more videos...
Videos Retrieved: 1002
Found all the videos.
```

</details>

#### More to the playlists

You can directly instanciate the `Playlist` class as follows to access its information & videos in the `info` and `videos` fields respectively.

YouTube offers only 100 videos in a single request, for getting more videos present in the playlist, you can check `hasMoreVideos` bool to see if playlist contains more videos.
If playlist has more videos, then you can call `getNextVideos` to fetch more videos.

Example below demonstrates a simple way to retrive all videos of a playlist.

```python
from youtubesearchpython import *

playlist = Playlist('https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK')

print(f'Videos Retrieved: {len(playlist.videos)}')

while playlist.hasMoreVideos:
    print('Getting more videos...')
    playlist.getNextVideos()
    print(f'Videos Retrieved: {len(playlist.videos)}')

print('Found all the videos.')
```

<details>
 <summary> Example Result</summary>

```bash
Videos Retrieved: 100
Getting more videos...
Videos Retrieved: 200
Getting more videos...
Videos Retrieved: 209
Found all the videos.
```

</details>

#### Getting search suggestions

```python
from youtubesearchpython import Suggestions

suggestions = Suggestions(language = 'en', region = 'US')

print(suggestions.get('NoCopyrightSounds', mode = ResultMode.json))
```

<details>
 <summary> Example Result</summary>

```json
{
    "result": [
        "nocopyrightsounds",
        "nocopyrightsounds best songs",
        "nocopyrightsounds gaming music",
        "nocopyrightsounds alan walker",
        "nocopyrightsounds fearless",
        "nocopyrightsounds invincible",
        "nocopyrightsounds background music",
        "nocopyrightsounds instrumental",
        "nocopyrightsounds fade",
        "nocopyrightsounds playlist",
        "nocopyrightsounds on and on",
        "nocopyrightsounds elektronomia",
        "nocopyrightsounds stronger",
        "nocopyrightsounds christmas"
    ]
}
```

</details>

#### Getting videos by hashtag

```python
from youtubesearchpython import Hashtag

hashtag = Hashtag('ncs', limit = 1)

print(hashtag.result())
```

<details>
 <summary> Example Result</summary>

```json
{
    "result": [
        {
            "type": "video",
            "id": "c9FF4Tfj2w8",
            "title": "Ascence - About You [NCS 1 HOUR]",
            "publishedTime": "1 year ago",
            "duration": "1:00:00",
            "viewCount": {
                "text": "226,354 views",
                "short": "226K views"
            },
            "thumbnails": [
                {
                    "url": "https://i.ytimg.com/vi/c9FF4Tfj2w8/hqdefault.jpg?sqp=-oaymwEbCKgBEF5IVfKriqkDDggBFQAAiEIYAXABwAEG&rs=AOn4CLA8V3x_PigkymVQxQcptr8Wfz20-A",
                    "width": 168,
                    "height": 94
                },
                {
                    "url": "https://i.ytimg.com/vi/c9FF4Tfj2w8/hqdefault.jpg?sqp=-oaymwEbCMQBEG5IVfKriqkDDggBFQAAiEIYAXABwAEG&rs=AOn4CLABh5Ylb5wbuulOAWLcSYtfYQKiAQ",
                    "width": 196,
                    "height": 110
                },
                {
                    "url": "https://i.ytimg.com/vi/c9FF4Tfj2w8/hqdefault.jpg?sqp=-oaymwEcCPYBEIoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLAykmTivOgjlW6a4tKWnLJpL9yqKw",
                    "width": 246,
                    "height": 138
                },
                {
                    "url": "https://i.ytimg.com/vi/c9FF4Tfj2w8/hqdefault.jpg?sqp=-oaymwEcCNACELwBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLC8qRkotPyH9kGGHe29QuyOh-F9KA",
                    "width": 336,
                    "height": 188
                }
            ],
            "richThumbnail": {
                "url": "https://i.ytimg.com/an_webp/c9FF4Tfj2w8/mqdefault_6s.webp?du=3000&sqp=CPGE-YgG&rs=AOn4CLAJAC5zmDOtySflLFMQpAoaPUqHjA",
                "width": 320,
                "height": 180
            },
            "descriptionSnippet": null,
            "channel": {
                "name": "Good Vibes Music",
                "id": "UChCPI0uvKwrkYhTEx8UVrnQ",
                "thumbnails": [
                    {
                        "url": "https://yt3.ggpht.com/ytc/AKedOLSFYY0mvwL0DbRzddMAQdbgFshM42R5byhI9FiEBQ=s68-c-k-c0x00ffffff-no-rj",
                        "width": 68,
                        "height": 68
                    }
                ],
                "link": "https://www.youtube.com/channel/UChCPI0uvKwrkYhTEx8UVrnQ"
            },
            "accessibility": {
                "title": "Ascence - About You [NCS 1 HOUR] by Good Vibes Music 1 year ago 1 hour 226,354 views",
                "duration": "1 hour"
            },
            "link": "https://www.youtube.com/watch?v=c9FF4Tfj2w8",
            "shelfTitle": null
        }
    ]
}
```

</details>

#### Getting videos and playlists in specific channel

```python
from youtubesearchpython import ChannelSearch,ResultMode

search = ChannelSearch('Watermelon Sugar', "UCZFWPqqPkFlNwIxcpsLOwew")
print(search.result(mode = ResultMode.json))
```

<details>
 <summary> Example Result</summary>

```json
{
    "result": [
        {
            "id": "WMcIfZuRuU8",
            "thumbnails": {
                "normal": [
                    {
                        "url": "https://i.ytimg.com/vi/WMcIfZuRuU8/hqdefault.jpg?sqp=-oaymwEbCKgBEF5IVfKriqkDDggBFQAAiEIYAXABwAEG&rs=AOn4CLClFg6C1r5NfTQy7TYUq6X5qHUmPA",
                        "width": 168,
                        "height": 94
                    },
                    {
                        "url": "https://i.ytimg.com/vi/WMcIfZuRuU8/hqdefault.jpg?sqp=-oaymwEbCMQBEG5IVfKriqkDDggBFQAAiEIYAXABwAEG&rs=AOn4CLAoOyftwY0jLV4geWb5hejULYp3Zw",
                        "width": 196,
                        "height": 110
                    },
                    {
                        "url": "https://i.ytimg.com/vi/WMcIfZuRuU8/hqdefault.jpg?sqp=-oaymwEcCPYBEIoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLCdqkhn7JDwLvRtTNx3jq-olz7k-Q",
                        "width": 246,
                        "height": 138
                    },
                    {
                        "url": "https://i.ytimg.com/vi/WMcIfZuRuU8/hqdefault.jpg?sqp=-oaymwEcCNACELwBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLAhYedsqBFKI0Ra2qzIv9cVoZhfKQ",
                        "width": 336,
                        "height": 188
                    }
                ],
                "rich": null
            },
            "title": "Harry Styles \u2013 Watermelon Sugar (Lost Tour Visual)",
            "descriptionSnippet": "This video is dedicated to touching.\nListen to Harry Styles\u2019 new album \u2018Fine Line\u2019 now: https://HStyles.lnk.to/FineLineAY \n\nFollow Harry Styles:\nFacebook: https://HarryStyles.lnk.to/followFI...",
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
            "channel": {
                "name": "Harry Styles",
                "thumbnails": [
                    {
                        "url": "https://yt3.ggpht.com/ytc/AAUvwnhR81ocC_KalYEk5ItnJcfMBqaiIpuM1B0lJyg4Rw=s88-c-k-c0x00ffffff-no-rj",
                        "width": 68,
                        "height": 68
                    }
                ]
            },
            "type": "video"
        },
    ]
}
```

</details>

#### Getting direct stream URL of a video

This class is able to fetch video URLs without any additional web requests (that's fast), as one might already have same response at the time of showing it to the user.

For making use of this functionality, you must install [yt-dlp](https://github.com/yt-dlp/yt-dlp) as a dependency.
StreamURLFetcher makes slight improvements & changes to YouTube class from [yt-dlp](https://github.com/yt-dlp/yt-dlp).

```py
from youtubesearchpython import *
fetcher = StreamURLFetcher()
video = Video.get("https://www.youtube.com/watch?v=aqz-KE-bpKQ")
url = fetcher.get(video, 251)
print(url)

'''
`getAll` method returns all stream URLs unlike `get` method which needs itag in its second parameter.
'''
```

<details>
 <summary> Example Result</summary>

```json
"https://r6---sn-gwpa-5bgk.googlevideo.com/videoplayback?expire=1610798125&ei=zX8CYITXEIGKz7sP9MWL0AE&ip=2409%3A4053%3A803%3A2b22%3Adc68%3Adfb9%3Aa676%3A26a3&id=o-APBakKSE2_eMDMegtCmeWXfuhhUfAzJTmOCWj4lkEjAM&itag=251&source=youtube&requiressl=yes&mh=aP&mm=31%2C29&mn=sn-gwpa-5bgk%2Csn-gwpa-qxad&ms=au%2Crdu&mv=m&mvi=6&pl=36&initcwndbps=146250&vprv=1&mime=audio%2Fwebm&ns=ULL4mkMO31KDtEhOjkOrmpkF&gir=yes&clen=10210834&dur=634.601&lmt=1544629945422176&mt=1610776131&fvip=6&keepalive=yes&c=WEB&txp=5511222&n=uEjSqtzBZaJyVn&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cdur%2Clmt&sig=AOq0QJ8wRAIgKKIEiwQTgXsdKPEyOckgVPs_LMH6KJoeaYmZic_lelECIHXHs1ZnSP5mgtpffNlIMJM3DhxcvDbA-4udFFE6AmVP&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRQIhAPmhL745RYeL_ffgUJk_xJLC-8riXKMylLTLA_pITYWWAiB2qUIXur8ThW7cLfQ73mIVK61mMZc2ncK6FZWjUHGcUw%3D%3D"
```

</details>

#### Get comments of a video
You can use a Comments class for that.
```python
from youtubesearchpython import *

# You can either pass an ID or a URL
video_id = "_ZdsmLgCVdU"
comments = Comments(video_id)

print(f'Comments Retrieved: {len(comments.comments["result"])}')

while comments.hasMoreComments:
    print('Getting more comments...')
    comments.getNextComments()
    print(f'Comments Retrieved: {len(comments.comments["result"])}')

print('Found all the comments.')
```

<details>
 <summary> Example Result</summary>

```bash
20
Getting more comments...
40
Getting more comments...
60
Getting more comments...
80
Getting more comments...
100
Getting more comments...
...
```

</details>

#### Get first 20 comments of a video
You can use a Comments.get method for that.
```python
from youtubesearchpython import *

# You can either pass an ID or a URL
video_id = "_ZdsmLgCVdU"
comments = Comments.get(video_id)

print(comments)
```

<details>
 <summary> Example Result</summary>

```bash
{
   "result":[
      {
         "id":"Ugh2UTT69BnjaHgCoAEC",
         "author":{
            "id":"UCBykgwvHh2SX5HH7dVWLkqQ",
            "name":"Daikaiju Danielle",
            "thumbnails":[
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLSC8WrgmUHF5l6DYEb8jabim9nE0Ko1vQ_KFOly0w=s48-c-k-c0x00ffffff-no-rj",
                  "width":48,
                  "height":48
               },
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLSC8WrgmUHF5l6DYEb8jabim9nE0Ko1vQ_KFOly0w=s88-c-k-c0x00ffffff-no-rj",
                  "width":88,
                  "height":88
               },
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLSC8WrgmUHF5l6DYEb8jabim9nE0Ko1vQ_KFOly0w=s176-c-k-c0x00ffffff-no-rj",
                  "width":176,
                  "height":176
               }
            ]
         },
         "content":"The boy probably represents youth and the pure, free spirit of being young. When you grow up, it's hard to find that spirit again. You have to search for it.",
         "published":"5 years ago",
         "isLiked":false,
         "authorIsChannelOwner":false,
         "voteStatus":"INDIFFERENT",
         "votes":{
            "simpleText":"5.9K",
            "label":"5.9K likes"
         },
         "replyCount":81
      },
      {
         "id":"UgzyjWeS_wVmoVrcyVZ4AaABAg",
         "author":{
            "id":"UCMMJk2iiIanIFtTwnLK8XBA",
            "name":"naomi",
            "thumbnails":[
               {
                  "url":"https://yt3.ggpht.com/wzrS0agEf0NBFXvcpQJFF-6BwdciRFqzVf_dmgv4Unk7e9AFA7Sb7K7hsLeXdZsOX26J0J4Y=s48-c-k-c0x00ffffff-no-rj",
                  "width":48,
                  "height":48
               },
               {
                  "url":"https://yt3.ggpht.com/wzrS0agEf0NBFXvcpQJFF-6BwdciRFqzVf_dmgv4Unk7e9AFA7Sb7K7hsLeXdZsOX26J0J4Y=s88-c-k-c0x00ffffff-no-rj",
                  "width":88,
                  "height":88
               },
               {
                  "url":"https://yt3.ggpht.com/wzrS0agEf0NBFXvcpQJFF-6BwdciRFqzVf_dmgv4Unk7e9AFA7Sb7K7hsLeXdZsOX26J0J4Y=s176-c-k-c0x00ffffff-no-rj",
                  "width":176,
                  "height":176
               }
            ]
         },
         "content":"Strange that I showed this to my brother three days before his death not knowing I would soon relate to it.",
         "published":"1 year ago",
         "isLiked":false,
         "authorIsChannelOwner":false,
         "voteStatus":"INDIFFERENT",
         "votes":{
            "simpleText":"5.2K",
            "label":"5.2K likes"
         },
         "replyCount":147
      },
      {
         "id":"UgyP3NpP-qA9T80YRVh4AaABAg",
         "author":{
            "id":"UCCekImfpPQw94ZHeQy98S_A",
            "name":"Noura",
            "thumbnails":[
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLSA9_Di2v12v_MycDkKjvhD8D3dRSt9pyZIcCekeg=s48-c-k-c0x00ffffff-no-rj",
                  "width":48,
                  "height":48
               },
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLSA9_Di2v12v_MycDkKjvhD8D3dRSt9pyZIcCekeg=s88-c-k-c0x00ffffff-no-rj",
                  "width":88,
                  "height":88
               },
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLSA9_Di2v12v_MycDkKjvhD8D3dRSt9pyZIcCekeg=s176-c-k-c0x00ffffff-no-rj",
                  "width":176,
                  "height":176
               }
            ]
         },
         "content":"In Arabic when we want to express how much we love and cherish someone we say \"you are my eyes\".. And for some reason that line \"don\\'t you know you got my eyes\" makes me really nostalgic and sad.",
         "published":"1 year ago (edited)",
         "isLiked":false,
         "authorIsChannelOwner":false,
         "voteStatus":"INDIFFERENT",
         "votes":{
            "simpleText":"3.8K",
            "label":"3.8K likes"
         },
         "replyCount":65
      },
      {
         "id":"Ugy-JqQw3w3MXwxGZHZ4AaABAg",
         "author":{
            "id":"UC6irqN4Fk_z-CdK47pkLTgQ",
            "name":"Leo Trombetta",
            "thumbnails":[
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLTogXyBXEX1LAzehhiYyx9amCWGkcMRCaa3e-pEgg=s48-c-k-c0x00ffffff-no-rj",
                  "width":48,
                  "height":48
               },
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLTogXyBXEX1LAzehhiYyx9amCWGkcMRCaa3e-pEgg=s88-c-k-c0x00ffffff-no-rj",
                  "width":88,
                  "height":88
               },
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLTogXyBXEX1LAzehhiYyx9amCWGkcMRCaa3e-pEgg=s176-c-k-c0x00ffffff-no-rj",
                  "width":176,
                  "height":176
               }
            ]
         },
         "content":"As a mother whose had to let her son go for his life to be better, this song is about exactly that. The pain and sacrifice and love and the warm memories you pray they will have of the sweetest moments you've shared when you held them so long ago.. I miss you.",
         "published":"2 years ago",
         "isLiked":false,
         "authorIsChannelOwner":false,
         "voteStatus":"INDIFFERENT",
         "votes":{
            "simpleText":"2K",
            "label":"2K likes"
         },
         "replyCount":23
      },
      {
         "id":"Ugwv8lwT4LS906Y9P1p4AaABAg",
         "author":{
            "id":"UClMs_LKpgCPC9acJQpGRcbQ",
            "name":"Arundhati",
            "thumbnails":[
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLTHadgrB-BvJ2zqtN9_f2ttscQEH0Sc3awtvg73ug=s48-c-k-c0x00ffffff-no-rj",
                  "width":48,
                  "height":48
               },
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLTHadgrB-BvJ2zqtN9_f2ttscQEH0Sc3awtvg73ug=s88-c-k-c0x00ffffff-no-rj",
                  "width":88,
                  "height":88
               },
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLTHadgrB-BvJ2zqtN9_f2ttscQEH0Sc3awtvg73ug=s176-c-k-c0x00ffffff-no-rj",
                  "width":176,
                  "height":176
               }
            ]
         },
         "content":"It’s been 3 years and I still can’t sing that chorus without tearing up",
         "published":"2 years ago",
         "isLiked":false,
         "authorIsChannelOwner":false,
         "voteStatus":"INDIFFERENT",
         "votes":{
            "simpleText":"1K",
            "label":"1K likes"
         },
         "replyCount":16
      },
      {
         "id":"Ugx5NiWjHQI1aGWI8ex4AaABAg",
         "author":{
            "id":"UCeuMECoMfhC9Fyn5veduj1w",
            "name":"dona nova",
            "thumbnails":[
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLQC9P35p4nKLBaoDkWwsGjQCVrrBs_lPVCNsTQ5oPg=s48-c-k-c0x00ffffff-no-rj",
                  "width":48,
                  "height":48
               },
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLQC9P35p4nKLBaoDkWwsGjQCVrrBs_lPVCNsTQ5oPg=s88-c-k-c0x00ffffff-no-rj",
                  "width":88,
                  "height":88
               },
               {
                  "url":"https://yt3.ggpht.com/ytc/AKedOLQC9P35p4nKLBaoDkWwsGjQCVrrBs_lPVCNsTQ5oPg=s176-c-k-c0x00ffffff-no-rj",
                  "width":176,
                  "height":176
               }
            ]
         }
```

</details>

#### Retrieve video transcript
YouTube auto-generates transcripts (subtitles) for videos. You can retrieve those transcripts using Transcript class:
```py
from youtubesearchpython import Transcript

print(Transcript.get("https://www.youtube.com/watch?v=-1xu0IP35FI"))
```

In response, you'll get available languages with `params` parameter. If you want to retrieve a different language, you have to pass the function that parameter. Example:
```py
from youtubesearchpython import Transcript

url = "https://www.youtube.com/watch?v=-1xu0IP35FI"

transcript_en = Transcript.get(url)
# you actually don't have to pass a valid URL in following Transcript call. You can input an empty string, but I do recommend still inputing a valid URL.
transcript_2 = Transcript.get(url, transcript_en["languages"][-1]["params"]) # in my case, it'd output Spanish.
print(transcript_2)
```

<details>
 <summary> Example Result</summary>

```json
{
   "segments":[
      {
         "startMs":"210",
         "endMs":"2129",
         "text":"- When Steve Jobs unveiled the original",
         "startTime":"0:00"
      },
      {
         "startMs":"2130",
         "endMs":"3670",
         "text":"iPhone back in 2007,",
         "startTime":"0:02"
      },
      {
         "startMs":"3670",
         "endMs":"4940",
         "text":"the year I graduated high school,",
         "startTime":"0:03"
      },
      {
         "startMs":"4940",
         "endMs":"7610",
         "text":"he pitched it as a music player, a phone,",
         "startTime":"0:04"
      },
      {
         "startMs":"7610",
         "endMs":"10760",
         "text":"and an internet communicator\nall rolled into one.",
         "startTime":"0:07"
      },
      {
         "startMs":"10760",
         "endMs":"11593",
         "text":"- Are you getting it?",
         "startTime":"0:10"
      },
      ...
   ],
   "languages":[
      {
         "params":"CgstMXh1MElQMzVGSRIOQ2dBU0FtVnVHZ0ElM0QYASozZW5nYWdlbWVudC1wYW5lbC1zZWFyY2hhYmxlLXRyYW5zY3JpcHQtc2VhcmNoLXBhbmVsMAE%3D",
         "selected":true,
         "title":"English"
      },
      {
         "params":"CgstMXh1MElQMzVGSRISQ2dOaGMzSVNBbVZ1R2dBJTNEGAEqM2VuZ2FnZW1lbnQtcGFuZWwtc2VhcmNoYWJsZS10cmFuc2NyaXB0LXNlYXJjaC1wYW5lbDAB",
         "selected":false,
         "title":"English (auto-generated)"
      },
      {
         "params":"CgstMXh1MElQMzVGSRISQ2dBU0JYQjBMVUpTR2dBJTNEGAEqM2VuZ2FnZW1lbnQtcGFuZWwtc2VhcmNoYWJsZS10cmFuc2NyaXB0LXNlYXJjaC1wYW5lbDAB",
         "selected":false,
         "title":"Portuguese (Brazil)"
      },
      {
         "params":"CgstMXh1MElQMzVGSRIQQ2dBU0JtVnpMVFF4T1JvQRgBKjNlbmdhZ2VtZW50LXBhbmVsLXNlYXJjaGFibGUtdHJhbnNjcmlwdC1zZWFyY2gtcGFuZWwwAQ%3D%3D",
         "selected":false,
         "title":"Spanish (Latin America)"
      }
   ]
}
```
</details>


#### Retrieve channel info
```py
from youtubesearchpython import Channel

print(Channel.get("UC_aEa8K-EOJ3D6gOs7HcyNg"))
```

<details>
 <summary> Example Result</summary>

```json
{
    "id": "UC_aEa8K-EOJ3D6gOs7HcyNg",
    "url": "https://www.youtube.com/channel/UC_aEa8K-EOJ3D6gOs7HcyNg",
    "description": "NoCopyrightSounds is a copyright free / stream safe record label, providing free to use music to the content creator community. \n\nWe work with artists from around the world in electronic music, representing genres from House to Dubstep via Trap, Drum & Bass, Electro Pop and more. \n\nNCS Music is free to use for independent Creators and their UGC (User Generated Content) on YouTube & Twitch - always remember to credit the Artist, track and NCS and link back to our original NCS upload.\n\nView our usage policy and some frequently asked questions here: http://ncs.io/UsagePolicy\n\nGrab our new apparel range here: http://ncs.io/Store",
    "title": "NoCopyrightSounds",
    "banners": [
        {
            "url": "https://yt3.ggpht.com/ZdXDhvCVn73Shu-QkqWFoUS_TlZ9MSkAXb8VJBeI6ZKSN6oH4QBvTG2BCfuFRegjXwdp6qH3=w1060-fcrop64=1,00005a57ffffa5a8-k-c0xffffffff-no-nd-rj",
            "width": 1060,
            "height": 175
        },
        {
            "url": "https://yt3.ggpht.com/ZdXDhvCVn73Shu-QkqWFoUS_TlZ9MSkAXb8VJBeI6ZKSN6oH4QBvTG2BCfuFRegjXwdp6qH3=w1138-fcrop64=1,00005a57ffffa5a8-k-c0xffffffff-no-nd-rj",
            "width": 1138,
            "height": 188
        },
        {
            "url": "https://yt3.ggpht.com/ZdXDhvCVn73Shu-QkqWFoUS_TlZ9MSkAXb8VJBeI6ZKSN6oH4QBvTG2BCfuFRegjXwdp6qH3=w1707-fcrop64=1,00005a57ffffa5a8-k-c0xffffffff-no-nd-rj",
            "width": 1707,
            "height": 283
        },
        {
            "url": "https://yt3.ggpht.com/ZdXDhvCVn73Shu-QkqWFoUS_TlZ9MSkAXb8VJBeI6ZKSN6oH4QBvTG2BCfuFRegjXwdp6qH3=w2120-fcrop64=1,00005a57ffffa5a8-k-c0xffffffff-no-nd-rj",
            "width": 2120,
            "height": 351
        },
        {
            "url": "https://yt3.ggpht.com/ZdXDhvCVn73Shu-QkqWFoUS_TlZ9MSkAXb8VJBeI6ZKSN6oH4QBvTG2BCfuFRegjXwdp6qH3=w2276-fcrop64=1,00005a57ffffa5a8-k-c0xffffffff-no-nd-rj",
            "width": 2276,
            "height": 377
        },
        {
            "url": "https://yt3.ggpht.com/ZdXDhvCVn73Shu-QkqWFoUS_TlZ9MSkAXb8VJBeI6ZKSN6oH4QBvTG2BCfuFRegjXwdp6qH3=w2560-fcrop64=1,00005a57ffffa5a8-k-c0xffffffff-no-nd-rj",
            "width": 2560,
            "height": 424
        }
    ],
    "subscribers": {
        "simpleText": "32.2M subscribers",
        "label": "32.2 million subscribers"
    },
    "thumbnails": [
        {
            "url": "https://yt3.ggpht.com/YIBi8NVC87fMfJHfQ2O0dyzjis7tUlO7VqWLhk1lq1fkIOQTrpX_Ip7G6S_u0IJosXYSe_Z9=s48-c-k-c0x00ffffff-no-rj",
            "width": 48,
            "height": 48
        },
        {
            "url": "https://yt3.ggpht.com/YIBi8NVC87fMfJHfQ2O0dyzjis7tUlO7VqWLhk1lq1fkIOQTrpX_Ip7G6S_u0IJosXYSe_Z9=s88-c-k-c0x00ffffff-no-rj",
            "width": 88,
            "height": 88
        },
        {
            "url": "https://yt3.ggpht.com/YIBi8NVC87fMfJHfQ2O0dyzjis7tUlO7VqWLhk1lq1fkIOQTrpX_Ip7G6S_u0IJosXYSe_Z9=s176-c-k-c0x00ffffff-no-rj",
            "width": 176,
            "height": 176
        },
        {
            "url": "https://yt3.ggpht.com/YIBi8NVC87fMfJHfQ2O0dyzjis7tUlO7VqWLhk1lq1fkIOQTrpX_Ip7G6S_u0IJosXYSe_Z9=s900-c-k-c0x00ffffff-no-rj",
            "width": 900,
            "height": 900
        },
        {
            "url": "https://yt3.ggpht.com/YIBi8NVC87fMfJHfQ2O0dyzjis7tUlO7VqWLhk1lq1fkIOQTrpX_Ip7G6S_u0IJosXYSe_Z9=s200-c-k-c0x00ffffff-no-rj?days_since_epoch=19098",
            "width": 200,
            "height": 200
        }
    ],
    "isFamilySafe": true,
    "keywords": "NoCopyrightSounds ncs no copyright sounds copyrighted music free royalty royaltyfree uncopyrighted copyrightfree",
    "tags": [
        "NoCopyrightSounds",
        "ncs",
        "no",
        "copyright",
        "sounds",
        "copyrighted",
        "music",
        "free",
        "royalty",
        "royaltyfree",
        "uncopyrighted",
        "copyrightfree"
    ],
    "views": "10,094,707,992 views",
    "joinedDate": "Aug 14, 2011",
    "country": "United Kingdom"
}
```
</details>



#### Retrieve channel playlists
```py
from youtubesearchpython import Channel

channel = Channel("UC_aEa8K-EOJ3D6gOs7HcyNg")
print(len(channel.result["playlists"]))
while channel.has_more_playlists():
    channel.next()
    print(len(channel.result["playlists"]))
```

<details>
 <summary> Example Result</summary>

```
30
49
```
</details>


---

## Credits & Thanks

### Major fixes (httpx 0.28.1+)

**CertifiedCoders** played a vital role in fixing and improving reliability for newer `httpx` versions (notably `httpx==0.28.1+`), and also addressed crucial calls that could lead to errors in asynchronous loops. [web:2]

### Credits for fixes in `Requests.py`

- Fixes credited to: **CertifiedCoders**
- [ Ritesh Mishra ]
- File reference:  
  https://github.com/BillaSpace/youtube-search-python/blob/main/youtubesearchpython/core/requests.py

---

## Upstream Reference

The original (archived) project:  
https://github.com/alexmercerind/youtube-search-python

It is now archived since 1 july 2k22 and read-only.

---

## Contributors (Legacy + Ongoing)

Thanks to everyone contributing to this library, including those not mentioned here.

- Hitesh Kumar Saini — Creator of this library, contributed most classes to this library.
- mytja — Current maintainer of this library. Author of Core classes, Comments and Transcript classes, ytdlp migration.
- Denis — Maintainer and reviewer of PRs. Author of Hashtag class.
- Fabian Wunsch — Fixes to ChannelSearch & retrieving Playlists from Channel class.
- Felix Stupp — Video and Playlist class contributor. Extensive issues.
- dscrofts — Extensive issues, mostly about Playlist and Video class.
- AlexandreOuellet — Added publishDate and uploadDate to Video class.
- None — Bumped httpx version to 0.14.2.
- Elter — Fixes to Playlist class.

---

## Notes

- For example outputs, prefer running test suites under `tests/sync` and `tests/async` to generate fresh results for your environment.
- If something breaks due to YouTube changes, open an issue with a reproducible snippet and logs.
- if using stream url fetcher features must provide cookies.txt in netscape format to avoid authorisation errors
- You can get cookies.txt by  chrome or firefox extensions ( search in youtube app for more information ℹ️)
- I strictly recommend to locally clone this repo under your project if you have a will to use for the streamurl fetcher functionality otherwise edit your requirements.txt

---

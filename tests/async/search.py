import asyncio
import json
import time
from youtubesearchpython.__future__ import (
    Search,
    VideosSearch,
    ChannelsSearch,
    PlaylistsSearch,
    CustomSearch,
    VideoSortOrder,
)

def pretty_print(data, elapsed):
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\n⏱ Time taken: {elapsed:.3f} seconds\n{'-'*60}\n")

async def timed_next(obj):
    start = time.perf_counter()
    result = await obj.next()
    elapsed = time.perf_counter() - start
    return result, elapsed

async def main():
    search = Search("TeraZikr", limit=5, language="en", region="US")
    result, t = await timed_next(search)
    pretty_print(result, t)

    videosSearch = VideosSearch("HumnavaMere", limit=10, language="en", region="US")
    result, t = await timed_next(videosSearch)
    pretty_print(result, t)

    channelsSearch = ChannelsSearch("T-Series", limit=5, language="en", region="US")
    result, t = await timed_next(channelsSearch)
    pretty_print(result, t)

    playlistsSearch = PlaylistsSearch(
        "BollywoodHipHop/TrapRemixes", limit=1, language="en", region="US"
    )
    result, t = await timed_next(playlistsSearch)
    pretty_print(result, t)

    customSearch = CustomSearch(
        "TuKaunKahanSe",
        VideoSortOrder.uploadDate,
        language="en",
        region="US",
    )
    result, t = await timed_next(customSearch)
    pretty_print(result, t)

    search = VideosSearch("PalPal")
    index = 0

    for _ in range(3):
        result, t = await timed_next(search)
        print(f"Batch fetched in {t:.3f} seconds")
        for video in result.get("result", []):
            index += 1
            print(f"{index} - {video.get('title')}")
        print("-" * 60)

asyncio.run(main())

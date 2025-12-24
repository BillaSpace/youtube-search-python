import asyncio
import json
import time

from youtubesearchpython.__future__ import (
    Search,
    VideosSearch,
    ChannelsSearch,
    PlaylistsSearch,
    CustomSearch,
    ChannelSearch,
    VideoSortOrder,
)


def pretty_print(data, fn_name, elapsed):
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\n⏱ {fn_name} took {elapsed:.3f} seconds\n{'-' * 60}\n")


async def timed_call(fn_name, coro):
    start = time.perf_counter()
    result = await coro
    elapsed = time.perf_counter() - start
    return result, fn_name, elapsed


async def main():
    start_all = time.perf_counter()

    all_search, fn, t = await timed_call(
        "Search.result",
        Search("EkdinMeri", limit=1, language="en", region="US").next(),
    )
    pretty_print(all_search, fn, t)

    videos_search, fn, t = await timed_call(
        "VideosSearch.result",
        VideosSearch("Mehrbanhua", limit=5, language="en", region="US").next(),
    )
    pretty_print(videos_search, fn, t)

    channels_search, fn, t = await timed_call(
        "ChannelsSearch.result",
        ChannelsSearch("TipsOfficial", limit=2, language="en", region="US").next(),
    )
    pretty_print(channels_search, fn, t)

    playlists_search, fn, t = await timed_call(
        "PlaylistsSearch.result",
        PlaylistsSearch("TipsOfficial", limit=1, language="en", region="US").next(),
    )
    pretty_print(playlists_search, fn, t)

    custom_search, fn, t = await timed_call(
        "CustomSearch.result",
        CustomSearch(
            "hindisongs",
            VideoSortOrder.uploadDate,
            language="en",
            region="US",
        ).next(),
    )
    pretty_print(custom_search, fn, t)

    search = VideosSearch("Suzume", limit=5)
    index = 0

    first_page, fn, t = await timed_call("VideosSearch.next (page 1)", search.next())
    print(f"⏱ {fn} took {t:.3f} seconds")
    for v in first_page["result"]:
        print(f"{index} - {v['title']}")
        index += 1
    print("-" * 60)

    second_page, fn, t = await timed_call("VideosSearch.next (page 2)", search.next())
    print(f"⏱ {fn} took {t:.3f} seconds")
    for v in second_page["result"]:
        print(f"{index} - {v['title']}")
        index += 1
    print("-" * 60)

    third_page, fn, t = await timed_call("VideosSearch.next (page 3)", search.next())
    print(f"⏱ {fn} took {t:.3f} seconds")
    for v in third_page["result"]:
        print(f"{index} - {v['title']}")
        index += 1
    print("-" * 60)

    channel_search_1, fn, t = await timed_call(
        "ChannelSearch.result (Watermelon Sugar)",
        ChannelSearch(
            "Watermelon Sugar",
            "UCZFWPqqPkFlNwIxcpsLOwew",
        ).next(),
    )
    pretty_print(channel_search_1, fn, t)

    channel_search_2, fn, t = await timed_call(
        "ChannelSearch.result (The Beatles - Topic)",
        ChannelSearch(
            "The Beatles - Topic",
            "UC2XdaAVUannpujzv32jcouQ",
        ).next(),
    )
    pretty_print(channel_search_2, fn, t)

    total_time = time.perf_counter() - start_all
    print(f"\n✅ All tasks completed successfully in {total_time:.3f} seconds")


asyncio.run(main())

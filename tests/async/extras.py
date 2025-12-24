import asyncio
import json
import time

from youtubesearchpython.__future__ import (
    Video,
    StreamURLFetcher,
    Suggestions,
)
from youtubesearchpython import Hashtag, Comments, Transcript, Channel


def pretty_print(data, fn_name, elapsed):
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\n⏱ {fn_name} took {elapsed:.3f} seconds\n{'-' * 60}\n")


async def timed_call(fn_name, coro):
    start = time.perf_counter()
    result = await coro
    elapsed = time.perf_counter() - start
    return result, fn_name, elapsed


async def timed_thread_call(fn_name, func, *args, **kwargs):
    start = time.perf_counter()
    result = await asyncio.to_thread(func, *args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, fn_name, elapsed


async def main():
    start_all = time.perf_counter()

    video, fn, t = await timed_call(
        "Video.get",
        Video.get("https://youtu.be/dQw4w9WgXcQ", get_upload_date=True),
    )
    pretty_print(video, fn, t)

    video_info, fn, t = await timed_call(
        "Video.getInfo",
        Video.getInfo("https://youtu.be/dQw4w9WgXcQ"),
    )
    pretty_print(video_info, fn, t)

    video_formats, fn, t = await timed_call(
        "Video.getFormats",
        Video.getFormats("dQw4w9WgXcQ"),
    )
    pretty_print(video_formats, fn, t)

    suggestions, fn, t = await timed_call(
        "Suggestions.get",
        Suggestions.get("AgarTumSaathHo", language="en", region="US"),
    )
    pretty_print(suggestions, fn, t)

    hashtag = Hashtag("IndianArmy", limit=5)
    hashtag_result, fn, t = await timed_thread_call(
        "Hashtag.result",
        hashtag.result,
    )
    pretty_print(hashtag_result, fn, t)

    fetcher = StreamURLFetcher()

    videoA = await Video.get("https://www.youtube.com/watch?v=aqz-KE-bpKQ")
    videoB = await Video.get("https://www.youtube.com/watch?v=ZwNxYJfW-eU")
    videoC = await Video.get("https://youtu.be/dQw4w9WgXcQ")
    videoD = await Video.get("https://www.youtube.com/watch?v=9bZkp7q19f0")

    singleA, fn, t = await timed_call(
        "StreamURLFetcher.get (251)",
        fetcher.get(videoA, 251),
    )
    pretty_print(singleA, fn, t)

    allB, fn, t = await timed_call(
        "StreamURLFetcher.getAll",
        fetcher.getAll(videoB),
    )
    pretty_print(allB, fn, t)

    singleC, fn, t = await timed_call(
        "StreamURLFetcher.get (251)",
        fetcher.get(videoC, 251),
    )
    pretty_print(singleC, fn, t)

    allC, fn, t = await timed_call(
        "StreamURLFetcher.getAll",
        fetcher.getAll(videoC),
    )
    pretty_print(allC, fn, t)

    singleD251, fn, t = await timed_call(
        "StreamURLFetcher.get (251)",
        fetcher.get(videoD, 251),
    )
    pretty_print(singleD251, fn, t)

    singleD140, fn, t = await timed_call(
        "StreamURLFetcher.get (140)",
        fetcher.get(videoD, 140),
    )
    pretty_print(singleD140, fn, t)

    allD, fn, t = await timed_call(
        "StreamURLFetcher.getAll",
        fetcher.getAll(videoD),
    )
    pretty_print(allD, fn, t)

    comments = Comments("dQw4w9WgXcQ")

    _, fn, t = await timed_thread_call(
        "Comments.getNextComments",
        comments.getNextComments,
    )
    print(f"⏱ {fn} took {t:.3f} seconds\n{'-' * 60}\n")

    while len(comments.comments["result"]) < 100 and getattr(comments, "hasMoreComments", False):
        await asyncio.to_thread(comments.getNextComments)

    pretty_print(comments.comments, "Comments (100+)", 0.0)

    transcript, fn, t = await timed_thread_call(
        "Transcript.get",
        Transcript.get,
        "https://youtu.be/89d02K5pIU8?si=z0NtBv6iV1Rc37Mq",
    )
    pretty_print(transcript, fn, t)

    url = "https://youtu.be/dQw4w9WgXcQ"
    transcript_main, fn, t = await timed_thread_call(
        "Transcript.get (default)",
        Transcript.get,
        url,
    )
    pretty_print(transcript_main, fn, t)

    if transcript_main.get("languages"):
        transcript_alt, fn, t = await timed_thread_call(
            "Transcript.get (alt language)",
            Transcript.get,
            url,
            transcript_main["languages"][-1]["params"],
        )
        pretty_print(transcript_alt, fn, t)

    channel_info, fn, t = await timed_thread_call(
        "Channel.get",
        Channel.get,
        "UC_aEa8K-EOJ3d6gOs7HcyNg",
    )
    pretty_print(channel_info, fn, t)

    channel = Channel("UC_aEa8K-EOJ3d6gOs7HcyNg")

    _, fn, t = await timed_thread_call(
        "Channel.init",
        channel.init,
    )
    print(f"⏱ {fn} took {t:.3f} seconds")
    print(f"Playlists: {len(channel.result['playlists'])}\n{'-' * 60}\n")

    while channel.has_more_playlists():
        await asyncio.to_thread(channel.next)
        print(f"Playlists: {len(channel.result['playlists'])}")

    total_time = time.perf_counter() - start_all
    print(f"\n✅ All tasks completed successfully in {total_time:.3f} seconds")


asyncio.run(main())

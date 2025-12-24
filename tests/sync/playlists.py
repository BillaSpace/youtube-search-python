import asyncio
import json
import time

from youtubesearchpython.__future__ import Playlist


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

    url_playlist = "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    url_video_playlist = "https://www.youtube.com/watch?v=bplUXwTTgbI&list=PL6edxAMqu2xfxgbf7Q09hSg1qCMfDI7IZ"

    playlist, fn, t = await timed_call(
        "Playlist.get (playlist url)",
        Playlist.get(url_playlist),
    )
    pretty_print(playlist, fn, t)

    playlist_info, fn, t = await timed_call(
        "Playlist.getInfo",
        Playlist.getInfo(url_playlist),
    )
    pretty_print(playlist_info, fn, t)

    playlist_videos, fn, t = await timed_call(
        "Playlist.getVideos",
        Playlist.getVideos(url_playlist),
    )
    pretty_print(playlist_videos, fn, t)

    playlist_from_video, fn, t = await timed_call(
        "Playlist.get (video+list url)",
        Playlist.get(url_video_playlist),
    )
    pretty_print(playlist_from_video, fn, t)

    playlist_obj = Playlist(url_playlist)

    _, fn, t = await timed_call(
        "Playlist.init",
        playlist_obj.init(),
    )
    print(f"⏱ {fn} took {t:.3f} seconds")
    print(f"Videos Retrieved: {len(playlist_obj.videos)}\n{'-' * 60}\n")

    while playlist_obj.hasMoreVideos:
        _, fn, t = await timed_thread_call(
            "Playlist.getNextVideos",
            playlist_obj.getNextVideos,
        )
        print(f"⏱ {fn} took {t:.3f} seconds | Videos Retrieved: {len(playlist_obj.videos)}")

    print("\nFetched all the videos. from the given playlist")

    total_time = time.perf_counter() - start_all
    print(f"\n✅ All tasks completed successfully in {total_time:.3f} seconds")


asyncio.run(main())

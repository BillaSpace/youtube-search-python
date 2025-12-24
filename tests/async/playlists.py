import asyncio
import json
import time
from youtubesearchpython.__future__ import *

def pretty_print(data, fn_name, elapsed):
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\n⏱ {fn_name} took {elapsed:.3f} seconds\n{'-'*60}\n")

async def timed_call(fn_name, coro):
    start = time.perf_counter()
    result = await coro
    elapsed = time.perf_counter() - start
    return result, fn_name, elapsed

async def main():
    url1 = "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    url2 = "https://www.youtube.com/watch?v=bplUXwTTgbI&list=PL6edxAMqu2xfxgbf7Q09hSg1qCMfDI7IZ"

    playlist, fn, t = await timed_call(
        "Playlist.get",
        Playlist.get(url1),
    )
    pretty_print(playlist, fn, t)

    playlistInfo, fn, t = await timed_call(
        "Playlist.getInfo",
        Playlist.getInfo(url1),
    )
    pretty_print(playlistInfo, fn, t)

    playlistVideos, fn, t = await timed_call(
        "Playlist.getVideos",
        Playlist.getVideos(url1),
    )
    pretty_print(playlistVideos, fn, t)

    playlist, fn, t = await timed_call(
        "Playlist.get",
        Playlist.get(url1),
    )
    pretty_print(playlist, fn, t)

    playlist, fn, t = await timed_call(
        "Playlist.get (video+playlist URL)",
        Playlist.get(url2),
    )
    pretty_print(playlist, fn, t)

asyncio.run(main())

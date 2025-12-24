import asyncio
import json
import time
from youtubesearchpython.__future__ import *

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

def print_timing(fn_name, elapsed):
    print(f"⏱ {fn_name}: {elapsed:.3f}s")
    print("-" * 60)

async def timed(fn_name, coro):
    start = time.perf_counter()
    result = await coro
    elapsed = time.perf_counter() - start
    print_timing(fn_name, elapsed)
    return result

async def main():
    url1 = "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    url2 = "https://www.youtube.com/watch?v=bplUXwTTgbI&list=PL6edxAMqu2xfxgbf7Q09hSg1qCMfDI7IZ"

    print_json(await timed("Playlist.get", Playlist.get(url1)))
    print_json(await timed("Playlist.getInfo", Playlist.getInfo(url1)))
    print_json(await timed("Playlist.getVideos", Playlist.getVideos(url1)))
    print_json(await timed("Playlist.get (cached)", Playlist.get(url1)))
    print_json(await timed("Playlist.get (video+playlist URL)", Playlist.get(url2)))

asyncio.run(main())

import asyncio
import json
import time
from youtubesearchpython.__future__ import *

def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))

async def run_get(url):
    start = time.perf_counter()
    result = await Playlist.get(url)
    elapsed = time.perf_counter() - start
    print_json(result)
    print(f"\n⏱ Playlist.get took {elapsed:.3f} seconds\n{'-'*60}\n")

async def run_get_info(url):
    start = time.perf_counter()
    result = await Playlist.getInfo(url)
    elapsed = time.perf_counter() - start
    print_json(result)
    print(f"\n⏱ Playlist.getInfo took {elapsed:.3f} seconds\n{'-'*60}\n")

async def run_get_videos(url):
    start = time.perf_counter()
    result = await Playlist.getVideos(url)
    elapsed = time.perf_counter() - start
    print_json(result)
    print(f"\n⏱ Playlist.getVideos took {elapsed:.3f} seconds\n{'-'*60}\n")

async def main():
    url1 = "https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK"
    url2 = "https://www.youtube.com/watch?v=bplUXwTTgbI&list=PL6edxAMqu2xfxgbf7Q09hSg1qCMfDI7IZ"

    await run_get(url1)
    await run_get_info(url1)
    await run_get_videos(url1)

    await run_get(url1)
    await run_get(url2)

asyncio.run(main())

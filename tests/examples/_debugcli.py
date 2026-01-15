import json
import httpx
from youtubesearchpython.core.video import VideoCore
from youtubesearchpython.core.constants import searchKey

async def debug_clients(video_id):
    video_link = f"https://www.youtube.com/watch?v={video_id}"
    clients = ["ANDROID", "WEB", "MWEB", "TV_EMBED", "ANDROID_EMBED"]
    
    for client_name in clients:
        print(f"\n--- Testing Client: {client_name} ---")
        try:
            video = VideoCore(video_link, None, 1, None, False, overridedClient=client_name)
            video.prepare_innertube_request()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    video.url,
                    json=video.data,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
            
            if response.status_code == 200:
                data = response.json()
                playability = data.get("playabilityStatus", {}).get("status")
                print(f"Status: {response.status_code}, Playability: {playability}")
                if "videoDetails" in data:
                    print("✓ Video Details Found")
                else:
                    print("✗ No Video Details")
                    if "playabilityStatus" in data:
                        print(f"Reason: {data['playabilityStatus'].get('reason')}")
            else:
                print(f"Failed with status: {response.status_code}")
        except Exception as e:
            print(f"Error: {str(e)}")

import asyncio
if __name__ == "__main__":
    asyncio.run(debug_clients("7bj_2x-IoRE"))

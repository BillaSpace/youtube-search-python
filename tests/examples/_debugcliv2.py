import json
import httpx
import asyncio
from youtubesearchpython.core.video import VideoCore
from youtubesearchpython.core.constants import searchKey
from urllib.parse import urlencode

async def debug_clients(video_id):
    video_link = f"https://www.youtube.com/watch?v={video_id}"
    # Try even more clients
    clients = ["ANDROID", "WEB", "MWEB", "TVHTML5_SIMPLY_EMBEDDED_PLAYER", "ANDROID_EMBED", "IOS"]
    
    # Custom InnerTube Clients to test
    CUSTOM_CLIENTS = {
        "IOS": {
            "context": {"client": {"clientName": "IOS", "clientVersion": "19.08.2"}},
            "api_key": searchKey
        }
    }

    for client_name in clients:
        print(f"\n--- Testing Client: {client_name} ---")
        try:
            video = VideoCore(video_link, None, 1, None, False, overridedClient="ANDROID")
            video.prepare_innertube_request()
            
            # Manually override client data for debugging
            if client_name == "TVHTML5_SIMPLY_EMBEDDED_PLAYER":
                video.data = {
                    "context": {
                        "client": {
                            "clientName": "TVHTML5_SIMPLY_EMBEDDED_PLAYER",
                            "clientVersion": "2.0",
                        },
                        "thirdParty": {"embedUrl": "https://www.youtube.com/"}
                    }
                }
            elif client_name == "IOS":
                video.data = CUSTOM_CLIENTS["IOS"]
            elif client_name == "WEB":
                 video.data = {
                    "context": {
                        "client": {
                            "clientName": "WEB",
                            "clientVersion": "2.20240502.07.00"
                        }
                    }
                }
            elif client_name == "MWEB":
                video.data = {
                    "context": {
                        "client": {
                            "clientName": "MWEB",
                            "clientVersion": "2.20240425.01.00"
                        }
                    }
                }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    video.url,
                    json=video.data,
                    headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
                )
            
            if response.status_code == 200:
                data = response.json()
                playability = data.get("playabilityStatus", {})
                status = playability.get("status")
                reason = playability.get("reason")
                print(f"Status: {response.status_code}, Playability: {status}")
                if reason:
                    print(f"Reason: {reason}")
                
                if "videoDetails" in data:
                    print("Video Details Found!")
                    print(f"Title: {data['videoDetails'].get('title')}")
                else:
                    print("No Video Details")
            else:
                print(f"Failed with status: {response.status_code}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug_clients("7bj_2x-IoRE"))

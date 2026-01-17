import asyncio
import sys
import os
import time

# Force UTF-8 encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

# Optional : Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from youtubesearchpython import (
    VideosSearch, ChannelsSearch, PlaylistsSearch, 
    Video, Playlist, Channel, Comments, Transcript, Suggestions
)
from youtubesearchpython.future import (
    VideosSearch as AsyncVideosSearch,
    ChannelsSearch as AsyncChannelsSearch,
    PlaylistsSearch as AsyncPlaylistsSearch,
    Video as AsyncVideo,
    Playlist as AsyncPlaylist,
    Channel as AsyncChannel,
    Comments as AsyncComments,
    Transcript as AsyncTranscript,
    Suggestions as AsyncSuggestions
)

def print_result(name, status, details=""):
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {name}: {details}")

def sync_tests():
    print("\n--- Starting SYNCHRONOUS Tests ---")
    
    # VideosSearch
    try:
        search = VideosSearch('NoCopyrightSounds', limit=2)
        res = search.result()
        print_result("VideosSearch", len(res['result']) > 0, f"Found {len(res['result'])} videos")
    except Exception as e:
        print_result("VideosSearch", False, str(e))

    # ChannelsSearch
    try:
        search = ChannelsSearch('NoCopyrightSounds', limit=1)
        res = search.result()
        print_result("ChannelsSearch", len(res['result']) > 0, f"Found {len(res['result'])} channels")
    except Exception as e:
        print_result("ChannelsSearch", False, str(e))

    # PlaylistsSearch
    try:
        search = PlaylistsSearch('NCS', limit=1)
        res = search.result()
        print_result("PlaylistsSearch", len(res['result']) > 0, f"Found {len(res['result'])} playlists")
    except Exception as e:
        print_result("PlaylistsSearch", False, str(e))

    # Video Info
    video_id = "aqz-KE-bpKQ" # Big Buck Bunny
    try:
        video = Video.get(video_id)
        print_result("Video.get", video is not None, f"Title: {video.get('title', 'Unknown')}")
    except Exception as e:
        print_result("Video.get", False, str(e))

    # Playlist Info
    playlist_id = "PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK" # NCS House
    try:
        playlist = Playlist.get("https://www.youtube.com/playlist?list=" + playlist_id)
        print_result("Playlist.get", playlist is not None, f"Title: {playlist.get('title', 'Unknown')}")
    except Exception as e:
        print_result("Playlist.get", False, str(e))

    # Channel Info
    channel_id = "UC_aEa8K-EOJ3D6gOs7HcyNg" # NCS
    try:
        channel = Channel.get(channel_id)
        print_result("Channel.get", channel is not None, f"Title: {channel.get('title', 'Unknown')}")
    except Exception as e:
        print_result("Channel.get", False, str(e))

    # Comments
    try:
        comments = Comments.get(video_id)
        print_result("Comments.get", comments is not None, f"Count: {len(comments.get('result', []))}")
    except Exception as e:
        print_result("Comments.get", False, str(e))
        
    # Transcript (Expect Failure/Issues)
    try:
        t = Transcript.get("https://www.youtube.com/watch?v=L_LUpnjgPso") # Video with transcript
        if t and 'segments' in t: # It might return empty dict on failure
             print_result("Transcript.get", True, f"Segments: {len(t.get('segments', []))}")
        else:
             print_result("Transcript.get", False, "No segments found (Known Issue: 400 Error)")
    except Exception as e:
        print_result("Transcript.get", False, f"Exception: {str(e)}")

    # Suggestions
    try:
        s = Suggestions(language='en', region='US')
        res = s.get('Harry Styles')
        print_result("Suggestions.get", len(res['result']) > 0, f"Found {len(res['result'])} suggestions")
    except Exception as e:
        print_result("Suggestions.get", False, str(e))


async def async_tests():
    print("\n--- Starting ASYNCHRONOUS Tests ---")
    
    # Async VideosSearch
    try:
        search = AsyncVideosSearch('NoCopyrightSounds', limit=2)
        res = await search.next()
        print_result("AsyncVideosSearch", len(res['result']) > 0, f"Found {len(res['result'])} videos")
    except Exception as e:
        print_result("AsyncVideosSearch", False, str(e))

    # Async ChannelsSearch
    try:
        search = AsyncChannelsSearch('NoCopyrightSounds', limit=1)
        res = await search.next()
        print_result("AsyncChannelsSearch", len(res['result']) > 0, f"Found {len(res['result'])} channels")
    except Exception as e:
        print_result("AsyncChannelsSearch", False, str(e))

    # Async PlaylistsSearch
    try:
        search = AsyncPlaylistsSearch('NCS', limit=1)
        res = await search.next()
        print_result("AsyncPlaylistsSearch", len(res['result']) > 0, f"Found {len(res['result'])} playlists")
    except Exception as e:
        print_result("AsyncPlaylistsSearch", False, str(e))
    
    video_id = "aqz-KE-bpKQ"

    # Async Video
    try:
        video = await AsyncVideo.get(video_id)
        print_result("AsyncVideo.get", video is not None, f"Title: {video.get('title', 'Unknown')}")
    except Exception as e:
        print_result("AsyncVideo.get", False, str(e))

    # Async Comments
    try:
        comments = await AsyncComments.get(video_id)
        print_result("AsyncComments.get", comments is not None, f"Count: {len(comments.get('result', []))}")
    except Exception as e:
        print_result("AsyncComments.get", False, str(e))

    # Async Channel (ID Check)
    channel_id = "UC_aEa8K-EOJ3D6gOs7HcyNg"
    try:
        channel = await AsyncChannel.get(channel_id)
        print_result("AsyncChannel.get (ID)", channel is not None, f"Title: {channel.get('title', 'Unknown')}")
    except Exception as e:
        print_result("AsyncChannel.get", False, str(e))


if __name__ == "__main__":
    sync_tests()
    asyncio.run(async_tests())

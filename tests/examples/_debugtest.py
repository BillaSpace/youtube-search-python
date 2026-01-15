import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from youtubesearchpython import PlaylistsSearch, Video
import traceback

print("Testing Playlist Search...")
try:
    s = PlaylistsSearch('Hindi songs', limit=1)
    result = s.result()
    print(f"Success: {len(result.get('result', []))} playlists found")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()

print("\nTesting Video Formats...")
try:
    result = Video.getFormats('7bj_2x-IoRE')
    if result:
        print(f"Success: Got formats, has streaming data: {'streamingData' in result}")
    else:
        print("Error: No result returned")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()

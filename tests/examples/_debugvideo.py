"""Debug script to trace Video.get() issue"""
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from youtubesearchpython.core.video import VideoCore
from youtubesearchpython.core.constants import ResultMode
import traceback
import json

print("="*70)
print("DEBUGGING Video.get() - Checking response")
print("="*70)

try:
    # Create VideoCore instance
    video = VideoCore('7bj_2x-IoRE', None, ResultMode.dict, 10, False, "ANDROID")
    
    print("\n1. Created VideoCore instance")
    print(f"   Video link: {video.videoLink}")
    print(f"   Client: ANDROID")
    
    # Try to fetch
    print("\n2. Preparing request...")
    video.prepare_innertube_request()
    print(f"   URL: {video.url[:80]}...")
    
    print("\n3. Making sync request...")
    video.sync_create()
    
    print("\n4. Checking response...")
    if hasattr(video, 'responseSource'):
        print(f"   Response source keys: {list(video.responseSource.keys())[:10]}")
        
        # Check videoDetails
        if 'videoDetails' in video.responseSource:
            vd = video.responseSource['videoDetails']
            print(f"\n5. VideoDetails found:")
            print(f"   - videoId: {vd.get('videoId')}")
            print(f"   - title: {vd.get('title', 'NOT FOUND')[:60]}")
            print(f"   - author: {vd.get('author')}")
            print(f"   - viewCount: {vd.get('viewCount')}")
        else:
            print("\n5. ❌ NO videoDetails in response!")
            print(f"   Available keys: {list(video.responseSource.keys())}")
    
    print("\n6. Getting result...")
    result = video.result
    print(f"   Result keys: {list(result.keys())[:10]}")
    print(f"   Title: {result.get('title')}")
    print(f"   ID: {result.get('id')}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    traceback.print_exc()

print("\n" + "="*70)

"""Check playability status"""
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from youtubesearchpython.core.video import VideoCore
from youtubesearchpython.core.constants import ResultMode
import json

video = VideoCore('7bj_2x-IoRE', None, ResultMode.dict, 10, False, "ANDROID")
video.prepare_innertube_request()
video.sync_create()

if hasattr(video, 'responseSource'):
    print("Playability Status:")
    ps = video.responseSource.get('playabilityStatus', {})
    print(json.dumps(ps, indent=2))
    
    # Try different video
    print("\n\n" + "="*70)
    print("Trying different video (original failing URL)...")
    print("="*70)
    
    video2 = VideoCore('_JND3HuOmDM', None, ResultMode.dict, 10, False, "ANDROID")
    video2.prepare_innertube_request()
    video2.sync_create()
    
    if 'videoDetails' in video2.responseSource:
        print("\n✅ VideoDetails FOUND for _JND3HuOmDM!")
        vd = video2.responseSource['videoDetails']
        print(f"Title: {vd.get('title')}")
        print(f"Views: {vd.get('viewCount')}")
    else:
        print("\n❌ Still no videoDetails")
        print(f"Keys: {list(video2.responseSource.keys())}")
        if 'playabilityStatus' in video2.responseSource:
            print("\nPlayability:")
            print(json.dumps(video2.responseSource['playabilityStatus'], indent=2))

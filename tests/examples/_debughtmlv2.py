import json
from youtubesearchpython.core.video import VideoCore

def test_html_fallback(video_id):
    video_link = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Testing HTML fallback for: {video_link}")
    
    video = VideoCore(video_link, None, 1, None, True)
    try:
        # Use HTML create
        video.sync_html_create()
        # This populates self.HTMLresponseSource
        if video.HTMLresponseSource:
            print("[OK] HTML response received!")
            video.post_request_only_html_processing()
            if video.result:
                print(f"Title: {video.result.get('title')}")
                print(f"Views: {video.result.get('viewCount', {}).get('text')}")
                return True
            else:
                print("[FAIL] Result is empty")
    except Exception as e:
        print(f"[FAIL] HTML fallback failed: {str(e)}")
    return False

if __name__ == "__main__":
    test_html_fallback("7bj_2x-IoRE")

import asyncio
import sys
import os

# Force UTF-8 encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

# Optional : Add parent directory to path fork this Repository & remove this line if having problem
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from youtubesearchpython import (
    VideosSearch, ChannelsSearch, PlaylistsSearch, CustomSearch,
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
    Suggestions as AsyncSuggestions,
    Recommendations as AsyncRecommendations,
    StreamURLFetcher
)

def section(title):
    print(f"\n{'='*60}\n{title}\n{'='*60}")

def subsection(title):
    print(f"\n--- {title} ---")

# ============================================================================
# SYNCHRONOUS TESTS
# ============================================================================

def test_sync():
    section("SYNCHRONOUS TESTS")
    
    # 1. VideosSearch
    subsection("1. VideosSearch: 'pal pal'")
    try:
        search = VideosSearch('pal pal', limit=2, region='IN')
        res = search.result()
        if res and 'result' in res and len(res['result']) > 0:
            v = res['result'][0]
            print(f"✅ Found: {v.get('title')}")
            print(f"   ID: {v.get('id')}")
            print(f"   Link: {v.get('link')}")
            
            # Test using the URL
            subsection("1a. Testing Video URL from search")
            video_url = v.get('link')
            video = Video.get(video_url)
            if video:
                print(f"✅ Video.get(URL) works: {video.get('title')}")
            else:
                print("❌ Video.get(URL) failed")
        else:
            print("❌ No results")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 2. VideosSearch - Second query
    subsection("2. VideosSearch: 'meharban hua bang bang'")
    try:
        search = VideosSearch('meharban hua bang bang', limit=2, region='IN')
        res = search.result()
        if res and 'result' in res and len(res['result']) > 0:
            v = res['result'][0]
            print(f"✅ Found: {v.get('title')}")
            print(f"   ID: {v.get('id')}")
            
            # Test using the ID
            subsection("2a. Testing Video ID from search")
            video_id = v.get('id')
            video = Video.get(video_id)
            if video:
                print(f"✅ Video.get(ID) works: {video.get('title')}")
            else:
                print("❌ Video.get(ID) failed")
        else:
            print("❌ No results")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 3. ChannelsSearch
    subsection("3. ChannelsSearch: 'T-Series'")
    try:
        search = ChannelsSearch('T-Series', limit=1, region='IN')
        res = search.result()
        if res and 'result' in res and len(res['result']) > 0:
            c = res['result'][0]
            print(f"✅ Found: {c.get('title')}")
            print(f"   Subscribers: {c.get('subscribers')}")
        else:
            print("❌ No results")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 4. PlaylistsSearch
    subsection("4. PlaylistsSearch: 'Bollywood'")
    try:
        search = PlaylistsSearch('Bollywood', limit=1, region='IN')
        res = search.result()
        if res and 'result' in res and len(res['result']) > 0:
            p = res['result'][0]
            print(f"✅ Found: {p.get('title')}")
            print(f"   Videos: {p.get('videoCount')}")
        else:
            print("❌ No results")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 5. Video Details
    subsection("5. Video.get: 'BddP6PYo2gs' (Kesariya)")
    try:
        video = Video.get('BddP6PYo2gs')
        if video:
            print(f"✅ Title: {video.get('title')}")
            print(f"   Views: {video.get('viewCount', {}).get('short', 'N/A')}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 6. Playlist Details (URL)
    subsection("6. Playlist.get: URL")
    try:
        playlist = Playlist.get('https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK')
        if playlist and playlist.get('info'):
            print(f"✅ Title: {playlist['info'].get('title')}")
            print(f"   Videos: {len(playlist.get('videos', []))}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 7. Playlist Details (ID)
    subsection("7. Playlist.get: ID only")
    try:
        playlist = Playlist.get('PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK')
        if playlist and playlist.get('info'):
            print(f"✅ Title: {playlist['info'].get('title')}")
            print(f"   Videos: {len(playlist.get('videos', []))}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 8. Channel Details
    subsection("8. Channel.get: 'UC_aEa8K-EOJ3D6gOs7HcyNg' (NCS)")
    try:
        channel = Channel.get('UC_aEa8K-EOJ3D6gOs7HcyNg')
        if channel:
            print(f"✅ Title: {channel.get('title')}")
            print(f"   Playlists: {len(channel.get('playlists', []))}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 9. Comments
    subsection("9. Comments.get: 'BddP6PYo2gs'")
    try:
        comments = Comments.get('BddP6PYo2gs')
        if comments and 'result' in comments:
            print(f"✅ Found {len(comments['result'])} comments")
            if len(comments['result']) > 0:
                print(f"   First: {comments['result'][0].get('author', {}).get('name')}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 10. Suggestions
    subsection("10. Suggestions.get: 'Arijit'")
    try:
        sug = Suggestions(language='en', region='IN')
        res = sug.get('Arijit')
        if res and 'result' in res and len(res['result']) > 0:
            print(f"✅ Found {len(res['result'])} suggestions")
            print(f"   First: {res['result'][0]}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 11. Transcript (Expected to fail with 400)
    subsection("11. Transcript.get: (Known Issue)")
    try:
        transcript = Transcript.get('https://www.youtube.com/watch?v=L_LUpnjgPso')
        if transcript and 'segments' in transcript and len(transcript['segments']) > 0:
            print(f"✅ Found {len(transcript['segments'])} segments")
        else:
            print("⚠️  No segments (Known 400 Error)")
    except Exception as e:
        print(f"⚠️  Error (Expected): {type(e).__name__}")


# ============================================================================
# ASYNCHRONOUS TESTS
# ============================================================================

async def test_async():
    section("ASYNCHRONOUS TESTS")
    
    # 1. AsyncVideosSearch
    subsection("1. AsyncVideosSearch: 'pal pal'")
    try:
        search = AsyncVideosSearch('pal pal', limit=2, region='IN')
        res = await search.next()
        if res and 'result' in res and len(res['result']) > 0:
            v = res['result'][0]
            print(f"✅ Found: {v.get('title')}")
            print(f"   ID: {v.get('id')}")
            
            # Test using the URL
            subsection("1a. Async Video.get with URL")
            video_url = v.get('link')
            video = await AsyncVideo.get(video_url)
            if video:
                print(f"✅ AsyncVideo.get(URL) works: {video.get('title')}")
            else:
                print("❌ AsyncVideo.get(URL) failed")
        else:
            print("❌ No results")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 2. AsyncVideosSearch - Second query
    subsection("2. AsyncVideosSearch: 'meharban hua bang bang'")
    try:
        search = AsyncVideosSearch('meharban hua bang bang', limit=2, region='IN')
        res = await search.next()
        if res and 'result' in res and len(res['result']) > 0:
            v = res['result'][0]
            print(f"✅ Found: {v.get('title')}")
            
            # Test using the ID
            subsection("2a. Async Video.get with ID")
            video_id = v.get('id')
            video = await AsyncVideo.get(video_id)
            if video:
                print(f"✅ AsyncVideo.get(ID) works: {video.get('title')}")
            else:
                print("❌ AsyncVideo.get(ID) failed")
        else:
            print("❌ No results")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 3. AsyncChannelsSearch
    subsection("3. AsyncChannelsSearch: 'T-Series'")
    try:
        search = AsyncChannelsSearch('T-Series', limit=1, region='IN')
        res = await search.next()
        if res and 'result' in res and len(res['result']) > 0:
            c = res['result'][0]
            print(f"✅ Found: {c.get('title')}")
            print(f"   Subscribers: {c.get('subscribers')}")
        else:
            print("❌ No results")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 4. AsyncPlaylistsSearch
    subsection("4. AsyncPlaylistsSearch: 'Bollywood'")
    try:
        search = AsyncPlaylistsSearch('Bollywood', limit=1, region='IN')
        res = await search.next()
        if res and 'result' in res and len(res['result']) > 0:
            p = res['result'][0]
            print(f"✅ Found: {p.get('title')}")
            print(f"   Videos: {p.get('videoCount')}")
        else:
            print("❌ No results")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 5. Async Video Details
    subsection("5. AsyncVideo.get: 'BddP6PYo2gs'")
    try:
        video = await AsyncVideo.get('BddP6PYo2gs')
        if video:
            print(f"✅ Title: {video.get('title')}")
            print(f"   Views: {video.get('viewCount', {}).get('short', 'N/A')}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 6. Async Playlist (URL)
    subsection("6. AsyncPlaylist.get: URL")
    try:
        playlist = await AsyncPlaylist.get('https://www.youtube.com/playlist?list=PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK')
        if playlist and playlist.get('info'):
            print(f"✅ Title: {playlist['info'].get('title')}")
            print(f"   Videos: {len(playlist.get('videos', []))}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 7. Async Playlist (ID)
    subsection("7. AsyncPlaylist.get: ID only")
    try:
        playlist = await AsyncPlaylist.get('PLRBp0Fe2GpgmsW46rJyudVFlY6IYjFBIK')
        if playlist and playlist.get('info'):
            print(f"✅ Title: {playlist['info'].get('title')}")
            print(f"   Videos: {len(playlist.get('videos', []))}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 8. Async Channel
    subsection("8. AsyncChannel.get: 'UC_aEa8K-EOJ3D6gOs7HcyNg'")
    try:
        channel = await AsyncChannel.get('UC_aEa8K-EOJ3D6gOs7HcyNg')
        if channel:
            print(f"✅ Title: {channel.get('title')}")
            print(f"   Playlists: {len(channel.get('playlists', []))}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 9. Async Comments
    subsection("9. AsyncComments.get: 'BddP6PYo2gs'")
    try:
        comments = await AsyncComments.get('BddP6PYo2gs')
        if comments and 'result' in comments:
            print(f"✅ Found {len(comments['result'])} comments")
            if len(comments['result']) > 0:
                print(f"   First: {comments['result'][0].get('author', {}).get('name')}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 10. Async Recommendations
    subsection("10. AsyncRecommendations.get: 'BddP6PYo2gs'")
    try:
        recs = await AsyncRecommendations.get('BddP6PYo2gs')
        if recs and len(recs) > 0:
            print(f"✅ Found {len(recs)} recommendations")
            print(f"   First: {recs[0].get('title')}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 11. Async Suggestions
    subsection("11. AsyncSuggestions.get: 'Arijit'")
    try:
        sug = AsyncSuggestions(language='en', region='IN')
        res = await sug.get('Arijit')
        if res and 'result' in res and len(res['result']) > 0:
            print(f"✅ Found {len(res['result'])} suggestions")
            print(f"   First: {res['result'][0]}")
        else:
            print("❌ Failed")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 12. Async Transcript
    subsection("12. AsyncTranscript.get: (Known Issue)")
    try:
        transcript = await AsyncTranscript.get('https://www.youtube.com/watch?v=L_LUpnjgPso')
        if transcript and 'segments' in transcript and len(transcript['segments']) > 0:
            print(f"✅ Found {len(transcript['segments'])} segments")
        else:
            print("⚠️  No segments (Known 400 Error)")
    except Exception as e:
        print(f"⚠️  Error (Expected): {type(e).__name__}")

    # 13. StreamURLFetcher
    subsection("13. StreamURLFetcher")
    try:
        fetcher = StreamURLFetcher()
        await fetcher.getJavaScript()
        video = await AsyncVideo.get('BddP6PYo2gs')
        if video:
            url = await fetcher.get(video, 18)
            if url:
                print(f"✅ Got stream URL (length: {len(url)})")
            else:
                print("❌ No URL returned")
        else:
            print("❌ Video fetch failed")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_sync()
    asyncio.run(test_async())
    
    section("VERIFICATION COMPLETE")
    print("\n✅ All major library functions tested")
    print("⚠️  Transcript has known 400 error (requires cookies/proxies)")
    

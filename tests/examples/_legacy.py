"""Comprehensive test script for youtube-search-python with Indian and Myanmar songs"""
import asyncio
import sys
# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from youtubesearchpython import Video, VideosSearch, ChannelsSearch, PlaylistsSearch, Playlist
from youtubesearchpython.future import VideosSearch as AsyncVideosSearch, Video as AsyncVideo

# Test queries
INDIAN_SONGS = [
    "Kesariya Brahmastra",
    "Tum Hi Ho Aashiqui 2",
    "Dil Diyan Gallan",
    "Apna Bana Le",
]

MYANMAR_SONGS = [
    "myanmar love song",
    "burmese music",
]

def test_sync_video_indian():
    """Test with Indian music video URL"""
    print("\n" + "="*60)
    print("🎵 Testing Sync Video with Indian Song")
    print("="*60)
    try:
        # Kesariya song
        result = Video.get('https://youtu.be/7bj_2x-IoRE')
        assert result is not None
        assert 'title' in result
        print(f"✅ Title: {result['title']}")
        print(f"✅ Views: {result['viewCount']['text']}")
        print(f"✅ Duration: {result['duration']['text']}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_sync_search_indian():
    """Test searching for Indian songs"""
    print("\n" + "="*60)
    print("🎵 Testing Sync Search with Indian Songs")
    print("="*60)
    
    for query in INDIAN_SONGS[:2]:  # Test first 2
        try:
            print(f"\n🔍 Searching: {query}")
            search = VideosSearch(query, limit=3)
            result = search.result()
            assert 'result' in result
            assert len(result['result']) > 0
            print(f"✅ Found {len(result['result'])} results")
            print(f"   Top result: {result['result'][0]['title']}")
        except Exception as e:
            print(f"❌ FAILED for '{query}': {e}")
            return False
    return True

def test_sync_search_myanmar():
    """Test searching for Myanmar songs"""
    print("\n" + "="*60)
    print("🎵 Testing Sync Search with Myanmar Songs")
    print("="*60)
    
    for query in MYANMAR_SONGS:
        try:
            print(f"\n🔍 Searching: {query}")
            search = VideosSearch(query, limit=2)
            result = search.result()
            assert 'result' in result
            assert len(result['result']) > 0
            print(f"✅ Found {len(result['result'])} results")
            print(f"   Top result: {result['result'][0]['title']}")
        except Exception as e:
            print(f"❌ FAILED for '{query}': {e}")
            return False
    return True

async def test_async_video_indian():
    """Test async video retrieval with Indian music"""
    print("\n" + "="*60)
    print("🎵 Testing Async Video with Indian Song")
    print("="*60)
    try:
        result = await AsyncVideo.get('7bj_2x-IoRE')
        assert result is not None
        print(f"✅ Title: {result['title']}")
        print(f"✅ Views: {result['viewCount']['text']}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

async def test_async_search_indian():
    """Test async search with Indian songs"""
    print("\n" + "="*60)
    print("🎵 Testing Async Search with Indian Songs")
    print("="*60)
    try:
        search = AsyncVideosSearch('Kesariya', limit=3)
        result = await search.next()
        assert 'result' in result
        assert len(result['result']) > 0
        print(f"✅ Found {len(result['result'])} results")
        print(f"   Top result: {result['result'][0]['title']}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_channels_search():
    """Test channel search"""
    print("\n" + "="*60)
    print("🎵 Testing Channel Search")
    print("="*60)
    try:
        search = ChannelsSearch('T-Series', limit=2)
        result = search.result()
        assert 'result' in result
        assert len(result['result']) > 0
        print(f"✅ Found {len(result['result'])} channels")
        print(f"   Top channel: {result['result'][0]['title']}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_playlists_search():
    """Test playlist search"""
    print("\n" + "="*60)
    print("🎵 Testing Playlist Search")
    print("="*60)
    try:
        search = PlaylistsSearch('Bollywood Hits', limit=2)
        result = search.result()
        assert 'result' in result
        assert len(result['result']) > 0
        print(f"✅ Found {len(result['result'])} playlists")
        print(f"   Top playlist: {result['result'][0]['title']}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_video_formats():
    """Test getting video formats"""
    print("\n" + "="*60)
    print("🎵 Testing Video Formats Retrieval")
    print("="*60)
    try:
        formats = Video.getFormats('7bj_2x-IoRE')
        assert formats is not None
        assert 'streamingData' in formats
        print(f"✅ Retrieved video formats successfully")
        print(f"   Format count: {len(formats['streamingData'].get('formats', []))}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_pagination():
    """Test search pagination"""
    print("\n" + "="*60)
    print("🎵 Testing Search Pagination")
    print("="*60)
    try:
        search = VideosSearch('Hindi songs', limit=5)
        page1 = search.result()
        print(f"✅ Page 1: {len(page1['result'])} videos")
        
        search.next()
        page2 = search.result()
        print(f"✅ Page 2: {len(page2['result'])} videos")
        
        # Ensure we got different results
        assert page1['result'][0]['id'] != page2['result'][0]['id']
        print("✅ Pagination working correctly")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("YouTube Search Python - Comprehensive Testing")
    print("Testing with Indian & Myanmar Songs")
    print("="*60)
    
    results = []
    
    # Sync tests
    results.append(("Sync Video (Indian)", test_sync_video_indian()))
    results.append(("Sync Search (Indian)", test_sync_search_indian()))
    results.append(("Sync Search (Myanmar)", test_sync_search_myanmar()))
    results.append(("Channel Search", test_channels_search()))
    results.append(("Playlist Search", test_playlists_search()))
    results.append(("Video Formats", test_video_formats()))
    results.append(("Search Pagination", test_pagination()))
    
    # Async tests
    results.append(("Async Video (Indian)", asyncio.run(test_async_video_indian())))
    results.append(("Async Search (Indian)", asyncio.run(test_async_search_indian())))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    return all(result for _, result in results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

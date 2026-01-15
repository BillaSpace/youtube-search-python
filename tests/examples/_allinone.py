"""Test script to verify refactored library functionality"""
import asyncio
import sys
# Fix Windows encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from youtubesearchpython import Video, VideosSearch, ChannelsSearch, Playlist
from youtubesearchpython.aio import VideosSearch as AsyncVideosSearch, Video as AsyncVideo

def test_sync_video():
    """Test synchronous video retrieval"""
    print("🧪 Testing Sync Video.get()...")
    result = Video.get('https://youtu.be/_JND3HuOmDM')
    assert result is not None
    assert 'title' in result
    assert 'viewCount' in result
    print(f"✅ PASSED - Title: {result['title'][:50]}...")
    print(f"   Views: {result['viewCount']['text']}")

def test_sync_search():
    """Test synchronous video search"""
    print("\n🧪 Testing Sync VideosSearch...")
    search = VideosSearch('Python programming', limit=3)
    result = search.result()
    assert 'result' in result
    assert len(result['result']) > 0
    print(f"✅ PASSED - Found {len(result['result'])} videos")
    print(f"   First result: {result['result'][0]['title'][:50]}...")

def test_sync_channel_search():
    """Test synchronous channel search"""
    print("\n🧪 Testing Sync ChannelsSearch...")
    search = ChannelsSearch('Tech', limit=2)
    result = search.result()
    assert 'result' in result
    assert len(result['result']) > 0
    print(f"✅ PASSED - Found {len(result['result'])} channels")

async def test_async_video():
    """Test asynchronous video retrieval"""
    print("\n🧪 Testing Async Video.get()...")
    result = await AsyncVideo.get('_JND3HuOmDM')
    assert result is not None
    assert 'title' in result
    print(f"✅ PASSED - Title: {result['title'][:50]}...")

async def test_async_search():
    """Test asynchronous video search"""
    print("\n🧪 Testing Async VideosSearch...")
    search = AsyncVideosSearch('Machine Learning', limit=2)
    result = await search.next()
    assert 'result' in result
    assert len(result['result']) > 0
    print(f"✅ PASSED - Found {len(result['result'])} videos")

def test_backward_compat():
    """Test backward compatibility with __future__"""
    print("\n🧪 Testing backward compatibility (__future__ -> aio)...")
    try:
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from youtubesearchpython.__future__ import VideosSearch as FutureVideosSearch
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "__future__" in str(w[0].message)
            assert "aio" in str(w[0].message)
            print("✅ PASSED - Deprecation warning shown correctly")
    except ImportError as e:
        print(f"❌ FAILED - {e}")
        return False
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("YouTube Search Python - Refactoring Verification Tests")
    print("=" * 60)
    
    try:
        # Sync tests
        test_sync_video()
        test_sync_search()
        test_sync_channel_search()
        
        # Async tests
        asyncio.run(test_async_video())
        asyncio.run(test_async_search())
        
        # Backward compatibility
        test_backward_compat()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

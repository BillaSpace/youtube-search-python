# Tests Directory

This directory contains test scripts for the yt-search-python library.

## Test Files

### `full_execution.py`
Comprehensive test script that verifies ALL library methods in both synchronous and asynchronous modes:
- **Search Methods**: VideosSearch, ChannelsSearch, PlaylistsSearch
- **Content Retrieval**: Video, Playlist (URL & ID support), Channel
- **Social Features**: Comments, Recommendations, Search Suggestions
- **Advanced**: StreamURLFetcher, Transcripts
- **Query Tests**: Includes specific tests for "pal pal" and "meharban hua bang bang" with URL/ID verification

Run with: `python3 tests/full_execution.py`

### `verify_all.py`
Legacy verification script for basic library functionality.

## Test Subdirectories

### `async/`
Contains async-specific test examples.

### `sync/`
Contains sync-specific test examples.

### `examples_and_debug/`
Contains various example scripts and debugging utilities.

## Running Tests

```bash
# Run comprehensive test suite
python3 tests/full_execution.py

# Run basic verification
python3 tests/verify_all.py
```

## Known Issues

- **Transcript**: Returns 400 error due to YouTube's IP/Auth blocking. Requires cookies or proxies (se
- e README.md).

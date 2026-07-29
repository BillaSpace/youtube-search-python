# Changelogs

All notable changes to this project will be documented in this file.

## [2.0.0] - 2026-01-18

### 🎉 Major Refactoring Release

### Added
- ✨ **`future` module** - Clear naming for async operations
- 🧪 **Comprehensive testing** - Tested with Indian & Myanmar songs
- 📚 **Professional README** - Complete rewrite with extensive examples
- 📝 **CHANGELOG** - Version tracking
- 🌍 **Regional examples** - Indian and Myanmar content examples
-  Channel , Playlist , Comments , Recommendations , Suggestions 

### Changed
- 📦 **Module structure**: async operations now in `youtubesearchpython.future`
- 📈 **Version**: 1.6.6+master → 2.0.0

### Fixed
- 🐛 **Duplicate method**: Removed duplicate `__enhanceThumbnailsAsync` in video.py
- ⚡ **Async correctness**: Fixed async/sync inconsistencies
- 🔗 **Import paths**: Updated all module imports

### what i Tested personally
- ✅ Indian songs (Kesariya, Arijit Singh, T-Series)
- ✅ Myanmar songs (love songs, Burmese music)
- ✅ Video search (sync & async)
- ✅ Channel search
- ✅ Pagination
- ✅ Video metadata retrieval

---

## [2.0.0] - Previous Release

### Added
- 📱 ANDROID client as default
- ✨ Async Video methods
- 🔄 Enhanced stream URL handling

### Changed
- 🔢 Updated Latest web client versions & parsing
- ⚙️ httpx 0.28+ compatibility

### Fixed
- Multiple bug fixes & code cleaned for rediabilty across modules

---

## Migration Guide

### To 2.0.0

**Async imports:**
```python
# Use this
from youtubesearchpython.future import VideosSearch

# Sync remains same  
from youtubesearchpython import VideosSearch
```

---

[2.0.0]: https://github.com/BillaSpace/yt-search-python/releases/tag/v2.0.0


## [2.1.1] - 2026-07-30

- fix: eliminate request-layer fd leak, dedupe HTTP/component handlers, fix crashes across hashtag/playlist/comments/transcript

- Replace per-call ephemeral httpx clients with a single pooled sync+async
  client shared across the whole library (root cause of "Too many open
  files" under sustained load)
- Add one canonical innertube request-body builder; fixes a recurring bug
  where hl/gl were set on a dead top-level "client" key instead of nested
  under context.client (search, channelsearch, hashtag comments,
  recommendations, video fallback search, legacy requesthandler)
- Fix Suggestions.get being permanently unreachable due to a duplicate
  method name silently overwriting it in the class body (sync + async)
- Fix Hashtag.get missing required constructor args; give Hashtag/Channel/
  Comments real instance APIs instead of static-only stubs
- Fix Playlist 'NoneType' object is not iterable crash; add graceful
  Mix/Radio playlist detection instead of a bare crash
- Fix a NameError crash in legacy comment parsing (undefined variable)
- Fix Video.getFormats referencing a nonexistent attribute
- Fix Transcript language-selection param being silently ignored
- Fix shelf title returning null for runs-based titles; fix a
  trailing-comma bug that wrapped playlist thumbnails in a 1-tuple
- Fix a crash in the wildcard JSON path-resolver on missing intermediate
  keys
- Dedupe two independent componenthandler.py copies and a third urllib-
  based request implementation into the canonical httpx-based one
- Strip leftover debug prints and disk writes (comments_response.json)
- Remove scratch/debug test scripts; rewrite README.md for better readability & set of examples exclusively 

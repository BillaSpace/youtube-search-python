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

## [2.0.0] - Current Release

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

[2.0.0]: https://github.com/BillaSpace/youtube-search-python/releases/tag/v2.0.0

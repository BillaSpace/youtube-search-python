from youtubesearchpython import PlaylistsSearch
import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

search = PlaylistsSearch('Bollywood Hits', limit=1)
if search.responseSource:
    print(json.dumps(search.responseSource[0], indent=2))

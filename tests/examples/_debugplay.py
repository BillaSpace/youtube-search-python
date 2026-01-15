from youtubesearchpython import PlaylistsSearch
import json
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Fetching Playlist search results for 'Bollywood Hits'...")
search = PlaylistsSearch('Bollywood Hits', limit=2)

print("\nResponse Source Type:")
print(type(search.responseSource))

if isinstance(search.responseSource, list):
    print(f"\nResponse Source Length: {len(search.responseSource)}")
    if len(search.responseSource) > 0:
        print("\nFirst element keys:")
        print(list(search.responseSource[0].keys()))
        print("\nFirst element (truncated):")
        print(json.dumps(search.responseSource[0], indent=2)[:1000])

# Find where the data is
def find_key(obj, target_key, depth=0, max_depth=5):
    if depth > max_depth: return
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == target_key:
                print(f"Found {target_key} at depth {depth}")
            find_key(v, target_key, depth + 1, max_depth)
    elif isinstance(obj, list):
        for item in obj:
            find_key(item, target_key, depth + 1, max_depth)

full_resp = json.loads(search.response)
find_key(full_resp, "playlistRenderer")
find_key(full_resp, "richItemRenderer")

print("\nFull Response (first 4000 chars):")
print(json.dumps(full_resp, indent=2)[:4000])

import json
import httpx
import copy
from urllib.parse import urlencode
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.componenthandler import getValue, getVideoId
from youtubesearchpython.core.utils import format_duration

def __findVideoDataInSearchResults(search_contents, video_id):
    if not search_contents:
        return None
    
    for item in search_contents:
        video_data = None
        if itemSectionKey in item:
            section_contents = getValue(item, [itemSectionKey, 'contents'])
            if section_contents:
                for section_item in section_contents:
                    if videoElementKey in section_item:
                        video_data = section_item[videoElementKey]
                        break
        elif videoElementKey in item:
            video_data = item[videoElementKey]
        
        if video_data:
            found_video_id = getValue(video_data, ['videoId'])
            if found_video_id == video_id:
                return video_data
            nav_video_id = getValue(video_data, ['navigationEndpoint', 'watchEndpoint', 'videoId'])
            if nav_video_id == video_id:
                return video_data
    return None

def test_search_fallback(video_id):
    query = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Searching for: {query}")
    
    request_body = copy.deepcopy(requestPayload)
    request_body['query'] = query
    request_body['client'] = {'hl': 'en', 'gl': 'US'}
    
    url = 'https://www.youtube.com/youtubei/v1/search' + '?' + urlencode({'key': searchKey})
    response = httpx.post(
        url,
        headers={"User-Agent": userAgent, "Content-Type": "application/json"},
        json=request_body,
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        contents = getValue(data, contentPath)
        fallback_contents = getValue(data, fallbackContentPath)
        search_contents = contents if contents else fallback_contents
        
        print(f"Results found in search: {len(search_contents) if search_contents else 0}")
        
        video_data = __findVideoDataInSearchResults(search_contents, video_id)
        if video_data:
            print("✓ Found video data in search results!")
            title = getValue(video_data, ['title', 'runs', 0, 'text'])
            print(f"Title: {title}")
        else:
            print("✗ Video NOT found in search results.")
            # Let's inspect what IS in the search results
            if search_contents:
                for idx, item in enumerate(search_contents[:3]):
                    print(f"Item {idx} keys: {list(item.keys())}")
                    if "richItemRenderer" in item:
                         content = getValue(item, ["richItemRenderer", "content"])
                         print(f"  RichItem content keys: {list(content.keys()) if content else 'None'}")
    else:
        print(f"Search failed with status: {response.status_code}")

if __name__ == "__main__":
    test_search_fallback("7bj_2x-IoRE")

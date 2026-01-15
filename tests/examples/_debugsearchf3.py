import json
import httpx
import copy
from urllib.parse import urlencode
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.componenthandler import getValue, getVideoId

def test_search_fallback(video_id):
    query = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Searching for: {query}")
    
    request_body = copy.deepcopy(requestPayload)
    # Use a bigger limit to be sure
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
        
        if search_contents:
            for idx, item in enumerate(search_contents):
                if "itemSectionRenderer" in item:
                    section_contents = getValue(item, ["itemSectionRenderer", "contents"])
                    print(f"Item {idx} is itemSectionRenderer with {len(section_contents) if section_contents else 0} contents")
                    if section_contents:
                        for s_idx, s_item in enumerate(section_contents):
                            print(f"  S_Item {s_idx} keys: {list(s_item.keys())}")
                            # Check if it's nested deep
                            # Sometimes it might be in 'videoRenderer' or 'richItemRenderer'
                            v_id = getValue(s_item, ["videoRenderer", "videoId"])
                            if v_id:
                                print(f"    Found videoId: {v_id}")
                                if v_id == video_id:
                                    print("    [MATCH!]")

if __name__ == "__main__":
    test_search_fallback("7bj_2x-IoRE")

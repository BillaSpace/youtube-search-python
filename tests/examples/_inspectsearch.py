import json
import httpx
import copy
from urllib.parse import urlencode
from youtubesearchpython.core.constants import *
from youtubesearchpython.core.componenthandler import getValue, getVideoId

def test_search_results(video_id):
    query = video_id
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
        
        print(f"Items in search: {len(search_contents) if search_contents else 0}")
        if search_contents:
            for i, item in enumerate(search_contents):
                print(f"Item {i} keys: {list(item.keys())}")
                if "itemSectionRenderer" in item:
                    sc = getValue(item, ["itemSectionRenderer", "contents"])
                    print(f"  Inner contents: {len(sc) if sc else 0}")
                    for j, s_item in enumerate(sc):
                        print(f"    S_Item {j} keys: {list(s_item.keys())}")
                        if "videoRenderer" in s_item:
                            print(f"      videoId: {s_item['videoRenderer'].get('videoId')}")
                        if "lockupViewModel" in s_item:
                             print(f"      lockup contentId: {s_item['lockupViewModel'].get('contentId')}")
                if "richItemRenderer" in item:
                    rich = getValue(item, ["richItemRenderer", "content"])
                    print(f"  Rich content keys: {list(rich.keys()) if rich else 'None'}")
                    if rich and "videoRenderer" in rich:
                         print(f"    videoId: {rich['videoRenderer'].get('videoId')}")
                    if rich and "lockupViewModel" in rich:
                         print(f"    lockup contentId: {rich['lockupViewModel'].get('contentId')}")

if __name__ == "__main__":
    test_search_results("7bj_2x-IoRE")

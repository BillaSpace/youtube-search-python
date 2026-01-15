
from youtubesearchpython import Video
import json

print("Testing Video.get()...")
video = Video.get('7bj_2x-IoRE')

if video:
    print(json.dumps(video, indent=2))
else:
    print("Returned None")

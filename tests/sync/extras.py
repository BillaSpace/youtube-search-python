from youtubesearchpython import *


video = Video.get('https://www.youtube.com/watch?v=z0GKGpObgPY', mode=ResultMode.json, get_upload_date=True)
print(video)

videoInfo = Video.getInfo('https://youtu.be/z0GKGpObgPY', mode=ResultMode.json)
print(videoInfo)

videoFormats = Video.getFormats('z0GKGpObgPY')
print(videoFormats)


suggestions = Suggestions(language='hi', region='IN')
print(suggestions.get('Humnava', mode=ResultMode.json))


hashtag = Hashtag('Bharat', limit=1)
print(hashtag.result())


fetcher = StreamURLFetcher()
videoA = Video.get("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # safe public video
videoB = Video.get("https://www.youtube.com/watch?v=9bZkp7q19f0")  # Gangnam Style - reliable

singleUrlA = fetcher.get(videoA, 22)
allUrlsB = fetcher.getAll(videoB)
print(singleUrlA)
print(allUrlsB)

from yt_dlp import YoutubeDL

ydl_opts = {
    'skip_download': True,
    'getcomments': True,
    'quiet': True,
}
with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info('https://www.youtube.com/watch?v=_ZdsmLgCVdU', download=False)
    comments_list = info.get('comments', [])
    print(f"Found {len(comments_list)} comments")
    for c in comments_list[:20]:
        print(c['text'])


print(Transcript.get("https://www.youtube.com/watch?v=L7kF4MXXCoA"))


url = "https://www.youtube.com/watch?v=-1xu0IP35FI"

transcript_en = Transcript.get(url)
if transcript_en.get("languages"):
    transcript_2 = Transcript.get(url, transcript_en["languages"][-1]["params"])
    print(transcript_2)
else:
    print("No additional languages available")


print(Channel.get("UC_aEa8K-EOJ3d6gOs7HcyNg"))


channel = Channel("UC_aEa8K-EOJ3d6gOs7HcyNg")
print(len(channel.result["playlists"]))
while channel.has_more_playlists():
    channel.next()
    print(len(channel.result["playlists"]))

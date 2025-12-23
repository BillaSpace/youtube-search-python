import asyncio
from youtubesearchpython.__future__ import Video, StreamURLFetcher, Suggestions
from youtubesearchpython import Hashtag, Comments, Transcript, Channel

async def main():
    video = await Video.get('https://www.youtube.com/watch?v=z0GKGpObgPY', get_upload_date=True)
    print(video)
    
    videoInfo = await Video.getInfo('https://youtu.be/z0GKGpObgPY')
    print(videoInfo)
    
    videoFormats = await Video.getFormats('z0GKGpObgPY')
    print(videoFormats)

    suggestions = await Suggestions.get('PyarHumara', language='en', region='US')
    print(suggestions)

    hashtag = Hashtag('raw', limit=1)
    result = await asyncio.to_thread(hashtag.result)
    print(result)

    fetcher = StreamURLFetcher()
    
    videoA = await Video.get("https://www.youtube.com/watch?v=aqz-KE-bpKQ")
    videoB = await Video.get("https://www.youtube.com/watch?v=ZwNxYJfW-eU")
    
    await fetcher.getJavaScript()
    
    singleUrlA = await fetcher.get(videoA, 22)
    allUrlsB = await fetcher.getAll(videoB)
    print(singleUrlA)
    print(allUrlsB)

    comments = Comments("_ZdsmLgCVdU")
    await asyncio.to_thread(comments.getNextComments)
    while len(comments.comments["result"]) < 100 and comments.hasMoreComments:
        print(len(comments.comments["result"]))
        await asyncio.to_thread(comments.getNextComments)
    print("Found all comments")

    transcript_en = await asyncio.to_thread(Transcript.get, "https://youtube.com?v=Um2PmRde4OQ")
    print(transcript_en)
    
    url = "https://www.youtube.com/watch?v=-1xu0IP35FI"
    transcript_en = await asyncio.to_thread(Transcript.get, url)
    if transcript_en.get("languages"):
        transcript_2 = await asyncio.to_thread(Transcript.get, url, transcript_en["languages"][-1]["params"])
        print(transcript_2)

    channel_info = await asyncio.to_thread(Channel.get, "UC_aEa8K-EOJ3D6gOs7HcyNg")
    print(channel_info)

    channel = Channel("UC_aEa8K-EOJ3D6gOs7HcyNg")
    await asyncio.to_thread(channel.init)
    print(len(channel.result["playlists"]))
    while channel.has_more_playlists():
        await asyncio.to_thread(channel.next)
        print(len(channel.result["playlists"]))

asyncio.run(main())

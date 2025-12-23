import asyncio
from youtubesearchpython.__future__ import Search, VideosSearch, ChannelsSearch, PlaylistsSearch, CustomSearch, VideoSortOrder

async def main():
    search = Search('TeraZikr', limit=5, language='en', region='US')
    result = await search.next()
    print(result)

    videosSearch = VideosSearch('HumnavaMere', limit=10, language='en', region='US')
    videosResult = await videosSearch.next()
    print(videosResult)

    channelsSearch = ChannelsSearch('T-Series', limit=5, language='en', region='US')
    channelsResult = await channelsSearch.next()
    print(channelsResult)

    playlistsSearch = PlaylistsSearch('BollywoodHipHop/TrapRemixes', limit=1, language='en', region='US')
    playlistsResult = await playlistsSearch.next()
    print(playlistsResult)

    customSearch = CustomSearch('NoCopyrightSounds', VideoSortOrder.uploadDate, language='en', region='US')
    customResult = await customSearch.next()
    print(customResult)

    search = VideosSearch('PalPal')
    index = 0
    result = await search.next()
    for video in result['result']:
        index += 1
        print(f'{index} - {video["title"]}')
    result = await search.next()
    for video in result['result']:
        index += 1
        print(f'{index} - {video["title"]}')
    result = await search.next()
    for video in result['result']:
        index += 1
        print(f'{index} - {video["title"]}')

asyncio.run(main())

import asyncio
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import patch

import httpx
import psutil

from youtubesearchpython.core.constants import ResultMode, SearchMode
from youtubesearchpython.core.playlist import PlaylistCore
from youtubesearchpython.core.componenthandler import getValue
from youtubesearchpython.core.requests import RequestCore, aclose_clients, close_clients
from youtubesearchpython.core.utils import get_cleaned_url, get_playlist_id, get_video_id, normalize_thumbnails
from youtubesearchpython.search import VideosSearch
from youtubesearchpython.future.search import VideosSearch as AsyncVideosSearch


def test_get_value_supports_negative_indices():
    assert getValue({"runs": [{"text": "a"}, {"text": "b"}]}, ["runs", -1, "text"]) == "b"


def test_url_normalization_and_playlist_id():
    assert get_video_id('https://youtu.be/pnxL4OOzPEc?si=abc') == 'pnxL4OOzPEc'
    assert get_video_id('https://youtube.com/shorts/pnxL4OOzPEc?feature=share') == 'pnxL4OOzPEc'
    assert get_video_id('https://youtube.com/live/pnxL4OOzPEc?si=abc') == 'pnxL4OOzPEc'
    assert get_cleaned_url('https://youtube.com/live/pnxL4OOzPEc?si=abc') == 'https://www.youtube.com/watch?v=pnxL4OOzPEc'
    assert get_playlist_id('https://youtube.com/playlist?list=RDpnxL4OOzPEc&playnext=1&si=abc') == 'RDpnxL4OOzPEc'


def test_thumbnail_normalization_rejects_wrong_video():
    thumbs = [
        {'url': 'https://i.ytimg.com/vi/WRONG000000/hqdefault.jpg', 'width': 480, 'height': 360},
        {'url': '//i.ytimg.com/vi/pnxL4OOzPEc/hqdefault.jpg', 'width': 480, 'height': 360},
    ]
    result = normalize_thumbnails(thumbs, 'pnxL4OOzPEc')
    assert len(result) == 1
    assert result[0]['url'] == 'https://i.ytimg.com/vi/pnxL4OOzPEc/hqdefault.jpg'
    fallback = normalize_thumbnails([], 'pnxL4OOzPEc')
    assert fallback[0]['url'].endswith('/pnxL4OOzPEc/hqdefault.jpg')


def test_videos_search_is_live_filter_sync_and_async():
    with patch('youtubesearchpython.core.search.SearchCore.sync_create', lambda self: None), \
         patch('youtubesearchpython.core.search.SearchCore._getComponents', lambda self, *args: None):
        normal = VideosSearch('test')
        live = VideosSearch('test', is_live=True)
    assert normal.searchPreferences == SearchMode.videos
    assert live.searchPreferences == SearchMode.livestreams
    async_normal = AsyncVideosSearch('test')
    async_live = AsyncVideosSearch('test', is_live=True)
    assert async_normal.searchPreferences == SearchMode.videos
    assert async_live.searchPreferences == SearchMode.livestreams


def _rd_fixture():
    return {
        'contents': {
            'twoColumnWatchNextResults': {
                'playlist': {
                    'playlist': {
                        'playlistPanelRenderer': {
                            'title': 'Mix - Azul',
                            'contents': [
                                {'playlistPanelVideoRenderer': {
                                    'videoId': 'pnxL4OOzPEc',
                                    'title': {'simpleText': 'AZUL'},
                                    'thumbnail': {'thumbnails': [
                                        {'url': 'https://i.ytimg.com/vi/pnxL4OOzPEc/hqdefault.jpg', 'width': 480, 'height': 360}
                                    ]},
                                    'longBylineText': {'runs': [{
                                        'text': 'Guru Randhawa',
                                        'navigationEndpoint': {'browseEndpoint': {'browseId': 'UC123'}}
                                    }]},
                                    'lengthText': {'simpleText': '2:32'},
                                    'selected': True,
                                }},
                                {'playlistPanelVideoRenderer': {
                                    'videoId': 'abcdefghijk',
                                    'title': {'simpleText': 'Next'},
                                    'thumbnail': {'thumbnails': [
                                        {'url': 'https://i.ytimg.com/vi/abcdefghijk/hqdefault.jpg', 'width': 480, 'height': 360}
                                    ]},
                                    'longBylineText': {'runs': [{'text': 'Artist'}]},
                                    'lengthText': {'simpleText': '3:00'},
                                }},
                            ],
                            'continuations': [{
                                'nextRadioContinuationData': {'continuation': 'RD_CONT'}
                            }],
                        }
                    }
                }
            }
        }
    }


def test_rd_playlist_uses_next_endpoint_and_parses_panel():
    core = PlaylistCore('https://youtube.com/playlist?list=RDpnxL4OOzPEc&playnext=1&si=x', None, ResultMode.dict, 10)
    core.prepare_first_request()
    assert '/youtubei/v1/next?' in core.url
    assert core.data['playlistId'] == 'RDpnxL4OOzPEc'
    assert core.data['videoId'] == 'pnxL4OOzPEc'
    core.responseSource = _rd_fixture()
    core._process(first=True)
    assert core.result['info']['id'] == 'RDpnxL4OOzPEc'
    assert core.result['info']['title'] == 'Mix - Azul'
    assert [x['id'] for x in core.result['videos']] == ['pnxL4OOzPEc', 'abcdefghijk']


def test_async_client_survives_repeated_event_loops():
    async def once():
        core = RequestCore(timeout=1)
        return core.timeout
    assert asyncio.run(once()) == 1
    assert asyncio.run(once()) == 1
    asyncio.run(aclose_clients())


class _Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def do_GET(self):
        body = b'{}'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(body)
    def do_POST(self):
        length = int(self.headers.get('content-length', '0'))
        if length:
            self.rfile.read(length)
        self.do_GET()
    def log_message(self, *args):
        pass


def _fd_count():
    return len(os.listdir('/proc/self/fd')) if os.path.isdir('/proc/self/fd') else 0


def test_fd_lifecycle_under_sync_async_load():
    server = ThreadingHTTPServer(('127.0.0.1', 0), _Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{server.server_port}/'
    close_clients()
    before = _fd_count()
    core = RequestCore(timeout=3)
    core.url = url
    core.data = {'x': 1}
    for _ in range(80):
        assert core.syncPostRequest().status_code == 200

    async def run_async():
        async_core = RequestCore(timeout=3)
        async_core.url = url
        async_core.data = {'x': 1}
        for _ in range(20):
            responses = await asyncio.gather(*(async_core.asyncPostRequest() for _ in range(8)))
            assert all(r.status_code == 200 for r in responses)
        await aclose_clients()

    asyncio.run(run_async())
    close_clients()
    time.sleep(0.2)
    after = _fd_count()
    close_wait = sum(c.status == psutil.CONN_CLOSE_WAIT for c in psutil.Process().net_connections(kind='tcp'))
    server.shutdown()
    server.server_close()
    assert after - before <= 4
    assert close_wait == 0



def test_async_client_auto_closes_on_loop_shutdown():
    import youtubesearchpython.core.requests as request_module
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/"
    seen = {}

    async def run():
        core = RequestCore(timeout=3)
        core.url = url
        response = await core.asyncGetRequest()
        assert response.status_code == 200
        loop = asyncio.get_running_loop()
        client = request_module._async_clients[loop]
        assert not client.is_closed
        seen["client"] = client

    asyncio.run(run())
    server.shutdown()
    server.server_close()
    assert seen["client"].is_closed
    assert not request_module._async_clients
    assert not request_module._async_guards

def _normal_playlist_fixture(continuation='PL_CONT'):
    return {
        'sidebar': {'playlistSidebarRenderer': {'items': [
            {'playlistSidebarPrimaryInfoRenderer': {
                'title': {'runs': [{'text': 'Normal Playlist'}]},
                'thumbnailRenderer': {'playlistVideoThumbnailRenderer': {'thumbnail': {'thumbnails': [
                    {'url': 'https://i.ytimg.com/vi/pnxL4OOzPEc/hqdefault.jpg', 'width': 480, 'height': 360}
                ]}}},
                'stats': [{'runs': [{'text': '2 videos'}]}, {'simpleText': '10 views'}],
            }},
            {'playlistSidebarSecondaryInfoRenderer': {
                'title': {'runs': [{'text': 'Owner', 'navigationEndpoint': {'browseEndpoint': {'browseId': 'UC123'}}}]}
            }},
        ]}},
        'contents': {'twoColumnBrowseResultsRenderer': {'tabs': [{'tabRenderer': {'content': {'sectionListRenderer': {'contents': [
            {'itemSectionRenderer': {'contents': [{'playlistVideoListRenderer': {'contents': [
                {'playlistVideoRenderer': {
                    'videoId': 'pnxL4OOzPEc', 'title': {'runs': [{'text': 'AZUL'}]},
                    'thumbnail': {'thumbnails': [{'url': 'https://i.ytimg.com/vi/pnxL4OOzPEc/hqdefault.jpg'}]},
                    'shortBylineText': {'runs': [{'text': 'Guru', 'navigationEndpoint': {'browseEndpoint': {'browseId': 'UC1'}}}]},
                    'lengthText': {'simpleText': '2:32'}, 'isPlayable': True,
                }},
                {'continuationItemRenderer': {'continuationEndpoint': {'continuationCommand': {'token': continuation}}}},
            ]}}]}}
        ]}}}}]}}
    }


def _normal_playlist_next_fixture():
    return {'onResponseReceivedActions': [{'appendContinuationItemsAction': {'continuationItems': [
        {'playlistVideoRenderer': {
            'videoId': 'pnxL4OOzPEc', 'title': {'runs': [{'text': 'AZUL duplicate'}]},
            'thumbnail': {'thumbnails': [{'url': 'https://i.ytimg.com/vi/pnxL4OOzPEc/hqdefault.jpg'}]},
        }},
        {'playlistVideoRenderer': {
            'videoId': 'abcdefghijk', 'title': {'runs': [{'text': 'Second'}]},
            'thumbnail': {'thumbnails': [{'url': 'https://i.ytimg.com/vi/abcdefghijk/hqdefault.jpg'}]},
        }},
    ]}}]}


def test_normal_playlist_browse_and_continuation_dedup():
    core = PlaylistCore('PL1234567890', None, ResultMode.dict, None)
    core.prepare_first_request()
    assert '/youtubei/v1/browse?' in core.url
    assert core.data['browseId'] == 'VLPL1234567890'
    core.responseSource = _normal_playlist_fixture()
    core._process(first=True)
    assert core.result['info']['title'] == 'Normal Playlist'
    assert core.continuationKey == 'PL_CONT'
    assert [v['id'] for v in core.result['videos']] == ['pnxL4OOzPEc']
    core.responseSource = _normal_playlist_next_fixture()
    core._process(first=False)
    assert [v['id'] for v in core.result['videos']] == ['pnxL4OOzPEc', 'abcdefghijk']


def test_request_timeout_defaults_are_not_overwritten():
    from youtubesearchpython.core.search import SearchCore
    from youtubesearchpython.core.channelsearch import ChannelSearchCore
    from youtubesearchpython.core.suggestions import SuggestionsCore
    from youtubesearchpython.core.video import VideoCore
    assert SearchCore('x', 1, 'en', 'US', SearchMode.videos, None).timeout == 10
    assert ChannelSearchCore('x', 'en', 'US', '', 'UC1', None).timeout == 10
    assert SuggestionsCore(timeout=None).timeout == 10
    assert VideoCore('pnxL4OOzPEc', None, ResultMode.dict, None, False).timeout == 10


def test_component_live_badge_and_thumbnail_identity():
    from youtubesearchpython.core.componenthandler import ComponentHandler
    from youtubesearchpython.core.constants import videoElementKey
    h = ComponentHandler()
    element = {videoElementKey: {
        'videoId': 'pnxL4OOzPEc',
        'title': {'runs': [{'text': 'Live'}]},
        'thumbnail': {'thumbnails': [
            {'url': 'https://i.ytimg.com/vi/WRONG000000/hqdefault.jpg'},
            {'url': 'https://i.ytimg.com/vi/pnxL4OOzPEc/hqdefault.jpg'},
        ]},
        'badges': [{'metadataBadgeRenderer': {'style': 'BADGE_STYLE_TYPE_LIVE_NOW'}}],
    }}
    result = h._getVideoComponent(element)
    assert result['id'] == 'pnxL4OOzPEc'
    assert result['isLive'] is True
    assert all('/vi/pnxL4OOzPEc/' in t['url'] for t in result['thumbnails'])


def test_custom_headers_reach_transport():
    seen = {}
    class HeaderHandler(_Handler):
        def do_GET(self):
            seen['token'] = self.headers.get('x-youtube-identity-token')
            super().do_GET()
    server = ThreadingHTTPServer(('127.0.0.1', 0), HeaderHandler)
    thread = Thread(target=server.serve_forever, daemon=True); thread.start()
    core = RequestCore(timeout=2)
    core.url = f'http://127.0.0.1:{server.server_port}/'
    core.headers = {'x-youtube-identity-token': 'abc'}
    assert core.syncGetRequest().status_code == 200
    server.shutdown(); server.server_close(); close_clients()
    assert seen['token'] == 'abc'


def test_async_transport_across_real_separate_event_loops():
    server = ThreadingHTTPServer(('127.0.0.1', 0), _Handler)
    thread = Thread(target=server.serve_forever, daemon=True); thread.start()
    url = f'http://127.0.0.1:{server.server_port}/'
    async def once():
        core = RequestCore(timeout=2); core.url = url
        return (await core.asyncGetRequest()).status_code
    before = _fd_count()
    assert asyncio.run(once()) == 200
    assert asyncio.run(once()) == 200
    asyncio.run(aclose_clients())
    time.sleep(0.1)
    after = _fd_count()
    server.shutdown(); server.server_close()
    assert after - before <= 3


def test_cookie_cleanup_respects_ownership(tmp_path):
    from youtubesearchpython.core.transcript import TranscriptCore
    user_cookie = tmp_path / 'cookies.txt'
    user_cookie.write_text('# Netscape HTTP Cookie File\n')
    core = TranscriptCore('pnxL4OOzPEc')
    with patch('youtubesearchpython.core.transcript.resolve_cookie_file_ex', return_value=(str(user_cookie), False)), \
         patch.object(core, '_native', lambda path: setattr(core, 'result', {'segments': [{'text': 'x'}], 'languages': []})):
        core.sync_create()
    assert user_cookie.exists()


def test_public_versions_and_live_signature():
    import inspect
    import youtubesearchpython as sync_api
    import youtubesearchpython.future as async_api
    assert sync_api.__version__ == async_api.__version__ == '2.2.1'
    assert 'is_live' in inspect.signature(sync_api.VideosSearch).parameters
    assert 'is_live' in inspect.signature(async_api.VideosSearch).parameters
    assert callable(sync_api.close_clients)
    assert callable(async_api.aclose_clients)


def test_comments_instances_do_not_share_state():
    from youtubesearchpython.core.comments import CommentsCore
    a = CommentsCore('pnxL4OOzPEc')
    b = CommentsCore('abcdefghijk')
    a.continuationKey = 'A'
    a.isNextRequest = True
    a.response = object()
    assert b.continuationKey is None
    assert b.isNextRequest is False
    assert b.response is None


def test_async_search_does_not_refetch_first_page_after_exhaustion():
    from youtubesearchpython.core.search import SearchCore
    core = SearchCore('x', 1, 'en', 'US', SearchMode.videos, 1)
    core.searchMode = (True, False, False)
    calls = {'n': 0}
    async def fake_request():
        calls['n'] += 1
        core.response = json.dumps({'contents': {'twoColumnSearchResultsRenderer': {'primaryContents': {'sectionListRenderer': {'contents': []}}}}})
    core._makeAsyncRequest = fake_request
    assert asyncio.run(core._nextAsync()) == {'result': []}
    assert asyncio.run(core._nextAsync()) == {'result': []}
    assert calls['n'] == 1


def _video_player_fixture():
    return {
        'videoDetails': {
            'videoId': 'pnxL4OOzPEc', 'title': 'AZUL', 'lengthSeconds': '152',
            'viewCount': '1234', 'author': 'Guru', 'channelId': 'UC1',
            'thumbnail': {'thumbnails': [
                {'url': 'https://i.ytimg.com/vi_webp/WRONG000000/hqdefault.webp'},
                {'url': 'https://i.ytimg.com/vi_webp/pnxL4OOzPEc/hqdefault.webp'},
            ]},
            'isLiveContent': False,
        },
        'microformat': {'playerMicroformatRenderer': {'publishDate': '2026-08-01', 'isFamilySafe': True}},
        'streamingData': {'formats': []},
    }


def test_video_result_mode_and_exact_webp_thumbnail():
    from youtubesearchpython.core.video import VideoCore
    core = VideoCore('pnxL4OOzPEc', 'getInfo', ResultMode.json, 1, False)
    core.response = json.dumps(_video_player_fixture())
    core.post_request_processing()
    parsed = json.loads(core.result)
    assert parsed['id'] == 'pnxL4OOzPEc'
    assert parsed['duration']['seconds'] == 152
    assert len(parsed['thumbnails']) == 1
    assert '/vi_webp/pnxL4OOzPEc/' in parsed['thumbnails'][0]['url']


def test_url_parser_rejects_lookalike_hosts():
    assert get_video_id('https://notyoutube.com/watch?v=pnxL4OOzPEc') != 'pnxL4OOzPEc'
    assert get_video_id('https://youtube.com.evil.test/watch?v=pnxL4OOzPEc') != 'pnxL4OOzPEc'
    assert get_playlist_id('VLPL123') == 'PL123'


def test_search_last_page_clears_stale_continuation():
    from youtubesearchpython.core.search import SearchCore
    core = SearchCore('x', 5, 'en', 'US', SearchMode.videos, 1)
    core.continuationKey = 'OLD'
    core.response = json.dumps({'onResponseReceivedCommands': [{'appendContinuationItemsAction': {'continuationItems': [
        {'itemSectionRenderer': {'contents': []}}
    ]}}]})
    core._parseSource()
    assert core.continuationKey is None


def test_comments_last_page_clears_stale_continuation():
    from youtubesearchpython.core.comments import CommentsCore
    class Response:
        def json(self):
            return {'onResponseReceivedEndpoints': [{'appendContinuationItemsAction': {'continuationItems': [
                {'commentThreadRenderer': {'comment': {'commentRenderer': {'commentId': '1'}}}}
            ]}}]}
    core = CommentsCore('pnxL4OOzPEc')
    core.continuationKey = 'OLD'
    core.response = Response()
    core.parse_source()
    assert core.continuationKey is None


def test_async_hashtag_stops_after_exhaustion_without_refetch():
    from youtubesearchpython.core.hashtag import HashtagCore
    core = HashtagCore('x', 5, 'en', 'US', 1)
    core._async_started = True
    core.continuationKey = None
    calls = {'n': 0}
    async def fake(): calls['n'] += 1
    core._asyncMakeRequest = fake
    assert asyncio.run(core._nextAsync()) == {'result': []}
    assert calls['n'] == 0


def test_stream_fetcher_has_no_ytdlp_dependency_and_preserves_direct_urls():
    from urllib.parse import parse_qs, urlsplit
    from youtubesearchpython.streamurlfetcher import StreamURLFetcher
    data = {
        'id': 'pnxL4OOzPEc',
        'streamingData': {
            'formats': [
                {'itag': 18, 'url': 'https://rr.example/videoplayback?id=x'},
                {'itag': 22, 'signatureCipher': 'url=https%3A%2F%2Frr.example%2Fv%3Fid%3Dy&sp=sig&sig=abc'},
                {'itag': 37, 'signatureCipher': 'url=https%3A%2F%2Frr.example%2Fv%3Fid%3Dz&sp=sig&s=encrypted'},
            ]
        }
    }
    fetcher = StreamURLFetcher(po_token='pot123')
    result = fetcher.getAll(data)
    assert [x['itag'] for x in result['streams']] == [18, 22]
    assert [x['itag'] for x in result['unresolved']] == [37]
    for stream in result['streams']:
        assert parse_qs(urlsplit(stream['url']).query)['pot'] == ['pot123']
    assert parse_qs(urlsplit(result['streams'][1]['url']).query)['sig'] == ['abc']


def test_video_player_request_supports_po_token_and_visitor_data():
    from youtubesearchpython.core.video import VideoCore
    from youtubesearchpython.core.constants import ResultMode
    core = VideoCore('pnxL4OOzPEc', 'getFormats', ResultMode.dict, 3, False, po_token='pot123', visitor_data='visitor123')
    core.prepare_innertube_request()
    assert core.data['serviceIntegrityDimensions']['poToken'] == 'pot123'
    assert core.data['context']['client']['visitorData'] == 'visitor123'


def test_video_format_score_prefers_direct_streams():
    from youtubesearchpython.core.video import VideoCore
    direct = {'streamingData': {'formats': [{'itag': 18, 'url': 'https://x'}]}}
    cipher = {'streamingData': {'formats': [{'itag': 18, 'signatureCipher': 'url=x&s=y'}]}}
    assert VideoCore._streaming_score(direct) > VideoCore._streaming_score(cipher)


def test_recommendations_preserve_order_dedupe_and_skip_source():
    from youtubesearchpython.core.recommendations import RecommendationsCore
    core = RecommendationsCore('source00001')
    def compact(video_id, title):
        return {'compactVideoRenderer': {
            'videoId': video_id,
            'title': {'simpleText': title},
            'thumbnail': {'thumbnails': [{'url': f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg'}]},
        }}
    payload = {'contents': {'twoColumnWatchNextResults': {'secondaryResults': {'secondaryResults': {'results': [
        compact('source00001', 'source'),
        compact('abcdefghijk', 'first'),
        compact('abcdefghijk', 'duplicate'),
        compact('lmnopqrstuv', 'second'),
    ]}}}}}
    core.parse_response(payload)
    assert [x['id'] for x in core.resultComponents] == ['abcdefghijk', 'lmnopqrstuv']
    assert all('/vi/' + x['id'] + '/' in x['thumbnails'][0]['url'] for x in core.resultComponents)


def test_channel_search_continuation_uses_token_and_does_not_repeat_first_request():
    from youtubesearchpython.core.channelsearch import ChannelSearchCore
    core = ChannelSearchCore('x', 'en', 'US', 'sp', 'UC1', 3)
    first = {
        'contents': {'twoColumnBrowseResultsRenderer': {'tabs': [{'tabRenderer': {'content': {'sectionListRenderer': {'contents': [
            {'itemSectionRenderer': {'contents': [{'videoRenderer': {'videoId': 'abcdefghijk', 'title': {'runs': [{'text': 'one'}]}}}]}},
            {'continuationItemRenderer': {'continuationEndpoint': {'continuationCommand': {'token': 'NEXT'}}}},
        ]}}}}]}}
    }
    core.response = first
    core.continuationKey = core._find_continuation(first)
    assert core.continuationKey == 'NEXT'
    core._getRequestBody(core.continuationKey)
    assert core.data['continuation'] == 'NEXT'
    assert 'browseId' not in core.data


def test_rd_real_shape_preserves_order_and_ignores_comment_continuations():
    core = PlaylistCore('RDpnxL4OOzPEc', None, ResultMode.dict, 10)
    def panel(video_id, title, selected=False):
        return {'playlistPanelVideoRenderer': {
            'videoId': video_id,
            'title': {'simpleText': title},
            'thumbnail': {'thumbnails': [{'url': f'https://i.ytimg.com/vi/{video_id}/hqdefault.jpg'}]},
            'lengthText': {'simpleText': '3:00'},
            'selected': selected,
        }}
    core.responseSource = {
        'contents': {'watchNext': [
            panel('pnxL4OOzPEc', 'seed', True),
            panel('abcdefghijk', 'two'),
            panel('lmnopqrstuv', 'three'),
            panel('abcdefghijk', 'duplicate'),
        ]},
        'engagementPanels': [{
            'continuationItemRenderer': {'continuationEndpoint': {'continuationCommand': {'token': 'COMMENTS'}}}
        }]
    }
    core._process(first=True)
    assert [x['id'] for x in core.result['videos']] == ['pnxL4OOzPEc', 'abcdefghijk', 'lmnopqrstuv']
    assert core.continuationKey is None


def test_search_skips_malformed_rich_items():
    from youtubesearchpython.core.search import SearchCore
    from youtubesearchpython.core.constants import richItemKey
    core = SearchCore('x', 5, 'en', 'US', SearchMode.videos, 1)
    core.responseSource = [{richItemKey: {'content': None}}]
    core._getComponents(True, False, False)
    assert core.resultComponents == []


def test_hashtag_last_nonempty_page_clears_stale_continuation():
    from youtubesearchpython.core.hashtag import HashtagCore
    from youtubesearchpython.core.constants import richItemKey, videoElementKey
    core = HashtagCore('x', 5, 'en', 'US', 1)
    core.continuationKey = 'OLD'
    core.response = json.dumps({'onResponseReceivedActions': [{'appendContinuationItemsAction': {'continuationItems': [
        {richItemKey: {'content': {videoElementKey: {'videoId': 'abcdefghijk', 'title': {'runs': [{'text': 'x'}]}}}}}
    ]}}]})
    core._getComponents()
    assert core.continuationKey is None


def test_suggestions_non_200_raises_request_error():
    from youtubesearchpython.core.suggestions import SuggestionsCore
    from youtubesearchpython.core.exceptions import YouTubeRequestError
    class Response:
        status_code = 503
        text = 'down'
    core = SuggestionsCore()
    with patch.object(core, 'syncGetRequest', return_value=Response()):
        try:
            core._get('x')
        except YouTubeRequestError:
            pass
        else:
            raise AssertionError('expected YouTubeRequestError')


def test_channel_continuation_keeps_items_after_token_and_dedupes():
    from youtubesearchpython.core.channel import ChannelCore
    from youtubesearchpython.core.constants import ChannelRequestType
    core = ChannelCore('UC1', ChannelRequestType.playlists)
    core.result = {'playlists': [{'id': 'PL1'}]}
    response = {'onResponseReceivedActions': [{'appendContinuationItemsAction': {'continuationItems': [
        {'continuationItemRenderer': {'continuationEndpoint': {'continuationCommand': {'token': 'NEXT'}}}},
        {'gridPlaylistRenderer': {'playlistId': 'PL1', 'title': {'runs': [{'text': 'dup'}]}}},
        {'gridPlaylistRenderer': {'playlistId': 'PL2', 'title': {'runs': [{'text': 'new'}]}}},
    ]}}]}
    core.parse_next_response(response)
    assert core.continuation == 'NEXT'
    assert [x['id'] for x in core.result['playlists']] == ['PL1', 'PL2']


def test_stream_fetcher_can_fetch_formats_from_video_id_without_ytdlp():
    from youtubesearchpython.streamurlfetcher import StreamURLFetcher
    payload = {'streamingData': {'formats': [{'itag': 18, 'url': 'https://rr.example/videoplayback?id=x'}]}}
    with patch('youtubesearchpython.extras.Video.getFormats', return_value=payload) as get_formats:
        fetcher = StreamURLFetcher(po_token='pot', visitor_data='visitor')
        url = fetcher.get('pnxL4OOzPEc', 18)
    assert url and 'pot=pot' in url
    get_formats.assert_called_once_with('pnxL4OOzPEc', po_token='pot', visitor_data='visitor', proxy=None)


def test_async_stream_fetcher_can_fetch_formats_from_video_id_without_ytdlp():
    from youtubesearchpython.future.streamurlfetcher import StreamURLFetcher
    payload = {'streamingData': {'formats': [{'itag': 18, 'url': 'https://rr.example/videoplayback?id=x'}]}}
    async def fake(*args, **kwargs):
        assert args == ('pnxL4OOzPEc',)
        assert kwargs == {'po_token': 'pot', 'visitor_data': 'visitor', 'proxy': None}
        return payload
    with patch('youtubesearchpython.future.extras.Video.getFormats', new=fake):
        result = asyncio.run(StreamURLFetcher(po_token='pot', visitor_data='visitor').getAll('pnxL4OOzPEc'))
    assert result['streams'][0]['itag'] == 18
    assert 'pot=pot' in result['streams'][0]['url']


def test_rd_selected_false_is_not_treated_as_unplayable():
    core = PlaylistCore('RDpnxL4OOzPEc', None, ResultMode.dict, 10)
    core.responseSource = {'items': [
        {'playlistPanelVideoRenderer': {'videoId': 'pnxL4OOzPEc', 'title': {'simpleText': 'seed'}, 'selected': True}},
        {'playlistPanelVideoRenderer': {'videoId': 'abcdefghijk', 'title': {'simpleText': 'next'}, 'selected': False}},
    ]}
    core._process(first=True)
    assert [x['isPlayable'] for x in core.result['videos']] == [True, True]


def test_rd_only_accepts_radio_continuation_not_generic_engagement_tokens():
    core = PlaylistCore('RDpnxL4OOzPEc', None, ResultMode.dict, 10)
    core.responseSource = {
        'items': [{'playlistPanelVideoRenderer': {'videoId': 'pnxL4OOzPEc', 'title': {'simpleText': 'seed'}}}],
        'comments': {'continuationCommand': {'token': 'COMMENTS'}},
        'radio': {'nextRadioContinuationData': {'continuation': 'RADIO_NEXT'}},
    }
    core._process(first=True)
    assert core.continuationKey == 'RADIO_NEXT'
    core.prepare_next_request()
    assert core.data['continuation'] == 'RADIO_NEXT'


def test_rd_continuation_appends_in_order_without_duplicates():
    core = PlaylistCore('RDpnxL4OOzPEc', None, ResultMode.dict, 10)
    core.responseSource = {'items': [
        {'playlistPanelVideoRenderer': {'videoId': 'pnxL4OOzPEc', 'title': {'simpleText': 'seed'}}},
        {'playlistPanelVideoRenderer': {'videoId': 'abcdefghijk', 'title': {'simpleText': 'two'}}},
    ], 'radio': {'nextRadioContinuationData': {'continuation': 'NEXT'}}}
    core._process(first=True)
    core.responseSource = {'items': [
        {'playlistPanelVideoRenderer': {'videoId': 'abcdefghijk', 'title': {'simpleText': 'dup'}}},
        {'playlistPanelVideoRenderer': {'videoId': 'lmnopqrstuv', 'title': {'simpleText': 'three'}}},
    ]}
    core._process(first=False)
    assert [x['id'] for x in core.result['videos']] == ['pnxL4OOzPEc', 'abcdefghijk', 'lmnopqrstuv']
    assert core.continuationKey is None


def test_stream_fetcher_forwards_proxy_to_native_video_fetch():
    from youtubesearchpython.streamurlfetcher import StreamURLFetcher
    payload = {'streamingData': {'formats': [{'itag': 18, 'url': 'https://rr.example/videoplayback?id=x'}]}}
    with patch('youtubesearchpython.extras.Video.getFormats', return_value=payload) as get_formats:
        StreamURLFetcher(proxy='http://127.0.0.1:8080').get('pnxL4OOzPEc', 18)
    assert get_formats.call_args.kwargs['proxy'] == 'http://127.0.0.1:8080'


def test_channel_search_keeps_all_items_in_item_section_order():
    from youtubesearchpython.core.componenthandler import ComponentHandler
    h = ComponentHandler()
    elements = [{'itemSectionRenderer': {'contents': [
        {'videoRenderer': {'videoId': 'abcdefghijk', 'title': {'runs': [{'text': 'one'}]}, 'thumbnail': {'thumbnails': [{'url': 'https://i.ytimg.com/vi/abcdefghijk/hqdefault.jpg'}]}}},
        {'videoRenderer': {'videoId': 'lmnopqrstuv', 'title': {'runs': [{'text': 'two'}]}, 'thumbnail': {'thumbnails': [{'url': 'https://i.ytimg.com/vi/lmnopqrstuv/hqdefault.jpg'}]}}},
    ]}}]
    result = h._getChannelSearchComponent(elements)
    assert [x['id'] for x in result] == ['abcdefghijk', 'lmnopqrstuv']


def test_search_parser_keeps_multiple_sections_and_handles_actions_continuation():
    from youtubesearchpython.core.search import SearchCore
    core = SearchCore('x', 10, 'en', 'US', SearchMode.videos, 1)
    core.continuationKey = 'OLD'
    core.response = json.dumps({'onResponseReceivedActions': [{'appendContinuationItemsAction': {'continuationItems': [
        {'itemSectionRenderer': {'contents': [{'videoRenderer': {'videoId': 'abcdefghijk'}}]}},
        {'itemSectionRenderer': {'contents': [{'videoRenderer': {'videoId': 'lmnopqrstuv'}}]}},
        {'continuationItemRenderer': {'continuationEndpoint': {'continuationCommand': {'token': 'NEXT'}}}},
    ]}}]})
    core._parseSource()
    assert [x['videoRenderer']['videoId'] for x in core.responseSource] == ['abcdefghijk', 'lmnopqrstuv']
    assert core.continuationKey == 'NEXT'


def test_search_continuation_body_does_not_repeat_query_or_filters():
    from youtubesearchpython.core.search import SearchCore
    core = SearchCore('x', 10, 'en', 'US', SearchMode.videos, 1)
    core.continuationKey = 'NEXT'
    core._getRequestBody()
    assert core.data['continuation'] == 'NEXT'
    assert 'query' not in core.data and 'params' not in core.data


def test_hashtag_continuation_body_and_token_position_are_stable():
    from youtubesearchpython.core.hashtag import HashtagCore
    core = HashtagCore('x', 10, 'en', 'US', 1)
    core.params = 'PARAM'
    core.continuationKey = 'NEXT'
    body = core._buildBrowseBody()
    assert body['continuation'] == 'NEXT'
    assert 'browseId' not in body and 'params' not in body
    core.response = json.dumps({'onResponseReceivedActions': [{'appendContinuationItemsAction': {'continuationItems': [
        {'continuationItemRenderer': {'continuationEndpoint': {'continuationCommand': {'token': 'NEXT2'}}}},
        {'richItemRenderer': {'content': {'videoRenderer': {'videoId': 'abcdefghijk'}}}},
    ]}}]})
    core._getComponents()
    assert core.continuationKey == 'NEXT2'


def test_comments_next_does_not_request_again_after_exhaustion():
    from youtubesearchpython.core.comments import CommentsCore
    core = CommentsCore('pnxL4OOzPEc')
    calls = {'sync': 0, 'async': 0}
    core.sync_make_comment_request = lambda: calls.__setitem__('sync', calls['sync'] + 1)
    async def fake_async(): calls['async'] += 1
    core.async_make_comment_request = fake_async
    core.continuationKey = None
    core.sync_create_next()
    asyncio.run(core.async_create_next())
    assert calls == {'sync': 0, 'async': 0}


def test_video_html_date_enhancement_does_not_replace_main_metadata():
    from youtubesearchpython.core.video import VideoCore
    main = _video_player_fixture()
    main['videoDetails']['title'] = 'MAIN TITLE'
    main['microformat']['playerMicroformatRenderer'].pop('publishDate', None)
    core = VideoCore('pnxL4OOzPEc', 'getInfo', ResultMode.dict, 1, True)
    core.responseSource = main
    core.HTMLresponseSource = {'videoDetails': {'title': 'WRONG HTML TITLE'}, 'microformat': {'playerMicroformatRenderer': {'publishDate': '2026-08-02'}}}
    core._VideoCore__getVideoDataFromSearch = lambda *args, **kwargs: core._VideoCore__emptySearchResult('pnxL4OOzPEc')
    core._VideoCore__getVideoComponent('getInfo')
    result = core._VideoCore__videoComponent
    assert result['title'] == 'MAIN TITLE'
    assert result['publishedTime']


def test_video_html_date_request_failure_is_non_fatal_sync_and_async():
    from youtubesearchpython.core.video import VideoCore
    class Response:
        status_code = 503
        def json(self):
            raise ValueError('not json')
    sync_core = VideoCore('pnxL4OOzPEc', 'getInfo', ResultMode.dict, 1, True)
    with patch.object(sync_core, 'syncPostRequest', return_value=Response()):
        sync_core.sync_html_create()
    assert sync_core.HTMLresponseSource == {}

    async_core = VideoCore('pnxL4OOzPEc', 'getInfo', ResultMode.dict, 1, True)
    async def fake_async():
        return Response()
    async_core.asyncPostRequest = fake_async
    asyncio.run(async_core.async_html_create())
    assert async_core.HTMLresponseSource == {}


def test_env_po_token_fallback(monkeypatch):
    monkeypatch.setenv("YT_PO_TOKEN", "env-pot")
    monkeypatch.setenv("YT_VISITOR_DATA", "env-visitor")
    from youtubesearchpython.core.video import VideoCore
    from youtubesearchpython.core.streamurlfetcher import StreamURLFetcherCore
    v=VideoCore("pnxL4OOzPEc", "getFormats", 1, None, False)
    s=StreamURLFetcherCore()
    assert (v.po_token, v.visitor_data)==("env-pot", "env-visitor")
    assert (s.po_token, s.visitor_data)==("env-pot", "env-visitor")


def test_explicit_po_token_beats_env(monkeypatch):
    monkeypatch.setenv("YT_PO_TOKEN", "env-pot")
    monkeypatch.setenv("YT_VISITOR_DATA", "env-visitor")
    from youtubesearchpython.core.video import VideoCore
    v=VideoCore("pnxL4OOzPEc", "getFormats", 1, None, False, po_token="explicit-pot", visitor_data="explicit-visitor")
    assert (v.po_token, v.visitor_data)==("explicit-pot", "explicit-visitor")


def test_legacy_componenthandler_import_path_preserved():
    from youtubesearchpython.handlers.componenthandler import ComponentHandler, getValue, getVideoId
    assert ComponentHandler is not None
    assert getValue({"a":{"b":1}}, ["a","b"]) == 1
    assert getVideoId("https://youtu.be/pnxL4OOzPEc") == "pnxL4OOzPEc"


def test_explicit_empty_auth_disables_env(monkeypatch):
    monkeypatch.setenv("YT_PO_TOKEN", "env-pot")
    monkeypatch.setenv("YT_VISITOR_DATA", "env-visitor")
    from youtubesearchpython.core.requests import get_env_auth
    assert get_env_auth("", "") == ("", "")


def test_cookie_helpers_are_runtime_complete(tmp_path, monkeypatch):
    from youtubesearchpython.core.requests import apply_cookies_to_client, resolve_cookie_file_ex
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text("# Netscape HTTP Cookie File\n.example.com\tTRUE\t/\tFALSE\t0\ttest\tvalue\n")
    monkeypatch.setenv("YOUTUBE_COOKIES_FILE", str(cookie_file))
    path, downloaded = resolve_cookie_file_ex()
    assert path == str(cookie_file.resolve())
    assert downloaded is False
    with httpx.Client() as client:
        apply_cookies_to_client(client, path)
        assert client.cookies.get("test") == "value"


def test_simultaneous_event_loops_do_not_close_each_other():
    import threading
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/"
    errors = []
    def worker():
        async def run():
            core = RequestCore(timeout=3)
            core.url = url
            for _ in range(8):
                responses = await asyncio.gather(*(core.asyncGetRequest() for _ in range(4)))
                assert all(response.status_code == 200 for response in responses)
            await aclose_clients()
        try:
            asyncio.run(run())
        except Exception as exc:
            errors.append(exc)
    threads = [threading.Thread(target=worker) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    server.shutdown()
    server.server_close()
    assert not errors


def test_sync_and_future_public_search_exports_remain_compatible():
    import inspect
    import youtubesearchpython as sync_api
    import youtubesearchpython.future as async_api

    names = [
        'Search', 'VideosSearch', 'ChannelsSearch', 'PlaylistsSearch',
        'CustomSearch', 'ChannelSearch', 'Video', 'Playlist', 'Suggestions',
        'Hashtag', 'Comments', 'Transcript', 'Channel', 'Recommendations',
        'StreamURLFetcher',
    ]
    for name in names:
        assert hasattr(sync_api, name)
        assert hasattr(async_api, name)

    assert 'is_live' in inspect.signature(sync_api.VideosSearch).parameters
    assert 'is_live' in inspect.signature(async_api.VideosSearch).parameters
    assert inspect.iscoroutinefunction(async_api.VideosSearch.next)
    assert inspect.iscoroutinefunction(async_api.PlaylistsSearch.next)
    assert inspect.iscoroutinefunction(async_api.Playlist.get)
    assert inspect.iscoroutinefunction(async_api.Recommendations.get)
    assert inspect.iscoroutinefunction(async_api.StreamURLFetcher.get)

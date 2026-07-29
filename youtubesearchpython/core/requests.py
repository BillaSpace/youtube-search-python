import atexit
import copy
from typing import Optional

import httpx
from youtubesearchpython.core.constants import userAgent, requestPayload

_LIMITS = httpx.Limits(max_connections=200, max_keepalive_connections=20, keepalive_expiry=30.0)
_sync_client: Optional[httpx.Client] = None
_async_client: Optional[httpx.AsyncClient] = None

def _get_sync_client() -> httpx.Client:
    global _sync_client
    if _sync_client is None or _sync_client.is_closed:
        _sync_client = httpx.Client(limits=_LIMITS, cookies={"CONSENT": "YES+1"})
    return _sync_client

def _get_async_client() -> httpx.AsyncClient:
    global _async_client
    if _async_client is None or _async_client.is_closed:
        _async_client = httpx.AsyncClient(limits=_LIMITS, cookies={"CONSENT": "YES+1"})
    return _async_client

def close_clients() -> None:
    global _sync_client, _async_client
    if _sync_client is not None and not _sync_client.is_closed:
        _sync_client.close()
    _sync_client = None
    if _async_client is not None and not _async_client.is_closed:
        try:
            _async_client.close()
        except Exception:
            pass
    _async_client = None

async def aclose_clients() -> None:
    global _async_client
    if _async_client is not None and not _async_client.is_closed:
        await _async_client.aclose()
    _async_client = None

atexit.register(close_clients)

class RequestCore:
    def __init__(self, timeout: Optional[int] = None):
        self.url = None
        self.data = None
        self.timeout = timeout if timeout is not None else 10

    def syncPostRequest(self) -> httpx.Response:
        timeout = self.timeout if self.timeout is not None else 10
        return _get_sync_client().post(
            self.url,
            headers={
                "User-Agent": userAgent,
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Origin": "https://www.youtube.com",
                "Referer": "https://www.youtube.com/",
            },
            json=self.data,
            timeout=timeout,
        )

    async def asyncPostRequest(self) -> httpx.Response:
        timeout = self.timeout if self.timeout is not None else 10
        return await _get_async_client().post(
            self.url,
            headers={
                "User-Agent": userAgent,
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Origin": "https://www.youtube.com",
                "Referer": "https://www.youtube.com/",
            },
            json=self.data,
            timeout=timeout,
        )


    def syncGetRequest(self) -> httpx.Response:
        timeout = self.timeout if self.timeout is not None else 10
        return _get_sync_client().get(self.url, headers={"User-Agent": userAgent}, timeout=timeout)

    async def asyncGetRequest(self) -> httpx.Response:
        timeout = self.timeout if self.timeout is not None else 10
        return await _get_async_client().get(self.url, headers={"User-Agent": userAgent}, timeout=timeout)

    @staticmethod
    def buildInnertubeBody(**overrides) -> dict:
        body = copy.deepcopy(requestPayload)
        client_overrides = overrides.pop("client", None) or {}
        ctx = body.setdefault("context", {})
        client = ctx.setdefault("client", {})
        client.update(client_overrides)
        body.update(overrides)
        return body

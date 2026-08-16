import atexit
import asyncio
import copy
import os
import tempfile
import threading
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from typing import Optional, Tuple

import httpx

from youtubesearchpython.core.constants import requestPayload, userAgent

_LIMITS = httpx.Limits(max_connections=200, max_keepalive_connections=8, keepalive_expiry=5.0)
_COOKIES = {"CONSENT": "YES+1"}
_POST_HEADERS = {
    "User-Agent": userAgent,
    "Accept": "*/*",
    "Content-Type": "application/json",
    "Origin": "https://www.youtube.com",
    "Referer": "https://www.youtube.com/",
}
_GET_HEADERS = {"User-Agent": userAgent}
_sync_client: Optional[httpx.Client] = None
_async_clients = {}
_async_guards = {}
_client_lock = threading.RLock()


def get_env_auth(po_token: Optional[str] = None, visitor_data: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    if po_token is None:
        po_token = os.getenv("YT_PO_TOKEN") or os.getenv("YOUTUBE_PO_TOKEN")
    if visitor_data is None:
        visitor_data = os.getenv("YT_VISITOR_DATA") or os.getenv("YOUTUBE_VISITOR_DATA")
    return po_token, visitor_data


def _get_sync_client() -> httpx.Client:
    global _sync_client
    with _client_lock:
        if _sync_client is None or _sync_client.is_closed:
            _sync_client = httpx.Client(limits=_LIMITS, cookies=_COOKIES)
        return _sync_client


async def _async_client_guard(loop, client: httpx.AsyncClient) -> None:
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        raise
    finally:
        if not client.is_closed:
            try:
                await client.aclose()
            except (RuntimeError, httpx.HTTPError):
                pass
        with _client_lock:
            if _async_clients.get(loop) is client:
                _async_clients.pop(loop, None)
            task = _async_guards.get(loop)
            if task is asyncio.current_task():
                _async_guards.pop(loop, None)


async def _get_async_client() -> httpx.AsyncClient:
    loop = asyncio.get_running_loop()
    with _client_lock:
        client = _async_clients.get(loop)
        if client is not None and not client.is_closed:
            return client
        client = httpx.AsyncClient(limits=_LIMITS, cookies=_COOKIES)
        _async_clients[loop] = client
        _async_guards[loop] = loop.create_task(_async_client_guard(loop, client))
        return client

def close_clients() -> None:
    global _sync_client
    with _client_lock:
        client, _sync_client = _sync_client, None
    if client is not None and not client.is_closed:
        client.close()


async def aclose_clients() -> None:
    global _sync_client
    loop = asyncio.get_running_loop()
    with _client_lock:
        async_client = _async_clients.pop(loop, None)
        guard = _async_guards.pop(loop, None)
        sync_client, _sync_client = _sync_client, None
    current = asyncio.current_task()
    if guard is not None and guard is not current and not guard.done():
        guard.cancel()
        try:
            await guard
        except asyncio.CancelledError:
            pass
    elif async_client is not None and not async_client.is_closed:
        try:
            await async_client.aclose()
        except (RuntimeError, httpx.HTTPError):
            pass
    if sync_client is not None and not sync_client.is_closed:
        sync_client.close()


atexit.register(close_clients)


class RequestCore:
    def __init__(self, timeout: Optional[float] = None):
        self.url = None
        self.data = None
        self.timeout = 10 if timeout is None else timeout
        self.headers = None
        self.proxy = None

    def _headers(self, base: dict) -> dict:
        return {**base, **(self.headers or {})}

    def syncPostRequest(self) -> httpx.Response:
        kwargs = {"headers": self._headers(_POST_HEADERS), "json": self.data, "timeout": self.timeout}
        if self.proxy:
            with httpx.Client(limits=_LIMITS, cookies=_COOKIES, proxy=self.proxy) as client:
                return client.post(self.url, **kwargs)
        return _get_sync_client().post(self.url, **kwargs)

    async def asyncPostRequest(self) -> httpx.Response:
        kwargs = {"headers": self._headers(_POST_HEADERS), "json": self.data, "timeout": self.timeout}
        if self.proxy:
            async with httpx.AsyncClient(limits=_LIMITS, cookies=_COOKIES, proxy=self.proxy) as client:
                return await client.post(self.url, **kwargs)
        client = await _get_async_client()
        return await client.post(self.url, **kwargs)

    def syncGetRequest(self) -> httpx.Response:
        kwargs = {"headers": self._headers(_GET_HEADERS), "timeout": self.timeout}
        if self.proxy:
            with httpx.Client(limits=_LIMITS, cookies=_COOKIES, proxy=self.proxy) as client:
                return client.get(self.url, **kwargs)
        return _get_sync_client().get(self.url, **kwargs)

    async def asyncGetRequest(self) -> httpx.Response:
        kwargs = {"headers": self._headers(_GET_HEADERS), "timeout": self.timeout}
        if self.proxy:
            async with httpx.AsyncClient(limits=_LIMITS, cookies=_COOKIES, proxy=self.proxy) as client:
                return await client.get(self.url, **kwargs)
        client = await _get_async_client()
        return await client.get(self.url, **kwargs)

    @staticmethod
    def buildInnertubeBody(**overrides) -> dict:
        body = copy.deepcopy(requestPayload)
        client_overrides = overrides.pop("client", None) or {}
        client = body.setdefault("context", {}).setdefault("client", {})
        client.update(client_overrides)
        body.update(overrides)
        return body


class YouTubeSearchError(Exception):
    """Base exception for youtube-search-python errors."""
    pass

class YouTubeRequestError(YouTubeSearchError):
    """Exception raised when a request to YouTube fails."""
    pass

class YouTubeParseError(YouTubeSearchError):
    """Exception raised when parsing YouTube response fails."""
    pass

def resolve_cookie_file(
    env_path_var: str = "YOUTUBE_COOKIES_FILE",
    env_url_var: str = "COOKIE_URL",
    default_path: str = "cookies.txt",
) -> Optional[str]:
    path, _downloaded = resolve_cookie_file_ex(env_path_var, env_url_var, default_path)
    return path


def resolve_cookie_file_ex(
    env_path_var: str = "YOUTUBE_COOKIES_FILE",
    env_url_var: str = "COOKIE_URL",
    default_path: str = "cookies.txt",
) -> "tuple[Optional[str], bool]":
  
    path = os.getenv(env_path_var, default_path).strip()
    if path and Path(path).is_file():
        return str(Path(path).resolve()), False
    url = os.getenv(env_url_var, "").strip()
    if not url:
        return None, False
    try:
        if "pastebin.com/" in url and "/raw/" not in url:
            url = url.replace("pastebin.com/", "pastebin.com/raw/", 1)
        elif "batbin.me/" in url and "/raw/" not in url:
            url = url.rstrip("/") + "/raw"

        response = _get_sync_client().get(url, timeout=20, follow_redirects=True)
        response.raise_for_status()
        text = response.text.strip()
        if text.startswith("{"):
            data = response.json()
            value = data.get("cookies") or data.get("content") or data.get("text") or data.get("data")
            raw = data.get("url") or data.get("raw") or data.get("raw_url")
            if not value and raw:
                response = _get_sync_client().get(raw, timeout=20, follow_redirects=True)
                response.raise_for_status()
                value = response.text
            text = value or ""

        if not text:
            return None, False
        if not text.startswith(("# Netscape HTTP Cookie File", "# HTTP Cookie File")):
            text = "# Netscape HTTP Cookie File\n" + text

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as file:
                temp_path = file.name
                file.write(text)
            return temp_path, True
        except Exception:
            if temp_path:
                cleanup_cookie_file(temp_path)
            raise
    except Exception:
        return None, False


def is_temp_cookie_file(path: Optional[str]) -> bool:
    return bool(path) and Path(path).parent == Path(tempfile.gettempdir())


def cleanup_cookie_file(path: Optional[str]) -> None:
    if path and is_temp_cookie_file(path):
        try:
            os.remove(path)
        except OSError:
            pass


def apply_cookies_to_client(client, path: Optional[str]) -> None:
    if not path:
        return
    try:
        jar = MozillaCookieJar(path)
        jar.load(ignore_discard=True, ignore_expires=True)
        for cookie in jar:
            client.cookies.set(cookie.name, cookie.value, domain=cookie.domain, path=cookie.path)
    except Exception:
        pass

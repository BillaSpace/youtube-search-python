"""
Single, shared cookie-file resolver used by both TranscriptCore and
StreamURLFetcherCore, so this logic exists in exactly one place instead of
being copy-pasted (and drifting) between them.

Resolution order:
  1. An explicit local path (env var, default "cookies.txt" in cwd).
  2. A remote COOKIE_URL (pastebin/batbin raw link, or a JSON blob containing
     the cookie text under a `cookies`/`content`/`text`/`data` key, or a
     nested `url`/`raw`/`raw_url` pointing at the real raw text) - downloaded
     once via the shared pooled httpx client (not a fresh client per call)
     and written to a temp file.
"""
import os
import tempfile
from http.cookiejar import MozillaCookieJar
from pathlib import Path
from typing import Optional

from youtubesearchpython.core.requests import _get_sync_client


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

        file = tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False)
        file.write(text)
        file.close()
        return file.name, True
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

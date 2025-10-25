import httpx
import os
from youtubesearchpython.core.constants import userAgent


class RequestCore:
    def __init__(self):
        self.url = None
        self.data = None
        self.timeout = 2
        self.proxy = {}

        http_proxy = os.environ.get("HTTP_PROXY")
        https_proxy = os.environ.get("HTTPS_PROXY")

        if http_proxy or https_proxy:
            self.proxy = {
                "http://": http_proxy,
                "https://": https_proxy,
            }

    def _build_transport(self, http2=True):
        """
        Build HTTP transport with optional HTTP/2.
        """
        proxy_url = self.proxy.get("https://") or self.proxy.get("http://") if self.proxy else None
        return httpx.HTTPTransport(http2=http2, proxy=proxy_url)

    # ---- Public methods ----
    def syncPostRequest(self) -> httpx.Response:
        try:
            with httpx.Client(transport=self._build_transport(http2=True)) as client:
                r = client.post(
                    self.url,
                    headers={"User-Agent": userAgent},
                    json=self.data,
                    timeout=self.timeout,
                )
        except Exception:
            with httpx.Client(transport=self._build_transport(http2=False)) as client:
                r = client.post(
                    self.url,
                    headers={"User-Agent": userAgent},
                    json=self.data,
                    timeout=self.timeout,
                )
        return r

    async def asyncPostRequest(self) -> httpx.Response:
        try:
            async with httpx.AsyncClient(transport=self._build_transport(http2=True)) as client:
                r = await client.post(
                    self.url,
                    headers={"User-Agent": userAgent},
                    json=self.data,
                    timeout=self.timeout,
                )
        except Exception:
            async with httpx.AsyncClient(transport=self._build_transport(http2=False)) as client:
                r = await client.post(
                    self.url,
                    headers={"User-Agent": userAgent},
                    json=self.data,
                    timeout=self.timeout,
                )
        return r

    def syncGetRequest(self) -> httpx.Response:
        try:
            with httpx.Client(transport=self._build_transport(http2=True)) as client:
                r = client.get(
                    self.url,
                    headers={"User-Agent": userAgent},
                    timeout=self.timeout,
                    cookies={"CONSENT": "YES+1"},
                )
        except Exception:
            with httpx.Client(transport=self._build_transport(http2=False)) as client:
                r = client.get(
                    self.url,
                    headers={"User-Agent": userAgent},
                    timeout=self.timeout,
                    cookies={"CONSENT": "YES+1"},
                )
        return r

    async def asyncGetRequest(self) -> httpx.Response:
        try:
            async with httpx.AsyncClient(transport=self._build_transport(http2=True)) as client:
                r = await client.get(
                    self.url,
                    headers={"User-Agent": userAgent},
                    timeout=self.timeout,
                    cookies={"CONSENT": "YES+1"},
                )
        except Exception:
            async with httpx.AsyncClient(transport=self._build_transport(http2=False)) as client:
                r = await client.get(
                    self.url,
                    headers={"User-Agent": userAgent},
                    timeout=self.timeout,
                    cookies={"CONSENT": "YES+1"},
                )
        return r

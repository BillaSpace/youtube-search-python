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

        # Store proxy URLs for manual transport configuration
        if http_proxy or https_proxy:
            self.proxy = {
                "http://": http_proxy,
                "https://": https_proxy,
            }

    def _build_transport(self):
        """
        Build HTTP/2-compatible transport with optional proxies for httpx>=0.28.0
        """
        if self.proxy:
            # pick https proxy first, then http proxy (same behavior as original intent)
            proxy_url = self.proxy.get("https://") or self.proxy.get("http://")
            return httpx.HTTPTransport(http2=True, proxy=proxy_url)
        return httpx.HTTPTransport(http2=True)

    def syncPostRequest(self) -> httpx.Response:
        with httpx.Client(transport=self._build_transport()) as client:
            return client.post(
                self.url,
                headers={"User-Agent": userAgent},
                json=self.data,
                timeout=self.timeout,
            )

    async def asyncPostRequest(self) -> httpx.Response:
        async with httpx.AsyncClient(transport=self._build_transport()) as client:
            r = await client.post(
                self.url,
                headers={"User-Agent": userAgent},
                json=self.data,
                timeout=self.timeout,
            )
            return r

    def syncGetRequest(self) -> httpx.Response:
        with httpx.Client(transport=self._build_transport()) as client:
            return client.get(
                self.url,
                headers={"User-Agent": userAgent},
                timeout=self.timeout,
                cookies={"CONSENT": "YES+1"},
            )

    async def asyncGetRequest(self) -> httpx.Response:
        async with httpx.AsyncClient(transport=self._build_transport()) as client:
            r = await client.get(
                self.url,
                headers={"User-Agent": userAgent},
                timeout=self.timeout,
                cookies={"CONSENT": "YES+1"},
            )
            return r

import httpx
from typing import Optional

from youtubesearchpython.core.constants import userAgent

class RequestCore:
    def __init__(self, timeout: Optional[int] = None):
        self.url = None
        self.data = None
        self.timeout = timeout if timeout is not None else 10

    def syncPostRequest(self) -> httpx.Response:
        timeout = self.timeout if self.timeout is not None else 10
        return httpx.post(
            self.url,
            headers={"User-Agent": userAgent},
            json=self.data,
            timeout=timeout,
        )

    async def asyncPostRequest(self) -> httpx.Response:
        timeout = self.timeout if self.timeout is not None else 10
        async with httpx.AsyncClient() as client:
            r = await client.post(self.url, headers={"User-Agent": userAgent}, json=self.data, timeout=timeout)
            return r

    def syncGetRequest(self) -> httpx.Response:
        timeout = self.timeout if self.timeout is not None else 10
        return httpx.get(self.url, headers={"User-Agent": userAgent}, timeout=timeout, cookies={'CONSENT': 'YES+1'})

    async def asyncGetRequest(self) -> httpx.Response:
        timeout = self.timeout if self.timeout is not None else 10
        async with httpx.AsyncClient() as client:
            r = await client.get(self.url, headers={"User-Agent": userAgent}, timeout=timeout, cookies={'CONSENT': 'YES+1'})
            return r

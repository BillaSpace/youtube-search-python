# Just experimental nor tried
from typing import Union
from youtubesearchpython.core.streamurlfetcher import StreamURLFetcherCore


class StreamURLFetcher(StreamURLFetcherCore):
    """
    Gets direct stream URLs for a YouTube video fetched using `Video.get` or `Video.getFormats`.

    This class can fetch direct video URLs without any additional network requests (that's fast).
    It relies on `yt-dlp` being installed and the core deciphering logic provided by the library.

    Usage notes:
    - Call `await fetcher.getJavaScript()` before `get`/`getAll` to ensure player JS is fetched.
    - Do not call getJavaScript more than once per instance (it's cached).
    - Instantiate once and reuse the instance.

    Raises:
        Exception: "ERROR: yt-dlp is not installed. To use this functionality of youtube-search-python, yt-dlp must be installed."

    Examples (async):
        >>> from youtubesearchpython.__future__ import StreamURLFetcher, Video
        >>> fetcher = StreamURLFetcher()
        >>> await fetcher.getJavaScript()
        >>> video = await Video.get("https://www.youtube.com/watch?v=aqz-KE-bpKQ")
        >>> url = await fetcher.get(video, 251)
        >>> print(url)
        "https://r6---sn-gwpa-5bgk.googlevideo.com/videoplayback?..."
    """

    def __init__(self):
        super().__init__()

    async def get(self, videoFormats: dict, itag: int) -> Union[str, None]:
        """
        Gets direct stream URL for a YouTube video fetched using `Video.get` or `Video.getFormats`.

        Args:
            videoFormats (dict): Dictionary returned by `Video.get` or `Video.getFormats`.
            itag (int): Itag of the required stream.

        Returns:
            Union[str, None]: Returns stream URL as string. None, if no stream is present for that itag.
        """
        # synchronous internal decipher fills self._streams
        self._getDecipheredURLs(videoFormats, itag)
        if len(self._streams) == 1:
            return self._streams[0].get("url")
        return None

    async def getAll(self, videoFormats: dict) -> dict:
        """
        Gets all stream URLs for a YouTube video fetched using `Video.get` or `Video.getFormats`.

        Args:
            videoFormats (dict): Dictionary returned by `Video.get` or `Video.getFormats`.

        Returns:
            dict: {"streams": [...]} where each stream is a dict including 'url', 'itag', 'type', etc.
        """
        self._getDecipheredURLs(videoFormats)
        return {"streams": self._streams}

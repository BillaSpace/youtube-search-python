from typing import Union
from youtubesearchpython.core.streamurlfetcher import StreamURLFetcherCore


class StreamURLFetcher(StreamURLFetcherCore):
    '''Gets direct stream URLs for a YouTube video (async version).

    This class can fetch direct video URLs without any additional network requests.
    Call `get` or `getAll` method & pass response returned by `Video.get` or `Video.getFormats` as parameter.
    
    Call `self.getJavaScript` method before any other method from this class.
    Do not call this method more than once & avoid reinstanciating the class.

    Raises:
        Exception: "ERROR: if yt-dlp is not installed. To use this functionality of yt-search-python, yt-dlp should be must installed."
    
    See Also:
        For usage examples, see docs/stream_examples.md (use await with async methods)
    '''
    def __init__(self, proxy: str = None, cookies_file: str = None):
        super().__init__(proxy, cookies_file)

    async def get(self, videoFormats: dict, itag: int) -> Union[str, None]:
        '''Gets direct stream URL for a YouTube video (async).

        Args:
            videoFormats (dict): Dictionary returned by `Video.get` or `Video.getFormats`.
            itag (int): Itag of the required stream.

        Returns:
            Union[str, None]: Returns stream URL as string. None, if no stream is present for that itag.
        
        See Also:
            For usage examples, see docs/stream_examples.md
        '''
        self._getDecipheredURLs(videoFormats, itag)
        if len(self._streams) == 1:
            return self._streams[0]["url"]
        return None

    async def getAll(self, videoFormats: dict) -> dict:
        '''Gets all stream URLs for a YouTube video (async).

        Args:
            videoFormats (dict): Dictionary returned by `Video.get` or `Video.getFormats`.

        Returns:
            dict: Returns stream URLs in a dictionary with 'streams' key.
        
        See Also:
            For usage examples, see docs/stream_examples.md
        '''
        self._getDecipheredURLs(videoFormats)
        return {"streams": self._streams}

    async def getJavaScript(self):
        '''Fetches JavaScript required for deciphering stream URLs (async).
        
        Must be called before using get() or getAll() methods.
        '''
        await super().getJavaScript()

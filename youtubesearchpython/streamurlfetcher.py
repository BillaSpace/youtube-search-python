from typing import Union
from youtubesearchpython.core.streamurlfetcher import StreamURLFetcherCore


class StreamURLFetcher(StreamURLFetcherCore):
    '''Gets direct stream URLs for a YouTube video fetched using `Video.get` or `Video.getFormats`.

    This class can fetch direct video URLs without any additional network requests (that's really fast).
    Call `get` or `getAll` method of this class & pass response returned by `Video.get` or `Video.getFormats` as parameter to fetch direct URLs.
    
    Getting URLs or downloading streams using youtube-dl or PyTube can be slow, because they make requests to fetch the same content.
    This class makes use of yt-dlp which might need the installation of deno runtime pack too (if installed) & makes some slight improvements to yt-dlp 's functioning.
    Avoid instantiating this class more than once (making a global object is recommended).

    Raises:
        Exception: "ERROR: yt-dlp is not installed. To use this functionality of yt-search-python, yt-dlp must be installed on your system."
    
    See Also:
        For usage examples, see docs/stream_examples.md
    '''
    def __init__(self):
        super().__init__()

    def get(self, videoFormats: dict, itag: int) -> Union[str, None]:
        '''Gets direct stream URL for a YouTube video fetched using `Video.get` or `Video.getFormats`.

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

    def getAll(self, videoFormats: dict) -> Union[dict, None]:
        '''Gets all stream URLs for a YouTube video fetched using `Video.get` or `Video.getFormats`.

        Args:
            videoFormats (dict): Dictionary returned by `Video.get` or `Video.getFormats`.

        Returns:
            Union[dict, None]: Returns stream URLs in a dictionary with 'streams' key containing list of stream objects.
        
        See Also:
            For usage examples, see docs/stream_examples.md
        '''
        self._getDecipheredURLs(videoFormats)
        return {"streams": self._streams}

class YouTubeSearchError(Exception):
    """Base exception for youtube-search-python errors."""
    pass

class YouTubeRequestError(YouTubeSearchError):
    """Exception raised when a request to YouTube fails."""
    pass

class YouTubeParseError(YouTubeSearchError):
    """Exception raised when parsing YouTube response fails."""
    pass

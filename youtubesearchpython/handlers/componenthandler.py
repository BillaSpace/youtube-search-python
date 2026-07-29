"""
Kept only for backwards-compatible import paths (`youtubesearchpython.legacy`,
older `HashtagCore` imports). The real, single-source-of-truth implementation
lives in `youtubesearchpython.core.componenthandler`; this used to be a
second hand-maintained copy of the same class that had drifted out of sync
(missing `_getLockupComponent`, `getVideoId`, etc.). Do not add logic here.
"""
from youtubesearchpython.core.componenthandler import ComponentHandler, getValue, getVideoId

__all__ = ["ComponentHandler", "getValue", "getVideoId"]

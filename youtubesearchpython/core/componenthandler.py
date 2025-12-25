from typing import Union, List

def getValue(source: dict, path: List[Union[str, int]]) -> Union[str, int, dict, None]:
    value = source
    for key in path:
        if value is None:
            return None
        if isinstance(key, str):
            if not isinstance(value, dict):
                return None
            value = value.get(key)
        elif isinstance(key, int):
            if not isinstance(value, (list, tuple)):
                return None
            if 0 <= key < len(value):
                value = value[key]
            else:
                return None
        else:
            return None
    return value


def getVideoId(videoLink: str) -> str:
    try:
        parsed = urlparse(videoLink)
        host = (parsed.netloc or "").lower()

        if "youtu.be" in host:
            path = parsed.path.strip("/")
            if path:
                return path.split("?")[0]

        if "youtube" in host or "youtube-nocookie" in host:
            qs = parse_qs(parsed.query)
            if "v" in qs and qs["v"]:
                return qs["v"][0]

            parts = [p for p in parsed.path.split("/") if p]
            for i, p in enumerate(parts):
                if p in ("embed", "v") and i + 1 < len(parts):
                    return parts[i + 1]

            if parts:
                return parts[-1]

        core = videoLink.split("?")[0].split("#")[0].rstrip("/")
        if "/" in core:
            return core.split("/")[-1]

        return core
    except Exception:
        return videoLink

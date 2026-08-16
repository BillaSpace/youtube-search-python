from datetime import datetime, timezone
from typing import Iterable, List, Optional
from urllib.parse import parse_qs, urlparse
import re


def playlist_from_channel_id(channel_id: str) -> str:
    list_id = "UU" + channel_id[2:]
    return f"https://www.youtube.com/playlist?list={list_id}"


def _is_video_id(value: str) -> bool:
    return len(value) == 11 and all(c.isalnum() or c in "-_" for c in value)


def _host_matches(host: str, domain: str) -> bool:
    return host == domain or host.endswith("." + domain)


def get_video_id(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    if _is_video_id(value):
        return value
    try:
        parsed = urlparse(value if "://" in value else "https://" + value)
        host = (parsed.netloc or "").lower().split(":", 1)[0]
        if _host_matches(host, "youtu.be"):
            return parsed.path.strip("/").split("/", 1)[0]
        if _host_matches(host, "youtube.com") or _host_matches(host, "youtube-nocookie.com"):
            query_id = parse_qs(parsed.query).get("v")
            if query_id:
                return query_id[0]
            parts = [part for part in parsed.path.split("/") if part]
            for index, part in enumerate(parts[:-1]):
                if part in {"embed", "shorts", "live", "v"}:
                    return parts[index + 1]
    except (TypeError, ValueError):
        pass
    return value


def get_playlist_id(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    try:
        parsed = urlparse(value if "://" in value else "https://" + value)
        playlist_id = parse_qs(parsed.query).get("list")
        if playlist_id:
            value = playlist_id[0]
    except (TypeError, ValueError):
        pass
    if value.startswith("VL"):
        value = value[2:]
    return value


def get_cleaned_url(video_link: str) -> str:
    video_id = get_video_id(video_link)
    if _is_video_id(video_id):
        return f"https://www.youtube.com/watch?v={video_id}"
    return video_link


def normalize_thumbnails(thumbnails: Optional[Iterable[dict]], video_id: Optional[str] = None) -> List[dict]:
    result = []
    seen = set()
    for thumbnail in thumbnails or []:
        if not isinstance(thumbnail, dict):
            continue
        url = str(thumbnail.get("url") or "").strip()
        if not url:
            continue
        if url.startswith("//"):
            url = "https:" + url
        if video_id:
            match = re.search(r"/(?:vi|vi_webp)/([^/?]+)/", url)
            if match and match.group(1) != video_id:
                continue
        key = url.split("&rs=", 1)[0]
        if key in seen:
            continue
        seen.add(key)
        item = dict(thumbnail)
        item["url"] = url
        result.append(item)
    if not result and video_id:
        result.append({
            "url": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            "width": 480,
            "height": 360,
        })
    return result


def format_view_count(view_count_str: Optional[str]) -> dict:
    if not view_count_str:
        return {"text": None, "short": None}
    try:
        view_count = int(view_count_str)
    except (ValueError, TypeError):
        return {"text": view_count_str, "short": view_count_str}
    text = f"{view_count:,} views"
    if view_count >= 1_000_000_000:
        short = f"{view_count / 1_000_000_000:.1f}B views".replace(".0", "")
    elif view_count >= 1_000_000:
        short = f"{view_count / 1_000_000:.1f}M views".replace(".0", "")
    elif view_count >= 1_000:
        short = f"{view_count / 1_000:.1f}K views".replace(".0", "")
    else:
        short = f"{view_count} views"
    return {"text": text, "short": short}


def format_duration(seconds_str: Optional[str]) -> dict:
    if seconds_str is None or seconds_str == "":
        return {"seconds": None, "text": None}
    try:
        seconds = int(seconds_str)
    except (ValueError, TypeError):
        return {"seconds": None, "text": seconds_str}
    hours, remainder = divmod(seconds, 3600)
    minutes, remaining_seconds = divmod(remainder, 60)
    text = f"{hours}:{minutes:02d}:{remaining_seconds:02d}" if hours else f"{minutes}:{remaining_seconds:02d}"
    return {"seconds": seconds, "text": text}


def format_published_time(publish_date: Optional[str]) -> Optional[str]:
    if not publish_date:
        return None
    try:
        pub_date = datetime.fromisoformat(publish_date.replace("Z", "+00:00"))
        if pub_date.tzinfo is None:
            pub_date = pub_date.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - pub_date.astimezone(timezone.utc)
        if delta.total_seconds() < 0:
            return "Upcoming"
        years = delta.days // 365
        months = delta.days // 30
        weeks = delta.days // 7
        days = delta.days
        if years:
            return f"{years} year{'s' if years != 1 else ''} ago"
        if months:
            return f"{months} month{'s' if months != 1 else ''} ago"
        if weeks:
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"
        if days:
            return f"{days} day{'s' if days != 1 else ''} ago"
        seconds = max(0, int(delta.total_seconds()))
        hours = seconds // 3600
        if hours:
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        minutes = (seconds % 3600) // 60
        if minutes:
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        return "Just now"
    except (ValueError, AttributeError, TypeError):
        return None

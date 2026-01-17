from typing import Optional
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone


def playlist_from_channel_id(channel_id: str) -> str:
    list_id = "UU" + channel_id[2:]
    return f"https://www.youtube.com/playlist?list={list_id}"


def get_cleaned_url(video_link: str) -> str:
    if "/live/" in video_link:
        video_id = video_link.split("/live/")[1].split("?")[0].split("#")[0]
        return f"https://www.youtube.com/watch?v={video_id}"

    parsed_url = urlparse(video_link)
    video_id = parse_qs(parsed_url.query).get("v")
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id[0]}"

    if "youtu.be" in video_link:
        path_part = video_link.split("?")[0].split("#")[0]
        video_id = path_part.rstrip("/").split("/")[-1]
        return f"https://www.youtube.com/watch?v={video_id}"

    if "/shorts/" in video_link:
        video_id = video_link.split("/shorts/")[1].split("?")[0].split("#")[0]
        return f"https://www.youtube.com/watch?v={video_id}"

    if len(video_link) == 11 and all(c.isalnum() or c in "-_" for c in video_link):
        return f"https://www.youtube.com/watch?v={video_link}"

    return video_link


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
    if not seconds_str:
        return {"seconds": None, "text": None}

    try:
        seconds = int(seconds_str)
    except (ValueError, TypeError):
        return {"seconds": None, "text": seconds_str}

    minutes = seconds // 60
    remaining_seconds = seconds % 60
    text = f"{minutes}:{remaining_seconds:02d}"

    return {"seconds": seconds, "text": text}


def format_published_time(publish_date: Optional[str]) -> Optional[str]:
    if not publish_date:
        return None

    try:
        pub_date = datetime.fromisoformat(publish_date.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - pub_date

        years = delta.days // 365
        months = delta.days // 30
        weeks = delta.days // 7
        days = delta.days

        if years > 0:
            return f"{years} year{'s' if years > 1 else ''} ago"
        if months > 0:
            return f"{months} month{'s' if months > 1 else ''} ago"
        if weeks > 0:
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        if days > 0:
            return f"{days} day{'s' if days > 1 else ''} ago"

        hours = delta.seconds // 3600
        if hours > 0:
            return f"{hours} hour{'s' if hours > 1 else ''} ago"

        minutes = (delta.seconds % 3600) // 60
        if minutes > 0:
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"

        return "Just now"
    except (ValueError, AttributeError):
        return None

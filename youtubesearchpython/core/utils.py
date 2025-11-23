def playlist_from_channel_id(channel_id: str) -> str:
    if not channel_id:
        raise ValueError("channel_id required")
    cid = channel_id.strip()
    if cid.startswith("UC"):
        list_id = "UU" + cid[2:]
    elif cid.startswith("U"):
        list_id = "UU" + cid[1:]
    else:
        # assume raw id given without prefix
        list_id = "UU" + cid
    return f"https://www.youtube.com/playlist?list={list_id}"

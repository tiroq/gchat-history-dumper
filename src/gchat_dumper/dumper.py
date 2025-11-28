import json
import os
from datetime import datetime
from typing import Optional, Tuple

from .chat_client import ChatClient
from .utils import parse_iso8601, to_rfc3339_utc, safe_parse_datetime


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def sanitize_space_name(space_name: str) -> str:
    return space_name.replace("/", "_")


def dump_space_messages(
    client: ChatClient,
    space_name: str,
    out_dir: str,
    since: Optional[datetime] = None,
    last_synced_iso: Optional[str] = None,
) -> Tuple[int, Optional[str]]:
    """Dump messages from a single space to a JSONL file.

    Returns: (count_written, max_seen_time_iso)
    """
    ensure_dir(out_dir)
    safe_name = sanitize_space_name(space_name)
    out_path = os.path.join(out_dir, f"{safe_name}.jsonl")

    lower_bound_dt: Optional[datetime] = None
    if since:
        lower_bound_dt = since
    if last_synced_iso:
        last_dt = safe_parse_datetime(last_synced_iso)
        if last_dt is not None and (lower_bound_dt is None or last_dt > lower_bound_dt):
            lower_bound_dt = last_dt

    filter_str = None
    if lower_bound_dt is not None:
        iso = to_rfc3339_utc(lower_bound_dt)
        # Field name and syntax are based on current Chat API docs and may change.
        # We still apply a client-side guard even if server ignores this filter.
        filter_str = f'create_time >= "{iso}"'

    written = 0
    page_token: Optional[str] = None
    max_seen_time: Optional[str] = None

    with open(out_path, "a", encoding="utf-8") as f:
        while True:
            resp = client.list_messages(
                space_name=space_name,
                filter_str=filter_str,
                page_size=1000,
                page_token=page_token,
            )
            msgs = resp.get("messages", [])
            if not msgs:
                break

            for msg in msgs:
                create_time = msg.get("createTime") or msg.get("sendTime")
                if create_time:
                    max_seen_time = create_time

                # Extra client-side guard
                if lower_bound_dt is not None and create_time:
                    try:
                        msg_dt = parse_iso8601(create_time)
                        if msg_dt <= lower_bound_dt:
                            continue
                    except Exception:
                        # If parsing fails, we still dump the message
                        pass

                f.write(json.dumps(msg, ensure_ascii=False))
                f.write("\n")
                written += 1

            page_token = resp.get("nextPageToken")
            if not page_token:
                break

    return written, max_seen_time

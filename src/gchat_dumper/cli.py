import argparse
from datetime import datetime
from typing import Dict, List, Optional

from .chat_client import ChatClient
from .checkpoint import load_checkpoint, save_checkpoint
from .dumper import dump_space_messages
from .utils import parse_iso8601


def parse_since_arg(value: str) -> datetime:
    try:
        return parse_iso8601(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gchat-dump",
        description="Dump Google Chat messages from spaces visible to a Chat app.",
    )
    p.add_argument(
        "--service-account-json",
        required=True,
        help="Path to service account JSON with chat.messages.readonly scope.",
    )
    p.add_argument(
        "--output-dir",
        default="chat_dump",
        help="Directory to store JSONL dumps (default: ./chat_dump).",
    )
    p.add_argument(
        "--space",
        action="append",
        help=(
            "Specific space name to dump (e.g. 'spaces/AAAA...'). "
            "Can be passed multiple times. If omitted and --all-spaces not set, "
            "the tool only lists spaces and exits."
        ),
    )
    p.add_argument(
        "--all-spaces",
        action="store_true",
        help="Dump all spaces visible to the app.",
    )
    p.add_argument(
        "--since",
        type=parse_since_arg,
        help=(
            "Only dump messages from this date/datetime (UTC). "
            "Format: YYYY-MM-DD or full ISO 8601."
        ),
    )
    p.add_argument(
        "--checkpoint-file",
        default="chat_dump_checkpoint.json",
        help=(
            "JSON file with per-space last synced timestamps "
            "(default: chat_dump_checkpoint.json)."
        ),
    )
    p.add_argument(
        "--no-checkpoint",
        action="store_true",
        help=(
            "Disable checkpointing; ignore existing checkpoint and do a full dump "
            "(respecting --since)."
        ),
    )
    p.add_argument(
        "--exclude-dms",
        action="store_true",
        help="When using --all-spaces, exclude DIRECT_MESSAGE spaces.",
    )
    return p


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    client = ChatClient(args.service_account_json)

    checkpoint: Dict[str, str] = {}
    if not args.no_checkpoint:
        checkpoint = load_checkpoint(args.checkpoint_file)

    # If no spaces and not all-spaces: list spaces and exit.
    if not args.space and not args.all_spaces:
        spaces = client.list_spaces(include_dms=not args.exclude_dms)
        print("Spaces visible to the app:")
        for s in spaces:
            print(
                f"- {s.get('name')} | type={s.get('spaceType')} "
                f"| display={s.get('displayName', '')}"
            )
        print("\nUse --space <name> or --all-spaces to dump messages.")
        return

    # Determine target spaces
    target_spaces: List[str] = []
    if args.all_spaces:
        spaces = client.list_spaces(include_dms=not args.exclude_dms)
        target_spaces.extend([s["name"] for s in spaces])
    if args.space:
        target_spaces.extend(args.space)

    # Remove duplicates preserving order
    seen = set()
    unique_spaces: List[str] = []
    for s in target_spaces:
        if s not in seen:
            unique_spaces.append(s)
            seen.add(s)

    total_msgs = 0
    updated_checkpoint = dict(checkpoint)

    for space_name in unique_spaces:
        last_synced_iso = None if args.no_checkpoint else checkpoint.get(space_name)
        print(
            f"Dumping space {space_name} "
            f"(since={args.since}, last_synced={last_synced_iso})..."
        )
        written, max_seen_time = dump_space_messages(
            client=client,
            space_name=space_name,
            out_dir=args.output_dir,
            since=args.since,
            last_synced_iso=last_synced_iso,
        )
        print(f"  -> wrote {written} messages")
        total_msgs += written
        if max_seen_time and not args.no_checkpoint:
            updated_checkpoint[space_name] = max_seen_time

    if not args.no_checkpoint:
        save_checkpoint(args.checkpoint_file, updated_checkpoint)
        print(f"Checkpoint updated at {args.checkpoint_file}")

    print(f"Done. Total messages written: {total_msgs}")

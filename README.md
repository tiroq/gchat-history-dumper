# gchat-history-dumper

`gchat-history-dumper` is a small CLI tool that exports **Google Chat** messages
from spaces visible to a **Chat app** (service account based).

- Exports messages to **JSON Lines** (`.jsonl`) per space.
- Supports **all spaces** or a **selected list**.
- Supports incremental sync via a **checkpoint file**.
- Optional `--since` parameter to limit by date.

> ⚠️ This uses the **Google Chat API**, not Google Takeout nor Google Vault.  
> It can only see spaces/messages that your Chat app (service account) is allowed to see.

---

## Features

- List spaces visible to the app.
- Dump one or many spaces to JSONL.
- Incremental sync:
  - Per-space checkpoint with last seen timestamp.
- Optional exclusion of direct messages (DMs).

---

## Installation

```bash
pip install gchat-history-dumper
# or from source:
# pip install .
```

---

## Prerequisites

1. A **Google Cloud project** with the **Google Chat API** enabled.
2. A **service account** JSON file.
3. The service account must have appropriate access:
   - Typically via **domain-wide delegation** and proper OAuth scopes, or
   - As the identity for your Chat app.

The tool uses the scope:

```text
https://www.googleapis.com/auth/chat.messages.readonly
```

---

## Usage

### 1. List spaces

This shows spaces the app can see; no messages are downloaded.

```bash
gchat-dump   --service-account-json service-account.json
```

Example output:

```text
Spaces visible to the app:
- spaces/AAAA1234567 | type=SPACE | display=Dev Chat
- spaces/AAAA9876543 | type=DIRECT_MESSAGE | display=
...
Use --space <name> or --all-spaces to dump messages.
```

---

### 2. Dump a single space

```bash
gchat-dump   --service-account-json service-account.json   --space spaces/AAAA1234567   --output-dir chat_dump
```

Produces:

```text
chat_dump/
  spaces_AAAA1234567.jsonl   # one JSON message per line
  chat_dump_checkpoint.json  # if checkpointing enabled (default)
```

---

### 3. Dump all spaces except DMs, incremental

```bash
gchat-dump   --service-account-json service-account.json   --all-spaces   --exclude-dms   --since 2024-01-01   --output-dir chat_dump   --checkpoint-file chat_dump_checkpoint.json
```

- `--since` gives an initial lower bound.
- On subsequent runs, the checkpoint is used to only fetch new messages per space.

---

### CLI options

```text
gchat-dump --help
```

Key flags:

- `--service-account-json PATH`  
  Path to service account JSON file. **Required.**

- `--output-dir DIR`  
  Where to store JSONL dumps. Default: `./chat_dump`.

- `--space NAME`  
  Space name (e.g. `spaces/AAAA...`). Can be repeated.

- `--all-spaces`  
  Dump all spaces visible to the app.

- `--since DATE_OR_DATETIME`  
  Only dump messages from this date/datetime (UTC).  
  Accepts `YYYY-MM-DD` or full ISO 8601 (`2024-01-01T00:00:00Z`).

- `--checkpoint-file PATH`  
  Path to checkpoint JSON file. Default: `chat_dump_checkpoint.json`.

- `--no-checkpoint`  
  Disable checkpointing (always full dump according to `--since`).

- `--exclude-dms`  
  When using `--all-spaces`, skip `DIRECT_MESSAGE` spaces.

---

## Output format

Each space gets one file: `<output-dir>/<space-name-sanitized>.jsonl`.

Each line is a single JSON object representing a Chat message, as returned by
the Google Chat API (`spaces.messages.list`).

You can process `.jsonl` with tools like `jq`, Python, Spark, etc.

---

## Limitations

- Only content visible to the Chat app is exported.
- Does **not** download attachments/media (yet).
- No Google Vault or Takeout integration.
- Uses service account authentication only (no interactive OAuth flow).

---

## License

MIT – see [LICENSE](LICENSE).

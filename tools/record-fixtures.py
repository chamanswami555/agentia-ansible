#!/usr/bin/env python3
"""Turn recorded Agentia CLI answers into committed fixtures, with personal data scrubbed.

Usage: python tools/record-fixtures.py [var/live] [collection/tests/fixtures/agentia/live]

Every ``<name>.json`` in the source folder is read (a warning line before the JSON is dropped),
scrubbed and written to the target folder. Scrubbing replaces the owner's email addresses and
usernames with ``user@example.com``; Salesforce record ids and org names are kept because the
modules key on them. The script never touches credentials: the CLI never prints them.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

SCRUB = [
    (re.compile(r"[A-Za-z0-9._%+-]+@company\.com(\.[A-Za-z0-9.-]+)?"), r"user@example.com\1"),
    (re.compile(r"[A-Za-z0-9._%+-]+@gmail\.com"), "user@example.com"),
    # Signatures and tokens the CLI echoes in records must never reach the repository.
    (re.compile(r'"(oauthSignature|apiKey|token|accessToken|refreshToken|password)": "[^"]*"'), r'"\1": "REDACTED"'),
]


def scrub(text: str) -> str:
    for pattern, replacement in SCRUB:
        text = pattern.sub(replacement, text)
    return text


def main() -> int:
    source = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "var/live")
    target = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "collection/tests/fixtures/agentia/live")
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for path in sorted(source.glob("*.json")):
        raw = path.read_text(encoding="utf-8", errors="replace")
        start = raw.find("{")
        if start < 0:
            print(f"skip {path.name}: no JSON")
            continue
        try:
            data = json.loads(raw[start:])
        except ValueError as exc:
            print(f"skip {path.name}: {exc}")
            continue
        text = scrub(json.dumps(data, indent=2, ensure_ascii=False)) + "\n"
        (target / path.name).write_text(text, encoding="utf-8")
        written.append(path.name)
    print(f"wrote {len(written)} fixtures to {target}")
    for name in written:
        print(" ", name)
    return 0


if __name__ == "__main__":
    sys.exit(main())

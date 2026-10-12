# MIT License. See LICENSE in the repository root.
"""Event-Driven Ansible source: Copado job and promotion status changes via Agentia CLI.

The plugin polls ``agentia cicd job list --json`` (and optionally ``cicd promotion list``)
and puts one event on the queue every time a record appears or changes status::

    {"agentia": {"kind": "job", "id": "a4N...", "name": "JE-0002", "status": "Error",
                 "previous_status": "In Progress", "record": {...}},
     "meta": {"received_at": 1760000000.0}}

Arguments (all optional):
  cli_path      Path to the agentia executable (default: agentia)
  working_dir   Directory to run the CLI in, where .agentia defaults live
  interval      Seconds between polls (default: 30)
  kinds         List of record kinds to watch: job, promotion (default: [job])
  page_size     Records per list call, 1 to 200 (default: 100)
  statuses      Only emit events whose new status is in this list (default: all)
  emit_initial  Emit an event for every record seen on the first poll (default: false)
  max_polls     Stop after this many polls (used by tests; default: run forever)

Credentials come from the Agentia keychain or AGENTIA_* environment variables of the
rulebook process. The source never receives or prints them.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

COMMANDS = {
    "job": ["cicd", "job", "list"],
    "promotion": ["cicd", "promotion", "list"],
}


def parse_envelope(text: str) -> Dict[str, Any]:
    """Parse the CLI JSON envelope, tolerating a warning line printed before it."""
    start = text.find("{")
    if start < 0:
        raise ValueError("no JSON object in CLI output")
    data = json.loads(text[start:])
    if not isinstance(data, dict):
        raise ValueError("CLI output is not a JSON object")
    if data.get("error"):
        err = data["error"]
        raise RuntimeError(err.get("message") if isinstance(err, dict) else str(err))
    return data


def items_of(result: Any) -> List[Dict[str, Any]]:
    if isinstance(result, list):
        return [r for r in result if isinstance(r, dict)]
    if isinstance(result, dict):
        for key in ("items", "records", "data", "results"):
            if isinstance(result.get(key), list):
                return [r for r in result[key] if isinstance(r, dict)]
    return []


def diff_states(previous: Optional[Dict[str, str]], items: List[Dict[str, Any]], kind: str,
                emit_initial: bool = False) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """Compare the records with the last known statuses; return (events, new_state)."""
    events: List[Dict[str, Any]] = []
    state: Dict[str, str] = {}
    for record in items:
        record_id = str(record.get("id") or record.get("name") or "")
        if not record_id:
            continue
        status = str(record.get("status") or "")
        state[record_id] = status
        if previous is None:
            if emit_initial:
                events.append(_event(kind, record_id, record, status, None))
            continue
        if record_id not in previous:
            events.append(_event(kind, record_id, record, status, None))
        elif previous[record_id] != status:
            events.append(_event(kind, record_id, record, status, previous[record_id]))
    return events, state


def _event(kind, record_id, record, status, previous_status):
    return {
        "kind": kind,
        "id": record_id,
        "name": record.get("name"),
        "template": record.get("template") or record.get("type"),
        "status": status,
        "previous_status": previous_status,
        "record": record,
    }


async def run_cli(cli_path: str, args: List[str], working_dir: Optional[str]) -> Tuple[int, str, str]:
    proc = await asyncio.create_subprocess_exec(
        cli_path, *args, "--json",
        cwd=working_dir or None,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        env=dict(os.environ, CI="1"),
    )
    out, err = await proc.communicate()
    return proc.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")


async def main(queue: asyncio.Queue, args: Dict[str, Any]) -> None:
    cli_path = args.get("cli_path") or "agentia"
    working_dir = args.get("working_dir")
    interval = float(args.get("interval") or 30)
    kinds = [k for k in (args.get("kinds") or ["job"]) if k in COMMANDS]
    page_size = str(args.get("page_size") or 100)
    statuses = args.get("statuses")
    wanted = {str(s).lower() for s in statuses} if statuses else None
    emit_initial = bool(args.get("emit_initial", False))
    max_polls = args.get("max_polls")
    state: Dict[str, Optional[Dict[str, str]]] = {kind: None for kind in kinds}
    polls = 0
    while True:
        for kind in kinds:
            rc, out, err = await run_cli(cli_path, COMMANDS[kind] + ["--page-size", page_size], working_dir)
            try:
                data = parse_envelope(out)
            except (ValueError, RuntimeError) as exc:
                print(f"agentia_jobs: {kind} list failed (rc={rc}): {exc} {err[-300:]}", file=sys.stderr)
                continue
            events, state[kind] = diff_states(state[kind], items_of(data.get("result")), kind, emit_initial)
            for event in events:
                if wanted is not None and event["status"].lower() not in wanted:
                    continue
                await queue.put({"agentia": event, "meta": {"received_at": time.time()}})
        polls += 1
        if max_polls and polls >= int(max_polls):
            return
        await asyncio.sleep(interval)


if __name__ == "__main__":
    # Manual check: python agentia_jobs.py prints events from two polls to stdout.
    class _PrintQueue:
        async def put(self, event):
            print(json.dumps(event))

    asyncio.run(main(_PrintQueue(), {"interval": 5, "max_polls": 2, "emit_initial": True}))

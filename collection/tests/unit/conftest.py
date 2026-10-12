# MIT License. See LICENSE in the repository root.
"""Shared test helpers: run a collection module in-process against the fake Agentia CLI."""

from __future__ import annotations

import importlib
import io
import json
import os
import sys
from pathlib import Path

import pytest
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

REPO = Path(__file__).resolve().parents[3]
FAKE_BIN = REPO / "tools" / "fake-agentia"
FIXTURES = REPO / "collection" / "tests" / "fixtures" / "agentia"
COLLECTIONS_ROOT = REPO / "var"

if str(COLLECTIONS_ROOT) not in sys.path:
    sys.path.insert(0, str(COLLECTIONS_ROOT))


@pytest.fixture
def fake_agentia(tmp_path, monkeypatch):
    """Put the fake CLI first on PATH and return the path of its call log."""
    log = tmp_path / "agentia-calls.jsonl"
    monkeypatch.setenv("PATH", f"{FAKE_BIN}{os.pathsep}{os.environ.get('PATH', '')}")
    monkeypatch.setenv("AGENTIA_FAKE_FIXTURES", str(FIXTURES))
    monkeypatch.setenv("AGENTIA_FAKE_LOG", str(log))
    return log


def read_calls(log):
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_module(module_name, args, check_mode=False):
    """Run ``main()`` of a module with the given options and return its JSON result."""
    payload = {"ANSIBLE_MODULE_ARGS": dict(args)}
    if check_mode:
        payload["ANSIBLE_MODULE_ARGS"]["_ansible_check_mode"] = True
    basic._ANSIBLE_ARGS = to_bytes(json.dumps(payload))
    module = importlib.import_module(f"ansible_collections.chamanswami555.agentia.plugins.modules.{module_name}")
    captured = io.StringIO()
    real_stdout = sys.stdout
    sys.stdout = captured
    try:
        with pytest.raises(SystemExit) as exit_info:
            module.main()
    finally:
        sys.stdout = real_stdout
    output = json.loads(captured.getvalue().strip())
    output["_rc"] = exit_info.value.code
    return output

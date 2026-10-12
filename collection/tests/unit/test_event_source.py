# MIT License. See LICENSE in the repository root.
import asyncio
import importlib.util
import os
from pathlib import Path

import pytest

from conftest import REPO, read_calls

SOURCE = REPO / "collection" / "extensions" / "eda" / "plugins" / "event_source" / "agentia_jobs.py"


def load_source():
    spec = importlib.util.spec_from_file_location("agentia_jobs", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_diff_states_reports_new_and_changed_records():
    src = load_source()
    first = [{"id": "a", "name": "JE-1", "status": "In Progress"}]
    events, state = src.diff_states(None, first, "job")
    assert events == [] and state == {"a": "In Progress"}
    events, state = src.diff_states(None, first, "job", emit_initial=True)
    assert [e["id"] for e in events] == ["a"] and events[0]["previous_status"] is None
    second = [{"id": "a", "name": "JE-1", "status": "Successful"}, {"id": "b", "name": "JE-2", "status": "Error"}]
    events, state = src.diff_states({"a": "In Progress"}, second, "job")
    assert [(e["id"], e["status"], e["previous_status"]) for e in events] == [("a", "Successful", "In Progress"), ("b", "Error", None)]
    assert state == {"a": "Successful", "b": "Error"}


def test_parse_envelope_tolerates_warning_and_raises_on_error():
    src = load_source()
    data = src.parse_envelope(' ›   Warning: x\n{"result": {"items": []}, "status": 0}')
    assert data["result"] == {"items": []}
    with pytest.raises(RuntimeError):
        src.parse_envelope('{"error": {"message": "CICD API key is not configured"}}')
    with pytest.raises(ValueError):
        src.parse_envelope("no json here")


def test_main_emits_status_change_and_new_job_on_second_poll(fake_agentia):
    src = load_source()

    class Queue:
        def __init__(self):
            self.events = []

        async def put(self, event):
            self.events.append(event)

    queue = Queue()
    asyncio.run(src.main(queue, {"interval": 0, "max_polls": 2, "page_size": 100}))
    kinds = [(e["agentia"]["name"], e["agentia"]["status"], e["agentia"]["previous_status"]) for e in queue.events]
    assert kinds == [("JE-0001", "Successful", "In Progress"), ("JE-0006", "Error", None)]
    assert all("received_at" in e["meta"] for e in queue.events)
    assert read_calls(fake_agentia) == [["cicd", "job", "list", "--page-size", "100"]] * 2


def test_main_filters_by_status(fake_agentia):
    src = load_source()

    class Queue:
        def __init__(self):
            self.events = []

        async def put(self, event):
            self.events.append(event)

    queue = Queue()
    asyncio.run(src.main(queue, {"interval": 0, "max_polls": 2, "page_size": 100, "statuses": ["Error"]}))
    assert [e["agentia"]["name"] for e in queue.events] == ["JE-0006"]


def test_main_survives_cli_errors(fake_agentia, monkeypatch, capsys):
    src = load_source()
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-nocreds.json")

    class Queue:
        async def put(self, event):
            raise AssertionError("no event expected")

    asyncio.run(src.main(Queue(), {"interval": 0, "max_polls": 1, "page_size": 100}))
    assert "list failed" in capsys.readouterr().err


def test_job_action_resume(fake_agentia):
    from conftest import run_module
    out = run_module("agentia_job_action", {"id": "a4N000000000002AAA", "action": "resume"})
    assert out["changed"] is True and out["job"]["resumed"] is True
    assert read_calls(fake_agentia)[0] == ["cicd", "job", "resume", "a4N000000000002AAA"]


def test_job_action_check_mode(fake_agentia):
    from conftest import run_module
    out = run_module("agentia_job_action", {"id": "x", "action": "run", "restart": True}, check_mode=True)
    assert out["command"] == ["cicd", "job", "run", "x", "--restart"]
    assert not Path(os.environ["AGENTIA_FAKE_LOG"]).exists()

# MIT License. See LICENSE in the repository root.
"""Modules against recordings of the real Agentia CLI (playground, 14 October 2026)."""
from conftest import read_calls, run_module


def test_auth_info_real_recording(fake_agentia, monkeypatch):
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-live.json")
    out = run_module("agentia_auth_info", {"require": ["cicd"]})
    assert out["_rc"] == 0
    assert out["configured"] == {"cicd": True, "ai": False, "crt": False}


def test_health_check_real_recording(fake_agentia, monkeypatch):
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-live.json")
    out = run_module("agentia_health_check", {})
    checks = out["health"]["checks"]
    assert any(c["checkId"] == "copado" and c["status"] == "pass" for c in checks)


def test_work_real_story_is_idempotent(fake_agentia, monkeypatch):
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-live.json")
    out = run_module("agentia_work", {"id": "US-0000024", "status": "Draft",
                                      "title": "My first Source Format User Story"})
    assert out["changed"] is False
    assert out["work_item"]["pipelineId"] == "a0Wi8000000Mr2TEAS"
    assert [c[:3] for c in read_calls(fake_agentia)] == [["cicd", "work", "get"]]


def test_job_info_real_recording(fake_agentia, monkeypatch):
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-live.json")
    out = run_module("agentia_job_info", {"id": "a0si8000000CVeLAAW", "logs": True})
    assert out["job"]["status"] == "Successful"
    assert out["job"]["template"]["name"] == "SFDX Git Initialization"
    assert out["job"]["steps"][0]["status"] == "Success"
    assert "log" in out["log"]


def test_job_info_list_real_shape(fake_agentia, monkeypatch):
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-live.json")
    out = run_module("agentia_job_info", {"page_size": 10})
    assert len(out["jobs"]) == 1
    assert out["jobs"][0]["name"] == "JE-000"


def test_job_wait_real_recording(fake_agentia, monkeypatch):
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-live.json")
    out = run_module("agentia_job_wait", {"id": "a0si8000000CVeLAAW", "interval": 0})
    assert out["status"] == "Successful" and out["polls"] == 1


def test_event_source_real_list_shape(fake_agentia, monkeypatch):
    import asyncio
    from test_event_source import load_source
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-live.json")
    src = load_source()

    class Queue:
        def __init__(self):
            self.events = []

        async def put(self, event):
            self.events.append(event)

    queue = Queue()
    asyncio.run(src.main(queue, {"interval": 0, "max_polls": 1, "page_size": 10, "emit_initial": True}))
    assert [e["agentia"]["name"] for e in queue.events] == ["JE-000"]
    assert queue.events[0]["agentia"]["status"] == "Successful"

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


def test_work_submit_real_recording(fake_agentia, monkeypatch, tmp_path):
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-live.json")
    out = run_module("agentia_work_submit", {"working_dir": str(tmp_path), "set_story": "US-0000024",
                                             "skip_local_tests": True})
    assert out["changed"] is True
    assert out["submission"]["submit"]["jobId"] == "a0si8000000CVjBAAW"
    assert out["submission"]["userStoriesAheadBehind"]["destinationEnvironmentName"] == "INT-SFP"
    calls = read_calls(fake_agentia)
    assert calls[0] == ["cicd", "work", "set", "US-0000024"]
    assert calls[1] == ["cicd", "work", "submit", "--skip-local-tests", "--skip-pull-request"]


def test_job_wait_real_deploy_job(fake_agentia, monkeypatch):
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-live.json")
    out = run_module("agentia_job_wait", {"id": "a0si8000000CVmPAAW", "interval": 0})
    assert out["status"] == "Successful"
    assert [s["name"] for s in out["job"]["steps"]] == ["Deploy", "Activate Deployed Datakits"]


def test_work_submit_done_real_recording(fake_agentia, monkeypatch, tmp_path):
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-live.json")
    out = run_module("agentia_work_submit", {"working_dir": str(tmp_path), "done": True, "skip_local_tests": True})
    assert out["submission"]["done"]["jobId"] == "a0si8000000CVw5AAG"
    assert "promotion_id=a17i800000XX2PfAAL" in out["submission"]["done"]["message"]


def test_promotion_info_real_get_and_list(fake_agentia, monkeypatch):
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-live.json")
    out = run_module("agentia_promotion_info", {"id": "a17i800000XX2PfAAL"})
    assert out["deployment_job_id"] == "a0si8000000CVxhAAG"
    assert out["promotion"]["isValidationRun"] is False
    assert out["promotion"]["identification"]["promotionName"] == "P00004"
    validation = run_module("agentia_promotion_info", {"id": "a17i800000XX9jaAAD"})
    assert validation["promotion"]["isValidationRun"] is True
    listed = run_module("agentia_promotion_info", {"work_id": "a1vi80000006OHNAA2"})
    assert [p["name"] for p in listed["promotions"]] == ["P00003", "P00002", "P00001"]

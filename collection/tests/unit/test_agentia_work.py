# MIT License. See LICENSE in the repository root.
from conftest import read_calls, run_module


def test_existing_story_with_same_values_is_unchanged(fake_agentia):
    out = run_module("agentia_work", {"id": "US-0001", "status": "Development In Progress"})
    assert out["_rc"] == 0
    assert out["changed"] is False
    assert out["work_item"]["name"] == "US-0001"
    assert out["transaction_id"] == "01a1-get-0001"
    assert [c[:3] for c in read_calls(fake_agentia)] == [["cicd", "work", "get"]]


def test_status_change_updates_and_reports_diff(fake_agentia):
    out = run_module("agentia_work", {"id": "US-0001", "status": "Ready for Testing"})
    assert out["changed"] is True
    assert out["diff"] == {"before": {"status": "Development In Progress"}, "after": {"status": "Ready for Testing"}}
    assert out["work_item"]["status"] == "Ready for Testing"
    calls = read_calls(fake_agentia)
    assert calls[-1] == ["cicd", "work", "update", "a1Y000000000001EAA", "--status", "Ready for Testing"]


def test_check_mode_reports_change_without_calling_update(fake_agentia):
    out = run_module("agentia_work", {"id": "US-0001", "status": "Ready for Testing"}, check_mode=True)
    assert out["changed"] is True
    assert [c[:3] for c in read_calls(fake_agentia)] == [["cicd", "work", "get"]]


def test_create_when_no_story_matches_title(fake_agentia):
    out = run_module("agentia_work", {"title": "Brand new story", "status": "Draft",
                                      "acceptance_criteria": "Created by Ansible"})
    assert out["changed"] is True
    assert out["work_item"]["name"] == "US-0002"
    calls = read_calls(fake_agentia)
    assert calls[0][:4] == ["cicd", "work", "list", "--title"]
    assert calls[1][:3] == ["cicd", "work", "create"]
    assert "--acceptance-criteria" in calls[1]


def test_lookup_by_title_finds_existing_story(fake_agentia):
    out = run_module("agentia_work", {"title": "Improve deployment validation",
                                      "status": "Development In Progress"})
    assert out["changed"] is False
    assert out["work_item"]["name"] == "US-0001"
    assert [c[2] for c in read_calls(fake_agentia)] == ["list"]


def test_create_requires_title(fake_agentia):
    out = run_module("agentia_work", {"status": "Draft", "lookup_by_title": False})
    assert out["_rc"] == 1
    assert "title is required" in out["msg"]


def test_absent_deletes_existing_story(fake_agentia):
    out = run_module("agentia_work", {"id": "US-0001", "state": "absent"})
    assert out["changed"] is True
    assert read_calls(fake_agentia)[-1] == ["cicd", "work", "delete", "a1Y000000000001EAA"]


def test_absent_missing_story_is_unchanged(fake_agentia):
    out = run_module("agentia_work", {"id": "US-9999", "state": "absent"})
    assert out["changed"] is False
    assert out["transaction_id"] == "01a1-get-missing"


def test_cli_error_fails_with_transaction_id(fake_agentia):
    out = run_module("agentia_work", {"id": "US-9999", "status": "Draft"})
    assert out["_rc"] == 1
    assert out["failed"] is True
    assert "US-9999 not found" in out["msg"]
    assert out["transaction_id"] == "01a1-get-missing"


def test_warning_line_before_json_is_tolerated(fake_agentia):
    out = run_module("agentia_work", {"id": "US-WARN", "status": "Draft"})
    assert out["changed"] is False
    assert out["work_item"]["name"] == "US-WARN"


def test_non_json_output_is_a_clear_failure(fake_agentia):
    out = run_module("agentia_work", {"id": "US-BROKEN"})
    assert out["_rc"] == 1
    assert "not JSON" in out["msg"]

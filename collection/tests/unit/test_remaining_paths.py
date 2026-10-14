# MIT License. See LICENSE in the repository root.
"""Optional flags, check mode, timeouts and CLI failures that the main scenarios do not reach."""
import pytest

from conftest import read_calls, run_module


def test_ai_ask_passes_timeout_and_returns_string_answers(fake_agentia):
    out = run_module("agentia_ai_ask", {"agent": "plan", "prompt": "Short answer", "ai_timeout": 30})
    assert out["answer"].startswith("The validation deployment passed")
    assert read_calls(fake_agentia)[0][-2:] == ["--timeout", "30"]


def test_ai_ask_check_mode_asks_nothing(fake_agentia):
    out = run_module("agentia_ai_ask", {"prompt": "Why?"}, check_mode=True)
    assert out["changed"] is False and out["answer"] is None
    assert read_calls(fake_agentia) == []


def test_promotion_check_mode_reports_the_command_with_step_ids(fake_agentia):
    out = run_module("agentia_promotion", {"id": "a0B000000000001EAA", "operation": "merge",
                                           "deployment_step_ids": ["a4O000000000001AAA", "a4O000000000002AAA"]},
                     check_mode=True)
    assert out["changed"] is True
    assert out["command"][-4:] == ["--deployment-step-id", "a4O000000000001AAA", "--deployment-step-id", "a4O000000000002AAA"]
    assert read_calls(fake_agentia) == []


def test_promotion_info_list_by_status(fake_agentia):
    out = run_module("agentia_promotion_info", {"status": "Completed"})
    assert out["promotions"]
    call = read_calls(fake_agentia)[0]
    assert call[:3] == ["cicd", "promotion", "list"]
    assert call[call.index("--status") + 1] == "Completed"


def test_test_run_passes_branch_and_check_mode_runs_nothing(fake_agentia):
    out = run_module("agentia_test_run", {"job_id": "196473", "project_id": "112901", "branch": "feature/US-0042"})
    assert out["passed"] is True
    assert read_calls(fake_agentia)[0][-2:] == ["--branch", "feature/US-0042"]
    dry = run_module("agentia_test_run", {"job_id": "196473", "project_id": "112901"}, check_mode=True)
    assert dry["changed"] is True and dry["command"][:3] == ["testing", "test", "run"]
    assert len(read_calls(fake_agentia)) == 1


def test_work_submit_skips_nested_metadata_detection(fake_agentia, tmp_path):
    out = run_module("agentia_work_submit", {"working_dir": str(tmp_path), "skip_nested_metadata_detection": True},
                     check_mode=True)
    assert "--skip-nested-metadata-detection" in out["commands"][-1]


def test_job_wait_times_out_with_the_last_status(fake_agentia):
    out = run_module("agentia_job_wait", {"id": "a4N000000000001AAA", "interval": 0, "timeout": 0})
    assert out["_rc"] == 1
    assert out["msg"].startswith("Timed out after 0s waiting for job a4N000000000001AAA (last status: In Progress)")
    assert out["polls"] == 1


@pytest.mark.parametrize("module_name, args", [
    ("agentia_ai_ask", {"prompt": "Why?"}),
    ("agentia_auth_info", {}),
    ("agentia_health_check", {}),
    ("agentia_metadata_compare", {"comparison_mode": "INDEX_FILE", "pipeline_id": "p1", "source_org_id": "s1",
                                  "source_credential_id": "c1", "target_org_id": "t1"}),
    ("agentia_promotion_info", {"id": "a0B000000000001EAA"}),
    ("agentia_job_info", {"id": "a4N000000000001AAA"}),
])
def test_modules_fail_with_the_cli_error_when_the_cli_breaks(fake_agentia, monkeypatch, module_name, args):
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "no-such-index.json")
    out = run_module(module_name, args)
    assert out["_rc"] == 1
    assert "fake agentia: cannot read no-such-index.json" in out["msg"]
    assert out["cli_command"].startswith("agentia ")

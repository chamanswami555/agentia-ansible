# MIT License. See LICENSE in the repository root.
from conftest import read_calls, run_module


def test_auth_info_reports_configured_types(fake_agentia):
    out = run_module("agentia_auth_info", {})
    assert out["changed"] is False
    assert out["configured"] == {"cicd": True, "ai": True, "crt": False}
    assert out["transaction_id"] == "01a1-auth-get"


def test_auth_info_fails_when_required_type_missing(fake_agentia, monkeypatch):
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-nocreds.json")
    out = run_module("agentia_auth_info", {"require": ["cicd"]})
    assert out["_rc"] == 1
    assert "cicd" in out["msg"] and "agentia auth set" in out["msg"]
    assert out["configured"]["cicd"] is False


def test_work_fails_clearly_without_credentials(fake_agentia, monkeypatch):
    monkeypatch.setenv("AGENTIA_FAKE_INDEX", "index-nocreds.json")
    out = run_module("agentia_work", {"id": "US-0001", "status": "Draft"})
    assert out["_rc"] == 1
    assert "AGENTIA_CICD_API_KEY" in out["msg"]


def test_health_check_returns_result_and_flags(fake_agentia):
    out = run_module("agentia_health_check", {"git_sizer": True, "path": "/srv/crm"})
    assert out["health"]["summary"]["warn"] == 1
    assert read_calls(fake_agentia)[0] == ["cicd", "health-check", "--git-sizer", "--path", "/srv/crm"]


def test_work_submit_sets_story_then_validates(fake_agentia, tmp_path):
    out = run_module("agentia_work_submit", {"working_dir": str(tmp_path), "set_story": "US-0042",
                                             "apex_test_classes": ["AccountServiceTest", "LeadScoringTest"]})
    assert out["changed"] is True
    assert out["submission"]["action"] == "validate"
    calls = read_calls(fake_agentia)
    assert calls[0] == ["cicd", "work", "set", "US-0042"]
    assert calls[1] == ["cicd", "work", "submit", "--skip-pull-request",
                        "--apex-test-classes=AccountServiceTest,LeadScoringTest"]


def test_work_submit_done_promotes(fake_agentia, tmp_path):
    out = run_module("agentia_work_submit", {"working_dir": str(tmp_path), "done": True})
    assert out["submission"]["action"] == "promote"
    assert read_calls(fake_agentia)[-1] == ["cicd", "work", "submit", "--done", "--skip-pull-request"]


def test_work_submit_check_mode_runs_nothing(fake_agentia, tmp_path):
    out = run_module("agentia_work_submit", {"working_dir": str(tmp_path), "set_story": "US-0042"}, check_mode=True)
    assert out["changed"] is True
    assert out["commands"][0] == ["cicd", "work", "set", "US-0042"]
    assert read_calls(fake_agentia) == []


def test_promotion_run_waits_and_returns_execution_ids(fake_agentia):
    out = run_module("agentia_promotion", {"id": "a0B000000000001EAA", "operation": "merge_and_deploy"})
    assert out["changed"] is True
    assert out["promotion"]["jobExecutionId"] == "a4N000000000001AAA"
    assert read_calls(fake_agentia)[0] == ["cicd", "promotion", "run", "a0B000000000001EAA",
                                           "--operation", "merge_and_deploy", "--wait", "--wait-timeout", "900"]


def test_promotion_resume_uses_resume_flag(fake_agentia):
    out = run_module("agentia_promotion", {"id": "a0B000000000001EAA", "resume": "a4N000000000001AAA"})
    assert out["promotion"]["resumedJobExecutionId"] == "a4N000000000001AAA"


def test_promotion_requires_operation_or_resume(fake_agentia):
    out = run_module("agentia_promotion", {"id": "a0B000000000001EAA"})
    assert out["_rc"] == 1
    assert "one of the following" in out["msg"]


def test_job_info_get_with_logs(fake_agentia):
    out = run_module("agentia_job_info", {"id": "a4N000000000001AAA", "logs": True})
    assert out["job"]["status"] == "In Progress"
    assert "Deploy started" in out["log"]["log"]


def test_job_info_list_with_filters(fake_agentia):
    out = run_module("agentia_job_info", {"status": "Error", "type": "Deploy", "mine": True})
    assert [j["name"] for j in out["jobs"]] == ["JE-0002", "JE-0005"]
    assert read_calls(fake_agentia)[0] == ["cicd", "job", "list", "--page-size", "50",
                                           "--status", "Error", "--type", "Deploy", "--mine"]


def test_job_wait_polls_until_success(fake_agentia):
    out = run_module("agentia_job_wait", {"id": "a4N000000000001AAA", "interval": 0})
    assert out["status"] == "Successful"
    assert out["polls"] == 2
    assert out["changed"] is False


def test_job_wait_fails_on_error_status(fake_agentia):
    out = run_module("agentia_job_wait", {"id": "a4N000000000002AAA", "interval": 0})
    assert out["_rc"] == 1
    assert "ended with status Error" in out["msg"]
    assert out["job"]["steps"][1]["message"].startswith("Apex test")


def test_job_wait_can_tolerate_error_status(fake_agentia):
    out = run_module("agentia_job_wait", {"id": "a4N000000000002AAA", "interval": 0, "fail_on_error": False})
    assert out["_rc"] == 0 and out["status"] == "Error"


def test_metadata_compare_builds_flags(fake_agentia):
    out = run_module("agentia_metadata_compare", {"comparison_mode": "INDEX_FILE", "filter_type": "ApexClass",
                                                  "pipeline_id": "p1", "source_org_id": "s1",
                                                  "source_credential_id": "c1", "target_org_id": "t1"})
    assert out["comparison"]["summary"]["modified"] == 1
    assert read_calls(fake_agentia)[0] == ["cicd", "metadata", "index", "compare", "--comparison-mode", "INDEX_FILE",
                                           "--filter-type", "ApexClass", "--pipeline-id", "p1",
                                           "--source-credential-id", "c1", "--source-org-id", "s1",
                                           "--target-org-id", "t1"]


def test_test_run_passes(fake_agentia):
    out = run_module("agentia_test_run", {"job_id": "196473", "project_id": "112901"})
    assert out["passed"] is True and out["changed"] is True
    assert out["run"]["tests"]["failed"] == 0


def test_test_run_failure_fails_task_with_result(fake_agentia):
    out = run_module("agentia_test_run", {"job_id": "196474", "project_id": "112901"})
    assert out["_rc"] == 1
    assert out["passed"] is False
    assert out["run"]["tests"]["failed"] == 2
    assert "exit code 1" in out["msg"]


def test_test_run_failure_can_be_tolerated(fake_agentia):
    out = run_module("agentia_test_run", {"job_id": "196474", "project_id": "112901", "fail_on_test_failure": False})
    assert out["_rc"] == 0 and out["passed"] is False


def test_ai_ask_returns_answer_and_context_flags(fake_agentia):
    out = run_module("agentia_ai_ask", {"agent": "operate", "prompt": "Why did JE-0002 fail?",
                                        "user_story": "US-0042", "sf_org": "qa"})
    assert out["answer"].startswith("The deploy step failed")
    assert out["response"]["dialogueId"]
    assert read_calls(fake_agentia)[0] == ["ai", "agent", "ask", "--agent", "operate", "-p", "Why did JE-0002 fail?",
                                           "--no-stream", "--user-story", "US-0042", "--sf-org", "qa"]

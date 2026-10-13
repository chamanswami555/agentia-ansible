# MIT License. See LICENSE in the repository root.
"""Every action module must turn a CLI error into a clean failure with the CLI's message.

The first live rehearsal crashed here: fail_json received ``command`` twice. These tests keep
that path covered for each module that passes its own ``command`` to fail_json.
"""
from conftest import run_module


def test_promotion_cli_error_is_a_clean_failure(fake_agentia):
    out = run_module("agentia_promotion", {"id": "P-BAD", "operation": "merge"})
    assert out["_rc"] == 1
    assert out["failed"] is True
    assert "18-character Salesforce ID" in out["msg"]
    assert out["transaction_id"] == "01a1-promotion-bad-id"
    assert out["command"][:3] == ["cicd", "promotion", "run"]
    assert out["cli_command"].startswith("agentia cicd promotion run P-BAD")


def test_work_submit_cli_error_is_a_clean_failure(fake_agentia, tmp_path):
    out = run_module("agentia_work_submit", {"working_dir": str(tmp_path), "set_story": "US-9999"})
    assert out["_rc"] == 1
    assert "US-9999 not found" in out["msg"]
    assert out["commands"][0] == ["cicd", "work", "set", "US-9999"]


def test_job_action_cli_error_is_a_clean_failure(fake_agentia):
    out = run_module("agentia_job_action", {"id": "a4N000000000009AAA", "action": "kill"})
    assert out["_rc"] == 1
    assert "no fixture" in out["msg"]
    assert out["command"] == ["cicd", "job", "kill", "a4N000000000009AAA"]


def test_test_run_cli_error_is_a_clean_failure(fake_agentia):
    out = run_module("agentia_test_run", {"job_id": "000000", "project_id": "112901"})
    assert out["_rc"] == 1
    assert "no fixture" in out["msg"]
    assert out["command"][:3] == ["testing", "test", "run"]


def test_job_wait_cli_error_is_a_clean_failure(fake_agentia):
    out = run_module("agentia_job_wait", {"id": "a4N000000000009AAA", "interval": 0})
    assert out["_rc"] == 1
    assert "no fixture" in out["msg"]
    assert out["polls"] == 0

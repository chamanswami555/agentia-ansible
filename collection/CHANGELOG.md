# Changelog

## 0.1.0 (2026-10-15)

First release.

- Modules: agentia_auth_info, agentia_work, agentia_work_submit, agentia_promotion, agentia_promotion_info,
  agentia_job_info, agentia_job_wait, agentia_job_action, agentia_test_run, agentia_metadata_compare,
  agentia_health_check, agentia_ai_ask.
- Playbooks: release_window (story mode with the Copado Submit, or promotion mode), nightly_validate,
  remediate_failed_job.
- Event-Driven Ansible: the agentia_jobs event source and the copado_release rulebook.
- Verified against a Copado Playground on 14 October 2026 with Agentia CLI 1.0.0-beta.5.

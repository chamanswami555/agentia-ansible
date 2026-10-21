#!/usr/bin/env bash
# Offline demo: run the three collection playbooks against the fake Agentia CLI.
# Needs `make setup` first. Evidence lands in var/demo.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEMO="$ROOT/var/demo"
PLAYBOOK="${ANSIBLE_PLAYBOOK_BIN:-$ROOT/.venv/bin/ansible-playbook}"
rm -rf "$DEMO"
mkdir -p "$DEMO"

export ANSIBLE_COLLECTIONS_PATH="$ROOT/var"
export PATH="$ROOT/tools/fake-agentia:$PATH"
export AGENTIA_FAKE_FIXTURES="$ROOT/collection/tests/fixtures/agentia"
# The fake answers job polls in sequence (running, then finished) by counting earlier calls
# in this log, so the log must be set for every run.
export AGENTIA_FAKE_LOG="$DEMO/agentia-calls.jsonl"
export ANSIBLE_LOCALHOST_WARNING=false
export ANSIBLE_INVENTORY_UNPARSED_WARNING=false

echo "== 0/7 approval gate: without approve and without a terminal the release must stop before the Copado Submit"
set +e
"$PLAYBOOK" "$ROOT/collection/playbooks/release_window.yml" \
  -e "{\"story_ids\":[\"US-0042\"],\"poll_interval\":1,\"repo_dir\":\"$DEMO/gate\",\"evidence_dir\":\"$DEMO/gate/evidence\"}" \
  < /dev/null > "$DEMO/gate.log" 2>&1
gate_rc=$?
set -e
grep -q "Deployment not approved" "$DEMO/gate.log" || { echo "the gate did not fire"; tail -20 "$DEMO/gate.log"; exit 1; }
[ "$gate_rc" -ne 0 ] || { echo "the playbook did not fail at the gate"; exit 1; }
grep -q -- '"--done"' "$AGENTIA_FAKE_LOG" && { echo "the Copado Submit ran without approval"; exit 1; }
echo "== gate held: no Copado Submit without approval"
rm -f "$AGENTIA_FAKE_LOG"

echo "== 1/7 release window (validate, smoke test, approve, promote and deploy, evidence)"
"$PLAYBOOK" "$ROOT/collection/playbooks/release_window.yml" \
  -e "{\"story_ids\":[\"US-0042\"],\"crt_job_id\":\"196473\",\"crt_project_id\":\"112901\",\"approve\":true,\"poll_interval\":1,\"repo_dir\":\"$DEMO\",\"evidence_dir\":\"$DEMO/evidence\"}" \
  | tee "$DEMO/release-window.log"
grep -q "Deployment jobs: \['Successful'\]" "$DEMO/release-window.log" \
  || { echo "release window did not reach a successful deployment job"; exit 1; }

echo "== 2/7 remediate a failed job (diagnosis, incident file, resume)"
"$PLAYBOOK" "$ROOT/collection/playbooks/remediate_failed_job.yml" \
  -e "{\"job_id\":\"a4N000000000002AAA\",\"job_name\":\"JE-0002\",\"resume_on_failure\":true,\"incident_dir\":\"$DEMO/incidents\"}"

echo "== 3/7 nightly validation"
"$PLAYBOOK" "$ROOT/collection/playbooks/nightly_validate.yml" \
  -e "{\"story_ids\":[\"US-0042\"],\"crt_job_id\":\"196473\",\"crt_project_id\":\"112901\",\"repo_dir\":\"$DEMO\",\"evidence_dir\":\"$DEMO/nightly\"}"

echo "== 4/7 release window in promotion mode (merge_and_deploy on an existing promotion)"
"$PLAYBOOK" "$ROOT/collection/playbooks/release_window.yml" \
  -e "{\"story_ids\":[\"US-0042\"],\"deploy_mode\":\"promotion\",\"promotion_id\":\"a0B000000000001EAA\",\"approve\":true,\"poll_interval\":1,\"repo_dir\":\"$DEMO/promotion\",\"evidence_dir\":\"$DEMO/promotion/evidence\"}" \
  | tee "$DEMO/promotion.log"
grep -q "released (promotion mode)" "$DEMO/promotion.log" || { echo "promotion mode did not finish"; exit 1; }

echo "== 5/7 release window with two stories"
"$PLAYBOOK" "$ROOT/collection/playbooks/release_window.yml" \
  -e "{\"story_ids\":[\"US-0042\",\"US-0043\"],\"approve\":true,\"poll_interval\":1,\"repo_dir\":\"$DEMO/two\",\"evidence_dir\":\"$DEMO/two/evidence\"}" \
  | tee "$DEMO/two.log"
grep -q "Deployment jobs: \['Successful', 'Successful'\]" "$DEMO/two.log" || { echo "two stories did not both deploy"; exit 1; }

echo "== 6/7 nightly validation that catches a failed validation deployment"
set +e
AGENTIA_FAKE_INDEX=index-failing-validation.json "$PLAYBOOK" "$ROOT/collection/playbooks/nightly_validate.yml" \
  -e "{\"story_ids\":[\"US-0042\"],\"poll_interval\":1,\"repo_dir\":\"$DEMO/nightly-fail\",\"evidence_dir\":\"$DEMO/nightly-fail/report\"}" \
  > "$DEMO/nightly-fail.log" 2>&1
nightly_rc=$?
set -e
[ "$nightly_rc" -ne 0 ] || { echo "the nightly run did not fail on a failed validation"; exit 1; }
grep -q "Nightly validation found failures" "$DEMO/nightly-fail.log" || { echo "the nightly run failed for another reason"; tail -20 "$DEMO/nightly-fail.log"; exit 1; }
[ -f "$DEMO/nightly-fail/report/nightly-report.json" ] || { echo "no nightly report written"; exit 1; }
echo "== nightly failed as it should, report written"

echo "== 7/7 check mode of every playbook"
"$PLAYBOOK" "$ROOT/collection/playbooks/release_window.yml" --check \
  -e "{\"story_ids\":[\"US-0042\"],\"repo_dir\":\"$DEMO/check\",\"evidence_dir\":\"$DEMO/check/release\"}" > "$DEMO/check-release.log" 2>&1
"$PLAYBOOK" "$ROOT/collection/playbooks/nightly_validate.yml" --check \
  -e "{\"story_ids\":[\"US-0042\"],\"repo_dir\":\"$DEMO/check\",\"evidence_dir\":\"$DEMO/check/nightly\"}" > "$DEMO/check-nightly.log" 2>&1
"$PLAYBOOK" "$ROOT/collection/playbooks/remediate_failed_job.yml" --check \
  -e "{\"job_id\":\"a4N000000000002AAA\",\"job_name\":\"JE-0002\",\"incident_dir\":\"$DEMO/check/incidents\"}" > "$DEMO/check-remediate.log" 2>&1
echo "== check mode: all three playbooks ran without changes"

echo "== evidence written:"
find "$DEMO" -type f -name '*.json' | sort
echo "== Agentia CLI calls replayed: $(wc -l < "$AGENTIA_FAKE_LOG")"

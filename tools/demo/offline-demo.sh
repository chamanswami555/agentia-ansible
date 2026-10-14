#!/usr/bin/env bash
# Offline demo: run the three collection playbooks against the fake Agentia CLI.
# Needs `make setup` first. Evidence lands in var/demo.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEMO="$ROOT/var/demo"
PLAYBOOK="$ROOT/.venv/bin/ansible-playbook"
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

echo "== 0/3 approval gate: without approve and without a terminal the release must stop before the Copado Submit"
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

echo "== 1/3 release window (validate, smoke test, approve, promote and deploy, evidence)"
"$PLAYBOOK" "$ROOT/collection/playbooks/release_window.yml" \
  -e "{\"story_ids\":[\"US-0042\"],\"crt_job_id\":\"196473\",\"crt_project_id\":\"112901\",\"approve\":true,\"poll_interval\":1,\"repo_dir\":\"$DEMO\",\"evidence_dir\":\"$DEMO/evidence\"}" \
  | tee "$DEMO/release-window.log"
grep -q "Deployment jobs: \['Successful'\]" "$DEMO/release-window.log" \
  || { echo "release window did not reach a successful deployment job"; exit 1; }

echo "== 2/3 remediate a failed job (diagnosis, incident file, resume)"
"$PLAYBOOK" "$ROOT/collection/playbooks/remediate_failed_job.yml" \
  -e "{\"job_id\":\"a4N000000000002AAA\",\"job_name\":\"JE-0002\",\"resume_on_failure\":true,\"incident_dir\":\"$DEMO/incidents\"}"

echo "== 3/3 nightly validation"
"$PLAYBOOK" "$ROOT/collection/playbooks/nightly_validate.yml" \
  -e "{\"story_ids\":[\"US-0042\"],\"crt_job_id\":\"196473\",\"crt_project_id\":\"112901\",\"repo_dir\":\"$DEMO\",\"evidence_dir\":\"$DEMO/nightly\"}"

echo "== evidence written:"
find "$DEMO" -type f -name '*.json' | sort
echo "== Agentia CLI calls replayed: $(wc -l < "$AGENTIA_FAKE_LOG")"

#!/usr/bin/env bash
# Offline demo of the Event-Driven Ansible chain: the shipped rulebook polls the fake Agentia CLI,
# sees a job turn to Error on the second poll, and runs remediate_failed_job against the fake.
# Needs `make setup`, ansible-rulebook in .venv and Java 17 (JAVA_HOME). Output lands in var/rulebook-demo.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DEMO="$ROOT/var/rulebook-demo"
rm -rf "$DEMO"
mkdir -p "$DEMO"

if [ -z "${JAVA_HOME:-}" ] && [ -d /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home ]; then
  export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
fi
export ANSIBLE_COLLECTIONS_PATH="$ROOT/var"
export PATH="$ROOT/tools/fake-agentia:$ROOT/.venv/bin:$PATH"
export AGENTIA_FAKE_FIXTURES="$ROOT/collection/tests/fixtures/agentia"
export AGENTIA_FAKE_LOG="$DEMO/agentia-calls.jsonl"
export ANSIBLE_LOCALHOST_WARNING=false
export ANSIBLE_INVENTORY_UNPARSED_WARNING=false

# The source polls every 30 s; the second poll reports the failed job. 100 s covers both polls
# and the remediation playbook; the alarm then stops the rulebook, which otherwise runs for ever.
cd "$DEMO"
set +e
perl -e 'alarm 100; exec @ARGV' ansible-rulebook \
  --rulebook "$ROOT/collection/extensions/eda/rulebooks/copado_release.yml" \
  -i "$ROOT/collection/extensions/eda/inventory.yml" \
  --env-vars AGENTIA_FAKE_FIXTURES,AGENTIA_FAKE_LOG,ANSIBLE_COLLECTIONS_PATH,PWD \
  --print-events > "$DEMO/rulebook.log" 2>&1
set -e

events=$(grep -c "received event" "$DEMO/rulebook.log" || true)
incidents=$(find "$DEMO/evidence/incidents" -name '*.json' 2> /dev/null | wc -l | tr -d ' ')
echo "== events received: $events"
echo "== fake CLI calls: $(wc -l < "$AGENTIA_FAKE_LOG" | tr -d ' ')"
echo "== incident files: $incidents"
grep -E "Incident recorded" "$DEMO/rulebook.log" | sed -E 's/^ *//' | head -1
if [ "$incidents" -lt 1 ] || ! grep -q "Incident recorded" "$DEMO/rulebook.log"; then
  echo "the failed job did not reach the remediation playbook; see $DEMO/rulebook.log"
  exit 1
fi
echo "== remediation ran for the failed job"

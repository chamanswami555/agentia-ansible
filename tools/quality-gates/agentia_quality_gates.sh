#!/usr/bin/env bash
# Local quality gates for a Copado Source Format project, run by `agentia cicd work test` and
# `agentia cicd work submit` when this file is the project root's .agentia_quality_gates.sh.
# Deterministic and offline: it checks the files changed on the story branch, needs no org login,
# and leaves Apex test execution to Copado's validation deployment.
#
# Checks: every changed XML metadata file is well-formed; no changed file carries an org id, a
# session id or a credential; every changed Apex class has a test class in the repository; no
# changed file is larger than 5 MB. Exit 1 on the first failed check, after printing them all.
set -uo pipefail

BASE="${AGENTIA_BASE_BRANCH:-main}"
if git rev-parse --verify -q "origin/$BASE" > /dev/null; then BASE_REF="origin/$BASE"; else BASE_REF="$BASE"; fi
if ! git rev-parse --verify -q "$BASE_REF" > /dev/null; then
  echo "quality gates: base branch $BASE not found; checking the last commit only"
  BASE_REF="HEAD~1"
fi
MERGE_BASE="$(git merge-base HEAD "$BASE_REF" 2>/dev/null || echo "$BASE_REF")"
# bash 3.2 on macOS has no mapfile, so the changed files go through a temporary list
CHANGED_LIST="$(mktemp)"
{ git diff --name-only --diff-filter=ACMR "$MERGE_BASE" HEAD; git diff --name-only --diff-filter=ACMR HEAD; } | awk 'NF' | sort -u > "$CHANGED_LIST"
CHANGED=()
while IFS= read -r line; do CHANGED+=("$line"); done < "$CHANGED_LIST"
rm -f "$CHANGED_LIST"

echo "quality gates: ${#CHANGED[@]} changed file(s) against $BASE_REF"
failed=0
fail() { echo "  FAIL  $1"; failed=1; }
pass() { echo "  ok    $1"; }

check_xml() {
  local f="$1"
  if command -v xmllint > /dev/null 2>&1; then
    xmllint --noout "$f" 2> /dev/null && pass "well-formed XML: $f" || fail "malformed XML: $f"
  elif command -v python3 > /dev/null 2>&1; then
    python3 -I -c "import sys, xml.dom.minidom; xml.dom.minidom.parse(sys.argv[1])" "$f" 2> /dev/null \
      && pass "well-formed XML: $f" || fail "malformed XML: $f"
  else
    echo "  skip  no xmllint or python3 to check $f"
  fi
}

check_secrets() {
  local f="$1"
  if grep -nE '00D[0-9A-Za-z]{12}(?:[0-9A-Za-z]{3})?|<accessToken>|<refreshToken>|password[[:space:]]*=[[:space:]]*["'"'"'][^"'"'"']+|sessionId=' "$f" > /dev/null 2>&1; then
    fail "org id, session id or credential in: $f"
  else
    pass "no secrets: $f"
  fi
}

check_apex_test() {
  local f="$1" name
  name="$(basename "$f" .cls)"
  case "$name" in *Test|*Tests|*_Test) return 0;; esac
  if grep -rlq --include="*.cls" -E "@isTest|@IsTest|testMethod" . 2> /dev/null && [ -n "$(find . -name "${name}Test.cls" -o -name "${name}_Test.cls" -o -name "Test${name}.cls" 2> /dev/null | head -1)" ]; then
    pass "test class exists for Apex class $name"
  else
    fail "no test class (${name}Test.cls) for Apex class $name"
  fi
}

for f in ${CHANGED[@]+"${CHANGED[@]}"}; do
  [ -f "$f" ] || continue
  size=$(wc -c < "$f" | tr -d ' ')
  if [ "$size" -gt 5242880 ]; then fail "larger than 5 MB: $f"; fi
  case "$f" in
    *.xml) check_xml "$f"; check_secrets "$f";;
    *.cls) check_apex_test "$f"; check_secrets "$f";;
    *.trigger|*.js|*.html|*.css|*.json|*.resource) check_secrets "$f";;
  esac
done

if [ -n "${AGENTIA_APEX_TEST_CLASSES:-}" ]; then
  echo "quality gates: Apex test classes ${AGENTIA_APEX_TEST_CLASSES} run in Copado's validation deployment, not locally"
fi

if [ "$failed" -ne 0 ]; then echo "quality gates: FAILED"; exit 1; fi
echo "quality gates: passed"

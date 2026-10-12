// MIT License. See LICENSE in the repository root.
import assert from 'node:assert/strict'
import {test} from 'node:test'

import {AgentiaCliError, itemsOf, parseEnvelope} from './agentia-cli.js'
import {parseRecap, renderReleasePlaybook} from './playbook.js'

test('renderReleasePlaybook produces valid YAML with quoted values', () => {
  const text = renderReleasePlaybook({
    storyIds: ['US-0042', 'US-0043'],
    promotionId: 'a0B000000000001EAA',
    crtJobId: '196473',
    repoDir: '/srv/crm',
    generatedAt: '2026-10-12T10:00:00.000Z',
  })
  assert.match(text, /import_playbook: chamanswami555\.agentia\.release_window/)
  assert.match(text, /story_ids: \["US-0042", "US-0043"\]/)
  assert.match(text, /promotion_id: "a0B000000000001EAA"/)
  assert.match(text, /crt_project_id: ""/)
  assert.match(text, /approve: false/)
  assert.ok(text.endsWith('\n'))
})

test('parseRecap reads the Ansible recap line', () => {
  const recap = parseRecap('PLAY RECAP ***\nlocalhost : ok=15   changed=10   unreachable=0    failed=0    skipped=1    rescued=0    ignored=0\n')
  assert.deepEqual(recap, {ok: 15, changed: 10, failed: 0, skipped: 1})
  assert.equal(parseRecap('nothing'), undefined)
})

test('parseEnvelope tolerates a warning line and surfaces CLI errors', () => {
  const envelope = parseEnvelope(' ›   Warning: update available\n{"result": {"items": [{"id": "p1"}]}, "status": 0, "transactionId": "t1"}')
  assert.deepEqual(itemsOf(envelope.result), [{id: 'p1'}])
  assert.throws(() => parseEnvelope('{"error": {"message": "CICD API key is not configured"}, "transactionId": "t2"}'), (error: unknown) => {
    assert.ok(error instanceof AgentiaCliError)
    assert.equal(error.transactionId, 't2')
    return true
  })
  assert.throws(() => parseEnvelope('plain text'), /not JSON/)
})

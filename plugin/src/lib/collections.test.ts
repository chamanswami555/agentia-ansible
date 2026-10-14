import assert from 'node:assert/strict'
import {test} from 'node:test'

import {collectionHint, resolveCollectionsPath} from './collections.js'

test('resolveCollectionsPath prefers the flag, then the environment, then the repository checkout', () => {
  const has = (dir: string) => dir === '/repo/var/ansible_collections/chamanswami555/agentia'
  assert.equal(resolveCollectionsPath('/flag', {ANSIBLE_COLLECTIONS_PATH: '/env'}, '/repo/var', has), '/flag')
  assert.equal(resolveCollectionsPath(undefined, {ANSIBLE_COLLECTIONS_PATH: '/env'}, '/repo/var', has), '/env')
  assert.equal(resolveCollectionsPath(undefined, {}, '/repo/var', has), '/repo/var')
  assert.equal(resolveCollectionsPath(undefined, {}, '/elsewhere/var', has), undefined)
})

test('collectionHint names the missing collection', () => {
  assert.match(collectionHint("ERROR! Unable to retrieve file contents\nCould not find or access '/x/chamanswami555.agentia.release_window'") ?? '', /ansible-galaxy or pass --collections-path/)
  assert.equal(collectionHint('fatal: something else'), undefined)
})

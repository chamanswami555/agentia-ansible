// Where ansible-playbook finds the chamanswami555.agentia collection for a run.
// Order: the --collections-path flag, then ANSIBLE_COLLECTIONS_PATH, then the var/ folder of a
// repository checkout (make setup links the collection there), else nothing (an installed collection).
export function resolveCollectionsPath(
  flag: string | undefined,
  env: NodeJS.ProcessEnv,
  repoVar: string,
  exists: (dir: string) => boolean,
): string | undefined {
  if (flag) return flag
  if (env.ANSIBLE_COLLECTIONS_PATH) return env.ANSIBLE_COLLECTIONS_PATH
  if (exists(`${repoVar}/ansible_collections/chamanswami555/agentia`)) return repoVar
  return undefined
}

export function collectionHint(output: string): string | undefined {
  if (/Could not find or access .*chamanswami555\.agentia/.test(output)) {
    return 'hint: the chamanswami555.agentia collection is not on ANSIBLE_COLLECTIONS_PATH; install it with ansible-galaxy or pass --collections-path'
  }
  return undefined
}

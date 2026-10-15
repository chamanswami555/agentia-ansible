// MIT License. See LICENSE in the repository root.
import {AgentiaCommand, getAgentiaHost} from '@copado/agentia-plugin-sdk'
import {Flags} from '@oclif/core'
import {spawn} from 'node:child_process'
import {existsSync} from 'node:fs'
import path from 'node:path'
import {fileURLToPath} from 'node:url'

import {collectionHint, resolveCollectionsPath} from '../../lib/collections.js'
import {parseRecap} from '../../lib/playbook.js'

export default class AnsibleRun extends AgentiaCommand {
  static override description = 'Run a generated release playbook with ansible-playbook and report the recap'
  static override examples = [
    '<%= config.bin %> <%= command.id %> --playbook release-window.yml --check',
    '<%= config.bin %> <%= command.id %> --playbook release-window.yml --approve',
    '<%= config.bin %> <%= command.id %> --playbook release-window.yml --json',
  ]
  static override flags = {
    playbook: Flags.string({char: 'f', description: 'Playbook file written by `agentia ansible scaffold`', default: 'release-window.yml'}),
    check: Flags.boolean({description: 'Ansible check mode: report what would change, change nothing', default: false}),
    approve: Flags.boolean({description: 'Skip the human approval pause (only with explicit consent)', default: false}),
    'extra-vars': Flags.string({char: 'e', description: 'Extra variables as a JSON object'}),
    'ansible-playbook-bin': Flags.string({description: 'ansible-playbook executable', default: 'ansible-playbook'}),
    'collections-path': Flags.string({description: 'ANSIBLE_COLLECTIONS_PATH for the run (default: the environment, else the var/ folder of a repository checkout, else the installed collections)'}),
  }

  public async run() {
    const {flags} = await this.parse(AnsibleRun)
    // Keep this list in sync with "agentia.requires" in package.json.
    getAgentiaHost({requires: ['auth.status', 'format.table', 'work.getWorkItem']})

    const playbook = path.resolve(flags.playbook)
    if (!existsSync(playbook)) this.error(`Playbook not found: ${playbook}. Run \`agentia ansible scaffold\` first.`, {exit: 2})

    const args = [playbook]
    if (flags.check) args.push('--check')
    let extra: Record<string, unknown> = {}
    if (flags['extra-vars']) {
      try {
        extra = JSON.parse(flags['extra-vars']) as Record<string, unknown>
      } catch (error) {
        this.error(`--extra-vars must be a JSON object, for example '{"skip_local_tests": true}': ${(error as Error).message}`, {exit: 2})
      }
    }
    if (flags.approve) extra.approve = true
    if (Object.keys(extra).length > 0) args.push('-e', JSON.stringify(extra))

    const repoVar = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..', '..', 'var')
    const collectionsPath = resolveCollectionsPath(flags['collections-path'], process.env, repoVar, (dir) => existsSync(dir))
    const output = await new Promise<{code: number | null; text: string}>((resolve, reject) => {
      const env: NodeJS.ProcessEnv = {...process.env, ANSIBLE_FORCE_COLOR: 'false', ANSIBLE_LOCALHOST_WARNING: 'false', ANSIBLE_INVENTORY_UNPARSED_WARNING: 'false'}
      if (collectionsPath) env.ANSIBLE_COLLECTIONS_PATH = collectionsPath
      const child = spawn(flags['ansible-playbook-bin'], args, {env})
      let text = ''
      const collect = (chunk: Buffer) => {
        text += chunk
        if (!this.jsonEnabled()) process.stdout.write(chunk)
      }
      child.stdout.on('data', collect)
      child.stderr.on('data', collect)
      child.on('error', (error) => reject(new Error(`cannot run ${flags['ansible-playbook-bin']}: ${error.message}`)))
      child.on('close', (code) => resolve({code, text}))
    })

    const recap = parseRecap(output.text)
    const stoppedAtApproval = /Deployment not approved/.test(output.text)
    const hint = collectionHint(output.text)
    const ok = output.code === 0
    this.display(() => {
      this.log(ok ? `Playbook finished: ${JSON.stringify(recap)}` : `Playbook failed with exit code ${output.code}: ${JSON.stringify(recap)}`)
      if (stoppedAtApproval) this.log('Stopped at the approval gate: nothing was deployed. Re-run with --approve once the release is approved.')
      if (hint) this.log(hint)
    })
    // Keep the playbook's exit code for scripts, but still return the structured result
    // (with --json the caller gets ok=false and the recap instead of an error envelope).
    if (!ok) process.exitCode = output.code ?? 1
    return {ok, exitCode: output.code, recap, playbook, check: flags.check, stoppedAtApproval, hint}
  }
}

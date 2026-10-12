// MIT License. See LICENSE in the repository root.
import {AgentiaCommand, getAgentiaHost} from '@copado/agentia-plugin-sdk'
import {Flags} from '@oclif/core'
import {mkdirSync, writeFileSync} from 'node:fs'
import path from 'node:path'

import {AgentiaCliError, itemsOf, runAgentiaJson} from '../../lib/agentia-cli.js'
import {renderReleasePlaybook} from '../../lib/playbook.js'

export default class AnsibleScaffold extends AgentiaCommand {
  static override description =
    'Write an Ansible release-window playbook from the current Copado state: the active or given user stories and their promotion'
  static override examples = [
    '<%= config.bin %> <%= command.id %>',
    '<%= config.bin %> <%= command.id %> --stories US-0042,US-0043 --promotion a0BXXXXXXXXXXXXXXX --out release.yml',
    '<%= config.bin %> <%= command.id %> --crt-job 196473 --crt-project 112901 --dry-run',
    '<%= config.bin %> <%= command.id %> --json',
  ]
  static override flags = {
    stories: Flags.string({char: 's', description: 'Comma-separated story ids or names; default: the active story from `agentia cicd work set`'}),
    promotion: Flags.string({char: 'p', description: 'Promotion id; default: the first promotion found for the first story'}),
    'crt-job': Flags.string({description: 'Robotic Testing job id for the smoke suite'}),
    'crt-project': Flags.string({description: 'Robotic Testing project id'}),
    'repo-dir': Flags.string({description: 'Git working copy of the Salesforce project', default: process.cwd()}),
    out: Flags.string({char: 'o', description: 'Playbook file to write', default: 'release-window.yml'}),
    'dry-run': Flags.boolean({description: 'Print the playbook instead of writing it', default: false}),
    'agentia-bin': Flags.string({description: 'Agentia CLI executable used to read Copado state', default: 'agentia'}),
    'skip-auth-check': Flags.boolean({description: 'Do not check the CI/CD credential before reading Copado (demos with a recorded CLI)', default: false}),
  }

  public async run() {
    const {flags} = await this.parse(AnsibleScaffold)
    // Keep this list in sync with "agentia.requires" in package.json.
    const host = getAgentiaHost({requires: ['auth.status', 'format.table', 'work.getWorkItem']})

    const status = host.auth.status() as unknown as Record<string, {configured?: boolean}>
    const cicdConfigured = status.cicd?.configured !== false

    let storyIds = (flags.stories ?? '')
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
    const needsCopado = storyIds.length === 0 || !flags.promotion
    if (needsCopado && !cicdConfigured && !flags['skip-auth-check']) {
      this.error('CI/CD authentication is not configured, so the active story and promotion cannot be read. Run `agentia auth set --cicd <key>` or pass both --stories and --promotion.', {exit: 2})
    }

    if (storyIds.length === 0) {
      let story: {name?: string; id?: string} | undefined
      try {
        story = (await host.work.getWorkItem()) as {name?: string; id?: string} | undefined
      } catch (error) {
        this.warn(`Could not read the active story: ${(error as Error).message}`)
      }
      const name = story?.name ?? story?.id
      if (!name) this.error('No stories given and no active story. Pass --stories or run `agentia cicd work set <story>` first.', {exit: 2})
      storyIds = [name]
    }

    let promotionId = flags.promotion
    if (!promotionId) {
      try {
        const envelope = await runAgentiaJson(flags['agentia-bin'], ['cicd', 'promotion', 'list', '--work-id', storyIds[0]], flags['repo-dir'])
        const first = itemsOf(envelope.result)[0]
        promotionId = (first?.id as string | undefined) ?? ''
      } catch (error) {
        if (!(error instanceof AgentiaCliError)) throw error
        this.warn(`Could not read promotions for ${storyIds[0]}: ${error.message}`)
        promotionId = ''
      }
      if (!promotionId) this.warn('No promotion found; set promotion_id in the playbook before running it.')
    }

    const repoDir = path.resolve(flags['repo-dir'])
    const stamp = new Date().toISOString().replace(/[:.]/g, '-')
    const playbook = renderReleasePlaybook({
      storyIds,
      promotionId: promotionId ?? '',
      crtJobId: flags['crt-job'],
      crtProjectId: flags['crt-project'],
      repoDir,
      evidenceDir: path.join(repoDir, 'evidence', stamp),
      generatedAt: new Date().toISOString(),
    })

    const outPath = path.resolve(flags['repo-dir'], flags.out)
    if (!flags['dry-run']) {
      mkdirSync(path.dirname(outPath), {recursive: true})
      writeFileSync(outPath, playbook, 'utf8')
    }

    this.display(() => {
      if (flags['dry-run']) {
        this.log(playbook)
      } else {
        this.log(`Wrote ${outPath}`)
        this.log(`  stories:    ${storyIds.join(', ')}`)
        this.log(`  promotion:  ${promotionId || '(none found, set promotion_id before running)'}`)
        this.log(`  smoke test: ${flags['crt-job'] ? `${flags['crt-job']} in project ${flags['crt-project'] ?? '?'}` : 'none'}`)
        this.log(`  next:       agentia ansible run --playbook ${outPath} --check`)
      }
    })

    return {playbook: flags['dry-run'] ? playbook : undefined, path: flags['dry-run'] ? undefined : outPath, storyIds, promotionId}
  }
}

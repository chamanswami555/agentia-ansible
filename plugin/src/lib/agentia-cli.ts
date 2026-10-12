// MIT License. See LICENSE in the repository root.
// Runs public `agentia ... --json` commands as child processes and parses the JSON envelope.
// Plugins may not import the CLI or call Copado endpoints directly; the public commands are
// the supported surface, and credentials stay inside the CLI's own keychain.
import {spawn} from 'node:child_process'

export interface Envelope {
  result?: unknown
  status?: number
  transactionId?: string
  error?: {message?: string; name?: string}
}

export class AgentiaCliError extends Error {
  constructor(
    message: string,
    public readonly transactionId?: string,
    public readonly command?: string,
  ) {
    super(message)
    this.name = 'AgentiaCliError'
  }
}

export function parseEnvelope(text: string): Envelope {
  const start = text.indexOf('{')
  if (start < 0) throw new AgentiaCliError(`Agentia CLI output is not JSON: ${text.slice(0, 200)}`)
  let data: unknown
  try {
    data = JSON.parse(text.slice(start))
  } catch (error) {
    throw new AgentiaCliError(`Agentia CLI output could not be parsed: ${(error as Error).message}`)
  }
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new AgentiaCliError('Agentia CLI output is not a JSON object')
  const envelope = data as Envelope
  if (envelope.error) {
    throw new AgentiaCliError(envelope.error.message ?? 'Agentia CLI reported an error', envelope.transactionId)
  }
  return envelope
}

export function itemsOf(result: unknown): Array<Record<string, unknown>> {
  if (Array.isArray(result)) return result.filter((r) => r && typeof r === 'object') as Array<Record<string, unknown>>
  if (result && typeof result === 'object') {
    for (const key of ['items', 'records', 'data', 'results']) {
      const value = (result as Record<string, unknown>)[key]
      if (Array.isArray(value)) return value.filter((r) => r && typeof r === 'object') as Array<Record<string, unknown>>
    }
  }
  return []
}

export async function runAgentiaJson(bin: string, args: string[], cwd?: string): Promise<Envelope> {
  const command = [bin, ...args, '--json'].join(' ')
  return new Promise((resolve, reject) => {
    const child = spawn(bin, [...args, '--json'], {cwd, env: {...process.env, CI: '1'}})
    let out = ''
    let err = ''
    child.stdout.on('data', (chunk) => {
      out += chunk
    })
    child.stderr.on('data', (chunk) => {
      err += chunk
    })
    child.on('error', (error) => reject(new AgentiaCliError(`cannot run ${command}: ${error.message}`, undefined, command)))
    child.on('close', () => {
      try {
        resolve(parseEnvelope(out))
      } catch (error) {
        const wrapped = error as AgentiaCliError
        reject(new AgentiaCliError(`${wrapped.message}${err ? ` (${err.trim().slice(-300)})` : ''}`, wrapped.transactionId, command))
      }
    })
  })
}

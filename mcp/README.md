# agentia-ansible-mcp

An MCP server so an AI coding agent (Cursor or any MCP client) triggers Copado
releases through the governed playbooks of the `chamanswami555.agentia` collection rather
than through raw commands. The playbooks keep the human approval pause, the evidence folder and
the Copado transaction ids; the agent only chooses what to run and reads the outcome.

## Tools

| Tool | What it does |
| --- | --- |
| `list_playbooks` | The playbooks available |
| `run_release_playbook` | Runs `release_window.yml` for given stories and promotion; stops at the approval pause unless `approve: true` |
| `run_playbook` | Runs `nightly_validate` or `remediate_failed_job` with extra variables |
| `list_evidence` | Lists evidence folders |
| `release_status` | Summarizes the latest evidence folder: deployment status, smoke tests, health checks |

`demo: true` on the run tools uses the fake Agentia CLI with recorded answers, so the whole
flow can be shown without a Copado licence.

## Run

```sh
cd mcp && npm install
node server.mjs            # speaks MCP over stdio
npm test                   # smoke tests
```

Client configuration (for example Cursor's `mcp.json`):

```json
{
  "mcpServers": {
    "agentia-ansible": {
      "type": "stdio",
      "command": "node",
      "args": ["/path/to/agentia-ansible/mcp/server.mjs"],
      "env": { "AGENTIA_MCP_DEMO": "0" }
    }
  }
}
```

Environment: `AGENTIA_ANSIBLE_ROOT` (repository root), `ANSIBLE_PLAYBOOK_BIN`,
`AGENTIA_EVIDENCE_ROOT`, `AGENTIA_MCP_DEMO=1` for the offline demo. Copado credentials stay
in the Agentia CLI keychain or `AGENTIA_*` environment variables; the server never handles them.

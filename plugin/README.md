# agentia-plugin-ansible

An Agentia CLI plugin, built with `@copado/create-agentia-plugin` and the official plugin SDK,
that connects the CLI to the `chamanswami555.agentia` Ansible collection.

| Command | What it does |
| --- | --- |
| `agentia ansible scaffold` | Reads the active story (plugin SDK) or the given stories, finds their promotion through the public CLI, and writes a release-window playbook that imports `chamanswami555.agentia.release_window` with those values |
| `agentia ansible run` | Runs that playbook with `ansible-playbook` (`--check` for a dry run, `--approve` to skip the human pause) and reports the recap |

```sh
cd plugin
npm install
npm run build
agentia plugins link .
agentia ansible scaffold --stories US-0042 --promotion a0BXXXXXXXXXXXXXXX --crt-job 196473 --crt-project 112901
agentia ansible run --playbook release-window.yml --check
```

The plugin never receives credentials: it reads Copado through `agentia ... --json` child
processes, which use the CLI's own keychain, and it declares the commands it runs in
`package.json` under `agentia.permissions`.

Tests: `npm test` builds the TypeScript and runs the unit tests in `src/lib/*.test.ts`.

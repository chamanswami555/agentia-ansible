#!/usr/bin/python
# MIT License. See LICENSE in the repository root.

from __future__ import annotations

DOCUMENTATION = r"""
---
module: agentia_auth_info
short_description: Report which Agentia CLI credentials are configured
version_added: "0.1.0"
description:
  - Runs C(agentia auth get --json) and reports, without exposing secrets, whether the
    CI/CD API key, the Copado AI PAK and the Robotic Testing PAK are configured.
  - Use it as the first task of a playbook so a missing credential fails early with a
    clear message instead of halfway through a release.
options:
  require:
    description: Credential types that must be configured; the module fails otherwise.
    type: list
    elements: str
    choices: [cicd, ai, crt]
    default: []
  cli_path:
    description: Path to the C(agentia) executable.
    type: str
    default: agentia
  working_dir:
    description: Directory to run the CLI in.
    type: path
  timeout:
    description: Seconds to wait for the CLI call.
    type: int
    default: 900
author:
  - Chaman Swami (@chamanswami555)
"""

EXAMPLES = r"""
- name: Stop early when the CI/CD key is missing
  chamanswami555.agentia.agentia_auth_info:
    require: [cicd]
"""

RETURN = r"""
configured:
  description: Map of credential type to whether it is configured (cicd, ai, crt).
  returned: always
  type: dict
credentials:
  description: The credential entries the CLI reported, secrets already masked by the CLI.
  returned: always
  type: list
transaction_id:
  description: Transaction id of the CLI call.
  returned: always
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.chamanswami555.agentia.plugins.module_utils.agentia import (
    AgentiaCli,
    AgentiaError,
    agentia_argument_spec,
)


def summarize(result):
    entries = result.get("credentials", []) if isinstance(result, dict) else []
    configured = {"cicd": False, "ai": False, "crt": False}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        kind = (entry.get("type") or "").lower()
        if kind in configured:
            configured[kind] = bool(entry.get("set")) and not entry.get("missing")
    return configured, entries


def run_module():
    spec = dict(agentia_argument_spec())
    spec["require"] = {"type": "list", "elements": "str", "choices": ["cicd", "ai", "crt"], "default": []}
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    cli = AgentiaCli(module)
    try:
        result, tx = cli.run(["auth", "get"])
    except AgentiaError as exc:
        module.fail_json(**exc.as_dict())
    configured, entries = summarize(result)
    missing = [kind for kind in module.params["require"] if not configured.get(kind)]
    if missing:
        module.fail_json(msg="Agentia credentials not configured: %s. Run `agentia auth set` or "
                             "set the AGENTIA_* environment variables." % ", ".join(missing),
                         configured=configured, credentials=entries, transaction_id=tx)
    module.exit_json(changed=False, configured=configured, credentials=entries, transaction_id=tx)


def main():
    run_module()


if __name__ == "__main__":
    main()

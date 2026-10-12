#!/usr/bin/python
# MIT License. See LICENSE in the repository root.

from __future__ import annotations

DOCUMENTATION = r"""
---
module: agentia_ai_ask
short_description: Ask a Copado AI agent a single question through Agentia CLI
version_added: "0.1.0"
description:
  - Runs C(agentia ai agent ask) with one prompt and returns the buffered answer.
  - Use it to let the Plan, Build, Test, Release, Operate or Knowledge agent explain a
    failure, draft release notes or recommend tests inside a playbook.
options:
  prompt:
    description: The question or instruction.
    type: str
    required: true
  agent:
    description: Which Copado AI agent answers.
    type: str
    choices: [plan, build, test, release, operate, knowledge]
    default: knowledge
  user_story:
    description: User story identifier to include as context.
    type: str
  sf_org:
    description: Salesforce org or environment name to include as context.
    type: str
  component:
    description: Metadata component name to include as context.
    type: str
  workspace:
    description: Copado AI workspace UUID to use.
    type: str
  dialogue:
    description: Copado AI dialogue UUID to continue.
    type: str
  ai_timeout:
    description: AI gateway timeout in seconds.
    type: int
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
- name: Ask the Operate agent why the deployment failed
  chamanswami555.agentia.agentia_ai_ask:
    agent: operate
    prompt: "Explain the failure of job {{ job.job.id }} and suggest the next step"
  register: diagnosis
"""

RETURN = r"""
answer:
  description: The agent's answer text when the CLI result contains one, else the full result.
  returned: always
  type: raw
response:
  description: The full result as the CLI returned it.
  returned: always
  type: raw
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

CONTEXT_FLAGS = (("user_story", "--user-story"), ("sf_org", "--sf-org"), ("component", "--component"),
                 ("workspace", "--workspace"), ("dialogue", "--dialogue"))


def extract_answer(result):
    if isinstance(result, dict):
        for key in ("answer", "response", "message", "content", "text"):
            value = result.get(key)
            if isinstance(value, str) and value.strip():
                return value
    if isinstance(result, str):
        return result
    return result


def run_module():
    spec = dict(agentia_argument_spec())
    spec.update({
        "prompt": {"type": "str", "required": True},
        "agent": {"type": "str", "choices": ["plan", "build", "test", "release", "operate", "knowledge"],
                  "default": "knowledge"},
        "ai_timeout": {"type": "int"},
    })
    for option, _flag in CONTEXT_FLAGS:
        spec[option] = {"type": "str"}
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    params = module.params
    args = ["ai", "agent", "ask", "--agent", params["agent"], "-p", params["prompt"], "--no-stream"]
    for option, flag in CONTEXT_FLAGS:
        if params[option]:
            args += [flag, params[option]]
    if params["ai_timeout"]:
        args += ["--timeout", str(params["ai_timeout"])]
    if module.check_mode:
        module.exit_json(changed=False, answer=None, response=None)
    cli = AgentiaCli(module)
    try:
        result, tx = cli.run(args)
    except AgentiaError as exc:
        module.fail_json(**exc.as_dict())
    module.exit_json(changed=False, answer=extract_answer(result), response=result, transaction_id=tx)


def main():
    run_module()


if __name__ == "__main__":
    main()

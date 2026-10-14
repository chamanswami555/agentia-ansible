# MIT License. See LICENSE in the repository root.
"""Shared helper for running Copado Agentia CLI commands from Ansible modules.

Every Agentia command is executed with ``--json``. The CLI answers with one JSON document
of the shape ``{"result": ..., "status": 0, "transactionId": "..."}`` on success and
``{"error": {"message": "...", "name": "..."}, "transactionId": "..."}`` on failure.
This helper runs the command, parses that envelope and turns failures into
``AgentiaError`` so modules can fail with a clear message and the transaction id.

Credentials are never passed as arguments. The CLI reads them from its keychain or from
the ``AGENTIA_CICD_API_KEY`` and related environment variables of the calling process.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess

from ansible.module_utils.basic import AnsibleModule

JSON_FLAG = "--json"


class AgentiaError(Exception):
    """A failed Agentia CLI call, with the message and transaction id the CLI reported."""

    def __init__(self, message, transaction_id=None, command=None, rc=None, stdout=None, stderr=None):
        super().__init__(message)
        self.message = message
        self.transaction_id = transaction_id
        self.command = command
        self.rc = rc
        self.stdout = stdout
        self.stderr = stderr

    def as_dict(self):
        """Fields for ``module.fail_json`` so the playbook user sees everything useful.

        The key is ``cli_command`` (the quoted command line), not ``command``, because action
        modules already return ``command`` (the argument list) and pass it to ``fail_json`` too.
        """
        return {
            "msg": self.message,
            "transaction_id": self.transaction_id,
            "cli_command": self.command,
            "rc": self.rc,
            "stderr": (self.stderr or "")[-2000:],
        }


def agentia_argument_spec():
    """Options every module in this collection accepts."""
    return {
        "cli_path": {"type": "str", "default": "agentia"},
        "working_dir": {"type": "path"},
        "timeout": {"type": "int", "default": 900},
    }


def _text(value):
    if value is None:
        return ""
    return value.decode("utf-8", "replace") if isinstance(value, bytes) else str(value)


class AgentiaCli:
    """Runs ``agentia`` commands for one Ansible module."""

    def __init__(self, module: AnsibleModule):
        self.module = module
        self.cli_path = module.params.get("cli_path") or "agentia"
        self.working_dir = module.params.get("working_dir")
        self.timeout = module.params.get("timeout") or 900
        self.calls = []
        self.last_rc = None

    def run(self, args, ok_exit_codes=(0,)):
        """Run one command and return the parsed ``result`` value.

        ``args`` is the argument list after the binary, for example
        ``["cicd", "work", "get", "US-0001"]``. ``--json`` is appended here.
        Raises ``AgentiaError`` when the CLI reports an error, exits with an unexpected
        code, or prints something that is not the JSON envelope.
        """
        argv = [self.cli_path] + [str(a) for a in args] + [JSON_FLAG]
        command = " ".join(shlex.quote(a) for a in argv)
        self.calls.append(argv[1:])
        env = dict(os.environ)
        env.setdefault("CI", "1")
        try:
            proc = subprocess.run(argv, cwd=self.working_dir or None, env=env, capture_output=True,
                                  text=True, errors="replace", timeout=self.timeout, check=False)
        except FileNotFoundError as exc:
            raise AgentiaError("Agentia CLI not found: %s (install @copado/agentia-cli or set cli_path)" % self.cli_path,
                               command=command, rc=127, stdout="", stderr="") from exc
        except subprocess.TimeoutExpired as exc:
            raise AgentiaError("Agentia CLI did not finish within %s seconds" % self.timeout,
                               command=command, rc=124, stdout=_text(exc.stdout), stderr=_text(exc.stderr)) from exc
        rc, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
        self.last_rc = rc
        data = self._parse(stdout, stderr, rc, command)
        if "error" in data and data["error"]:
            err = data["error"] if isinstance(data["error"], dict) else {"message": str(data["error"])}
            raise AgentiaError(
                err.get("message") or "Agentia CLI reported an error",
                transaction_id=data.get("transactionId"),
                command=command, rc=rc, stdout=stdout, stderr=stderr,
            )
        if rc not in ok_exit_codes:
            raise AgentiaError(
                "Agentia CLI exited with code %s" % rc,
                transaction_id=data.get("transactionId"),
                command=command, rc=rc, stdout=stdout, stderr=stderr,
            )
        return data.get("result"), data.get("transactionId")

    @staticmethod
    def _parse(stdout, stderr, rc, command):
        text = (stdout or "").strip()
        if not text:
            raise AgentiaError(
                "Agentia CLI printed no JSON (exit code %s)" % rc,
                command=command, rc=rc, stdout=stdout, stderr=stderr,
            )
        # The CLI may print a beta-update warning before the JSON document; take the
        # first line that starts a JSON object.
        start = text.find("{")
        if start < 0:
            raise AgentiaError(
                "Agentia CLI output is not JSON: %s" % text[:300],
                command=command, rc=rc, stdout=stdout, stderr=stderr,
            )
        try:
            data = json.loads(text[start:])
        except ValueError as exc:
            raise AgentiaError(
                "Agentia CLI output could not be parsed as JSON: %s" % exc,
                command=command, rc=rc, stdout=stdout, stderr=stderr,
            )
        if not isinstance(data, dict):
            raise AgentiaError(
                "Agentia CLI output is not a JSON object",
                command=command, rc=rc, stdout=stdout, stderr=stderr,
            )
        return data


def is_not_found(error: AgentiaError) -> bool:
    """True when the CLI error means the record does not exist."""
    text = (error.message or "").lower()
    return "not found" in text or "does not exist" in text or "no user story" in text


def as_list(result):
    """Normalize list-style results: the CLI returns either a list or an object with items."""
    if result is None:
        return []
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        for key in ("items", "records", "data", "results"):
            if isinstance(result.get(key), list):
                return result[key]
    return []

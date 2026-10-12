# MIT License. See LICENSE in the repository root.
import pytest

from ansible_collections.chamanswami555.agentia.plugins.module_utils.agentia import (
    AgentiaCli,
    AgentiaError,
    as_list,
    is_not_found,
)


def test_parse_skips_warning_prefix():
    text = " ›   Warning: update available\n{\"result\": {\"id\": 1}, \"status\": 0, \"transactionId\": \"t1\"}"
    data = AgentiaCli._parse(text, "", 0, "agentia x")
    assert data["result"] == {"id": 1}
    assert data["transactionId"] == "t1"


def test_parse_rejects_empty_and_non_json():
    with pytest.raises(AgentiaError) as info:
        AgentiaCli._parse("", "boom", 2, "agentia x")
    assert "no JSON" in str(info.value)
    with pytest.raises(AgentiaError) as info:
        AgentiaCli._parse("plain text", "", 0, "agentia x")
    assert "not JSON" in str(info.value)
    with pytest.raises(AgentiaError) as info:
        AgentiaCli._parse("{not valid", "", 0, "agentia x")
    assert "could not be parsed" in str(info.value)


def test_as_list_accepts_both_shapes():
    assert as_list([1, 2]) == [1, 2]
    assert as_list({"items": [3]}) == [3]
    assert as_list({"records": [4]}) == [4]
    assert as_list(None) == []
    assert as_list({"other": 1}) == []


def test_is_not_found():
    assert is_not_found(AgentiaError("User story US-1 not found"))
    assert is_not_found(AgentiaError("Record does not exist"))
    assert not is_not_found(AgentiaError("CICD API key is not configured"))


def test_error_as_dict_trims_stderr():
    err = AgentiaError("m", transaction_id="t", command="c", rc=1, stderr="x" * 5000)
    data = err.as_dict()
    assert data["msg"] == "m" and data["transaction_id"] == "t" and len(data["stderr"]) == 2000

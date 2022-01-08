import pytest
from tap_krow.normalize import flatten_dict, remove_unnecessary_keys


def test_flattens_dict():
    d = {"a": {"a": "hi"}}
    flattened = flatten_dict(d)
    assert "a.a" in flattened
    assert "a" not in flattened
    assert flattened["a.a"] == d["a"]["a"]


def test_accepts_delimiter():
    d = {"a": {"a": "hi"}}
    flattened = flatten_dict(d, delimiter="__")
    assert "a__a" in flattened
    assert "a" not in flattened
    assert flattened["a__a"] == d["a"]["a"]


def test_removes_extraneous_data_key():
    d = {"a": {"data": {"b": {"data": {"c": "hi"}}}}}
    purged = remove_unnecessary_keys(d, keys_to_remove=["data"])
    flattened = flatten_dict(purged)
    assert "a.b.c" in flattened
    assert "a.data.b.data.c" not in flattened
    assert flattened["a.b.c"] == d["a"]["data"]["b"]["data"]["c"]


def test_errors_if_child_key_already_exists_in_parent():
    d = {"a": "hi", "to_be_removed": {"a": "hi2"}}
    with pytest.raises(Exception) as exc_info:
        remove_unnecessary_keys(d, ["to_be_removed"])

    assert (
        str(exc_info.value)
        == 'The key "a" already exists in the output, so cannot promote the child of key "to_be_removed"'
    )

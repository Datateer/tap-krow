import pytest
from tap_krow.normalize import flatten_dict, remove_unnecessary_keys, make_fields_meltano_select_compatible


def test_flattens_dict():
    d = {"a": {"a": "hi"}}
    flattened = flatten_dict(d)
    assert "a_a" in flattened
    assert "a" not in flattened
    assert flattened["a_a"] == d["a"]["a"]


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
    assert "a_b_c" in flattened
    assert "a_data_b_data_c" not in flattened
    assert flattened["a_b_c"] == d["a"]["data"]["b"]["data"]["c"]


def test_errors_if_child_key_already_exists_in_parent():
    d = {"a": "hi", "to_be_removed": {"a": "hi2"}}
    with pytest.raises(Exception) as exc_info:
        remove_unnecessary_keys(d, ["to_be_removed"])

    assert (
        str(exc_info.value)
        == 'The key "a" already exists in the output, so cannot promote the child of key "to_be_removed"'
    )


def test_make_fields_meltano_select_compatible_replaces_dots_with_underscores_in_field_name():
    d = {"opening.position": "hi", "nested": {"a.b": "hi2"}}
    cleaned = make_fields_meltano_select_compatible(d)
    assert "opening.position" not in cleaned
    assert "opening_position" in cleaned
    assert cleaned["opening_position"] == "hi"
    assert "a.b" not in cleaned["nested"]
    assert "a_b" in cleaned["nested"]
    assert cleaned["nested"]["a_b"] == "hi2"

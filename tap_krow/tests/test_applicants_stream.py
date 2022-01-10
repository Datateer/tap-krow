"""Test general stream capabilities"""

import pytest

from tap_krow.streams import ApplicantsStream


@pytest.fixture(scope="module")
def stream(tap_instance):
    return ApplicantsStream(tap_instance)


@pytest.fixture(scope="module")
def responses(api_responses):
    """Returns an instance of a stream, which """
    return api_responses["applicants"]


def test_applicants_stream_correctly_parses_fields(responses, stream, get_parsed_records):
    res = get_parsed_records(stream, responses["applicants_default.json"])
    assert "first_name" in res[0]
    assert "last_name" in res[0]
    assert "full_name" in res[0]
    assert "locality_id" in res[0]
    assert "locality_type" in res[0]
    assert "opening_position_id" in res[0]
    assert "state_changed_at" in res[0]
    assert "state_action" in res[0]
    assert "state_name" in res[0]
    assert "status" in res[0]
    assert "transitioning" in res[0]

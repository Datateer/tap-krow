"""Test general stream capabilities"""

import pytest

from tap_krow.streams import PositionsStream


@pytest.fixture(scope="module")
def stream(tap_instance):
    return PositionsStream(tap_instance)


@pytest.fixture(scope="module")
def responses(api_responses):
    """Returns an instance of a stream, which """
    return api_responses["positions"]


def test_positions_stream_correctly_parses_fields(responses, stream, get_parsed_records):
    res = get_parsed_records(stream, responses["positions_default.json"])
    assert "average_days_to_decision" in res[0]
    assert "average_days_to_decision_updated_at" in res[0]
    assert "description" in res[0]
    assert "id" in res[0]
    assert "name" in res[0]
    assert "rolling_apply_count_updated_at" in res[0]
    assert "rolling_daily_apply_change" in res[0]
    assert "rolling_daily_apply_count" in res[0]
    assert "rolling_daily_hire_change" in res[0]
    assert "rolling_daily_hire_count" in res[0]
    assert "rolling_hire_count_updated_at" in res[0]
    assert "rolling_monthly_apply_change" in res[0]
    assert "rolling_monthly_apply_count" in res[0]
    assert "rolling_monthly_hire_change" in res[0]
    assert "rolling_monthly_hire_count" in res[0]
    assert "updated_at" in res[0]

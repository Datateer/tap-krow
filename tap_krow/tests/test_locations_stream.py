"""Test general stream capabilities"""

import pytest

from tap_krow.streams import LocationsStream


@pytest.fixture(scope="module")
def stream(tap_instance):
    return LocationsStream(tap_instance)


@pytest.fixture(scope="module")
def responses(api_responses):
    """Returns an instance of a stream, which """
    return api_responses["locations"]


def test_locations_stream_correctly_parses_fields(responses, stream, get_parsed_records):
    res = get_parsed_records(stream, responses["locations_default.json"])
    assert "city" in res[0]
    assert "id" in res[0]
    assert "latitude" in res[0]
    assert "longitude" in res[0]
    assert "name" in res[0]
    assert "parent_id" in res[0]
    assert "postal_code" in res[0]
    assert "region_id" in res[0]
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
    assert "state" in res[0]
    assert "time_zone" in res[0]
    assert "updated_at" in res[0]

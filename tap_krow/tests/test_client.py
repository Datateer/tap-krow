"""Test general stream capabilities"""

from datetime import datetime
import pytest
import pytz
from urllib.parse import urlparse

from tap_krow.streams import CampaignStream, OrganizationsStream


@pytest.fixture(scope="module")
def responses(api_responses):
    """Returns an instance of a stream, which"""
    return api_responses["organizations"]


def test_returns_results(responses, stream_factory, get_parsed_records):
    stream = stream_factory(OrganizationsStream)
    records = get_parsed_records(stream, responses["orgs_default.json"])
    assert len(records) == 25


def test_get_url_params_includes_page_number(stream_factory):
    stream = stream_factory(OrganizationsStream)
    expected_page_number = "33"
    next_page_token = urlparse(
        f"/v1/organizations/9d85117d-0b3a-4d39-ae83-b8abaa4d2114/campaigns?page%5Bnumber%5D={expected_page_number}&page%5Bsize%5D=100&sort=-updated_at"
    )
    actual = stream.get_url_params(None, next_page_token)
    assert expected_page_number == actual["page[number]"]


def test_get_url_params_includes_sort_by_updated_descending(stream_factory):
    stream = stream_factory(OrganizationsStream)
    expected_sort_param = "-updated_at"
    next_page_token = urlparse(
        f"/v1/organizations/9d85117d-0b3a-4d39-ae83-b8abaa4d2114/campaigns?page%5Bnumber%5D=33&page%5Bsize%5D=100&sort={expected_sort_param}"
    )
    values = stream.get_url_params(None, next_page_token)
    assert expected_sort_param == values["sort"]


# region parse_response
def test_parse_response_flattens_attributes_property(responses, stream_factory):
    stream = stream_factory(OrganizationsStream)
    parsed = list(stream.parse_response(responses["orgs_default.json"]))
    assert 25 == len(parsed)
    assert "id" in parsed[0]
    assert "attributes" not in parsed[0]
    assert "name" in parsed[0]
    assert "kobe" == parsed[0]["name"]


def test_parse_response_does_not_return_extraneous_properties(responses, stream_factory):
    stream = stream_factory(OrganizationsStream)
    parsed = list(stream.parse_response(responses["orgs_default.json"]))
    assert 25 == len(parsed)
    assert "regions_count_updated_at" not in parsed[0]


def test_parse_response_does_not_return_records_earlier_than_the_stop_point(responses, stream_factory):
    stream = stream_factory(OrganizationsStream)
    stream.get_starting_timestamp = lambda x: datetime(2020, 1, 1, tzinfo=pytz.utc)  # simulate that the last run was some days ago
    records = list(stream.parse_response(responses["orgs_records_before_and_after_2020-01-01.json"]))
    ids = [r["id"] for r in records]
    assert ids == ["record_updated_at_jan_3", "record_updated_at_jan_2"]


# endregion

def test_handles_when_entities_do_not_have_a_relationships_property(api_responses, stream_factory):
    stream = stream_factory(CampaignStream)
    # test with a file that contains campaign entities without a "relationship" property
    res = stream.parse_response(api_responses["campaigns"]["campaigns_no_relationships_property.json"])
    # the simple fact that no exception was thrown indicates that this test succeeded
    assert next(res)['id'] == '9b2f9b64-ddb5-477b-ac24-4cf015df8c2d'

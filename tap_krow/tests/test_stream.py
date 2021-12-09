"""Test general stream capabilities"""

from datetime import datetime, timedelta
import json
import pytest
import pytz

from tap_krow.streams import OrganizationsStream
from tap_krow.tap import TapKrow

SAMPLE_CONFIG = {"api_key": "testing"}


@pytest.fixture
def stream():
    """Returns an instance of a stream, which """
    return OrganizationsStream(TapKrow(SAMPLE_CONFIG))


# @pytest.fixture
# def tap() -> TapKrow:
#     return TapKrow(config={"api_key": "testing"}, parse_env_config=False)


class FakeResponse(object):
    def __init__(self, response_body: str):
        self.response_body = response_body

    def json(self):
        return json.loads(self.response_body)


def build_basic_response(page_count=17, page_size=2):
    """Simulate a response from the KROW API
    :page_count: Simulate the API returning a certain number of pages, by overriding this value
    """
    response_string = (
        "{"
        '  "data": ['
        "    {"
        '      "id": "ea196757-acbb-4be2-a685-703e8349f443",'
        '      "type": "organizations",'
        '        "attributes": {'
        '            "name": "JS Helwig Testbed",'
        '            "status": "pending",'
        '            "regions_count": 2,'
        '            "regions_count_updated_at": "2021-11-10T21:05:49.085Z",'
        '            "created_at": "2021-11-09T21:07:39.828Z",'
        '            "updated_at": "2021-11-11T22:42:50.304Z"'
        "        }"
        "    },"
        "    {"
        '      "id": "9e48251e-929b-45f8-bcc6-93fb5c753072",'
        '      "type": "organizations",'
        '      "attributes": {'
        '          "name": "Lowe\'s Testbed",'
        '          "status": "pending",'
        '          "regions_count": 0,'
        '          "regions_count_updated_at": null,'
        '          "created_at": "2021-11-09T20:49:20.077Z",'
        '          "updated_at": "2021-11-10T22:42:50.278Z"'
        "      }"
        "    }"
        "  ],"
        '  "meta": {'
        '    "pagination": {'
        f'     "total": 526,'
        f'     "pages": {page_count}'
        "    }"
        "  },"
        '  "links": {'
        f'    "self": "/v1/organizations?page%5Bnumber%5D=1&page%5Bsize%5D={page_size}",'
        f'    "next": "/v1/organizations?page%5Bnumber%5D=2&page%5Bsize%5D={page_size}",'
        '    "prev": null'
        "  }"
        "}"
    )
    return FakeResponse(response_string)


def test_returns_results(stream):
    res = build_basic_response()
    records = list(stream.parse_response(res))
    assert len(records) == 2


def test_get_next_page_url(stream):
    res = build_basic_response()
    actual = stream.get_next_page_url(res)
    assert actual == "/v1/organizations?page%5Bnumber%5D=2&page%5Bsize%5D=2"


def test_get_next_page_url_returns_null_if_on_last_page(stream):
    response_string = "{" '  "links": {' '    "next": null' "  }" "}"
    response = FakeResponse(response_string)
    url = stream.get_next_page_url(response)
    assert url is None


def test_get_url_params_includes_page_number(stream):
    next_page_token = {"current_page": 33}
    actual = stream.get_url_params(None, next_page_token)
    assert next_page_token["current_page"] == actual["page[number]"]


def test_get_url_params_includes_sort_by_updated_descending(stream):
    sort = "-updated_at"
    next_page_token = {"current_page": 33}
    values = stream.get_url_params(None, next_page_token)
    assert sort == values["sort"]


# region parse_response
def test_parse_response_flattens_attributes_property(stream):
    res = build_basic_response()
    parsed = list(stream.parse_response(res))
    assert 2 == len(parsed)
    assert "id" in parsed[0]
    assert "attributes" not in parsed[0]
    assert "name" in parsed[0]
    assert "JS Helwig Testbed" == parsed[0]["name"]


def test_parse_response_does_not_return_extraneous_properties(stream):
    res = build_basic_response()
    parsed = list(stream.parse_response(res))
    assert 2 == len(parsed)
    assert "regions_count_updated_at" not in parsed[0]


def test_parse_response_does_not_return_records_earlier_than_the_stop_point(stream):
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    stream.get_starting_timestamp = lambda x: now - timedelta(2)  # simulate that the last run was some days ago
    body = {
        "data": [
            {"id": "1111", "attributes": {"updated_at": now}},
            {"id": "2222", "attributes": {"updated_at": now - timedelta(1)}},
            {"id": "3333", "attributes": {"updated_at": now - timedelta(3)}},
        ]
    }
    res = FakeResponse(json.dumps(body, default=str))
    records = list(stream.parse_response(res))
    ids = [r["id"] for r in records]
    assert ids == ["1111", "2222"]


# endregion

# region pagination tests
def test_get_next_page_token_returns_next_page_if_no_state(stream):
    res = build_basic_response()
    next_page_token = stream.get_next_page_token(res, None)
    assert next_page_token["current_page"] == 2


def test_get_next_page_token_returns_null_if_response_has_no_data_records(stream):
    stream.get_starting_timestamp = lambda x: datetime.utcnow().replace(tzinfo=pytz.utc)
    body = {"data": [], "links": {"next": "/v1/organizations?page%5Bnumber%5D=4&page%5Bsize%5D=2"}}
    response = FakeResponse(json.dumps(body))
    actual = stream.get_next_page_token(response, None)
    assert actual is None


def test_get_next_page_token_returns_next_page(stream):
    now = datetime.utcnow().replace(tzinfo=pytz.utc)
    stream.get_starting_timestamp = lambda x: now - timedelta(1)
    body = {
        "data": [{"attributes": {"updated_at": now}}],
        "links": {"next": "/v1/organizations?page%5Bnumber%5D=4&page%5Bsize%5D=2"},
    }
    response = FakeResponse(json.dumps(body, default=str))

    actual = stream.get_next_page_token(response, None)

    assert actual["current_page"] == 4


def test_get_next_page_token_returns_null_if_last_page(stream):
    body = {"data": [], "links": {"next": None}}
    response = FakeResponse(json.dumps(body))
    url = stream.get_next_page_token(response, None)
    assert url is None


# endregion

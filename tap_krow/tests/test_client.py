"""Tests standard tap features using the built-in SDK tests library."""

import json
import pytest

from tap_krow.streams import OrganizationsStream
from tap_krow.tap import TapKrow

SAMPLE_CONFIG = {"api_key": "testing"}


@pytest.fixture
def tap() -> TapKrow:
    return TapKrow(config={"api_key": "testing"}, parse_env_config=False)


class FakeResponse(object):
    def __init__(self, response_body: str):
        self.response_body = response_body

    def json(self):
        print(self.response_body)
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
        '          "updated_at": "2021-11-11T22:42:50.278Z"'
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


BASE_CLIENT = OrganizationsStream(TapKrow(SAMPLE_CONFIG))


def test_returns_results():
    res = build_basic_response()
    records = list(BASE_CLIENT.parse_response(res))
    print(records)
    assert len(records) == 2
    assert records[0]["attributes"]["name"] == "JS Helwig Testbed"


def test_get_next_page_url():
    res = build_basic_response()
    actual = BASE_CLIENT.get_next_page_url(res)
    assert actual == "/v1/organizations?page%5Bnumber%5D=2&page%5Bsize%5D=2"


def test_get_next_page_url_returns_null_if_on_last_page():
    response_string = "{" '  "links": {' '    "next": null' "  }" "}"
    response = FakeResponse(response_string)
    url = BASE_CLIENT.get_next_page_url(response)
    assert url is None


def test_get_url_params_includes_page_number():
    next_page_token = 33
    actual = BASE_CLIENT.get_url_params(None, next_page_token)
    print(actual)
    assert next_page_token == actual["page[number]"]


def test_get_next_page_token():
    res = build_basic_response()
    actual = BASE_CLIENT.get_next_page_token(res, None)
    assert actual == 2


def test_get_next_page_token_returns_null_if_last_page():
    response_string = "{" '  "links": {' '    "next": null' "  }" "}"
    response = FakeResponse(response_string)
    url = BASE_CLIENT.get_next_page_token(response, None)
    assert url is None


# TODO
def test_has_replication_key():
    pass


# TODO
def test_emits_state():
    pass

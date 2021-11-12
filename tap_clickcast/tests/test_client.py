"""Tests standard tap features using the built-in SDK tests library."""

import json
import requests_mock
import pytest

from tap_clickcast.streams import EmployersStream
from tap_clickcast.tap import TapClickcast

SAMPLE_CONFIG = {"partner_token": "testing"}


@pytest.fixture
def tap() -> TapClickcast:
    return TapClickcast(config={"partner_token": "testing"}, parse_env_config=False)


class FakeResponse(object):
    def __init__(self, response_body: str):
        self.response_body = response_body

    def json(self):
        return json.loads(self.response_body)


def build_basic_response(current_page, page_count=6):
    response_string = (
        "{"
        '  "count": 526,'
        f'  "num_pages": {page_count},'
        f'  "page": {current_page},'
        '  "results": ['
        "    {"
        '      "employer_id": 4508,'
        '      "employer_name": "2020 Companies"'
        "    },"
        "    {"
        '        "employer_id": 5287,'
        '        "employer_name": "2020 Companies - Jobcase"'
        "    }"
        "  ]"
        "}"
    )
    return FakeResponse(response_string)


BASE_CLIENT = EmployersStream(TapClickcast(SAMPLE_CONFIG))


def test_get_current_page_returns_current_page():
    res = build_basic_response(2)
    actual = BASE_CLIENT.get_current_page(res)
    assert actual == 2


def test_get_page_count_returns_page_count():
    res = build_basic_response(2)
    actual = BASE_CLIENT.get_page_count(res)
    assert actual == 6


def test_get_next_page_token_returns_next_page():
    res = build_basic_response(2)
    actual = BASE_CLIENT.get_next_page_token(res, None)
    assert actual == 3


def test_get_next_page_token_returns_none_if_on_last_page():
    res = build_basic_response(6)
    actual = BASE_CLIENT.get_next_page_token(res, None)
    assert actual is None


def test_get_next_page_token_returns_none_if_only_one_page():
    res = build_basic_response(1, page_count=1)
    actual = BASE_CLIENT.get_next_page_token(res, None)
    assert actual is None


def test_handles_429_too_many_requests_and_retries():
    with requests_mock.Mocker() as m:
        fake_response_text = json.dumps(build_basic_response(1, page_count=1).json())
        m.get(
            "https://api.clickcast.cloud/clickcast/api/employers?fields=employer_id",
            [
                {"status_code": 429},
                {"status_code": 429},
                {"status_code": 200, "text": fake_response_text},
            ],
        )
        BASE_CLIENT.sync()


def test_get_params_returns_correct_page_size_param(tap):
    # Chuck Officer gave us a hint to use the param _page_size to get up to 1000 records at once
    stream = EmployersStream(tap)
    params = stream.get_url_params({}, 2)
    assert "_page_size" in params
    assert params["_page_size"] == 1000

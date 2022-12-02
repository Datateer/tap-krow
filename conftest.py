import json
import os

import pytest

from tap_krow.tap import TapKrow


class FakeResponse(object):
    def __init__(self, response_body: str):
        self.response_body = response_body

    def json(self):
        return json.loads(self.response_body)


@pytest.fixture(scope="session", autouse=True)
def tap_instance():
    SAMPLE_CONFIG = {"api_key": "testing"}
    return TapKrow(SAMPLE_CONFIG)


@pytest.fixture(scope="session", autouse=True)
def api_responses():
    responses = {}
    for root, dirs, _files in os.walk("tap_krow/tests/api_responses"):
        for d in dirs:
            responses[d] = {}
            response_files = [
                f for f in os.listdir(os.path.join(root, d)) if f.endswith(".json")
            ]
            for file in response_files:
                with open(os.path.join(root, d, file)) as f:
                    responses[d][file] = FakeResponse(f.read())
    return responses


@pytest.fixture
def get_parsed_records():
    """This fixture returns a function so you can pass in an API response body
    as a string and get back a parsed response object, parsed by the Stream"""

    def response_parser(stream_instance, response):
        return list(stream_instance.parse_response(response))

    return response_parser

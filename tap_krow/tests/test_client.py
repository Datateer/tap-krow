"""Test general stream capabilities"""

from datetime import datetime
import pytest
import pytz

from tap_krow.streams import OrganizationsStream


@pytest.fixture(scope="module")
def stream(tap_instance):
    return OrganizationsStream(tap_instance)


@pytest.fixture(scope="module")
def responses(api_responses):
    """Returns an instance of a stream, which """
    return api_responses["organizations"]


# def build_basic_response(page_count=17, page_size=2):
#     """Simulate a response from the KROW API
#     :page_count: Simulate the API returning a certain number of pages, by overriding this value
#     """
#     response_string = (
#         "{"
#         '  "data": ['
#         "    {"
#         '      "id": "ea196757-acbb-4be2-a685-703e8349f443",'
#         '      "type": "organizations",'
#         '        "attributes": {'
#         '            "name": "JS Helwig Testbed",'
#         '            "status": "pending",'
#         '            "regions_count": 2,'
#         '            "regions_count_updated_at": "2021-11-10T21:05:49.085Z",'
#         '            "created_at": "2021-11-09T21:07:39.828Z",'
#         '            "updated_at": "2021-11-11T22:42:50.304Z"'
#         "        }"
#         "    },"
#         "    {"
#         '      "id": "9e48251e-929b-45f8-bcc6-93fb5c753072",'
#         '      "type": "organizations",'
#         '      "attributes": {'
#         '          "name": "Lowe\'s Testbed",'
#         '          "status": "pending",'
#         '          "regions_count": 0,'
#         '          "regions_count_updated_at": null,'
#         '          "created_at": "2021-11-09T20:49:20.077Z",'
#         '          "updated_at": "2021-11-10T22:42:50.278Z"'
#         "      }"
#         "    }"
#         "  ],"
#         '  "meta": {'
#         '    "pagination": {'
#         f'     "total": 526,'
#         f'     "pages": {page_count}'
#         "    }"
#         "  },"
#         '  "links": {'
#         f'    "self": "/v1/organizations?page%5Bnumber%5D=1&page%5Bsize%5D={page_size}",'
#         f'    "next": "/v1/organizations?page%5Bnumber%5D=2&page%5Bsize%5D={page_size}",'
#         '    "prev": null'
#         "  }"
#         "}"
#     )
#     return FakeResponse(response_string)


def test_returns_results(responses, stream, get_parsed_records):
    records = get_parsed_records(stream, responses["orgs_default.json"])
    assert len(records) == 25


def test_get_next_page_url(responses, stream):
    actual = stream.get_next_page_url(responses["orgs_default.json"])
    assert actual == "/v1/organizations?page%5Bnumber%5D=2&page%5Bsize%5D=25&sort=updated_at"


def test_get_next_page_url_returns_null_if_on_last_page(responses, stream):
    url = stream.get_next_page_url(responses["orgs_last_page.json"])
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
def test_parse_response_flattens_attributes_property(responses, stream):
    parsed = list(stream.parse_response(responses["orgs_default.json"]))
    assert 25 == len(parsed)
    assert "id" in parsed[0]
    assert "attributes" not in parsed[0]
    assert "name" in parsed[0]
    assert "kobe" == parsed[0]["name"]


def test_parse_response_does_not_return_extraneous_properties(responses, stream):
    parsed = list(stream.parse_response(responses["orgs_default.json"]))
    assert 25 == len(parsed)
    assert "regions_count_updated_at" not in parsed[0]


def test_parse_response_does_not_return_records_earlier_than_the_stop_point(responses, stream):
    stream.get_starting_timestamp = lambda x: datetime(
        2020, 1, 1, tzinfo=pytz.utc
    )  # simulate that the last run was some days ago
    records = list(stream.parse_response(responses["orgs_records_before_and_after_2020-01-01.json"]))
    ids = [r["id"] for r in records]
    assert ids == ["record_updated_at_jan_3", "record_updated_at_jan_2"]


# endregion

# region pagination tests
def test_get_next_page_token_returns_next_page_if_no_state(responses, stream):
    next_page_token = stream.get_next_page_token(responses["orgs_default.json"], None)
    assert next_page_token["current_page"] == 2


def test_get_next_page_token_returns_null_if_response_has_no_data_records(responses, stream):
    stream.get_starting_timestamp = lambda x: datetime.utcnow().replace(tzinfo=pytz.utc)
    actual = stream.get_next_page_token(responses["orgs_last_page.json"], None)
    assert actual is None


def test_get_next_page_token_returns_next_page(responses, stream):
    stream.get_starting_timestamp = lambda x: datetime(2001, 1, 1, tzinfo=pytz.utc)

    actual = stream.get_next_page_token(responses["orgs_records_before_and_after_2020-01-01.json"], None)

    assert actual["current_page"] == 2


def test_get_next_page_token_returns_null_if_last_page(responses, stream):
    url = stream.get_next_page_token(responses["orgs_last_page.json"], None)
    assert url is None


# endregion

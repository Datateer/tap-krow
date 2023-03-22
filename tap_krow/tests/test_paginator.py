from datetime import datetime
from dateutil.relativedelta import relativedelta
from tap_krow.client import KrowPaginator
from urllib.parse import urlparse, parse_qsl


# region get_next_url
def test_returns_next_page_when_bookmark_is_null(api_responses):
    paginator = KrowPaginator(None)
    actual = paginator.get_next_url(api_responses["organizations"]["orgs_default.json"])
    assert actual == "/v1/organizations?page%5Bnumber%5D=2&page%5Bsize%5D=25&sort=updated_at"


def test_get_next_url_returns_null_next_page_when_api_response_with_zero_records(api_responses):
    paginator = KrowPaginator(datetime.now())
    actual = paginator.get_next_url(api_responses["campaigns"]["campaigns_zero_records.json"])
    assert actual is None


def test_get_next_url_returns_null_if_on_last_page(api_responses):
    paginator = KrowPaginator(datetime.now())
    actual = paginator.get_next_url(api_responses["organizations"]["orgs_last_page.json"])
    assert actual is None


def test_get_next_url_returns_next_page_url_when_old_bookmark(api_responses):
    bookmark = datetime.now().astimezone() - relativedelta(years=100)
    paginator = KrowPaginator(bookmark)
    url = paginator.get_next_url(api_responses["organizations"]["orgs_default.json"])
    parsed = parse_qsl(urlparse(url).query)
    assert ("page[number]", "2") in parsed


# endregion

# region get_earliest_timestamp
def test_get_earliest_timestamp_in_response_returns_null_if_no_records_when_no_records(api_responses):
    paginator = KrowPaginator(None)
    actual = paginator.get_earliest_timestamp_in_response(api_responses["campaigns"]["campaigns_zero_records.json"])
    assert actual is None


# endregion

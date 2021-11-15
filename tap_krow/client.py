"""REST client handling, including krowStream base class."""

import backoff
import re
import requests
from pathlib import Path
from typing import Any, Dict, Optional, Iterable, cast

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream
from tap_krow.auth import krowAuthenticator


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class KrowStream(RESTStream):
    """KROW stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url_base"]

    is_sorted = True  # ref https://sdk.meltano.com/en/latest/implementation/state.html?highlight=incremental#the-impact-of-sorting-on-incremental-sync
    records_jsonpath = "$.data[*]"  # "$[*]"  # Or override `parse_response`.
    current_page_jsonpath = "$.meta."
    next_page_url_jsonpath = "$.links.next"

    @property
    def authenticator(self) -> krowAuthenticator:
        """Return a new authenticator object."""
        return krowAuthenticator.create_for_stream(self)

    def get_next_page_url(self, response: requests.Response):
        matches = extract_jsonpath(self.next_page_url_jsonpath, response.json())
        next_page_url = next(iter(matches), None)
        return next_page_url

    def get_next_page_token(self, response: requests.Response, previous_token: Optional[Any]) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        next_page_token = None
        next_page_url = self.get_next_page_url(response)
        if next_page_url:
            search = re.search("page%5Bnumber%5D=(\d+)", next_page_url)
            if search:
                next_page_token = int(search.group(1))

        return next_page_token

    def get_url_params(self, context: Optional[dict], next_page_token: Optional[Any]) -> Dict[str, Any]:
        # print(self.schema)
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {
            "page[size]": 2,  # TODO: remove or increase when testing of pagination is complete
            "sort": "updated_at",
        }
        if next_page_token:
            params["page[number]"] = next_page_token

        # TODO: support incremental replication
        # if self.replication_key:
        #     params["sort"] = "asc"
        #     params["order_by"] = self.replication_key
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

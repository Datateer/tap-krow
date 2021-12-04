"""REST client handling, including krowStream base class."""

import dateutil
import re
import requests
from pathlib import Path
from typing import Any, Dict, Optional, Iterable

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

    records_jsonpath = "$.data[*]"  # "$[*]"  # Or override `parse_response`.
    current_page_jsonpath = "$.meta."
    next_page_url_jsonpath = "$.links.next"
    # the number of records to request in each page
    page_size = 2  # TODO: remove or increase when testing of pagination is complete
    replication_key = "updated_at"
    # replication_key_value = None
    # a custom property
    earliest_signpost = None

    @property
    def authenticator(self) -> krowAuthenticator:
        """Return a new authenticator object."""
        return krowAuthenticator.create_for_stream(self)

    def get_next_page_url(self, response: requests.Response):
        matches = extract_jsonpath(self.next_page_url_jsonpath, response.json())
        next_page_url = next(iter(matches), None)
        return next_page_url

    def get_earliest_timestamp_in_response(self, response: requests.Response):
        """This assumes the response is sorted in descending order"""
        matches = extract_jsonpath(f"$.data[-1:].attributes.{self.replication_key}", response.json())
        earliest_timestamp_in_response = next(iter(matches), None)
        if earliest_timestamp_in_response is None:
            return None
        return dateutil.parser.parse(earliest_timestamp_in_response)

    def get_next_page_token(self, response: requests.Response, previous_token: Optional[Any]) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages.
        For KROW, the only option is to sort in descending order, so we return only if earliest time in response < stop point
        We use a dictionary here to keep track of the stop point and the current page, whereas a simpler implementation might just return the current page
        """
        # set previous token if not exists, including stop point
        if previous_token is None:
            previous_token = {"stop_point": self.get_starting_timestamp(self.stream_state), "current_page": 1}
        next_page_token = None
        earliest_timestamp = self.get_earliest_timestamp_in_response(response)

        # if no earliest timestamp is available, then no data was returned, and we should exit
        if earliest_timestamp is None:
            return None

        # if stop_point is None, then no state was passed in, and we want all records
        # if stop_point is < the earliest timestamp in the response, we want to get the next page
        if previous_token["stop_point"] is None or previous_token["stop_point"] < earliest_timestamp:
            next_page_url = self.get_next_page_url(response)
            if next_page_url:
                search = re.search("page%5Bnumber%5D=(\\d+)", next_page_url)
                if search:
                    next_page_token = {**previous_token, "current_page": int(search.group(1))}
        print("--------- end of 'get_next_page_token'. Returning next_page_token: ", next_page_token)
        return next_page_token

    def get_url_params(self, context: Optional[dict], next_page_token: Optional[Any]) -> Dict[str, Any]:
        # if self.replication_key_value is None:
        #     self.replication_key_value = self.get_starting_timestamp(context)
        # print(self.schema)
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {
            "page[size]": self.page_size,
            # the minus sign indicates a descending sort. We sort on updated_at until we reach a state
            # we have already extracted. Then we short circuit to stop paginating and stop returning records
            "sort": f"-{self.replication_key}",
        }
        if next_page_token:
            params["page[number]"] = next_page_token["current_page"]

        # TODO: support incremental replication
        # if self.replication_key:
        #     params["sort"] = "asc"
        #     params["order_by"] = self.replication_key
        print("--------- end of 'get_url_params', returning params: ", params)
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows. The response is slightly nested, like this:
            {
                "id" "...",
                "attributes": {
                    "attr1": "...",
                    "attr2": "...
                }
            }

        We need the ID and the properties inside the "attributes" property. The only way I have found to do this so far with the
        Singer SDK is to do the work here to flatten things
        """
        # stop_point = self.get_starting_timestamp(self.stream_state)

        properties_defined_in_schema = self.schema["properties"].keys()
        for record in extract_jsonpath(self.records_jsonpath, input=response.json()):
            flattened = {"id": record["id"], **record["attributes"]}
            keys_to_remove = [k for k in flattened.keys() if k not in properties_defined_in_schema]
            for k in keys_to_remove:
                flattened.pop(k)
            # TODO: short circuit if we encounter records from earlier than our stop_point
            # if flattened["updated_at"] is None or (
            #     stop_point is not None and dateutil.parser.parse(flattened["updated_at"]) < stop_point
            # ):
            #     return
            # self.replication_key_value = flattened["updated_at"]
            yield flattened

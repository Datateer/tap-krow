"""REST client handling, including krowStream base class."""

from datetime import datetime
import dateutil
import logging
from urllib.parse import parse_qsl
import requests
from typing import Any, Dict, Optional, Iterable

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream
from singer_sdk.exceptions import FatalAPIError, RetriableAPIError
from tap_krow.auth import krowAuthenticator
from tap_krow.normalize import (
    flatten_dict,
    remove_unnecessary_keys,
    make_fields_meltano_select_compatible,
)
from singer_sdk.pagination import BaseHATEOASPaginator, BaseAPIPaginator

REPLICATION_KEY = "updated_at"


class KrowPaginator(BaseHATEOASPaginator):
    """The pagination strategy sorts updated_at descending.
    It will continue requesting records until we reach the bookmark
    When we reach a record with an updated_at value that is earlier than the bookmarked updated_at, we stop"""

    current_page_jsonpath = "$.meta."

    def __init__(self, bookmarked_timestamp, logger=logging, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.bookmarked_timestamp = bookmarked_timestamp
        self.logger = logger

    def get_next_url(self, response):
        """overrides method from base class. Returns None if no next page should be requested, otherwise returns a URL for the next page"""

        earliest_timestamp_in_response = self.get_earliest_timestamp_in_response(response)
        matches = extract_jsonpath("$.links.next", response.json())
        url = next(iter(matches), None)

        if earliest_timestamp_in_response is None:
            # in this case, there were no records returned in the page. Return None so that paging stops
            return None
        elif self.bookmarked_timestamp is None:
            # in this case, there is no bookmark, so the run is a full refresh. Return the next page's URL (the last page will have a None value, so paging will stop)
            return url
        elif earliest_timestamp_in_response < self.bookmarked_timestamp:
            # in this case, we've reached the bookmark, and there are no more updates to retrieve. Stop the pagination by returning None
            self.logger.info(
                f"Reached bookmark (the earliest timestamp in this page is {earliest_timestamp_in_response}, which is less than the bookmark {self.bookmarked_timestamp}. No more pages for this stream/partition need to be requested)"
            )
            return None
        else:
            # in this case, there are more records that are earlier than the bookmark. Return the next page's URL
            return url

    def get_earliest_timestamp_in_response(self, response: requests.Response):
        """Finds the earliest timestamp in the response and returns it.
        This assumes the response is sorted in descending order"""
        records = list(extract_jsonpath("$.data", response.json()))[0]
        if len(records) == 0:
            return None
        matches = extract_jsonpath(f"$.data[-1:].attributes.{REPLICATION_KEY}", response.json())
        earliest_timestamp_in_response = next(iter(matches), None)
        if earliest_timestamp_in_response is None:
            return None
        return dateutil.parser.parse(earliest_timestamp_in_response)


class KrowStream(RESTStream):
    """KROW stream class."""

    page_size = 100  # this is the upper limit allowed by the KROW API

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url_base"]

    records_jsonpath = "$.data[*]"  # "$[*]"  # Or override `parse_response`.
    # the number of records to request in each page warning at 1,000 records,
    # the KROW API returned errors without any additional info.
    # Lots of troubleshooting difficulty
    replication_key = "updated_at"
    primary_keys = ["id"]

    # Capture the starting timestamp, so that when this stream completes,
    # the state's bookmark value will be as of when the tap started
    tap_start_datetime = datetime.now().isoformat()

    @property
    def authenticator(self) -> krowAuthenticator:
        """Return a new authenticator object."""
        return krowAuthenticator.create_for_stream(self)

    def get_new_paginator(self) -> BaseAPIPaginator:
        """overrides base class method to return a paginator"""

        return KrowPaginator(bookmarked_timestamp=self._bookmarked_updated_at, logger=self.logger)

    def get_url_params(self, context: Optional[dict], next_page_token: Optional[Any]) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {
            "page[size]": self.page_size,
            # the minus sign indicates a descending sort. We sort on updated_at
            # until we reach a state we have already extracted. Then we short
            # circuit to stop paginating and stop returning records
            "sort": f"-{REPLICATION_KEY}",
        }
        if next_page_token:
            params.update(parse_qsl(next_page_token.query))
        return params

    def validate_response(self, response):
        # Still catch error status codes
        if response.status_code == 409:
            msg = f"{response.status_code} Conflict Error: " f"{response.reason} for url: {response.url}"
            raise CustomerNotEnabledError(msg)

        if 400 <= response.status_code < 500:
            msg = f"{response.status_code} Client Error: " f"{response.reason} for path: {self.path}." f"response.json() {response.json()}:"
            raise FatalAPIError(msg)

        elif 500 <= response.status_code < 600:
            msg = f"{response.status_code} Server Error: " f"{response.reason} for path: {self.path}"
            raise RetriableAPIError(msg)

    def get_records(self, context: Optional[dict]) -> Iterable[Dict[str, Any]]:
        """Return a generator of row-type dictionary objects.

        Each row emitted should be a dictionary of property names to their values.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            One item per (possibly processed) record in the API.
        """
        # at this point, we have the stream/partition's starting timestamp. We cache it here
        # so that it is available when get_new_paginator is called
        self._bookmarked_updated_at = self.get_starting_timestamp(context)

        try:
            for record in self.request_records(context):
                transformed_record = self.post_process(record, context)
                if transformed_record is None:
                    # Record filtered out during post_process()
                    continue
                yield transformed_record

        except CustomerNotEnabledError as e:
            self.logger.warning(
                f"""We hit the Conflict Error.
                This happens when an organization does not have interviewing enabled
                {e=}"""
            )

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows.
        The response is slightly nested, like this:
            {
                "id" "...",
                "attributes": {
                    "attr1": "...",
                    "attr2": "...
                }
            }

        We need the ID and the properties inside the "attributes" property.
        The only way I have found to do this so far with the
        Singer SDK is to do the work here to flatten things.

        This function will also strip out records that are earlier than the stop point;
        we do not need these records, because they were synced earlier
        """
        stop_point = self.get_starting_timestamp(None)
        properties_defined_in_schema = self.schema["properties"].keys()

        for record in extract_jsonpath(self.records_jsonpath, input=response.json()):
            d = {
                "id": record["id"],
                **record["attributes"],
            }
            if 'relationships' in record:
                d.update(record["relationships"])
            d = make_fields_meltano_select_compatible(d)

            # remove extraneous keys that only muddle the field names in the output
            d = remove_unnecessary_keys(d, ["data"])

            d = flatten_dict(d)

            # remove extraneous keys that are not in the stream's schema
            keys_to_remove = [k for k in d.keys() if k not in properties_defined_in_schema]
            d = remove_unnecessary_keys(d, keys_to_remove)

            # short circuit if we encounter records from earlier than our stop_point
            if d["updated_at"] is None or (stop_point is not None and dateutil.parser.parse(d["updated_at"]) < stop_point):
                logging.info(
                    f"""The record for stream "{self.tap_stream_id}" with ID "{d["id"]}" has updated_at = {d["updated_at"]} which is less than the stop point of {stop_point}. The stream will stop syncing here and not return any more records, because they were synced in an earlier run"""
                )
                return
            yield d


class CustomerNotEnabledError(Exception):
    """
    Some organizations do not have interviewing enabled.
    """

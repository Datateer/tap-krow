"""REST client handling, including ClickcastStream base class."""

import backoff
import requests
from pathlib import Path
from typing import Any, Dict, Optional, Iterable, cast

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream
from tap_clickcast.auth import clickcastAuthenticator


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class ClickcastStream(RESTStream):
    """clickcast stream class."""

    # TODO: this is overriding the _request_with_backoff so that we can handle 429 appropriately
    # this should be removed and code be refactored when https://gitlab.com/meltano/sdk/-/issues/137 is completed
    @backoff.on_exception(
        backoff.expo,
        (requests.exceptions.RequestException),
        max_tries=8,
        giveup=lambda e: e.response is not None
        and 400 <= e.response.status_code < 500
        and e.response.status_code != 429,
        factor=2,
    )
    def _request_with_backoff(self, prepared_request, context: Optional[dict]) -> requests.Response:
        response = self.requests_session.send(prepared_request)
        if self._LOG_REQUEST_METRICS:
            extra_tags = {}
            if self._LOG_REQUEST_METRIC_URLS:
                extra_tags["url"] = cast(str, prepared_request.path_url)
            self._write_request_duration_log(
                endpoint=self.path,
                response=response,
                context=context,
                extra_tags=extra_tags,
            )
        if response.status_code in [401, 403]:
            self.logger.info("Failed request for {}".format(prepared_request.url))
            self.logger.info(f"Reason: {response.status_code} - {str(response.content)}")
            raise RuntimeError("Requested resource was unauthorized, forbidden, or not found.")
        if response.status_code == 429:
            self.logger.info("Throttled request for {}".format(prepared_request.url))
            raise requests.exceptions.RequestException(request=prepared_request, response=response)
        elif response.status_code >= 400:
            raise RuntimeError(
                f"Error making request to API: {prepared_request.url} "
                f"[{response.status_code} - {str(response.content)}]".replace("\\n", "\n")
            )

        return response

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config["api_url_base"]

    records_jsonpath = "$.results[*]"  # "$[*]"  # Or override `parse_response`.
    current_page_jsonpath = "$.page"
    page_count_jsonpath = "$.num_pages"
    # next_page_token_jsonpath = "$.next_page"  # Or override `get_next_page_token`.

    @property
    def authenticator(self) -> clickcastAuthenticator:
        """Return a new authenticator object."""
        return clickcastAuthenticator.create_for_stream(self)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        # If not using an authenticator, you may also provide inline auth headers:
        # headers["Private-Token"] = self.config.get("auth_token")
        return headers

    def get_current_page(self, response: requests.Response):
        matches = extract_jsonpath(self.current_page_jsonpath, response.json())
        current_page = next(iter(matches), None)
        return current_page

    def get_page_count(self, response: requests.Response):
        matches = extract_jsonpath(self.page_count_jsonpath, response.json())
        page_count = next(iter(matches), None)
        return page_count

    def get_next_page_token(self, response: requests.Response, previous_token: Optional[Any]) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        next_page_token = None

        current = self.get_current_page(response)
        count = self.get_page_count(response)
        if current == count:
            next_page_token = None
        elif current < count:
            next_page_token = current + 1

        return next_page_token

    def get_url_params(self, context: Optional[dict], next_page_token: Optional[Any]) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {"_page_size": 1000}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        if self.metadata:
            fields = [
                item["breadcrumb"][1]
                for item in self.metadata
                if "breadcrumb" in item
                and len(item["breadcrumb"]) == 2
                and (
                    "inclusion" in item["metadata"]
                    and (
                        item["metadata"]["inclusion"] == "automatic"
                        or (
                            item["metadata"]["inclusion"] == "available"
                            and ("selected" in item["metadata"] and item["metadata"]["selected"] is True)
                        )
                    )
                )
            ]
            params["fields"] = ",".join(fields)
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())

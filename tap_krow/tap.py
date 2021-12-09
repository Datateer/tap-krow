"""krow tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_krow.streams import ApplicantsStream, LocationsStream, OrganizationsStream, PositionsStream, RegionsStream

STREAM_TYPES = [ApplicantsStream, LocationsStream, OrganizationsStream, PositionsStream, RegionsStream]


class TapKrow(Tap):
    """krow tap class."""

    name = "tap-krow"

    config_jsonschema = th.PropertiesList(
        th.Property("api_key", th.StringType, required=True),
        th.Property(
            "api_url_base",
            th.StringType,
            default="https://industry-staging.herokuapp.com/v1",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]

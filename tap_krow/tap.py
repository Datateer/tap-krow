"""krow tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_krow.streams import (
    ApplicantsStream,
    CampaignStream,
    LocationInterviewStream,
    RegionInterviewStream,
    LocationCalendarStream,
    LocationsStream,
    OrganizationsStream,
    PositionsStream,
    RegionCalendarStream,
    RegionsStream,
)

# from tap_krow.streams.applicants import ApplicantsStream

STREAM_TYPES = [
    ApplicantsStream,
    CampaignStream,
    LocationInterviewStream,
    RegionInterviewStream,
    LocationCalendarStream,
    LocationsStream,
    OrganizationsStream,
    PositionsStream,
    RegionCalendarStream,
    RegionsStream,
]


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

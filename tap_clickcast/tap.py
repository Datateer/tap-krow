"""clickcast tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_clickcast.streams import CampaignsStream, EmployersStream, JobsStream, JobStatsStream

STREAM_TYPES = [CampaignsStream, EmployersStream, JobsStream, JobStatsStream]


class TapClickcast(Tap):
    """clickcast tap class."""

    name = "tap-clickcast"

    config_jsonschema = th.PropertiesList(
        th.Property("partner_token", th.StringType, required=True),
        th.Property(
            "api_url_base",
            th.StringType,
            default="https://api.clickcast.cloud/clickcast/api",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]

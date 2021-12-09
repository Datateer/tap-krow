"""Stream type classes for tap-krow."""
from typing import Optional

from singer_sdk.typing import (
    DateTimeType,
    NumberType,
    PropertiesList,
    Property,
    StringType,
)

from tap_krow.client import KrowStream


class OrganizationsStream(KrowStream):
    name = "organizations"
    path = "/organizations"
    schema = PropertiesList(
        Property("id", StringType, required=True),
        Property("name", StringType),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for the child streams. Refer to https://sdk.meltano.com/en/latest/parent_streams.html"""
        return {"organization_id": record["id"]}


class PositionsStream(KrowStream):
    name = "positions"
    path = "/organizations/{organization_id}/positions"
    schema = PropertiesList(
        Property("id", StringType, required=True),
        Property("name", StringType),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    parent_stream_type = OrganizationsStream
    ignore_parent_replication_key = True


class RegionsStream(KrowStream):
    name = "regions"
    path = "/organizations/{organization_id}/regions"
    schema = PropertiesList(
        Property("id", StringType, required=True),
        Property("name", StringType),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    parent_stream_type = OrganizationsStream
    ignore_parent_replication_key = True


class LocationsStream(KrowStream):
    name = "locations"
    path = "/organizations/{organization_id}/locations"
    schema = PropertiesList(
        Property("id", StringType, required=True),
        Property("name", StringType),
        Property("city", StringType),
        Property("state", StringType),
        Property("postal_code", StringType),
        Property("time_zone", StringType),
        Property("latitude", NumberType),
        Property("longitude", NumberType),
        Property("parent_id", StringType),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    parent_stream_type = OrganizationsStream
    ignore_parent_replication_key = True


class ApplicantsStream(KrowStream):
    name = "applicants"
    path = "/organizations/{organization_id}/applicants"
    schema = PropertiesList(
        Property("id", StringType, required=True),
        Property("name", StringType),
        Property("action", StringType),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    parent_stream_type = OrganizationsStream
    ignore_parent_replication_key = True

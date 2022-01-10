"""Stream type classes for tap-krow."""
from typing import Optional

from singer_sdk.typing import (
    BooleanType,
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
        Property("account_managers_count", NumberType),
        Property("account_managers_count_updated_at", StringType),
        Property("average_days_to_decision", NumberType),
        Property("average_days_to_decision_updated_at", StringType),
        Property("description", StringType),
        Property("id", StringType, required=True),
        Property("onboarding", BooleanType),
        Property("name", StringType),
        Property("organization_members_count", NumberType),
        Property("organization_members_count_updated_at", DateTimeType),
        Property("rolling_apply_count_updated_at", DateTimeType),
        Property("rolling_daily_apply_change", NumberType),
        Property("rolling_daily_apply_count", NumberType),
        Property("rolling_daily_hire_change", NumberType),
        Property("rolling_daily_hire_count", NumberType),
        Property("rolling_hire_count_updated_at", DateTimeType),
        Property("rolling_monthly_apply_change", NumberType),
        Property("rolling_monthly_apply_count", NumberType),
        Property("rolling_monthly_hire_change", NumberType),
        Property("rolling_monthly_hire_count", NumberType),
        Property("status", StringType),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for the child streams. Refer to https://sdk.meltano.com/en/latest/parent_streams.html"""
        return {"organization_id": record["id"]}


class PositionsStream(KrowStream):
    name = "positions"
    path = "/organizations/{organization_id}/positions"
    schema = PropertiesList(
        Property("average_days_to_decision", NumberType),
        Property("average_days_to_decision_updated_at", DateTimeType),
        Property("description", StringType),
        Property("id", StringType, required=True),
        Property("organization_id", StringType),
        Property("name", StringType),
        Property("rolling_apply_count_updated_at", DateTimeType),
        Property("rolling_daily_apply_change", NumberType),
        Property("rolling_daily_apply_count", NumberType),
        Property("rolling_daily_hire_change", NumberType),
        Property("rolling_daily_hire_count", NumberType),
        Property("rolling_hire_count_updated_at", DateTimeType),
        Property("rolling_monthly_apply_change", NumberType),
        Property("rolling_monthly_apply_count", NumberType),
        Property("rolling_monthly_hire_change", NumberType),
        Property("rolling_monthly_hire_count", NumberType),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    parent_stream_type = OrganizationsStream
    ignore_parent_replication_key = True


class RegionsStream(KrowStream):
    name = "regions"
    path = "/organizations/{organization_id}/regions"
    schema = PropertiesList(
        Property("average_days_to_decision", NumberType),
        Property("average_days_to_decision_updated_at", DateTimeType),
        Property("id", StringType, required=True),
        Property("name", StringType),
        Property("organization_id", StringType),
        Property("region_managers_count", NumberType),
        Property("region_managers_count_updated_at", DateTimeType),
        Property("rolling_apply_count_updated_at", DateTimeType),
        Property("rolling_daily_apply_change", NumberType),
        Property("rolling_daily_apply_count", NumberType),
        Property("rolling_daily_hire_change", NumberType),
        Property("rolling_daily_hire_count", NumberType),
        Property("rolling_hire_count_updated_at", DateTimeType),
        Property("rolling_monthly_apply_change", NumberType),
        Property("rolling_monthly_apply_count", NumberType),
        Property("rolling_monthly_hire_change", NumberType),
        Property("rolling_monthly_hire_count", NumberType),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    parent_stream_type = OrganizationsStream
    ignore_parent_replication_key = True


class LocationsStream(KrowStream):
    name = "locations"
    path = "/organizations/{organization_id}/locations"
    schema = PropertiesList(
        Property("city", StringType),
        Property("id", StringType, required=True),
        Property("latitude", NumberType),
        Property("longitude", NumberType),
        Property("name", StringType),
        Property("parent_id", StringType),
        Property("postal_code", StringType),
        Property("region_id", StringType),
        Property("rolling_apply_count_updated_at", DateTimeType),
        Property("rolling_daily_apply_change", NumberType),
        Property("rolling_daily_apply_count", NumberType),
        Property("rolling_daily_hire_change", NumberType),
        Property("rolling_daily_hire_count", NumberType),
        Property("rolling_hire_count_updated_at", DateTimeType),
        Property("rolling_monthly_apply_change", NumberType),
        Property("rolling_monthly_apply_count", NumberType),
        Property("rolling_monthly_hire_change", NumberType),
        Property("rolling_monthly_hire_count", NumberType),
        Property("state", StringType),
        Property("time_zone", StringType),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    parent_stream_type = OrganizationsStream
    ignore_parent_replication_key = True


class ApplicantsStream(KrowStream):
    name = "applicants"
    path = "/organizations/{organization_id}/applicants"
    schema = PropertiesList(
        Property("id", StringType, required=True),
        Property("action", StringType),
        Property("first_name", StringType),
        Property("full_name", StringType),
        Property("last_name", StringType),
        Property("locality_id", StringType),
        Property("locality_type", StringType),
        Property("status", StringType),
        Property("opening_position_id", StringType),
        Property("organization_id", StringType),
        Property("state_action", StringType),
        Property("state_changed_at", DateTimeType),
        Property("state_name", StringType),
        Property("transitioning", BooleanType),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    parent_stream_type = OrganizationsStream
    ignore_parent_replication_key = True

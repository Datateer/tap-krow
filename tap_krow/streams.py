"""Stream type classes for tap-krow."""
from typing import Optional

from singer_sdk.typing import (
    DateTimeType,
    NumberType,
    PropertiesList,
    Property,
    StringType,
)

from tap_krow.client import KrowStream, CustomerNotEnabledError


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
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for the child streams.
        Refer to https://sdk.meltano.com/en/latest/parent_streams.html"""
        return {"organization_id": record["id"]}


class CampaignStream(KrowStream):
    name = "campaigns"
    path = "/organizations/{organization_id}/campaigns"
    schema = PropertiesList(
        Property("created_at", DateTimeType, required=True),
        Property("id", StringType, required=True),
        Property("updated_at", DateTimeType, required=True),
        Property("utm_campaign", StringType),
        Property("utm_content", StringType),
        Property("utm_medium", StringType),
        Property("utm_source", StringType),
        Property("utm_term", StringType),
        Property("organization_id", StringType),
        Property("locality_type", StringType),
        Property("locality_id", StringType),
        Property("applicant_id", StringType),
    ).to_dict()

    parent_stream_type = OrganizationsStream
    ignore_parent_replication_key = True


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

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for the child streams.
        Refer to https://sdk.meltano.com/en/latest/parent_streams.html"""
        return {"region_id": record["id"]}


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

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for the child streams.
        Refer to https://sdk.meltano.com/en/latest/parent_streams.html"""
        return {"location_id": record["id"]}


class ApplicantsStream(KrowStream):
    name = "applicants"
    path = "/organizations/{organization_id}/applicants"
    schema = PropertiesList(
        Property("id", StringType, required=True),
        Property("action", StringType),
        Property("created_at", DateTimeType),
        Property("first_name", StringType),
        Property("full_name", StringType),
        Property("last_name", StringType),
        Property("interview_id", StringType),
        Property("locality_id", StringType),
        Property("locality_type", StringType),
        Property("status", StringType),
        Property("opening_position_id", StringType),
        Property("organization_id", StringType),
        Property("state_action", StringType),
        Property("state_changed_at", DateTimeType),
        Property("state_name", StringType),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    parent_stream_type = OrganizationsStream
    ignore_parent_replication_key = True


class RegionCalendarStream(KrowStream):
    name = "region_calendars"
    path = "/regions/{region_id}/calendar"
    schema = PropertiesList(
        Property("id", StringType, required=True),
        Property("created_at", DateTimeType, required=True),
        Property("ending_on", DateTimeType),
        Property("organization_id", StringType),
        Property("starting_on", DateTimeType),
        Property("locality_id", StringType),
        Property("locality_type", StringType),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    parent_stream_type = RegionsStream
    ignore_parent_replication_key = True

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for the child streams.
        Refer to https://sdk.meltano.com/en/latest/parent_streams.html"""
        return {"calendar_id": record["id"]}

    def validate_response(self, response):
        # Still catch error status codes
        if response.status_code == 404:
            msg = f"{response.status_code} Customer without Calendar in this Region: " f"{response.reason} for url: {response.url}"
            raise CustomerNotEnabledError(msg)
        if response.status_code == 409:
            msg = f"{response.status_code} Conflict Error: " f"{response.reason} for url: {response.url}"
            raise CustomerNotEnabledError(msg)


class LocationCalendarStream(KrowStream):
    name = "location_calendars"
    path = "/locations/{location_id}/calendar"
    schema = PropertiesList(
        Property("id", StringType, required=True),
        Property("created_at", DateTimeType, required=True),
        Property("ending_on", DateTimeType),
        Property("organization_id", StringType),
        Property("starting_on", DateTimeType),
        Property("locality_id", StringType),
        Property("locality_type", StringType),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    parent_stream_type = LocationsStream
    ignore_parent_replication_key = True

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for the child streams.
        Refer to https://sdk.meltano.com/en/latest/parent_streams.html"""
        return {"calendar_id": record["id"]}


class RegionInterviewStream(KrowStream):
    name = "interviews"
    path = "/calendars/{calendar_id}/interviews"
    schema = PropertiesList(
        Property("id", StringType, required=True),
        Property("created_at", DateTimeType, required=True),
        Property("organization_id", StringType),
        Property("applicant_id", StringType),
        Property("calendar_id", StringType),
        Property("time_zone", StringType),
        Property("summary", DateTimeType),
        Property("description", StringType),
        Property("starting_at", DateTimeType),
        Property("ending_at", DateTimeType),
        Property("local_starting_at", DateTimeType),
        Property("local_ending_at", DateTimeType),
        Property("abandoned_at", DateTimeType),
        Property("ending_at", DateTimeType),
        Property("state_name", StringType, required=True),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    parent_stream_type = RegionCalendarStream
    ignore_parent_replication_key = True


class LocationInterviewStream(KrowStream):
    name = "interviews"
    path = "/calendars/{calendar_id}/interviews"
    schema = PropertiesList(
        Property("id", StringType, required=True),
        Property("created_at", DateTimeType, required=True),
        Property("organization_id", StringType),
        Property("applicant_id", StringType),
        Property("calendar_id", StringType),
        Property("time_zone", StringType),
        Property("summary", DateTimeType),
        Property("description", StringType),
        Property("starting_at", DateTimeType),
        Property("ending_at", DateTimeType),
        Property("local_starting_at", DateTimeType),
        Property("local_ending_at", DateTimeType),
        Property("abandoned_at", DateTimeType),
        Property("ending_at", DateTimeType),
        Property("state_name", StringType, required=True),
        Property("updated_at", DateTimeType, required=True),
    ).to_dict()

    parent_stream_type = LocationCalendarStream
    ignore_parent_replication_key = True

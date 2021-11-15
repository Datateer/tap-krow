"""Stream type classes for tap-krow."""
from pathlib import Path
from typing import Optional

from singer_sdk.typing import (
    DateTimeType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from tap_krow.client import KrowStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class OrganizationsStream(KrowStream):
    name = "Organizations"
    path = "/organizations"
    # schema_filepath = SCHEMAS_DIR / "organizations.json"
    primary_keys = ["id"]
    schema = PropertiesList(
        Property("id", StringType, required=True),
        Property(
            "attributes",
            ObjectType(
                Property("name", StringType),
                Property("created_at", DateTimeType),
                Property("updated_at", DateTimeType, required=True),
            ),
        ),
    ).to_dict()

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for the child streams. Refer to https://sdk.meltano.com/en/latest/parent_streams.html"""
        return {"organization_id": record["id"]}


# class EmployersStream(KrowStream):
#     name = "employers"
#     # path = "/employers?employer_id=8583"
#     path = "/employers"
#     schema_filepath = SCHEMAS_DIR / "employers.json"
#     primary_keys = ["employer_id"]
#     replication_key = None

#     def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
#         """Return a context dictionary for the child streams. Refer to https://sdk.meltano.com/en/latest/parent_streams.html"""
#         return {"employer_id": record["employer_id"]}


# class CampaignsStream(KrowStream):
#     name = "campaigns"
#     path = "/campaigns"
#     # path = "/campaigns?campaign_id=95929"
#     schema_filepath = SCHEMAS_DIR / "campaigns.json"
#     primary_keys = ["campaign_id"]
#     replication_key = None

#     def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
#         return {"campaign_id": record["campaign_id"]}


# class JobStatsStream(KrowStream):
#     name = "jobstats"
#     path = "/employer/{employer_id}/job_stats"
#     schema_filepath = SCHEMAS_DIR / "jobstats.json"
#     primary_keys = ["job_id"]
#     replication_key = None
#     parent_stream_type = EmployersStream


# class JobsStream(KrowStream):
#     name = "jobs"
#     path = "/campaign/{campaign_id}/jobs"
#     schema_filepath = SCHEMAS_DIR / "jobs.json"
#     primary_keys = ["job_id"]
#     replication_key = None
#     parent_stream_type = CampaignsStream


# class PublishersStream(KrowStream):
#     name = "publishers"
#     path = "/publishers"
#     schema_filepath = SCHEMAS_DIR / "publishers.json"
#     primary_keys = ["publisher_id"]
#     replication_key = None

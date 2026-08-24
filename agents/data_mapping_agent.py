"""Legacy data-mapping and SQL-conversion extraction agent."""

from langchain_core.language_models import BaseChatModel

from agents.extraction_common import create_extraction_agent
from schemas.extraction import DataMappingReport


def create_data_mapping_agent(model: BaseChatModel):
    return create_extraction_agent(
        model,
        report_type=DataMappingReport,
        output_state_key="data_mapping",
        source_state_key="data_source_paths",
        required_reports={
            "architecture": "architecture",
            "dependencies": "dependencies",
            "business_rules": "business_rules",
        },
        specialist_prompt=(
            "You extract legacy-to-target data mappings and propose SQL conversions. "
            "Map entities, fields, types, nullability, keys, constraints, relationships, "
            "sequences, and transformations. Use stable SQL-### conversion IDs. Include "
            "validation and rollback SQL where evidence permits. Generated SQL is a "
            "review artifact only and must never be described as already executed."
        ),
    )

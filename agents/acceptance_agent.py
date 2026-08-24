"""Traceable acceptance-criteria synthesis agent."""

from langchain_core.language_models import BaseChatModel

from agents.extraction_common import create_extraction_agent
from schemas.extraction import AcceptanceCriteriaReport


def create_acceptance_agent(model: BaseChatModel):
    return create_extraction_agent(
        model,
        report_type=AcceptanceCriteriaReport,
        output_state_key="acceptance_criteria",
        source_state_key=None,
        required_reports={
            "architecture": "architecture",
            "dependencies": "dependencies",
            "business_rules": "business_rules",
            "data_mapping": "data_mapping",
            "api_events": "api_events",
            "non_functional": "non_functional",
        },
        specialist_prompt=(
            "You synthesize testable, traceable acceptance criteria in Given/When/Then "
            "form. Use stable IDs AC-### and reference only IDs present in prerequisite "
            "reports. Cover primary and alternate user journeys, business rules, API "
            "compatibility, data transformations, and non-functional verification."
        ),
    )

"""Business-rule and user-journey extraction agent."""

from langchain_core.language_models import BaseChatModel

from agents.extraction_common import create_extraction_agent
from schemas.extraction import BusinessRulesReport


def create_business_rules_agent(model: BaseChatModel):
    return create_extraction_agent(
        model,
        report_type=BusinessRulesReport,
        output_state_key="business_rules",
        source_state_key="business_source_paths",
        required_reports={"architecture": "architecture", "dependencies": "dependencies"},
        specialist_prompt=(
            "You extract business rules and end-to-end user journeys from legacy code. "
            "Find validations, calculations, conditions, permissions, state transitions, "
            "error paths, actors, triggers, and observable outcomes. Use stable IDs "
            "BR-### and UJ-###. Mark every rule explicit or inferred."
        ),
    )

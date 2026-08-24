"""Non-functional-requirements extraction agent."""

from langchain_core.language_models import BaseChatModel

from agents.extraction_common import create_extraction_agent
from schemas.extraction import NonFunctionalReport


def create_nfr_agent(model: BaseChatModel):
    return create_extraction_agent(
        model,
        report_type=NonFunctionalReport,
        output_state_key="non_functional",
        source_state_key="nfr_source_paths",
        required_reports={"architecture": "architecture", "dependencies": "dependencies"},
        specialist_prompt=(
            "You extract non-functional requirements covering security, performance, "
            "availability, resilience, scalability, observability, data integrity, "
            "privacy, deployment, and maintainability. Use stable IDs NFR-###. Mark "
            "requirements observed or inferred. Never invent numeric service levels; "
            "leave measurable_target null when repository evidence does not define one."
        ),
    )

"""API-contract and event extraction agent."""

from langchain_core.language_models import BaseChatModel

from agents.extraction_common import create_extraction_agent
from schemas.extraction import ApiEventsReport


def create_api_events_agent(model: BaseChatModel):
    return create_extraction_agent(
        model,
        report_type=ApiEventsReport,
        output_state_key="api_events",
        source_state_key="api_source_paths",
        required_reports={"architecture": "architecture", "dependencies": "dependencies"},
        specialist_prompt=(
            "You extract HTTP API contracts and asynchronous event contracts. Capture "
            "methods, routes, handlers, request/response shapes, authentication, "
            "authorization, errors, and legacy-to-target compatibility. Use stable IDs "
            "API-### and EVT-###. If repository evidence contains no messaging or domain "
            "events, return an empty events list and set no_events_found true."
        ),
    )

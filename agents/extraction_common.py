"""Shared runtime for structured requirements-extraction agents."""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from langchain_core.exceptions import OutputParserException
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, ValidationError

from agents.architecture_agent import _load_json, _read_sources
from graph.state import ModernizationState
from schemas.architecture import Evidence

MAX_MODEL_ATTEMPTS = 2


class ExtractionEvidenceError(ValueError):
    """Raised when extracted evidence is not an exact repository file."""


def _collect_evidence(value: Any) -> list[Evidence]:
    if isinstance(value, Evidence):
        return [value]
    if isinstance(value, BaseModel):
        found: list[Evidence] = []
        for field_name in type(value).model_fields:
            found.extend(_collect_evidence(getattr(value, field_name)))
        return found
    if isinstance(value, (list, tuple)):
        found = []
        for item in value:
            found.extend(_collect_evidence(item))
        return found
    if isinstance(value, dict):
        found = []
        for item in value.values():
            found.extend(_collect_evidence(item))
        return found
    return []


def validate_report_evidence(report: BaseModel, repository_root: str) -> None:
    """Require every evidence citation to resolve to one exact repository file."""

    root = Path(repository_root).resolve()
    invalid: list[str] = []
    for evidence in _collect_evidence(report):
        relative_path = evidence.source_path
        candidate = (root / relative_path).resolve()
        if (
            any(character in relative_path for character in "*?[]")
            or not candidate.is_relative_to(root)
            or not candidate.is_file()
        ):
            invalid.append(relative_path)
    if invalid:
        raise ExtractionEvidenceError(
            "Evidence must cite exact existing repository files: "
            + ", ".join(sorted(set(invalid)))
        )


def _relevant_graph(code_graph: dict[str, Any], source_paths: list[str]) -> dict:
    selected = set(source_paths)
    nodes = [
        node
        for node in code_graph.get("nodes", [])
        if isinstance(node, dict) and node.get("source_file") in selected
    ]
    node_ids = {node.get("id") for node in nodes}
    links = [
        link
        for link in code_graph.get("links", [])
        if isinstance(link, dict)
        and (link.get("source") in node_ids or link.get("target") in node_ids)
    ]
    return {
        "nodes": [
            {
                key: node.get(key)
                for key in ("id", "label", "file_type", "source_file", "metadata")
            }
            for node in nodes
        ],
        "links": [
            {
                key: link.get(key)
                for key in ("source", "target", "relation", "confidence_score")
            }
            for link in links
        ],
    }


def create_extraction_agent(
    model: BaseChatModel,
    *,
    report_type: type[BaseModel],
    output_state_key: str,
    source_state_key: str | None,
    required_reports: dict[str, str],
    specialist_prompt: str,
) -> Callable[[ModernizationState], dict[str, BaseModel]]:
    """Create a validated, retrying extraction node."""

    structured_model = model.with_structured_output(
        report_type,
        method="json_schema",
    )

    def extraction_node(state: ModernizationState) -> dict[str, BaseModel]:
        missing = [key for key in required_reports.values() if key not in state]
        if missing:
            raise ValueError(
                f"{output_state_key} requires state reports: {', '.join(missing)}"
            )

        source_paths = list(state.get(source_state_key, [])) if source_state_key else []
        sources = _read_sources(state["repository_root"], source_paths)
        code_graph = _load_json(state["code_graph_path"])
        context = {
            "repository_inventory": _load_json(state["inventory_path"]),
            "prerequisite_reports": {
                context_name: state[state_key].model_dump(mode="json")
                for context_name, state_key in required_reports.items()
            },
            "source_files": sources,
            "relevant_code_graph": _relevant_graph(code_graph, source_paths),
        }
        messages = [
            SystemMessage(
                content=(
                    specialist_prompt
                    + " Base every extracted fact on supplied repository evidence. "
                    "Distinguish explicit observations from inference, never invent "
                    "missing behavior, and record uncertainties as unresolved questions. "
                    "Use exact repository-relative file paths without wildcards. Keep "
                    "the result concise and always populate every required schema field. "
                    "Leave source_files_read empty when that field exists because the "
                    "runtime populates it."
                )
            ),
            HumanMessage(
                content="Extract the requested information from:\n"
                + json.dumps(context, ensure_ascii=False)
            ),
        ]

        last_error: Exception | None = None
        for attempt in range(MAX_MODEL_ATTEMPTS):
            try:
                report = structured_model.invoke(messages)
                if not isinstance(report, report_type):
                    report = report_type.model_validate(report)
                validate_report_evidence(report, state["repository_root"])
                break
            except (ExtractionEvidenceError, OutputParserException, ValidationError) as error:
                last_error = error
                if attempt + 1 == MAX_MODEL_ATTEMPTS:
                    raise RuntimeError(
                        f"{output_state_key} returned invalid structured output after "
                        f"{MAX_MODEL_ATTEMPTS} attempts: {error}"
                    ) from error
                messages.append(
                    HumanMessage(
                        content=(
                            "Correct the previous response and return the complete "
                            f"schema. Validation error: {error}"
                        )
                    )
                )
        else:  # pragma: no cover
            raise RuntimeError(f"{output_state_key} extraction failed") from last_error

        if hasattr(report, "source_files_read"):
            report.source_files_read = [source["path"] for source in sources]
        return {output_state_key: report}

    return extraction_node

"""Generic architecture-discovery agent for legacy repositories."""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from langchain_core.exceptions import OutputParserException
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from graph.state import ModernizationState
from schemas.architecture import ArchitectureReport

MAX_SOURCE_CHARACTERS = 12_000
MAX_MODEL_ATTEMPTS = 2


class ArchitectureEvidenceError(ValueError):
    """Raised when model evidence does not resolve to an exact repository file."""


def _load_json(path: str) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as file:
        value = json.load(file)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def _inventory_summary(inventory: dict[str, Any]) -> dict[str, Any]:
    categories = inventory.get("categories", {})
    return {
        "total_files": inventory.get("total_files"),
        "categories": {
            name: [item.get("path") for item in files]
            for name, files in categories.items()
        },
    }


def _graph_summary(code_graph: dict[str, Any]) -> dict[str, Any]:
    nodes = code_graph.get("nodes", [])
    links = code_graph.get("links", [])
    return {
        "built_at_commit": code_graph.get("built_at_commit"),
        "nodes": [
            {
                key: node.get(key)
                for key in ("id", "label", "file_type", "source_file", "community_name")
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


def _graph_files(code_graph: dict[str, Any], repository_root: str) -> list[str]:
    root = Path(repository_root).resolve()
    observed = {
        node.get("source_file")
        for node in code_graph.get("nodes", [])
        if isinstance(node, dict) and isinstance(node.get("source_file"), str)
    }
    return sorted(
        path
        for path in observed
        if path and (root / path).resolve().is_relative_to(root) and (root / path).is_file()
    )


def _read_sources(repository_root: str, source_paths: list[str]) -> list[dict[str, str]]:
    root = Path(repository_root).resolve()
    sources: list[dict[str, str]] = []

    for relative_path in source_paths:
        candidate = (root / relative_path).resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file():
            continue
        content = candidate.read_text(encoding="utf-8", errors="replace")
        sources.append(
            {"path": relative_path, "content": content[:MAX_SOURCE_CHARACTERS]}
        )

    return sources


def _report_paths(report: ArchitectureReport) -> list[str]:
    paths = [path for component in report.components for path in component.source_paths]
    paths.extend(item.source_path for item in report.entry_points)
    for dependency in report.data_stores + report.external_dependencies:
        paths.extend(item.source_path for item in dependency.evidence)
    for risk in report.risks:
        paths.extend(item.source_path for item in risk.evidence)
    return paths


def _validate_evidence_paths(
    report: ArchitectureReport, repository_root: str
) -> None:
    root = Path(repository_root).resolve()
    invalid: list[str] = []
    for relative_path in _report_paths(report):
        candidate = (root / relative_path).resolve()
        if (
            any(character in relative_path for character in "*?[]")
            or not candidate.is_relative_to(root)
            or not candidate.is_file()
        ):
            invalid.append(relative_path)
    if invalid:
        invalid_list = ", ".join(sorted(set(invalid)))
        raise ArchitectureEvidenceError(
            f"Evidence must cite exact existing repository files: {invalid_list}"
        )


def create_architecture_agent(
    model: BaseChatModel,
) -> Callable[[ModernizationState], dict[str, ArchitectureReport]]:
    """Create a LangGraph node using the model's Pydantic structured output."""

    structured_model = model.with_structured_output(
        ArchitectureReport,
        method="json_schema",
    )

    def architecture_discovery(
        state: ModernizationState,
    ) -> dict[str, ArchitectureReport]:
        inventory = _load_json(state["inventory_path"])
        code_graph = _load_json(state["code_graph_path"])
        sources = _read_sources(state["repository_root"], state["source_paths"])

        context = {
            "inventory": _inventory_summary(inventory),
            "code_graph": _graph_summary(code_graph),
            "source_files": sources,
        }
        messages = [
            SystemMessage(
                content=(
                    "You are a repository architecture discovery specialist. "
                    "Infer architecture only from the supplied evidence. Be explicit "
                    "about uncertainty, cite repository-relative paths, and do not "
                    "assume application-specific business rules. Keep the report "
                    "concise: include at most 15 components, 10 risks, and 3 evidence "
                    "items per finding. Always populate every required schema field, "
                    "including confidence. Every source_path must name one exact file "
                    "from the supplied inventory; never use wildcards or directories. "
                    "Leave source_files_read and graph_files_observed empty because "
                    "the runtime populates those provenance fields."
                )
            ),
            HumanMessage(
                content="Analyze this repository evidence:\n"
                + json.dumps(context, ensure_ascii=False)
            ),
        ]
        last_error: Exception | None = None
        for attempt in range(MAX_MODEL_ATTEMPTS):
            try:
                report = structured_model.invoke(messages)
                if not isinstance(report, ArchitectureReport):
                    report = ArchitectureReport.model_validate(report)
                _validate_evidence_paths(report, state["repository_root"])
                break
            except (ArchitectureEvidenceError, OutputParserException, ValidationError) as error:
                last_error = error
                if attempt + 1 == MAX_MODEL_ATTEMPTS:
                    raise RuntimeError(
                        "Architecture discovery returned invalid structured output "
                        f"after {MAX_MODEL_ATTEMPTS} attempts: {error}"
                    ) from error
                messages.append(
                    HumanMessage(
                        content=(
                            "Correct the previous response and return the complete "
                            f"schema. Validation error: {error}"
                        )
                    )
                )
        else:  # pragma: no cover - loop either breaks or raises
            raise RuntimeError("Architecture discovery failed") from last_error

        report.source_files_read = [source["path"] for source in sources]
        report.graph_files_observed = _graph_files(
            code_graph, state["repository_root"]
        )
        return {"architecture": report}

    return architecture_discovery

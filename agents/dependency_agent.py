"""Generic dependency-analysis agent for legacy repositories."""

import json
from collections.abc import Callable
from pathlib import Path

from langchain_core.exceptions import OutputParserException
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from agents.architecture_agent import _load_json, _read_sources
from graph.state import ModernizationState
from schemas.dependency import DependencyReport

MAX_MODEL_ATTEMPTS = 2


class DependencyEvidenceError(ValueError):
    """Raised when dependency evidence is not an exact repository file."""


def _evidence_paths(report: DependencyReport) -> list[str]:
    paths = [
        item.source_path
        for dependency in report.dependencies
        for item in dependency.evidence
    ]
    paths.extend(
        item.source_path
        for issue in report.compatibility_issues
        for item in issue.evidence
    )
    return paths


def _validate_evidence(report: DependencyReport, repository_root: str) -> None:
    root = Path(repository_root).resolve()
    invalid: list[str] = []
    for relative_path in _evidence_paths(report):
        candidate = (root / relative_path).resolve()
        if (
            any(character in relative_path for character in "*?[]")
            or not candidate.is_relative_to(root)
            or not candidate.is_file()
        ):
            invalid.append(relative_path)
    if invalid:
        raise DependencyEvidenceError(
            "Dependency evidence must cite exact existing files: "
            + ", ".join(sorted(set(invalid)))
        )


def _relevant_graph(code_graph: dict, source_paths: list[str]) -> dict:
    selected = set(source_paths)
    nodes = [
        node
        for node in code_graph.get("nodes", [])
        if node.get("source_file") in selected
    ]
    node_ids = {node.get("id") for node in nodes}
    links = [
        link
        for link in code_graph.get("links", [])
        if link.get("source") in node_ids or link.get("target") in node_ids
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


def create_dependency_agent(
    model: BaseChatModel,
) -> Callable[[ModernizationState], dict[str, DependencyReport]]:
    """Create the dependency-analysis LangGraph node."""

    structured_model = model.with_structured_output(
        DependencyReport,
        method="json_schema",
    )

    def dependency_analysis(
        state: ModernizationState,
    ) -> dict[str, DependencyReport]:
        if "architecture" not in state:
            raise ValueError("Dependency analysis requires architecture discovery")

        inventory = _load_json(state["inventory_path"])
        code_graph = _load_json(state["code_graph_path"])
        source_paths = state["dependency_source_paths"]
        sources = _read_sources(state["repository_root"], source_paths)
        context = {
            "architecture": state["architecture"].model_dump(mode="json"),
            "inventory": inventory,
            "dependency_files": sources,
            "relevant_code_graph": _relevant_graph(code_graph, source_paths),
        }
        messages = [
            SystemMessage(
                content=(
                    "You are a repository dependency-analysis specialist. Identify "
                    "framework, package, runtime, build, and external library "
                    "dependencies only from supplied evidence. Do not invent target "
                    "versions; use status 'unknown' when support status cannot be "
                    "established from repository evidence. Keep findings concise, "
                    "cite exact repository-relative files without wildcards, provide "
                    "at most 3 evidence items per finding, and always populate "
                    "confidence. Leave source_files_read empty because runtime owns it."
                )
            ),
            HumanMessage(
                content="Analyze dependency evidence:\n"
                + json.dumps(context, ensure_ascii=False)
            ),
        ]

        last_error: Exception | None = None
        for attempt in range(MAX_MODEL_ATTEMPTS):
            try:
                report = structured_model.invoke(messages)
                if not isinstance(report, DependencyReport):
                    report = DependencyReport.model_validate(report)
                _validate_evidence(report, state["repository_root"])
                break
            except (DependencyEvidenceError, OutputParserException, ValidationError) as error:
                last_error = error
                if attempt + 1 == MAX_MODEL_ATTEMPTS:
                    raise RuntimeError(
                        "Dependency analysis returned invalid structured output "
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
        else:  # pragma: no cover
            raise RuntimeError("Dependency analysis failed") from last_error

        report.source_files_read = [source["path"] for source in sources]
        return {"dependencies": report}

    return dependency_analysis

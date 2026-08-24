import json
from pathlib import Path

import pytest

from agents.extraction_common import ExtractionEvidenceError, validate_report_evidence
from graph.workflow import build_workflow
from schemas.architecture import ArchitectureReport, Evidence
from schemas.dependency import DependencyReport
from schemas.extraction import (
    AcceptanceCriteriaReport,
    ApiEventsReport,
    BusinessRulesReport,
    DataMappingReport,
    JourneyStep,
    NonFunctionalReport,
    UserJourney,
)


class _StructuredModel:
    def __init__(self, report):
        self.report = report

    def invoke(self, messages):
        return self.report.model_copy(deep=True)


class _FakeModel:
    def __init__(self, report):
        self.report = report

    def with_structured_output(self, schema, **kwargs):
        assert kwargs == {"method": "json_schema"}
        return _StructuredModel(self.report)


def test_nested_journey_evidence_is_validated(tmp_path: Path) -> None:
    report = BusinessRulesReport(
        summary="Rules",
        confidence=0.8,
        user_journeys=[
            UserJourney(
                journey_id="UJ-001",
                title="Journey",
                actor="User",
                trigger="Request",
                outcome="Done",
                steps=[
                    JourneyStep(
                        sequence=1,
                        actor_action="Act",
                        system_response="Respond",
                        evidence=[Evidence(source_path="*.cs", observation="Code")],
                    )
                ],
            )
        ],
    )

    with pytest.raises(ExtractionEvidenceError):
        validate_report_evidence(report, str(tmp_path))


def test_complete_pipeline_runs_with_structured_fake_models(tmp_path: Path) -> None:
    inventory = tmp_path / "inventory.json"
    graph = tmp_path / "graph.json"
    inventory.write_text(
        json.dumps({"total_files": 0, "categories": {}}), encoding="utf-8"
    )
    graph.write_text(json.dumps({"nodes": [], "links": []}), encoding="utf-8")

    workflow = build_workflow(
        _FakeModel(ArchitectureReport(summary="Architecture", confidence=0.9)),
        _FakeModel(DependencyReport(summary="Dependencies", confidence=0.9)),
        _FakeModel(BusinessRulesReport(summary="Rules", confidence=0.9)),
        _FakeModel(DataMappingReport(summary="Data", confidence=0.9)),
        _FakeModel(ApiEventsReport(summary="APIs", no_events_found=True, confidence=0.9)),
        _FakeModel(NonFunctionalReport(summary="NFRs", confidence=0.9)),
        _FakeModel(AcceptanceCriteriaReport(summary="Acceptance", confidence=0.9)),
    )
    result = workflow.invoke(
        {
            "repository_root": str(tmp_path),
            "inventory_path": str(inventory),
            "code_graph_path": str(graph),
            "source_paths": [],
            "dependency_source_paths": [],
            "business_source_paths": [],
            "data_source_paths": [],
            "api_source_paths": [],
            "nfr_source_paths": [],
        }
    )

    assert result["acceptance_criteria"].summary == "Acceptance"
    assert result["api_events"].no_events_found is True

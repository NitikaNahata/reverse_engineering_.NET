from graph.workflow import build_workflow
from schemas.architecture import ArchitectureReport
from schemas.dependency import DependencyReport
from schemas.extraction import (
    AcceptanceCriteriaReport,
    ApiEventsReport,
    BusinessRulesReport,
    DataMappingReport,
    NonFunctionalReport,
)


class _StructuredModel:
    def __init__(self, report):
        self.report = report

    def invoke(self, messages):
        return self.report


class _FakeModel:
    def __init__(self, report):
        self.report = report

    def with_structured_output(self, schema, **kwargs):
        return _StructuredModel(self.report)


def test_workflow_topology_is_sequential() -> None:
    workflow = build_workflow(
        _FakeModel(ArchitectureReport(summary="App", confidence=0.9)),
        _FakeModel(DependencyReport(summary="Dependencies", confidence=0.9)),
        _FakeModel(BusinessRulesReport(summary="Rules", confidence=0.9)),
        _FakeModel(DataMappingReport(summary="Data", confidence=0.9)),
        _FakeModel(
            ApiEventsReport(summary="APIs", no_events_found=True, confidence=0.9)
        ),
        _FakeModel(NonFunctionalReport(summary="NFRs", confidence=0.9)),
        _FakeModel(AcceptanceCriteriaReport(summary="Acceptance", confidence=0.9)),
    )
    graph = workflow.get_graph()

    assert list(graph.nodes) == [
        "__start__",
        "architecture_discovery",
        "dependency_analysis",
        "business_rules_extraction",
        "data_mapping_extraction",
        "api_events_extraction",
        "nfr_extraction",
        "acceptance_criteria_synthesis",
        "__end__",
    ]
    assert {(edge.source, edge.target) for edge in graph.edges} == {
        ("__start__", "architecture_discovery"),
        ("architecture_discovery", "dependency_analysis"),
        ("dependency_analysis", "business_rules_extraction"),
        ("dependency_analysis", "api_events_extraction"),
        ("dependency_analysis", "nfr_extraction"),
        ("business_rules_extraction", "data_mapping_extraction"),
        ("data_mapping_extraction", "acceptance_criteria_synthesis"),
        ("api_events_extraction", "acceptance_criteria_synthesis"),
        ("nfr_extraction", "acceptance_criteria_synthesis"),
        ("acceptance_criteria_synthesis", "__end__"),
    }

"""State shared by the modernization workflow."""

from typing import NotRequired, TypedDict

from schemas.architecture import ArchitectureReport
from schemas.dependency import DependencyReport
from schemas.extraction import (
    AcceptanceCriteriaReport,
    ApiEventsReport,
    BusinessRulesReport,
    DataMappingReport,
    NonFunctionalReport,
)


class ModernizationState(TypedDict):
    repository_root: str
    inventory_path: str
    code_graph_path: str
    source_paths: list[str]
    dependency_source_paths: list[str]
    business_source_paths: list[str]
    data_source_paths: list[str]
    api_source_paths: list[str]
    nfr_source_paths: list[str]
    architecture: NotRequired[ArchitectureReport]
    dependencies: NotRequired[DependencyReport]
    business_rules: NotRequired[BusinessRulesReport]
    data_mapping: NotRequired[DataMappingReport]
    api_events: NotRequired[ApiEventsReport]
    non_functional: NotRequired[NonFunctionalReport]
    acceptance_criteria: NotRequired[AcceptanceCriteriaReport]
    errors: NotRequired[list[str]]

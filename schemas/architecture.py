"""Structured output produced by architecture discovery."""

from typing import Literal

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """A repository location supporting an architectural observation."""

    source_path: str
    observation: str
    symbol: str | None = None


class ArchitecturalComponent(BaseModel):
    """A logical or deployable component found in the repository."""

    name: str
    kind: str
    responsibility: str
    source_paths: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class ExternalDependency(BaseModel):
    """A data store, service, framework, or other external dependency."""

    name: str
    kind: str
    evidence: list[Evidence] = Field(default_factory=list)


class ArchitectureRisk(BaseModel):
    """A modernization risk supported by repository evidence."""

    title: str
    description: str
    severity: Literal["low", "medium", "high"]
    evidence: list[Evidence] = Field(default_factory=list)


class ArchitectureReport(BaseModel):
    """Technology- and business-domain-neutral architecture assessment."""

    summary: str
    architectural_styles: list[str] = Field(default_factory=list)
    components: list[ArchitecturalComponent] = Field(default_factory=list)
    entry_points: list[Evidence] = Field(default_factory=list)
    data_stores: list[ExternalDependency] = Field(default_factory=list)
    external_dependencies: list[ExternalDependency] = Field(default_factory=list)
    cross_cutting_concerns: list[str] = Field(default_factory=list)
    risks: list[ArchitectureRisk] = Field(default_factory=list)
    source_files_read: list[str] = Field(
        default_factory=list,
        description="Exact files whose contents were supplied; populated by runtime.",
    )
    graph_files_observed: list[str] = Field(
        default_factory=list,
        description="Exact files observed in graph metadata; populated by runtime.",
    )
    confidence: float = Field(ge=0.0, le=1.0)

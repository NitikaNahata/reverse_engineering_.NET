"""Structured output produced by dependency analysis."""

from typing import Literal

from pydantic import BaseModel, Field

from schemas.architecture import Evidence


class DependencyFinding(BaseModel):
    name: str
    ecosystem: str
    current_version: str | None = None
    category: str
    status: Literal["supported", "outdated", "deprecated", "unknown"]
    usage: str
    recommendation: str
    evidence: list[Evidence] = Field(default_factory=list)


class CompatibilityIssue(BaseModel):
    title: str
    severity: Literal["low", "medium", "high"]
    description: str
    affected_dependencies: list[str] = Field(default_factory=list)
    remediation: str
    evidence: list[Evidence] = Field(default_factory=list)


class DependencyReport(BaseModel):
    summary: str
    dependencies: list[DependencyFinding] = Field(default_factory=list)
    compatibility_issues: list[CompatibilityIssue] = Field(default_factory=list)
    migration_order: list[str] = Field(default_factory=list)
    source_files_read: list[str] = Field(
        default_factory=list,
        description="Exact files whose contents were supplied; populated by runtime.",
    )
    confidence: float = Field(ge=0.0, le=1.0)

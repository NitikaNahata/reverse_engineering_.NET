"""Structured outputs for legacy requirements extraction."""

from typing import Literal

from pydantic import BaseModel, Field

from schemas.architecture import Evidence


class BusinessRule(BaseModel):
    rule_id: str
    title: str
    description: str
    category: str
    basis: Literal["explicit", "inferred"]
    conditions: list[str] = Field(default_factory=list)
    outcomes: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)


class JourneyStep(BaseModel):
    sequence: int
    actor_action: str
    system_response: str
    evidence: list[Evidence] = Field(default_factory=list)


class UserJourney(BaseModel):
    journey_id: str
    title: str
    actor: str
    trigger: str
    preconditions: list[str] = Field(default_factory=list)
    steps: list[JourneyStep] = Field(default_factory=list)
    alternate_paths: list[str] = Field(default_factory=list)
    outcome: str


class BusinessRulesReport(BaseModel):
    summary: str
    rules: list[BusinessRule] = Field(default_factory=list)
    user_journeys: list[UserJourney] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    source_files_read: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class FieldMapping(BaseModel):
    source_field: str
    target_field: str
    source_type: str | None = None
    target_type: str | None = None
    transformation: str
    nullable_change: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class EntityMapping(BaseModel):
    source_entity: str
    target_entity: str
    mapping_status: Literal["direct", "transformed", "split", "merged", "unmapped"]
    fields: list[FieldMapping] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)


class SqlConversion(BaseModel):
    conversion_id: str
    title: str
    description: str
    proposed_sql: str
    validation_sql: str
    rollback_sql: str | None = None
    execution_order: int
    manual_review_required: bool = True
    evidence: list[Evidence] = Field(default_factory=list)


class DataMappingReport(BaseModel):
    summary: str
    entity_mappings: list[EntityMapping] = Field(default_factory=list)
    sql_conversions: list[SqlConversion] = Field(default_factory=list)
    migration_order: list[str] = Field(default_factory=list)
    data_quality_risks: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    source_files_read: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class ApiContract(BaseModel):
    contract_id: str
    application: str
    method: str
    route: str
    handler: str
    request_contract: str
    response_contract: str
    authentication: str | None = None
    authorization: str | None = None
    error_behaviors: list[str] = Field(default_factory=list)
    counterpart_contract_id: str | None = None
    compatibility: Literal["equivalent", "changed", "missing", "unknown"]
    evidence: list[Evidence] = Field(default_factory=list)


class EventContract(BaseModel):
    event_id: str
    name: str
    direction: Literal["published", "consumed"]
    producer_or_consumer: str
    payload: str
    transport: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)


class ApiEventsReport(BaseModel):
    summary: str
    api_contracts: list[ApiContract] = Field(default_factory=list)
    events: list[EventContract] = Field(default_factory=list)
    no_events_found: bool
    compatibility_gaps: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    source_files_read: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class NonFunctionalRequirement(BaseModel):
    requirement_id: str
    category: Literal[
        "security",
        "performance",
        "availability",
        "resilience",
        "scalability",
        "observability",
        "data_integrity",
        "privacy",
        "deployment",
        "maintainability",
        "other",
    ]
    statement: str
    basis: Literal["observed", "inferred"]
    priority: Literal["low", "medium", "high"]
    measurable_target: str | None = None
    verification_method: str
    evidence: list[Evidence] = Field(default_factory=list)


class NonFunctionalReport(BaseModel):
    summary: str
    requirements: list[NonFunctionalRequirement] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    source_files_read: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class AcceptanceCriterion(BaseModel):
    criterion_id: str
    title: str
    given: str
    when: str
    then: str
    priority: Literal["low", "medium", "high"]
    verification_method: str
    related_rule_ids: list[str] = Field(default_factory=list)
    related_journey_ids: list[str] = Field(default_factory=list)
    related_contract_ids: list[str] = Field(default_factory=list)
    related_requirement_ids: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)


class AcceptanceCriteriaReport(BaseModel):
    summary: str
    criteria: list[AcceptanceCriterion] = Field(default_factory=list)
    coverage_gaps: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)

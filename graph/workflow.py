"""LangGraph workflow assembly."""

import os
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from dotenv import load_dotenv

from agents.architecture_agent import create_architecture_agent
from agents.acceptance_agent import create_acceptance_agent
from agents.api_events_agent import create_api_events_agent
from agents.business_rules_agent import create_business_rules_agent
from agents.data_mapping_agent import create_data_mapping_agent
from agents.dependency_agent import create_dependency_agent
from agents.nfr_agent import create_nfr_agent
from graph.state import ModernizationState


def build_architecture_workflow(model: BaseChatModel) -> CompiledStateGraph:
    """Build START -> architecture_discovery -> END."""

    builder = StateGraph(ModernizationState)
    builder.add_node("architecture_discovery", create_architecture_agent(model))
    builder.add_edge(START, "architecture_discovery")
    builder.add_edge("architecture_discovery", END)
    return builder.compile()


def build_dependency_workflow(model: BaseChatModel) -> CompiledStateGraph:
    """Build START -> dependency_analysis -> END for a saved architecture."""

    builder = StateGraph(ModernizationState)
    builder.add_node("dependency_analysis", create_dependency_agent(model))
    builder.add_edge(START, "dependency_analysis")
    builder.add_edge("dependency_analysis", END)
    return builder.compile()


def _build_single_node_workflow(name: str, node) -> CompiledStateGraph:
    builder = StateGraph(ModernizationState)
    builder.add_node(name, node)
    builder.add_edge(START, name)
    builder.add_edge(name, END)
    return builder.compile()


def build_business_workflow(model: BaseChatModel) -> CompiledStateGraph:
    return _build_single_node_workflow(
        "business_rules_extraction", create_business_rules_agent(model)
    )


def build_data_workflow(model: BaseChatModel) -> CompiledStateGraph:
    return _build_single_node_workflow(
        "data_mapping_extraction", create_data_mapping_agent(model)
    )


def build_api_workflow(model: BaseChatModel) -> CompiledStateGraph:
    return _build_single_node_workflow(
        "api_events_extraction", create_api_events_agent(model)
    )


def build_nfr_workflow(model: BaseChatModel) -> CompiledStateGraph:
    return _build_single_node_workflow(
        "nfr_extraction", create_nfr_agent(model)
    )


def build_acceptance_workflow(model: BaseChatModel) -> CompiledStateGraph:
    return _build_single_node_workflow(
        "acceptance_criteria_synthesis", create_acceptance_agent(model)
    )


def build_workflow(
    architecture_model: BaseChatModel,
    dependency_model: BaseChatModel,
    business_model: BaseChatModel,
    data_model: BaseChatModel,
    api_model: BaseChatModel,
    nfr_model: BaseChatModel,
    acceptance_model: BaseChatModel,
) -> CompiledStateGraph:
    """Build the complete seven-stage extraction pipeline."""

    builder = StateGraph(ModernizationState)
    builder.add_node(
        "architecture_discovery",
        create_architecture_agent(architecture_model),
    )
    builder.add_node("dependency_analysis", create_dependency_agent(dependency_model))
    builder.add_node(
        "business_rules_extraction", create_business_rules_agent(business_model)
    )
    builder.add_node("data_mapping_extraction", create_data_mapping_agent(data_model))
    builder.add_node("api_events_extraction", create_api_events_agent(api_model))
    builder.add_node("nfr_extraction", create_nfr_agent(nfr_model))
    builder.add_node(
        "acceptance_criteria_synthesis", create_acceptance_agent(acceptance_model)
    )
    builder.add_edge(START, "architecture_discovery")
    builder.add_edge("architecture_discovery", "dependency_analysis")
    # These three analyses depend on the same foundation reports and can run
    # concurrently because they write to distinct state fields.
    builder.add_edge("dependency_analysis", "business_rules_extraction")
    builder.add_edge("dependency_analysis", "api_events_extraction")
    builder.add_edge("dependency_analysis", "nfr_extraction")

    # Data transformations can depend on business rules, so this branch stays
    # sequential after business-rule extraction.
    builder.add_edge("business_rules_extraction", "data_mapping_extraction")

    # Acceptance synthesis requires all parallel branches to be complete.
    builder.add_edge(
        ["data_mapping_extraction", "api_events_extraction", "nfr_extraction"],
        "acceptance_criteria_synthesis",
    )
    builder.add_edge("acceptance_criteria_synthesis", END)
    return builder.compile()


def _anthropic_model(variable_name: str) -> BaseChatModel:
    from langchain_anthropic import ChatAnthropic

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    return ChatAnthropic(
        model=os.getenv(variable_name, "claude-haiku-4-5-20251001"),
        max_tokens=16_384,
    )


def build_configured_architecture_workflow() -> CompiledStateGraph:
    return build_architecture_workflow(_anthropic_model("ARCHITECTURE_MODEL"))


def build_configured_dependency_workflow() -> CompiledStateGraph:
    return build_dependency_workflow(_anthropic_model("DEPENDENCY_MODEL"))


def build_business_rules_workflow() -> CompiledStateGraph:
    return build_business_workflow(_anthropic_model("BUSINESS_RULES_MODEL"))


def build_data_mapping_workflow() -> CompiledStateGraph:
    return build_data_workflow(_anthropic_model("DATA_MAPPING_MODEL"))


def build_api_events_workflow() -> CompiledStateGraph:
    return build_api_workflow(_anthropic_model("API_EVENTS_MODEL"))


def build_non_functional_workflow() -> CompiledStateGraph:
    return build_nfr_workflow(_anthropic_model("NFR_MODEL"))


def build_acceptance_criteria_workflow() -> CompiledStateGraph:
    return build_acceptance_workflow(_anthropic_model("ACCEPTANCE_MODEL"))


def build_configured_workflow() -> CompiledStateGraph:
    """Build the complete pipeline with independently configured models."""

    architecture_model = _anthropic_model("ARCHITECTURE_MODEL")
    dependency_model = _anthropic_model("DEPENDENCY_MODEL")
    return build_workflow(
        architecture_model,
        dependency_model,
        _anthropic_model("BUSINESS_RULES_MODEL"),
        _anthropic_model("DATA_MAPPING_MODEL"),
        _anthropic_model("API_EVENTS_MODEL"),
        _anthropic_model("NFR_MODEL"),
        _anthropic_model("ACCEPTANCE_MODEL"),
    )

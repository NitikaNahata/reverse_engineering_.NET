"""Run resumable legacy-requirements extraction stages."""

import argparse
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from graph.workflow import (
    build_acceptance_criteria_workflow,
    build_api_events_workflow,
    build_business_rules_workflow,
    build_data_mapping_workflow,
    build_non_functional_workflow,
    build_configured_architecture_workflow,
    build_configured_dependency_workflow,
    build_configured_workflow,
)
from schemas.architecture import ArchitectureReport
from schemas.dependency import DependencyReport
from schemas.extraction import (
    AcceptanceCriteriaReport,
    ApiEventsReport,
    BusinessRulesReport,
    DataMappingReport,
    NonFunctionalReport,
)

DEFAULT_REPOSITORY = Path("../eShopModernizing/eShopLegacyMVCSolution")
DEFAULT_INVENTORY = Path("outputs/repo_inventory.json")
DEFAULT_GRAPH = Path("../eShopModernizing/eShopLegacyMVCSolution/graphify-out/graph.json")
DEFAULT_OUTPUTS = {
    "architecture": Path("outputs/architecture_report.json"),
    "dependencies": Path("outputs/dependency_report.json"),
    "business_rules": Path("outputs/business_rules_report.json"),
    "data_mapping": Path("outputs/data_mapping_report.json"),
    "api_events": Path("outputs/api_events_report.json"),
    "non_functional": Path("outputs/non_functional_report.json"),
    "acceptance_criteria": Path("outputs/acceptance_criteria_report.json"),
}
REPORT_TYPES: dict[str, type[BaseModel]] = {
    "architecture": ArchitectureReport,
    "dependencies": DependencyReport,
    "business_rules": BusinessRulesReport,
    "data_mapping": DataMappingReport,
    "api_events": ApiEventsReport,
    "non_functional": NonFunctionalReport,
    "acceptance_criteria": AcceptanceCriteriaReport,
}
STAGES = (
    "architecture",
    "dependency",
    "business",
    "data",
    "api",
    "nfr",
    "acceptance",
    "all",
)
STAGE_OUTPUT_KEYS = {
    "architecture": ("architecture",),
    "dependency": ("dependencies",),
    "business": ("business_rules",),
    "data": ("data_mapping",),
    "api": ("api_events",),
    "nfr": ("non_functional",),
    "acceptance": ("acceptance_criteria",),
    "all": tuple(DEFAULT_OUTPUTS),
}


def _load_inventory(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        inventory = json.load(file)
    if not isinstance(inventory, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return inventory


def _load_report(state_key: str, path: Path) -> BaseModel:
    if not path.is_file():
        raise FileNotFoundError(f"Required report not found: {path}. Run its stage first.")
    return REPORT_TYPES[state_key].model_validate_json(path.read_text(encoding="utf-8"))


def _write_report(report: BaseModel, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Report written to {path.resolve()}")


def select_category_paths(
    inventory: dict[str, Any], categories: tuple[str, ...], max_files: int
) -> list[str]:
    """Select deterministic, category-prioritized repository files."""

    inventory_categories = inventory.get("categories", {})
    paths: list[str] = []
    for category in categories:
        category_paths = sorted(
            item["path"]
            for item in inventory_categories.get(category, [])
            if item.get("path")
        )
        paths.extend(path for path in category_paths if path not in paths)
    return paths[:max_files]


def select_source_paths(inventory: dict[str, Any], max_files: int = 20) -> list[str]:
    return select_category_paths(
        inventory,
        ("project_files", "configuration", "controllers", "services", "models"),
        max_files,
    )


def select_dependency_paths(inventory: dict[str, Any]) -> list[str]:
    return select_category_paths(
        inventory, ("project_files", "configuration"), max_files=50
    )


def _base_state(args: argparse.Namespace, inventory: dict[str, Any]) -> dict[str, Any]:
    return {
        "repository_root": str(args.repository),
        "inventory_path": str(args.inventory),
        "code_graph_path": str(args.graph),
        "source_paths": select_source_paths(inventory, args.max_source_files),
        "dependency_source_paths": select_dependency_paths(inventory),
        "business_source_paths": select_category_paths(
            inventory,
            ("controllers", "services", "models", "views", "configuration"),
            args.max_specialist_files,
        ),
        "data_source_paths": select_category_paths(
            inventory,
            ("sql", "models", "configuration", "project_files"),
            args.max_specialist_files,
        ),
        "api_source_paths": select_category_paths(
            inventory,
            ("controllers", "services", "models", "configuration"),
            args.max_specialist_files,
        ),
        "nfr_source_paths": select_category_paths(
            inventory,
            ("configuration", "project_files", "services", "controllers", "other"),
            args.max_specialist_files,
        ),
    }


def _load_prerequisites(
    state: dict[str, Any], keys: tuple[str, ...], outputs: dict[str, Path]
) -> None:
    for key in keys:
        state[key] = _load_report(key, outputs[key])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=DEFAULT_REPOSITORY)
    parser.add_argument("--stage", choices=STAGES, default="all")
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    parser.add_argument("--max-source-files", type=int, default=20)
    parser.add_argument("--max-specialist-files", type=int, default=40)
    for key, default in DEFAULT_OUTPUTS.items():
        parser.add_argument(
            f"--{key.replace('_', '-')}-output",
            dest=f"{key}_output",
            type=Path,
            default=default,
        )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inventory = _load_inventory(args.inventory)
    state = _base_state(args, inventory)
    outputs = {key: getattr(args, f"{key}_output") for key in DEFAULT_OUTPUTS}
    print(f"Running stage '{args.stage}' on {args.repository.resolve()}")

    if args.stage == "architecture":
        result = build_configured_architecture_workflow().invoke(state)
    elif args.stage == "dependency":
        _load_prerequisites(state, ("architecture",), outputs)
        result = build_configured_dependency_workflow().invoke(state)
    elif args.stage == "business":
        _load_prerequisites(state, ("architecture", "dependencies"), outputs)
        result = build_business_rules_workflow().invoke(state)
    elif args.stage == "data":
        _load_prerequisites(
            state, ("architecture", "dependencies", "business_rules"), outputs
        )
        result = build_data_mapping_workflow().invoke(state)
    elif args.stage == "api":
        _load_prerequisites(state, ("architecture", "dependencies"), outputs)
        result = build_api_events_workflow().invoke(state)
    elif args.stage == "nfr":
        _load_prerequisites(state, ("architecture", "dependencies"), outputs)
        result = build_non_functional_workflow().invoke(state)
    elif args.stage == "acceptance":
        _load_prerequisites(
            state,
            (
                "architecture",
                "dependencies",
                "business_rules",
                "data_mapping",
                "api_events",
                "non_functional",
            ),
            outputs,
        )
        result = build_acceptance_criteria_workflow().invoke(state)
    else:
        result = build_configured_workflow().invoke(state)

    for state_key in STAGE_OUTPUT_KEYS[args.stage]:
        _write_report(result[state_key], outputs[state_key])


if __name__ == "__main__":
    main()

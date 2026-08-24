"""Render extraction JSON artifacts as one human-readable Markdown report."""

import argparse
import json
from pathlib import Path
from typing import Any

REPORT_FILES = {
    "architecture": "architecture_report.json",
    "dependencies": "dependency_report.json",
    "business": "business_rules_report.json",
    "data": "data_mapping_report.json",
    "api": "api_events_report.json",
    "nfr": "non_functional_report.json",
    "acceptance": "acceptance_criteria_report.json",
}


def _load_reports(outputs_dir: Path) -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    missing: list[Path] = []
    for name, filename in REPORT_FILES.items():
        path = outputs_dir / filename
        if not path.is_file():
            missing.append(path)
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(f"Expected a JSON object in {path}")
        reports[name] = value
    if missing:
        names = "\n".join(f"- {path}" for path in missing)
        raise FileNotFoundError(f"Required reports are missing:\n{names}")
    return reports


def _text(value: Any) -> str:
    if value is None or value == "":
        return "Not specified"
    return str(value).replace("|", "\\|").replace("\n", " ")


def _items(values: list[Any]) -> str:
    return ", ".join(_text(value) for value in values) if values else "None identified"


def _evidence(items: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for item in items:
        symbol = f" (`{item['symbol']}`)" if item.get("symbol") else ""
        lines.append(
            f"  - `{item.get('source_path', 'unknown')}`{symbol}: "
            f"{item.get('observation', 'No observation')}"
        )
    return lines


def _dashboard(reports: dict[str, dict[str, Any]]) -> list[str]:
    business = reports["business"]
    data = reports["data"]
    api = reports["api"]
    nfr = reports["nfr"]
    acceptance = reports["acceptance"]
    entity_mappings = data.get("entity_mappings", [])
    unresolved = sum(
        len(report.get("unresolved_questions", [])) for report in reports.values()
    )
    counts = (
        ("Business rules", len(business.get("rules", []))),
        ("User journeys", len(business.get("user_journeys", []))),
        ("Entity mappings", len(entity_mappings)),
        ("Field mappings", sum(len(item.get("fields", [])) for item in entity_mappings)),
        ("SQL conversions", len(data.get("sql_conversions", []))),
        ("API contracts", len(api.get("api_contracts", []))),
        ("Events", len(api.get("events", []))),
        ("Non-functional requirements", len(nfr.get("requirements", []))),
        ("Acceptance criteria", len(acceptance.get("criteria", []))),
        ("Unresolved questions", unresolved),
    )
    lines = [
        "## Extraction dashboard",
        "",
        "| Artifact | Extracted |",
        "|---|---:|",
    ]
    lines.extend(f"| {name} | {count} |" for name, count in counts)
    lines += ["", "### Confidence", "", "| Report | Confidence |", "|---|---:|"]
    confidence_names = (
        ("Architecture", "architecture"),
        ("Dependencies", "dependencies"),
        ("Business rules", "business"),
        ("Data mapping", "data"),
        ("API and events", "api"),
        ("Non-functional", "nfr"),
        ("Acceptance criteria", "acceptance"),
    )
    lines.extend(
        f"| {name} | {reports[key].get('confidence', 'unknown')} |"
        for name, key in confidence_names
    )
    lines.append("")
    return lines


def _architecture(report: dict[str, Any]) -> list[str]:
    lines = ["## 1. System overview", "", report["summary"], ""]
    lines += ["### Architectural styles", ""]
    lines += [f"- {item}" for item in report.get("architectural_styles", [])]
    lines += ["", "### Major components", "", "| Component | Type | Responsibility |", "|---|---|---|"]
    for item in report.get("components", []):
        lines.append(
            f"| {_text(item['name'])} | {_text(item['kind'])} | "
            f"{_text(item['responsibility'])} |"
        )
    lines += ["", f"**Confidence:** {report.get('confidence', 'unknown')}", ""]
    return lines


def _dependencies(report: dict[str, Any]) -> list[str]:
    lines = ["## 2. Dependencies", "", report["summary"], ""]
    lines += ["| Dependency | Ecosystem | Version | Status | Recommendation |", "|---|---|---|---|---|"]
    for item in report.get("dependencies", []):
        lines.append(
            f"| {_text(item['name'])} | {_text(item['ecosystem'])} | "
            f"{_text(item.get('current_version'))} | {_text(item['status'])} | "
            f"{_text(item['recommendation'])} |"
        )
    if report.get("compatibility_issues"):
        lines += ["", "### Compatibility issues", ""]
        for item in report["compatibility_issues"]:
            lines += [
                f"#### {item['title']} ({item['severity']})",
                "",
                item["description"],
                "",
                f"**Remediation:** {item['remediation']}",
                "",
            ]
    return lines


def _business(report: dict[str, Any]) -> list[str]:
    lines = ["## 3. Business rules and user journeys", "", report["summary"], ""]
    lines += ["### Business rules", ""]
    for rule in report.get("rules", []):
        lines += [
            f"#### {rule['rule_id']}: {rule['title']}",
            "",
            rule["description"],
            "",
            f"- **Basis:** {rule['basis']}",
            f"- **Category:** {rule['category']}",
            f"- **Conditions:** {_items(rule.get('conditions', []))}",
            f"- **Outcomes:** {_items(rule.get('outcomes', []))}",
            "- **Evidence:**",
        ]
        lines += _evidence(rule.get("evidence", [])) or ["  - None supplied"]
        lines.append("")
    lines += ["### User journeys", ""]
    for journey in report.get("user_journeys", []):
        lines += [
            f"#### {journey['journey_id']}: {journey['title']}",
            "",
            f"- **Actor:** {journey['actor']}",
            f"- **Trigger:** {journey['trigger']}",
            f"- **Preconditions:** {_items(journey.get('preconditions', []))}",
            "",
        ]
        for step in journey.get("steps", []):
            lines += [
                f"{step['sequence']}. **User:** {step['actor_action']}",
                f"   **System:** {step['system_response']}",
            ]
        lines += [
            "",
            f"**Alternate paths:** {_items(journey.get('alternate_paths', []))}",
            "",
            f"**Outcome:** {journey['outcome']}",
            "",
        ]
    return lines


def _data(report: dict[str, Any]) -> list[str]:
    lines = ["## 4. Legacy data mapping and SQL conversions", "", report["summary"], ""]
    for mapping in report.get("entity_mappings", []):
        lines += [
            f"### {mapping['source_entity']} → {mapping['target_entity']}",
            "",
            f"**Mapping:** {mapping['mapping_status']}",
            "",
            "| Source field | Target field | Source type | Target type | Transformation |",
            "|---|---|---|---|---|",
        ]
        for field in mapping.get("fields", []):
            lines.append(
                f"| {_text(field['source_field'])} | {_text(field['target_field'])} | "
                f"{_text(field.get('source_type'))} | {_text(field.get('target_type'))} | "
                f"{_text(field['transformation'])} |"
            )
        lines.append("")
    for conversion in report.get("sql_conversions", []):
        lines += [
            f"### {conversion['conversion_id']}: {conversion['title']}",
            "",
            conversion["description"],
            "",
            "> Review only—this SQL has not been executed.",
            "",
            "```sql",
            conversion["proposed_sql"],
            "```",
            "",
            "**Validation SQL**",
            "",
            "```sql",
            conversion["validation_sql"],
            "```",
            "",
        ]
        if conversion.get("rollback_sql"):
            lines += ["**Rollback SQL**", "", "```sql", conversion["rollback_sql"], "```", ""]
    return lines


def _api(report: dict[str, Any]) -> list[str]:
    lines = ["## 5. API contracts and events", "", report["summary"], ""]
    lines += ["| ID | Application | Method | Route | Compatibility |", "|---|---|---|---|---|"]
    for item in report.get("api_contracts", []):
        lines.append(
            f"| {_text(item['contract_id'])} | {_text(item['application'])} | "
            f"{_text(item['method'])} | `{_text(item['route'])}` | "
            f"{_text(item['compatibility'])} |"
        )
    lines += ["", "### Events", ""]
    if report.get("no_events_found"):
        lines.append("No repository evidence of published or consumed events was found.")
    else:
        for event in report.get("events", []):
            lines.append(
                f"- **{event['event_id']} — {event['name']}**: "
                f"{event['direction']} by {event['producer_or_consumer']}"
            )
    lines.append("")
    return lines


def _nfr(report: dict[str, Any]) -> list[str]:
    lines = ["## 6. Non-functional requirements", "", report["summary"], ""]
    lines += ["| ID | Category | Requirement | Basis | Priority | Verification |", "|---|---|---|---|---|---|"]
    for item in report.get("requirements", []):
        lines.append(
            f"| {_text(item['requirement_id'])} | {_text(item['category'])} | "
            f"{_text(item['statement'])} | {_text(item['basis'])} | "
            f"{_text(item['priority'])} | {_text(item['verification_method'])} |"
        )
    lines.append("")
    return lines


def _acceptance(report: dict[str, Any]) -> list[str]:
    lines = ["## 7. Acceptance criteria", "", report["summary"], ""]
    for item in report.get("criteria", []):
        lines += [
            f"### {item['criterion_id']}: {item['title']}",
            "",
            f"- **Given** {item['given']}",
            f"- **When** {item['when']}",
            f"- **Then** {item['then']}",
            f"- **Priority:** {item['priority']}",
            f"- **Verification:** {item['verification_method']}",
            f"- **Related rules:** {_items(item.get('related_rule_ids', []))}",
            f"- **Related journeys:** {_items(item.get('related_journey_ids', []))}",
            f"- **Related APIs:** {_items(item.get('related_contract_ids', []))}",
            f"- **Related NFRs:** {_items(item.get('related_requirement_ids', []))}",
            "",
        ]
    return lines


def render(reports: dict[str, dict[str, Any]]) -> str:
    lines = [
        "# Legacy application requirements report",
        "",
        "> Generated deterministically from validated extraction artifacts. "
        "Inferred findings still require human review.",
        "",
    ]
    lines += _dashboard(reports)
    lines += _architecture(reports["architecture"])
    lines += _dependencies(reports["dependencies"])
    lines += _business(reports["business"])
    lines += _data(reports["data"])
    lines += _api(reports["api"])
    lines += _nfr(reports["nfr"])
    lines += _acceptance(reports["acceptance"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs-dir", type=Path, default=Path("outputs"))
    parser.add_argument(
        "--output", type=Path, default=Path("outputs/requirements_report.md")
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(_load_reports(args.outputs_dir)), encoding="utf-8")
    print(f"Requirements report written to {args.output.resolve()}")


if __name__ == "__main__":
    main()

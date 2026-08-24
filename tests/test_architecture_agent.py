import json
from pathlib import Path

from agents.architecture_agent import create_architecture_agent
from schemas.architecture import ArchitecturalComponent, ArchitectureReport


class _RetryingStructuredModel:
    def __init__(self) -> None:
        self.calls = 0

    def invoke(self, messages):
        self.calls += 1
        source_path = "*.cs" if self.calls == 1 else "Program.cs"
        return ArchitectureReport(
            summary="Example",
            confidence=0.8,
            components=[
                ArchitecturalComponent(
                    name="App",
                    kind="application",
                    responsibility="Runs",
                    source_paths=[source_path],
                )
            ],
        )


class _FakeModel:
    def __init__(self) -> None:
        self.structured = _RetryingStructuredModel()

    def with_structured_output(self, schema, **kwargs):
        assert kwargs == {"method": "json_schema"}
        return self.structured


def test_agent_retries_invalid_evidence_and_sets_provenance(tmp_path: Path) -> None:
    source = tmp_path / "Program.cs"
    source.write_text("class Program {}", encoding="utf-8")
    inventory = tmp_path / "inventory.json"
    inventory.write_text(
        json.dumps({"total_files": 1, "categories": {}}), encoding="utf-8"
    )
    graph = tmp_path / "graph.json"
    graph.write_text(
        json.dumps(
            {
                "nodes": [{"id": "Program", "source_file": "Program.cs"}],
                "links": [],
            }
        ),
        encoding="utf-8",
    )
    model = _FakeModel()
    agent = create_architecture_agent(model)

    result = agent(
        {
            "repository_root": str(tmp_path),
            "inventory_path": str(inventory),
            "code_graph_path": str(graph),
            "source_paths": ["Program.cs"],
        }
    )

    assert model.structured.calls == 2
    assert result["architecture"].source_files_read == ["Program.cs"]
    assert result["architecture"].graph_files_observed == ["Program.cs"]

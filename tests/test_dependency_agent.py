import json
from pathlib import Path

from agents.dependency_agent import create_dependency_agent
from schemas.architecture import ArchitectureReport, Evidence
from schemas.dependency import DependencyFinding, DependencyReport


class _RetryingDependencyModel:
    def __init__(self) -> None:
        self.calls = 0

    def invoke(self, messages):
        self.calls += 1
        source_path = "*.csproj" if self.calls == 1 else "App.csproj"
        return DependencyReport(
            summary="Example dependencies",
            confidence=0.8,
            dependencies=[
                DependencyFinding(
                    name="Example.Package",
                    ecosystem="NuGet",
                    category="library",
                    status="unknown",
                    usage="Example usage",
                    recommendation="Verify compatibility",
                    evidence=[
                        Evidence(source_path=source_path, observation="Declared")
                    ],
                )
            ],
        )


class _FakeModel:
    def __init__(self) -> None:
        self.structured = _RetryingDependencyModel()

    def with_structured_output(self, schema, **kwargs):
        assert kwargs == {"method": "json_schema"}
        return self.structured


def test_dependency_agent_retries_and_sets_provenance(tmp_path: Path) -> None:
    project = tmp_path / "App.csproj"
    project.write_text("<Project />", encoding="utf-8")
    inventory = tmp_path / "inventory.json"
    inventory.write_text(
        json.dumps({"total_files": 1, "categories": {}}), encoding="utf-8"
    )
    graph = tmp_path / "graph.json"
    graph.write_text(json.dumps({"nodes": [], "links": []}), encoding="utf-8")
    model = _FakeModel()
    agent = create_dependency_agent(model)

    result = agent(
        {
            "repository_root": str(tmp_path),
            "inventory_path": str(inventory),
            "code_graph_path": str(graph),
            "source_paths": [],
            "dependency_source_paths": ["App.csproj"],
            "architecture": ArchitectureReport(summary="App", confidence=0.9),
        }
    )

    assert model.structured.calls == 2
    assert result["dependencies"].source_files_read == ["App.csproj"]

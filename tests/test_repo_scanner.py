from pathlib import Path

import pytest

from agents.architecture_agent import (
    ArchitectureEvidenceError,
    _validate_evidence_paths,
)
from schemas.architecture import ArchitecturalComponent, ArchitectureReport


def test_architecture_report_provenance_is_runtime_owned() -> None:
    report = ArchitectureReport(summary="Example", confidence=0.8)

    assert report.source_files_read == []
    assert report.graph_files_observed == []


def test_evidence_paths_must_be_exact_files(tmp_path: Path) -> None:
    source = tmp_path / "Program.cs"
    source.write_text("class Program {}", encoding="utf-8")
    report = ArchitectureReport(
        summary="Example",
        confidence=0.8,
        components=[
            ArchitecturalComponent(
                name="App",
                kind="application",
                responsibility="Runs",
                source_paths=["*.cs"],
            )
        ],
    )

    with pytest.raises(ArchitectureEvidenceError, match="exact existing"):
        _validate_evidence_paths(report, str(tmp_path))

    report.components[0].source_paths = ["Program.cs"]
    _validate_evidence_paths(report, str(tmp_path))

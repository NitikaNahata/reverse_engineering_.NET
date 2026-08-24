from pathlib import Path

# File types relevant to a legacy .NET application
RELEVANT_EXTENSIONS = {
    ".cs",
    ".csproj",
    ".sln",
    ".config",
    ".json",
    ".xml",
    ".sql",
    ".cshtml",
    ".aspx",
}

# Folders we don't want to analyze
IGNORE_DIRS = {
    ".git",
    "bin",
    "obj",
    "packages",
    "node_modules",
    ".vs",
    "graphify-out",
}


def classify_file(path: Path) -> str:
    """Classify a legacy file based on its path and extension."""

    path_lower = str(path).lower()

    if path.suffix == ".sln" or path.suffix == ".csproj":
        return "project_files"

    if path.suffix == ".sql":
        return "sql"

    if path.suffix in {".config", ".json", ".xml"}:
        return "configuration"

    if path.suffix in {".cshtml", ".aspx"}:
        return "views"

    if "controller" in path_lower:
        return "controllers"

    if "service" in path_lower:
        return "services"

    if "repository" in path_lower:
        return "repositories"

    if "model" in path_lower:
        return "models"

    if "test" in path_lower:
        return "tests"

    return "other"


def scan_repository(repo_path: str) -> dict:
    """Scan a legacy .NET repository and create an inventory."""

    repo = Path(repo_path).resolve()

    if not repo.exists():
        raise FileNotFoundError(f"Repository not found: {repo}")

    inventory = {
        "repository": str(Path(repo_path)),
        "total_files": 0,
        "categories": {}
    }

    for path in sorted(repo.rglob("*")):

        if not path.is_file():
            continue

        # Skip generated/ignored directories
        if any(part.lower() in IGNORE_DIRS for part in path.parts):
            continue

        if path.suffix.lower() not in RELEVANT_EXTENSIONS:
            continue

        category = classify_file(path)

        inventory["categories"].setdefault(category, [])

        inventory["categories"][category].append(
            {
                "path": str(path.relative_to(repo)),
                "extension": path.suffix.lower(),
                "size_bytes": path.stat().st_size,
            }
        )

        inventory["total_files"] += 1

    return inventory

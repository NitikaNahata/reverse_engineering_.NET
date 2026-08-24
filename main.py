import json
from pathlib import Path

from scanners.repo_scanner import scan_repository


# Legacy .NET repository is the sibling folder

LEGACY_REPO = "../eShopModernizing/eShopLegacyMVCSolution"

OUTPUT_FILE = Path("outputs/repo_inventory.json")


def main():
    print("Scanning legacy .NET repository...")

    inventory = scan_repository(LEGACY_REPO)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(inventory, file, indent=2)

    print(f"Scan complete.")
    print(f"Files discovered: {inventory['total_files']}")
    print(f"Inventory written to: {OUTPUT_FILE}")

    print("\nCategories:")

    for category, files in inventory["categories"].items():
        print(f"  {category}: {len(files)}")


if __name__ == "__main__":
    main()
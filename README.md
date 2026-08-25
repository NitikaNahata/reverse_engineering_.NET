# Legacy .NET Requirements Extraction

This project analyzes a legacy .NET repository and extracts architecture, dependencies, business rules, user journeys, data mappings, proposed SQL conversions, API contracts, events, non-functional requirements, and acceptance criteria.

The pipeline uses deterministic repository inventory and Graphify evidence as inputs. LangGraph coordinates independently runnable extraction stages. Each model response is validated with Pydantic and must cite exact repository files.

## Architecture

```text
Legacy .NET repository
        │
        ├── deterministic repository scanner
        │       └── outputs/repo_inventory.json
        │
        └── Graphify
                └── graphify-out/graph.json
                         │
                         ▼
              Architecture Discovery
                         │
                         ▼
                Dependency Analysis
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
     Business Rules  API & Events   NFRs
             │           │           │
             ▼           │           │
       Data Mapping      │           │
             └───────────┴───────────┘
                         │
                         ▼
                Acceptance Criteria
                         │
                         ▼
              outputs/requirements_report.md
```

In a complete run, Business Rules, API & Events, and NFR extraction execute in
parallel after Dependency Analysis. Data Mapping follows Business Rules, and
Acceptance Criteria waits for all three branches. Every stage can also load
saved prerequisite reports and run independently. Running one stage does not
rerun its prerequisites.

## Project structure

```text
agents/                  LangGraph extraction nodes and shared validation
graph/state.py           Typed workflow state
graph/workflow.py        Full and single-stage graph builders
schemas/                 Pydantic structured-output models
scanners/repo_scanner.py Deterministic repository inventory scanner
tests/                   Unit and fake-model workflow tests
main.py                  Repository scanner entry point
run_pipeline.py          Requirements-extraction CLI
render_requirements.py   JSON-to-Markdown report renderer
outputs/                 Generated artifacts (git-ignored)
```

## Safety and evidence rules

- Agents are generic and contain no eShop-specific business rules.
- Evidence must cite an exact repository-relative file; wildcards and paths outside the repository are rejected.
- Inferred findings are marked separately from explicit or observed behavior.
- Invalid structured output receives at most one corrective retry.
- Proposed SQL is a review artifact only. The pipeline never connects to or changes a database.
- Generated reports and `.env` are excluded from Git.

## Prerequisites

- Python 3.11 or newer
- An Anthropic API key
- A repository inventory JSON file
- A Graphify `graph.json`

The included defaults expect this sibling layout:

```text
parent-directory/
├── ai-modernization/
└── eShopModernizing/
    └── eShopLegacyMVCSolution/
```

All paths can be overridden through command-line arguments.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add a newly created Anthropic key to `.env`:

```dotenv
ANTHROPIC_API_KEY=your-key
```

The default model is the lower-cost Claude Haiku 4.5. Each stage has an independent model variable, so one difficult stage can be promoted without changing the others.

## Generate repository inventory

From the project directory:

```bash
python main.py
```

This creates `outputs/repo_inventory.json` using the repository path configured in `main.py`.

## Run extraction stages independently

If Architecture and Dependency reports already exist, begin with Business Rules:

```bash
python run_pipeline.py --stage business
python run_pipeline.py --stage data
python run_pipeline.py --stage api
python run_pipeline.py --stage nfr
python run_pipeline.py --stage acceptance
```

Available stages:

| Stage | Output | Required saved reports |
|---|---|---|
| `architecture` | `architecture_report.json` | None |
| `dependency` | `dependency_report.json` | Architecture |
| `business` | `business_rules_report.json` | Architecture, Dependency |
| `data` | `data_mapping_report.json` | Architecture, Dependency, Business |
| `api` | `api_events_report.json` | Architecture, Dependency |
| `nfr` | `non_functional_report.json` | Architecture, Dependency |
| `acceptance` | `acceptance_criteria_report.json` | All preceding extraction reports |

For example:

```bash
python run_pipeline.py --stage api
```

This loads Architecture and Dependency from disk, makes one API-agent request, and writes only `outputs/api_events_report.json`.

## Run the complete pipeline

```bash
python run_pipeline.py --stage all
```

This runs all seven model stages from scratch. The independent middle branches
run concurrently to reduce elapsed time. Each stage is still a billable model
request, and a failed validation may cause one corrective retry.

## Use another repository

```bash
python run_pipeline.py \
  --stage all \
  --repository /absolute/path/to/legacy-repository \
  --inventory /absolute/path/to/repo_inventory.json \
  --graph /absolute/path/to/graph.json
```

## Generate the readable report

After all seven JSON reports exist:

```bash
python render_requirements.py
```

Open:

```text
outputs/requirements_report.md
```

The Markdown report combines the validated artifacts without another model call.
It begins with an extraction dashboard showing counts and confidence scores for
business rules, user journeys, mappings, SQL conversions, APIs, events, NFRs,
acceptance criteria, and unresolved questions.

## Run tests

```bash
PYTHONPATH=. python -m pytest -q
```

Tests use fake models, so they verify schemas, evidence validation, retries, stage ordering, and state handoffs without making billable API calls.

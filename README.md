# Project IM — FMCG Production & Supply Planning Simulator

Simulator for FMCG production and supply planning: demand forecasting, capacity,
inventory (safety stock, reorder point) and MRP, built in Python with synthetic,
fictional data. Work in progress.

## 1. Purpose

This is an **educational** simulator. It demonstrates how the core planning
techniques of consumer-goods manufacturing fit together — weekly demand
forecasting with promotional uplift, machine-capacity utilization (including
changeover time), inventory policies (safety stock, reorder point), and
material requirements planning (MRP) — on a small, self-generated dataset.

Every company, product, material, and supplier that appears in the sample data
is **fictional**, generated deterministically by a committed script. No real
company's operational data is used, ingested, or referenced anywhere in this
repository.

## 2. Scope and Status

| Milestone | Content | Status |
|---|---|---|
| Phase 0 | Project scaffold: packaging, tooling, CI, docs | **Completed** |
| Phase 1 | Data foundation: synthetic dataset generator, validation, inventory engine, capacity engine | Not yet implemented |
| Milestone 2 (planned) | Streamlit application, scenario overlays, audit/export features | Not started |

Phase 0 provides the repository skeleton only. The planning engine
(`src/fmcg_planner`) is deliberately near-empty at this stage: demand
generation, capacity computation, inventory policies, and data validation all
belong to Phase 1 and later milestones.

## 3. Planned Features (across the approved milestones)

- **Synthetic data foundation** — a deterministic generator (fixed RNG stream)
  producing a brands table, a production-lines table, weekly demand history/
  planning periods, a bills of materials, raw-material suppliers, and monthly
  snapshots, all committed as canonical CSVs.
- **Forecasting** — training/planning frame separation with explicit
  leak-prevention rules (planning weeks may never enter a training fit).
- **Capacity** — per-line weekly hours required vs. available, including
  changeover allowances, with utilization and overload detection.
- **Inventory** — safety stock and reorder-point policies, weekly balance
  accounting where fulfilled + shortage = demand and closing stock never goes
  negative (lost-demand semantics).
- **MRP** — explode bills of materials down to raw-material requirements,
  offset by supplier lead times.
- **Streamlit front end** (Milestone 2) — scenario selection, snapshot views,
  and CSV export; runs locally only.

## 4. Technology Stack

| Component | Choice |
|---|---|
| Language | Python ≥ 3.13 (CI-tested on 3.13 and 3.14) |
| Package manager | `uv` (CLI pinned to **0.13.6** in CI) |
| Build backend | `uv_build` (PEP 517 + PEP 517-editable via `src/` layout) |
| Runtime dependencies | `pandas`, `numpy` (Streamlit/Plotly/OpenPyXL join in Milestone 2) |
| Test / QA | `pytest`, `pytest-cov` (80% coverage gate), `ruff`, `mypy` |
| CI | GitHub Actions, 2×2 matrix (Ubuntu/Windows × Python 3.13/3.14) |
| License | MIT |

## 5. Architecture Overview

The project enforces a strict engine/UI layering:

```
src/fmcg_planner/     ← planning engine: pure, typed, UI-agnostic
tests/                ← unit tests (engine packages never import Streamlit)
app/                  ← (Milestone 2) Streamlit front end; contains no logic rules
scripts/              ← (Phase 1) sample-data generator entry point
```

- The engine package returns plain typed frames; the future Streamlit layer
  only renders and orchestrates them. A structural guard test verifies that
  no engine module imports Streamlit (checked via AST, not text search).
- Data snapshots are treated as units: each sample Data snapshot is
  identified by an explicit `snapshot_date`, and engineering documentation
  distinguishes *expected* (noiseless) values from the *realized* seeded
  values, with conformance tests for both.

## 6. Repository Structure

```
.
├── .github/
│   ├── dependabot.yml        # weekly "uv" + "github-actions" updates
│   └── workflows/ci.yml      # 2×2 matrix CI workflow
├── data/                     # (Phase 1) canonical synthetic CSVs live here
├── docs/                     # (Phase 1) data dictionary + methodology
├── scripts/                  # (Phase 1) generator entry point
├── src/
│   └── fmcg_planner/
│       ├── __init__.py       # engine package (v0.1.0 skeleton)
│       └── py.typed          # PEP 561 marker
├── tests/
│   └── unit/test_package.py  # Phase 0 package guards
├── .env.example              # placeholder: the project uses no env vars
├── .gitignore                # secrets/venv/build/data-generation exclusions
├── .python-version           # 3.14 (local development)
├── LICENSE                   # MIT
├── README.md
├── pyproject.toml            # build, lint, type-check, test configuration
└── uv.lock                   # (generated) reproducible dependency lock — via uv only
```

## 7. System Requirements

- **Python 3.13 and 3.14 are both supported** (CI runs both; Windows and
  Ubuntu).
- **Local development** targets the interpreter named in `.python-version`
  (currently **3.14**).
- **uv CLI pinned to 0.13.6** for local development and in CI. Using a
  different uv version risks lockfile deltas, since the lockfile format and
  resolver evolve with uv itself. Check with `uv --version`.
- No operating system beyond what Python supports; no environment variables
  or network credentials are needed for local development (see
  `.env.example`).

## 8. Windows Setup

Tested on Windows 11; equivalent PowerShell commands run on other platforms.

```powershell
# 1. Install uv 0.13.6 (one-time)
#    https://docs.astral.sh/uv/getting-started/installation/
uv --version   # must report 0.13.6

# 2. Clone the repository, then from its root:
uv sync        # creates .venv and installs dependencies (see §9)
```

`uv sync` honors `.python-version`; if that interpreter is missing,
`uv python install 3.14` installs it.

## 9. Dependency Installation

```powershell
uv sync
```

What `uv sync` does:

1. Creates the project virtual environment in `.venv/`.
2. Generates (or updates) `uv.lock` from the constraints declared in
   `pyproject.toml`.
3. Installs the locked dependencies — including the `dev` tool group — and the
   project itself in **editable** mode.

For an already-locked repository (the normal case), `uv sync` alone is
sufficient; CI additionally uses `uv sync --locked`, which fails if
`uv.lock` and `pyproject.toml` disagree.

## 10. Development Commands

```powershell
# Run the test suite (pytest + coverage gate, 80% minimum)
uv run --no-sync pytest -v

# Lint and format checks
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .

# Type-check the engine package only
uv run --no-sync mypy src/fmcg_planner

# Build a distributable wheel
uv build --wheel
```

The current (Phase 0) test suite verifies packaging integrity, version
metadata consistency, and the engine/UI boundary guard; it intentionally
contains no business-logic tests yet.

## 11. CI Workflow

`.github/workflows/ci.yml` runs a **four-job matrix** — Ubuntu + Windows,
each on Python 3.13 and 3.14 — with `fail-fast: false` so every leg reports
independently. All actions are pinned to full commit SHAs; permissions are
least-privilege (`contents: read`); checkout does not persist credentials.

Per job, in order:

1. `uv sync --locked` — fail-fast guard on lockfile/version consistency.
2. Cross-platform Python-version assertion (env-var pass-through, AssertionError on mismatch).
3. Package import verification (`fmcg_planner.__version__`).
4. `ruff check .` and `ruff format --check .`.
5. `mypy src/fmcg_planner`.
6. `pytest -v` with the configured 80% coverage gate.

**Note:** CI status for this repository has not yet been observed (no run has
completed); the workflow description above is the specification, not a claim
of passing runs.

## 12. Lockfile Policy & Reproducibility

- `uv.lock` **must always be produced and updated by uv commands** — never
  hand-edited. The file contains version selectors, wheels, and checksums that
  uv validates on every operation like `uv sync --locked`.
- Reproducibility contract: same committed `uv.lock` + same uv CLI
  (0.13.6) ⇒ same dependency set, same editable wheel graph, and (because the
  sample-data generator will use a fixed stream, in Phase 1) the same sample
  dataset.
- Lifecycle: your local `uv sync` creates/updates the lock; `uv lock --check`
  (or CI's `uv sync --locked`) verifies it; lock changes are committed
  together with any `pyproject.toml` change. Dependabot may propose lockfile
  bumps via its `uv` ecosystem; always review those together with any
  `pyproject.toml` edits.
- Committed sample CSVs (created in Phase 1) are the **canonical synthetic
  dataset**: they are reproducible from the committed generator script and
  locked dependencies, and any dependency upgrade that could shift the data
  requires regeneration and an explicit diff review.

## 13. Security & Data-Protection Practices

- `.env` variants are fully ignored; the placeholder `.env.example` is the
  only tracked file of that family, and it contains no secrets (the project
  uses no environment variables for local operation).
- No credentials, API keys, or tokens are committed; required-by-design CI
  credentials are limited to the ephemeral, least-privilege GITHUB_TOKEN
  (`contents: read`), and checkout runs with `persist-credentials: false`.
- Third-party GitHub Actions are pinned to full commit SHAs, verified against
  their release commits; Dependabot keeps both applications and the uv CLI
  ecosystem updated weekly.
- Generated runtime artifacts (`.venv/`, `dist/`, caches, `data/generated/`,
  `exports/`) stay out of version control via `.gitignore`.

## 14. Synthetic & Fictional Data Disclaimer

All sample companies, products, materials, suppliers, demand series, capacity
figures, and pricing parameters in this repository are **fictional and
synthetic**, produced by committed deterministic scripts for educational
modeling. They do **not** represent, describe, or derive from any real
company's operations, and no real enterprise is a source of, or affiliate of,
this project's data. The committed CSVs produced in Phase 1 constitute the
canonical synthetic dataset, self-contained and reproducible from source.
Documentation figures in later phases distinguish *expected* noiseless
arithmetic from *realized* seeded values, and the two are always labeled.

## 15. Hosting Note (GitHub Pages)

The planned **Streamlit** front end is a Python server process: it cannot be
hosted on **GitHub Pages**, which statically serves files only and provides no
Python runtime. The application is designed to run on the local machine
(`localhost`); see the Milestone 2 command below. Publishable artifacts
(starting in Phase 1) are the methodology documentation and the CSV dataset
itself.

## 16. Milestone 2 — Local application preview (future)

The Streamlit command below belongs to **Milestone 2**. It is **not currently
executable** — no `app/app.py` and no Streamlit dependency exist in Phase 0.

```powershell
# Scheduled for Milestone 2 (do NOT attempt before then):
uv run streamlit run app/app.py --server.address localhost
```

## 17. License

MIT — see [`LICENSE`](LICENSE). © 2026 To Hung.

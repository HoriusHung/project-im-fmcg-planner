"""Phase 0 package-level tests for the fmcg_planner distribution.

Covers: importability, version metadata consistency, source-tree
provenance, and the engine/UI boundary guard (the planning engine must not
depend on Streamlit). All configuration checks parse the real pyproject.toml
rather than duplicating literals, except for __version__, which the spec
defines as `0.1.0`.
"""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

import fmcg_planner

EXPECTED_VERSION = "0.1.0"

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC_DIR = REPO_ROOT / "src" / "fmcg_planner"


def test_package_imports() -> None:
    """The wheel-installed (editable) package imports successfully."""
    assert fmcg_planner.__name__ == "fmcg_planner"


def test_dunder_version_is_defined() -> None:
    """__version__ is present and equals the approved Phase 0 value."""
    assert fmcg_planner.__version__ == EXPECTED_VERSION


def test_package_resolves_from_project_src() -> None:
    """The imported package comes from this project's src/fmcg_planner tree."""
    pkg_init = Path(fmcg_planner.__file__).resolve()
    assert pkg_init.name == "__init__.py"
    assert pkg_init.parent == PACKAGE_SRC_DIR


def test_pyproject_version_matches_package() -> None:
    """pyproject.toml's declared project version equals __version__."""
    config = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    pyproject_version = config["project"]["version"]
    assert pyproject_version == fmcg_planner.__version__ == EXPECTED_VERSION


def _collect_streamlit_violations(path: Path) -> list[str]:
    """Return Streamlit import violations found in one Python source file.

    Uses the AST to distinguish real imports from comments and string
    literals. Catches `import streamlit`, `import streamlit.x`, and
    `from streamlit import ...` / `from streamlit.x import ...`.
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    violations: list[str] = []
    for node in ast.walk(tree):
        match node:
            case ast.Import(names=aliases):
                violations.extend(
                    f"line {alias.lineno}: import {alias.name}"
                    for alias in aliases
                    if alias.name == "streamlit" or alias.name.startswith("streamlit.")
                )
            case ast.ImportFrom(module=module) if module is not None and (
                module == "streamlit" or module.startswith("streamlit.")
            ):
                violations.append(f"line {node.lineno}: from {module} import ...")
    return violations


def test_engine_package_does_not_import_streamlit() -> None:
    """No .py file under src/fmcg_planner imports Streamlit (AST-based)."""
    violations: list[str] = []
    for py_file in sorted(PACKAGE_SRC_DIR.rglob("*.py")):
        violations.extend(_collect_streamlit_violations(py_file))
    assert violations == [], f"Engine files import Streamlit: {violations}"

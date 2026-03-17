"""Tests enforcing explicit modular pipeline package boundaries."""

from __future__ import annotations

import ast
from pathlib import Path

from scraperweb.enrichment.models import EnrichedListingRecord
from scraperweb.modeling.models import ModelingInputRecord
from scraperweb.normalization.models import NormalizedListingRecord
from scraperweb.scraper.models import RawListingRecord


PACKAGE_ROOT = Path(__file__).resolve().parents[2] / "scraperweb"
DISALLOWED_IMPORT_PREFIXES = {
    "scraper": ("scraperweb.normalization", "scraperweb.enrichment", "scraperweb.modeling"),
    "normalization": ("scraperweb.enrichment", "scraperweb.modeling"),
    "enrichment": ("scraperweb.modeling",),
    "modeling": (),
}


def test_legacy_transitional_modules_are_removed() -> None:
    """Keep the package layout free of redundant transitional module trees."""

    assert not (PACKAGE_ROOT / "scraping").exists()
    assert not (PACKAGE_ROOT / "persistence" / "models.py").exists()


def test_stage_contract_modules_are_importable() -> None:
    """Expose all planned stage contracts from importable package boundaries."""

    assert RawListingRecord.__name__ == "RawListingRecord"
    assert NormalizedListingRecord.__name__ == "NormalizedListingRecord"
    assert EnrichedListingRecord.__name__ == "EnrichedListingRecord"
    assert ModelingInputRecord.__name__ == "ModelingInputRecord"


def test_application_layer_exposes_linear_pipeline_module() -> None:
    """Keep the application-layer linear pipeline orchestration importable."""

    module_path = PACKAGE_ROOT / "application" / "linear_pipeline_service.py"

    assert module_path.exists()


def test_stage_packages_follow_one_way_dependency_rules() -> None:
    """Reject imports from downstream pipeline stages inside upstream packages."""

    for package_name, disallowed_prefixes in DISALLOWED_IMPORT_PREFIXES.items():
        package_dir = PACKAGE_ROOT / package_name
        for module_path in package_dir.rglob("*.py"):
            imported_modules = _collect_imported_modules(module_path)
            for imported_module in imported_modules:
                assert not imported_module.startswith(disallowed_prefixes), (
                    f"{module_path.relative_to(PACKAGE_ROOT.parent)} imports "
                    f"downstream stage module {imported_module!r}."
                )


def _collect_imported_modules(module_path: Path) -> set[str]:
    """Return absolute imported module names referenced by one Python file."""

    tree = ast.parse(module_path.read_text(encoding="utf-8"), filename=str(module_path))
    imported_modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
            continue

        if isinstance(node, ast.ImportFrom):
            imported_module = _resolve_imported_module(
                module_path=module_path,
                module_name=node.module,
                level=node.level,
            )
            if imported_module:
                imported_modules.add(imported_module)

    return imported_modules


def _resolve_imported_module(
    module_path: Path,
    module_name: str | None,
    level: int,
) -> str | None:
    """Resolve absolute module names for direct and relative imports."""

    if level == 0:
        return module_name

    current_parts = module_path.relative_to(PACKAGE_ROOT.parent).with_suffix("").parts
    package_parts = current_parts[:-1]
    anchor_parts = package_parts[: len(package_parts) - (level - 1)]
    resolved_parts = list(anchor_parts)
    if module_name:
        resolved_parts.extend(module_name.split("."))

    return ".".join(resolved_parts) if resolved_parts else None

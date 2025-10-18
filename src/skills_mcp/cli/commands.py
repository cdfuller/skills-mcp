"""Shared CLI command implementations."""

from __future__ import annotations

import json
from pathlib import Path
import difflib

from ..tools import get_skill_detail

from ..resources import SkillResourceAdapter
from ..registry import SkillRegistry
from ..parser import parse_skill_dir


def _print_table(headers, rows):
    """Render a simple left-aligned table."""
    widths = [len(header) for header in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            widths[idx] = max(widths[idx], len(str(cell)))

    header_line = "  ".join(
        header.ljust(widths[idx]) for idx, header in enumerate(headers)
    )
    separator = "  ".join("-" * width for width in widths)
    print(header_line)
    print(separator)
    for row in rows:
        print(
            "  ".join(str(cell).ljust(widths[idx]) for idx, cell in enumerate(row))
        )


def status_command(registry: SkillRegistry):
    """Display registry summary."""
    summary = registry.summary()
    if not summary:
        print("No registries configured.")
        return

    rows = []
    total_skills = 0
    for row in summary:
        total_skills += row["count"]
        rows.append(
            (
                row["id"],
                "yes" if row["writable"] else "no",
                str(row["count"]),
                row["path"],
            )
        )

    _print_table(("ID", "Writable", "Count", "Path"), rows)
    print(f"Total skills: {total_skills}")


def list_command(
    adapter: SkillResourceAdapter,
    *,
    registry_ids=None,
    tags=None,
    limit=50,
    as_json=False,
):
    """List skills with optional filters."""
    page = adapter.list_resources(registry_ids=registry_ids, tags=tags, limit=limit)
    items = page["items"]

    if as_json:
        print(json.dumps(items, indent=2, sort_keys=True))
        return

    if not items:
        print("No skills found.")
        return

    rows = []
    for item in items:
        rows.append(
            (
                item["registry_id"],
                item["slug"],
                item.get("display_name") or "",
                ",".join(item.get("tags") or []),
                item.get("last_modified") or "",
            )
        )
    _print_table(("Registry", "Slug", "Name", "Tags", "Updated"), rows)


def validate_command(registry: SkillRegistry, *, path: str | None = None):
    """Validate skills and report warnings."""
    reports = []
    if path:
        target = Path(path)
        if target.is_dir():
            metadata = parse_skill_dir(target)
            if metadata and metadata.get("warnings"):
                reports.append(
                    {
                        "registry_id": "manual",
                        "slug": target.name,
                        "path": str(target / "SKILL.md"),
                        "warnings": metadata["warnings"],
                    }
                )
        else:
            print(f"Provided path '{path}' is not a directory.")
            return 1
    else:
        reports = registry.warning_report()

    if not reports:
        print("All skills valid.")
        return 0

    for report in reports:
        print(f"[{report['registry_id']}/{report['slug']}] {report['path']}")
        for warning in report["warnings"]:
            print(f"  - {warning}")
    return 1


def scaffold_command(
    registry: SkillRegistry,
    slug: str,
    *,
    template_dir: Path,
    registry_id: str | None = None,
):
    """Create a new skill directory from template."""
    target_registry = None
    for config in registry.summary():
        if registry_id and config["id"] != registry_id:
            continue

        if config["writable"]:
            target_registry = config
            break

    if not target_registry:
        raise SystemExit("No writable registry found. Configure a writable registry.")

    destination = Path(target_registry["path"]) / slug
    if destination.exists():
        raise SystemExit(f"Skill '{slug}' already exists at {destination}.")

    destination.mkdir(parents=True, exist_ok=False)
    template_file = template_dir / "SKILL.md"
    if not template_file.exists():
        raise SystemExit(f"Template SKILL.md not found in {template_dir}.")

    target_file = destination / "SKILL.md"
    target_file.write_text(template_file.read_text(encoding="utf-8"), encoding="utf-8")
    registry.refresh()
    print(f"Created skill scaffold at {target_file}")


def export_command(
    adapter: SkillResourceAdapter,
    registry_id: str,
    slug: str,
    *,
    fmt: str = "markdown",
    output: Path | None = None,
):
    """Export a skill to stdout or file."""
    detail = get_skill_detail(adapter, registry_id, slug)
    if not detail:
        raise SystemExit(f"Skill {registry_id}/{slug} not found.")

    content = detail["content"]
    if fmt == "markdown":
        text = content["body"]
    elif fmt == "json":
        text = json.dumps(
            {"metadata": detail["metadata"], "content": content},
            indent=2,
            sort_keys=True,
        )
    else:
        raise SystemExit(f"Unsupported export format '{fmt}'.")

    if output:
        output.write_text(text, encoding="utf-8")
        print(f"Wrote {fmt} export to {output}")
        return

    print(text)


def diff_command(
    adapter: SkillResourceAdapter,
    registry_a: str,
    slug_a: str,
    registry_b: str,
    slug_b: str | None = None,
):
    """Show unified diff between two skills."""
    slug_b = slug_b or slug_a
    first = get_skill_detail(adapter, registry_a, slug_a)
    second = get_skill_detail(adapter, registry_b, slug_b)

    if not first:
        raise SystemExit(f"Skill {registry_a}/{slug_a} not found.")
    if not second:
        raise SystemExit(f"Skill {registry_b}/{slug_b} not found.")

    first_lines = first["content"]["body"].splitlines()
    second_lines = second["content"]["body"].splitlines()

    diff_lines = list(
        difflib.unified_diff(
            first_lines,
            second_lines,
            fromfile=f"{registry_a}/{slug_a}",
            tofile=f"{registry_b}/{slug_b}",
            lineterm="",
        )
    )
    if not diff_lines:
        print("No differences.")
        return

    for line in diff_lines:
        print(line)

"""Command-line interface entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..server import initialize_components
from .commands import (
    diff_command,
    export_command,
    list_command,
    scaffold_command,
    status_command,
    validate_command,
)


def build_parser():
    """Build argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="skills-cli",
        description="Manage Skills catalogs for the skills-mcp server.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    subparsers.add_parser(
        "status",
        help="Show configured registries and discovered Skills.",
    )

    list_parser = subparsers.add_parser(
        "list",
        help="List skills across registries.",
    )
    list_parser.add_argument(
        "--registry",
        action="append",
        dest="registries",
        help="Filter results to specific registry IDs (repeatable).",
    )
    list_parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        help="Filter results to skills including the given tag (repeatable).",
    )
    list_parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum number of skills to display.",
    )
    list_parser.add_argument(
        "--json",
        action="store_true",
        help="Return results as JSON.",
    )

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate skills and report warnings.",
    )
    validate_parser.add_argument(
        "path",
        nargs="?",
        help="Optional path to a skill directory to validate directly.",
    )

    scaffold_parser = subparsers.add_parser(
        "scaffold",
        help="Create a new skill scaffold in a writable registry.",
    )
    scaffold_parser.add_argument("slug", help="Slug for the new skill directory.")
    scaffold_parser.add_argument(
        "--registry",
        help="Target writable registry ID. Defaults to the first writable registry.",
    )
    scaffold_parser.add_argument(
        "--template",
        default="basic",
        help="Template name to use (default: basic).",
    )

    export_parser = subparsers.add_parser(
        "export",
        help="Export a skill as Markdown or JSON.",
    )
    export_parser.add_argument("registry", help="Registry ID to export from.")
    export_parser.add_argument("slug", help="Skill slug to export.")
    export_parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Export format (default: markdown).",
    )
    export_parser.add_argument(
        "--output",
        help="Optional file path to write the export.",
    )

    diff_parser = subparsers.add_parser(
        "diff",
        help="Compare two skills and show differences.",
    )
    diff_parser.add_argument("registry_a", help="First registry ID.")
    diff_parser.add_argument("slug_a", help="First skill slug.")
    diff_parser.add_argument("registry_b", help="Second registry ID.")
    diff_parser.add_argument(
        "slug_b",
        nargs="?",
        help="Second skill slug (defaults to slug_a).",
    )

    return parser


def resolve_template_dir(name: str) -> Path:
    """Return the path to a template directory by name."""
    templates_root = Path(__file__).resolve().parent.parent / "templates"
    candidate = templates_root / f"{name}_skill"
    if not candidate.exists():
        raise SystemExit(f"Unknown template '{name}'. Expected directory {candidate}.")
    return candidate


def main(argv: list[str] | None = None):
    """Parse arguments and trigger CLI actions."""
    parser = build_parser()
    args = parser.parse_args(argv)

    registry, adapter = initialize_components()

    if args.command == "status":
        status_command(registry)
        return

    if args.command == "list":
        list_command(
            adapter,
            registry_ids=args.registries,
            tags=args.tags,
            limit=args.limit,
            as_json=args.json,
        )
        return

    if args.command == "validate":
        exit_code = validate_command(registry, path=args.path)
        if exit_code:
            sys.exit(exit_code)
        return

    if args.command == "scaffold":
        template_dir = resolve_template_dir(args.template)
        scaffold_command(
            registry,
            args.slug,
            template_dir=template_dir,
            registry_id=args.registry,
        )
        return

    if args.command == "export":
        output_path = Path(args.output).expanduser() if args.output else None
        export_command(
            adapter,
            args.registry,
            args.slug,
            fmt=args.format,
            output=output_path,
        )
        return

    if args.command == "diff":
        diff_command(
            adapter,
            args.registry_a,
            args.slug_a,
            args.registry_b,
            args.slug_b,
        )
        return

    parser.print_help()


if __name__ == "__main__":
    main()

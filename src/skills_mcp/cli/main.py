"""Command-line interface entry point."""

import argparse

from ..config import get_registries
from ..registry import SkillRegistry


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
    return parser


def handle_status():
    """Display registry status information."""
    registries = get_registries()
    registry = SkillRegistry(registries)
    summary = registry.summary()

    if not summary:
        print("No registries configured.")
        return

    header = f"{'ID':<15} {'Writable':<10} {'Count':<6} Path"
    print(header)
    print("-" * len(header))
    total = 0
    for row in summary:
        writable_flag = "yes" if row["writable"] else "no"
        print(
            f"{row['id']:<15} {writable_flag:<10} {row['count']:<6} {row['path']}"
        )
        total += row["count"]
    print("-" * len(header))
    print(f"Total skills: {total}")


def main():
    """Parse arguments and trigger CLI actions."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "status":
        handle_status()
        return

    parser.print_help()


if __name__ == "__main__":
    main()

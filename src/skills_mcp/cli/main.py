"""Command-line interface entry point."""

import argparse


def build_parser():
    """Build argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="skills-cli",
        description="Manage Skills catalogs for the skills-mcp server.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True

    subparsers.add_parser("status", help="Show configured registries (stub).")
    return parser


def main():
    """Parse arguments and trigger CLI actions."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "status":
        raise SystemExit("skills-cli status is not implemented yet.")

    parser.print_help()

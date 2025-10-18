"""Entry point for the skills MCP server."""

from .config import get_registries
from .registry import SkillRegistry


def main():
    """Run the MCP server (stub)."""
    registries = get_registries()
    registry = SkillRegistry(registries)
    summary = registry.summary()
    registry_ids = [row["id"] for row in summary]
    raise SystemExit(
        "skills-mcp server is not implemented yet. "
        "Registries loaded: "
        f"{', '.join(registry_ids)}"
    )


if __name__ == "__main__":
    main()

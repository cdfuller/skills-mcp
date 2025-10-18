"""Entry point for the skills MCP server."""

import os

from .config import get_registries
from .registry import SkillRegistry
from .resources import SkillResourceAdapter
from .tools import changes_since, get_skill_detail, registry_info, search_skills


def initialize_components():
    """Return initialized registry and adapter instances."""
    registries = get_registries()
    ttl_value = os.environ.get("SKILLS_MCP_CACHE_TTL")
    cache_ttl = None
    if ttl_value:
        try:
            cache_ttl = float(ttl_value)
        except ValueError:
            cache_ttl = None
    registry = SkillRegistry(registries, cache_ttl=cache_ttl)
    adapter = SkillResourceAdapter(registry)
    return registry, adapter


def main():
    """Run the MCP server (stub)."""
    registry, adapter = initialize_components()
    summary = registry.summary()
    registry_ids = [row["id"] for row in summary]
    raise SystemExit(
        "skills-mcp server not yet connected to stdio transport.\n"
        f"Loaded registries: {', '.join(registry_ids) or 'none'}\n"
        "Available tools: skills.search, skills.detail, skills.registry_info, "
        "skills.changes_since"
    )


__all__ = [
    "initialize_components",
    "SkillResourceAdapter",
    "search_skills",
    "get_skill_detail",
    "registry_info",
    "changes_since",
]


if __name__ == "__main__":
    main()

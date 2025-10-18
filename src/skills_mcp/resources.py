"""MCP resource adapter exposing Skill metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .registry import SkillRegistry


DEFAULT_PAGE_SIZE = 20


@dataclass
class ResourceResult:
    """Represents a single skill resource."""

    resource_id: str
    display_name: str
    description: str
    excerpt: str
    registry_id: str
    slug: str
    tags: List[str]
    hash_value: str
    last_modified: str
    warnings: List[str]

    def to_dict(self):
        """Return a serializable representation."""
        return {
            "id": self.resource_id,
            "display_name": self.display_name,
            "description": self.description,
            "excerpt": self.excerpt,
            "registry_id": self.registry_id,
            "slug": self.slug,
            "tags": self.tags,
            "hash": self.hash_value,
            "last_modified": self.last_modified,
            "warnings": self.warnings,
        }


class SkillResourceAdapter:
    """Adapter that surfaces SkillRegistry data as MCP resources."""

    def __init__(self, registry: SkillRegistry):
        self.registry = registry

    @staticmethod
    def resource_id_for(registry_id: str, slug: str) -> str:
        """Return the resource ID for a skill path."""
        return f"skill://{registry_id}/{slug}"

    @staticmethod
    def parse_resource_id(resource_id: str) -> Optional[Tuple[str, str]]:
        """Split a resource identifier into registry and slug."""
        if not resource_id.startswith("skill://"):
            return None
        parts = resource_id[len("skill://") :].split("/", 1)
        if len(parts) != 2 or not all(parts):
            return None
        return parts[0], parts[1]

    def _records(self, registry_ids: Optional[Iterable[str]] = None):
        """Yield cached skill records optionally filtered by registry."""
        ids = set(registry_ids) if registry_ids else None
        for record in self.registry.list_skills():
            if ids and record["registry_id"] not in ids:
                continue
            yield record

    def _build_resource(self, record: Dict[str, Any]) -> ResourceResult:
        """Convert a registry record into a resource representation."""
        metadata = record["metadata"]
        frontmatter = metadata.get("frontmatter", {})
        extra_tags = frontmatter.get("tags") or []
        consolidated_tags = sorted(
            {tag for tag in (*record.get("tags", []), *extra_tags) if tag}
        )
        return ResourceResult(
            resource_id=self.resource_id_for(record["registry_id"], record["slug"]),
            display_name=metadata.get("name") or record["slug"],
            description=metadata.get("description") or "",
            excerpt=metadata.get("excerpt") or "",
            registry_id=record["registry_id"],
            slug=record["slug"],
            tags=consolidated_tags,
            hash_value=metadata.get("sha256") or "",
            last_modified=record.get("last_modified") or "",
            warnings=metadata.get("warnings") or [],
        )

    def list_resources(
        self,
        cursor: Optional[str] = None,
        limit: int = DEFAULT_PAGE_SIZE,
        registry_ids: Optional[Iterable[str]] = None,
        tags: Optional[Iterable[str]] = None,
    ):
        """Return a paginated list of resources."""
        try:
            offset = int(cursor) if cursor else 0
        except ValueError:
            offset = 0

        requested_tags = set(tag.lower() for tag in tags) if tags else None

        all_resources = []
        for record in self._records(registry_ids):
            resource = self._build_resource(record)
            if requested_tags:
                resource_tags = {tag.lower() for tag in resource.tags}
                if not resource_tags.issuperset(requested_tags):
                    continue
            all_resources.append(resource)

        all_resources.sort(key=lambda res: (res.registry_id, res.slug))

        slice_end = offset + max(limit, 1)
        page = all_resources[offset:slice_end]
        next_cursor = str(slice_end) if slice_end < len(all_resources) else None

        return {
            "items": [resource.to_dict() for resource in page],
            "next_cursor": next_cursor,
            "total": len(all_resources),
        }

    def get_resource(self, resource_id: str):
        """Return the resource and content payload for a given resource_id."""
        parsed = self.parse_resource_id(resource_id)
        if not parsed:
            return None

        registry_id, slug = parsed
        record = self.registry.find_skill(registry_id, slug)
        if not record:
            return None

        resource = self._build_resource(record)
        metadata = record["metadata"]
        return {
            "resource": resource.to_dict(),
            "content": {
                "frontmatter": metadata.get("frontmatter", {}),
                "body": metadata.get("body", ""),
            },
        }

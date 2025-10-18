"""MCP resource adapter exposing Skill metadata."""

DEFAULT_PAGE_SIZE = 20


class SkillResourceAdapter:
    """Adapter that surfaces SkillRegistry data as MCP resources."""

    def __init__(self, registry):
        self.registry = registry

    @staticmethod
    def resource_id_for(registry_id, slug):
        """Return the resource ID for a skill path."""
        return f"skill://{registry_id}/{slug}"

    @staticmethod
    def parse_resource_id(resource_id):
        """Split a resource identifier into registry and slug."""
        if not resource_id.startswith("skill://"):
            return None
        parts = resource_id[len("skill://") :].split("/", 1)
        if len(parts) != 2 or not all(parts):
            return None
        return parts[0], parts[1]

    def _records(self, registry_ids=None):
        """Yield cached skill records optionally filtered by registry."""
        ids = set(registry_ids) if registry_ids else None
        for record in self.registry.list_skills():
            if ids and record["registry_id"] not in ids:
                continue
            yield record

    def _build_resource(self, record):
        """Convert a registry record into a resource representation."""
        metadata = record["metadata"]
        frontmatter = metadata.get("frontmatter", {})
        extra_tags = frontmatter.get("tags") or []
        consolidated_tags = sorted(
            {tag for tag in (*record.get("tags", []), *extra_tags) if tag}
        )
        return {
            "id": self.resource_id_for(record["registry_id"], record["slug"]),
            "display_name": metadata.get("name") or record["slug"],
            "description": metadata.get("description") or "",
            "excerpt": metadata.get("excerpt") or "",
            "registry_id": record["registry_id"],
            "slug": record["slug"],
            "tags": consolidated_tags,
            "hash": metadata.get("sha256") or "",
            "last_modified": record.get("last_modified") or "",
            "warnings": metadata.get("warnings") or [],
        }

    def list_resources(
        self,
        cursor=None,
        limit=DEFAULT_PAGE_SIZE,
        registry_ids=None,
        tags=None,
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
                resource_tags = {tag.lower() for tag in resource.get("tags", [])}
                if not resource_tags.issuperset(requested_tags):
                    continue
            all_resources.append(resource)

        all_resources.sort(key=lambda res: (res["registry_id"], res["slug"]))

        slice_end = offset + max(limit, 1)
        page = all_resources[offset:slice_end]
        next_cursor = str(slice_end) if slice_end < len(all_resources) else None

        return {
            "items": page,
            "next_cursor": next_cursor,
            "total": len(all_resources),
        }

    def get_resource(self, resource_id):
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
            "resource": resource,
            "content": {
                "frontmatter": metadata.get("frontmatter", {}),
                "body": metadata.get("body", ""),
            },
        }

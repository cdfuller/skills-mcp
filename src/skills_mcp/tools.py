"""Read-only MCP tool implementations for Skills catalogs."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Optional

from .resources import SkillResourceAdapter


def _coerce_limit(limit: Optional[int], default: int = 20) -> int:
    """Normalize limit values."""
    if limit is None:
        return default
    try:
        parsed = int(limit)
    except (TypeError, ValueError):
        return default
    return max(parsed, 1)


def _normalize_query(text: Optional[str]) -> List[str]:
    """Break query text into comparable tokens."""
    if not text:
        return []
    return [part for part in text.lower().split() if part]


def _parse_iso8601(timestamp: Optional[str]) -> Optional[datetime]:
    """Parse a subset of ISO-8601 timestamps."""
    if not timestamp:
        return None
    try:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        return None


def search_skills(
    adapter: SkillResourceAdapter,
    *,
    query: Optional[str] = None,
    registry_ids: Optional[Iterable[str]] = None,
    tags: Optional[Iterable[str]] = None,
    limit: Optional[int] = None,
):
    """Return skills matching query, registries, and tags."""
    tokens = _normalize_query(query)
    normalized_tags = {tag.lower() for tag in tags} if tags else None
    limit_value = _coerce_limit(limit)
    filtered_records = []

    allowed_registries = set(registry_ids) if registry_ids else None

    for record in adapter.registry.list_skills():
        if allowed_registries and record["registry_id"] not in allowed_registries:
            continue

        resource = adapter._build_resource(record).to_dict()
        resource_tags = {tag.lower() for tag in resource.get("tags", [])}
        if normalized_tags and not resource_tags.issuperset(normalized_tags):
            continue

        haystack = " ".join(
            [
                resource.get("display_name") or "",
                resource.get("description") or "",
                resource.get("excerpt") or "",
                " ".join(resource.get("tags") or []),
            ]
        ).lower()

        if tokens and not all(token in haystack for token in tokens):
            continue

        filtered_records.append(resource)

    filtered_records.sort(key=lambda item: (item["registry_id"], item["slug"]))

    results = []
    for item in filtered_records[:limit_value]:
        results.append(item)

    exhausted = len(filtered_records) <= limit_value
    return {"results": results, "exhausted": exhausted}


def get_skill_detail(adapter: SkillResourceAdapter, registry_id: str, slug: str):
    """Return full metadata and content for a skill."""
    resource_id = adapter.resource_id_for(registry_id, slug)
    data = adapter.get_resource(resource_id)
    if not data:
        return None

    resource = data["resource"]
    return {
        "metadata": resource,
        "content": data["content"],
    }


def registry_info(adapter: SkillResourceAdapter):
    """Return registry status information."""
    return {"registries": adapter.registry.summary()}


def changes_since(
    adapter: SkillResourceAdapter,
    *,
    registry_id: Optional[str] = None,
    since: Optional[str] = None,
    hashes: Optional[Iterable[str]] = None,
):
    """Return skills updated since timestamp or matching hashes."""
    since_dt = _parse_iso8601(since)
    hash_set = {value for value in hashes if value} if hashes else None
    updated = []

    registry_ids = [registry_id] if registry_id else None
    current_hashes = set()
    for record in adapter.registry.list_skills():
        if registry_ids and record["registry_id"] not in registry_ids:
            continue
        metadata = record["metadata"]
        record_hash = metadata.get("sha256")
        last_modified = _parse_iso8601(record.get("last_modified"))

        if record_hash:
            current_hashes.add(record_hash)

        if hash_set:
            if record_hash not in hash_set:
                updated.append(adapter._build_resource(record).to_dict())
            continue

        if since_dt and last_modified and last_modified > since_dt:
            updated.append(adapter._build_resource(record).to_dict())

    removed = []
    if hash_set:
        orphan_hashes = hash_set - {value for value in current_hashes if value}
        if orphan_hashes:
            removed = [{"hash": value} for value in sorted(orphan_hashes)]

    return {"updated": updated, "removed": removed}

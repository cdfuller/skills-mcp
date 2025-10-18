"""Registry management for Skills catalogs."""

from datetime import datetime, timezone
from pathlib import Path

from .parser import parse_skill_dir


class SkillRegistry:
    """Manage discovery of Skills across multiple registries."""

    def __init__(self, registries):
        """Store the registry definitions."""
        self.registries = registries
        self._cache = {}

    def refresh(self):
        """Rebuild the cache from disk."""
        active_ids = set()
        for registry in self.registries:
            registry_id = registry["id"]
            active_ids.add(registry_id)
            refreshed = self._refresh_registry(registry)
            self._cache[registry_id] = refreshed

        # Drop registries that are no longer configured.
        for cached_id in list(self._cache.keys()):
            if cached_id not in active_ids:
                del self._cache[cached_id]

        return self._cache

    def _refresh_registry(self, registry):
        """Refresh cache entries for a single registry."""
        registry_id = registry["id"]
        path = Path(registry["path"])
        previous = self._cache.get(registry_id, {})
        cached_skills = previous.get("skills", {})
        updated_skills = {}

        if path.exists():
            for entry in sorted(path.iterdir()):
                if not entry.is_dir():
                    continue

                skill_file = entry / "SKILL.md"
                if not skill_file.exists():
                    continue

                slug = entry.name
                stat_info = skill_file.stat()
                cached_record = cached_skills.get(slug)
                cached_mtime = cached_record["_mtime"] if cached_record else None

                if cached_record and cached_mtime == stat_info.st_mtime:
                    record = cached_record
                else:
                    metadata = parse_skill_dir(entry)
                    if not metadata:
                        continue
                    record = self._build_record(
                        registry,
                        slug,
                        skill_file,
                        metadata,
                        stat_info.st_mtime,
                    )
                updated_skills[slug] = record

        return {
            "skills": updated_skills,
            "refreshed_at": datetime.now(timezone.utc).isoformat(),
        }

    def _build_record(self, registry, slug, skill_file, metadata, mtime):
        """Construct the cache record for a parsed skill."""
        return {
            "registry_id": registry["id"],
            "slug": slug,
            "metadata": metadata,
            "path": skill_file,
            "writable": registry.get("writable", False),
            "last_modified": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
            "tags": registry.get("tags", []),
            "_mtime": mtime,
            "_sha256": metadata.get("sha256"),
        }

    def list_skills(self):
        """Return cached skills across registries."""
        if not self._cache:
            self.refresh()
        skills = []
        for registry_cache in self._cache.values():
            skills.extend(registry_cache["skills"].values())
        return skills

    def summary(self):
        """Return a summary of registries and skill counts."""
        if not self._cache:
            self.refresh()

        summary_rows = []
        for registry in self.registries:
            registry_id = registry["id"]
            skills = self._cache.get(registry_id, {}).get("skills", {})
            summary_rows.append(
                {
                    "id": registry_id,
                    "path": str(registry["path"]),
                    "writable": registry.get("writable", False),
                    "count": len(skills),
                }
            )
        return summary_rows

    def find_skill(self, registry_id, slug):
        """Locate a skill record by registry and slug."""
        if not self._cache:
            self.refresh()

        registry_cache = self._cache.get(registry_id, {})
        record = registry_cache.get("skills", {}).get(slug)
        if record:
            return record
        return None

    def warning_report(self):
        """Return a list of skills that produced warnings while parsing."""
        if not self._cache:
            self.refresh()

        reports = []
        for registry_cache in self._cache.values():
            for record in registry_cache.get("skills", {}).values():
                warnings = record["metadata"].get("warnings", [])
                if warnings:
                    reports.append(
                        {
                            "registry_id": record["registry_id"],
                            "slug": record["slug"],
                            "path": str(record["path"]),
                            "warnings": warnings,
                        }
                    )
        return reports

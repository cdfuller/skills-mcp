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
        self._cache = {}
        for registry in self.registries:
            skills = self._scan_registry(registry)
            self._cache[registry["id"]] = skills
        return self._cache

    def _scan_registry(self, registry):
        """Scan a registry path for SKILL.md entries."""
        path = Path(registry["path"])
        if not path.exists():
            return []

        skills = []
        for entry in sorted(path.iterdir()):
            if not entry.is_dir():
                continue

            metadata = parse_skill_dir(entry)
            if not metadata:
                continue

            skill_path = entry / "SKILL.md"
            mtime = datetime.fromtimestamp(
                skill_path.stat().st_mtime, tz=timezone.utc
            )

            record = {
                "registry_id": registry["id"],
                "slug": entry.name,
                "metadata": metadata,
                "path": skill_path,
                "writable": registry.get("writable", False),
                "last_modified": mtime.isoformat(),
                "tags": registry.get("tags", []),
            }
            skills.append(record)
        return skills

    def list_skills(self):
        """Return cached skills across registries."""
        if not self._cache:
            self.refresh()
        skills = []
        for items in self._cache.values():
            skills.extend(items)
        return skills

    def summary(self):
        """Return a summary of registries and skill counts."""
        if not self._cache:
            self.refresh()

        summary_rows = []
        for registry in self.registries:
            registry_id = registry["id"]
            skills = self._cache.get(registry_id, [])
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

        for record in self._cache.get(registry_id, []):
            if record["slug"] == slug:
                return record
        return None

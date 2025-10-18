"""Configuration helpers for skills_mcp."""

import os
from pathlib import Path
import tomllib


CONFIG_DIR_NAME = "skills-mcp"
CONFIG_FILENAME = "skills_mcp.toml"
CLI_REGISTRY_DIR = "skills"


def project_root_candidates():
    """Return potential project root locations."""
    here = Path(__file__).resolve()
    candidates = [
        Path(os.environ.get("SKILLS_MCP_ROOT", "")),
        Path.cwd(),
        here.parents[3] if len(here.parents) >= 4 else None,
    ]
    return [path for path in candidates if path and path.exists()]


def anthropic_repo_path():
    """Resolve the path to the anthropic-skills repository if available."""
    env_override = os.environ.get("SKILLS_MCP_ANTHROPIC_PATH")
    if env_override:
        path = Path(env_override).expanduser()
        if path.exists():
            return path

    for base in project_root_candidates():
        candidate = base / "anthropic-skills"
        if candidate.exists():
            return candidate
    return None


def cli_config_dir():
    """Return the CLI configuration directory, creating it if necessary."""
    env_override = os.environ.get("SKILLS_MCP_HOME")
    if env_override:
        config_dir = Path(env_override).expanduser()
    else:
        config_dir = Path.home() / ".config" / CONFIG_DIR_NAME

    try:
        config_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        fallback = Path.cwd() / f".{CONFIG_DIR_NAME}"
        fallback.mkdir(parents=True, exist_ok=True)
        config_dir = fallback
    return config_dir


def cli_registry_dir():
    """Return the directory where CLI-managed skills are stored."""
    registry_dir = cli_config_dir() / CLI_REGISTRY_DIR
    registry_dir.mkdir(parents=True, exist_ok=True)
    return registry_dir


def load_config_file():
    """Load configuration data from the CLI config file if it exists."""
    config_path = cli_config_dir() / CONFIG_FILENAME
    if not config_path.exists():
        return {}

    with config_path.open("rb") as handle:
        data = tomllib.load(handle)
    return data or {}


def normalize_registry_entry(entry):
    """Normalize a registry map from configuration."""
    path_value = entry.get("path")
    if not path_value:
        return None

    registry_path = Path(path_value).expanduser()
    registry = {
        "id": entry.get("id") or registry_path.name,
        "path": registry_path,
        "writable": bool(entry.get("writable", False)),
        "tags": list(entry.get("tags", [])),
    }
    return registry


def get_registries():
    """Assemble the list of skill registries."""
    registries = []

    anthropic_path = anthropic_repo_path()
    if anthropic_path:
        registries.append(
            {
                "id": "anthropic",
                "path": anthropic_path,
                "writable": False,
                "tags": ["reference"],
            }
        )

    local_registry = cli_registry_dir()
    registries.append(
        {
            "id": "local",
            "path": local_registry,
            "writable": True,
            "tags": ["user"],
        }
    )

    config_data = load_config_file()
    for entry in config_data.get("registries", []):
        normalized = normalize_registry_entry(entry)
        if normalized:
            registries.append(normalized)

    return registries

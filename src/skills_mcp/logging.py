"""Logging utilities for skills_mcp."""

import logging
import os


_CONFIGURED = False
_DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging(level=None):
    """Configure root logging once."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    level_name = level or os.environ.get("SKILLS_MCP_LOG_LEVEL", "INFO")
    log_level = getattr(logging, level_name.upper(), logging.INFO)

    logging.basicConfig(level=log_level, format=_DEFAULT_FORMAT)
    _CONFIGURED = True


def get_logger(name):
    """Return a namespaced logger configured for the package."""
    configure_logging()
    return logging.getLogger(name)

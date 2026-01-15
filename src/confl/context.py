"""Execution context for CLI operations.

Provides a context object to pass CLI flags and settings throughout the application,
breaking circular dependencies between cli.py and other modules.
"""

from dataclasses import dataclass


@dataclass
class ExecutionContext:
    """Context for CLI execution with flags and settings.

    This object is created by the CLI layer and passed to command functions
    and client creation functions to provide access to CLI flags without
    requiring imports from cli.py.

    Attributes:
        profile: Name of the configuration profile to use, or None for default
        verbose: Whether verbose output mode is enabled
        debug: Whether debug mode is enabled (includes HTTP request/response logging)
    """

    profile: str | None = None
    verbose: bool = False
    debug: bool = False

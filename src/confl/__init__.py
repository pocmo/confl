"""confl - An unofficial CLI for Atlassian Confluence Cloud."""

try:
    from confl._version import __version__
except ImportError:
    # Fallback for development installations without build
    __version__ = "dev"

__all__ = ["__version__"]

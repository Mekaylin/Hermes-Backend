"""Backend package marker for Hermes project.

This file makes the `backend` directory importable as a package so internal
relative imports (e.g., `from .routers import ...`) work during tests and
when running the app.
"""

__all__ = []

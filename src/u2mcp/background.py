"""Global background task management for long-running tasks."""

from __future__ import annotations

from anyio.abc import TaskGroup

# Global task group for background tasks (set by lifespan, None before that)
_task_group: TaskGroup | None = None


def get_background_task_group() -> TaskGroup | None:
    """Get the global background task group, or None if the server has not started."""
    return _task_group


def set_background_task_group(tg: TaskGroup):
    """Set the global monitor task group."""
    global _task_group
    _task_group = tg

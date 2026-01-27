"""Global background task management for long-running tasks."""

from __future__ import annotations

from anyio.abc import TaskGroup

# Global task group for background tasks (set by lifespan)
_task_group: TaskGroup


def get_background_task_group() -> TaskGroup:
    """Get the global background task group."""
    return _task_group


def set_background_task_group(tg: TaskGroup) -> None:
    """Set the global monitor task group."""
    global _task_group
    _task_group = tg

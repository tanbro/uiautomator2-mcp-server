"""Global background task management for long-running tasks."""

from __future__ import annotations

from anyio.abc import TaskGroup

# Global task group for background tasks (set by lifespan)
_monitor_task_group: TaskGroup


def get_monitor_task_group() -> TaskGroup:
    """Get the global monitor task group."""
    return _monitor_task_group


def set_monitor_task_group(tg: TaskGroup) -> None:
    """Set the global monitor task group."""
    global _monitor_task_group
    _monitor_task_group = tg

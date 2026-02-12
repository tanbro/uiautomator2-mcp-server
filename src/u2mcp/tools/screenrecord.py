from __future__ import annotations

from anyio import to_thread
from anyio.abc import TaskStatus

from ..background import get_background_task_group
from ..mcp import mcp
from .device import get_device

__all__ = ("screen_record_start", "screen_record_stop", "screen_record")


# Global tracking of recording status
_recording_active: dict[str, bool] = {}


@mcp.tool("screen_record_start", tags={"screen:record"})
async def screen_record_start(serial: str, file: str, duration: float) -> str:
    """Start screen recording to file. Runs in background, use screen_record_stop to stop.

    Args:
        serial (str): Android device serial number.
        file (str): Output file path for the recording.
        duration (float): Maximum recording duration in seconds.

    Returns:
        str: Output file path.
    """
    task_group = get_background_task_group()

    async def run_recording(task_status: TaskStatus):
        _recording_active[serial] = True
        task_status.started()

        try:
            async with get_device(serial) as device:
                await to_thread.run_sync(lambda: device.screenrecord(file, duration))
        finally:
            _recording_active.pop(serial, None)

    await task_group.start(run_recording)
    _recording_active[serial] = True
    return file


@mcp.tool("screen_record_stop", tags={"screen:record"})
async def screen_record_stop(serial: str):
    """Stop screen recording for the device. Stops any active background recording task.

    Args:
        serial (str): Android device serial number.
    """
    _recording_active.pop(serial, None)


@mcp.tool("screen_record", tags={"screen:record"})
async def screen_record(serial: str, filename: str, fps: int = 20):
    """Record screen to file with blocking wait. For non-blocking recording use screen_record_start.

    Args:
        serial (str): Android device serial number.
        filename (str): Output file path for the recording.
        fps (int): Frames per second for recording.

    Returns:
        str: Output file path.
    """
    async with get_device(serial) as device:
        await to_thread.run_sync(lambda: device.screenrecord(filename, fps))

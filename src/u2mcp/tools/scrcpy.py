from __future__ import annotations

import os

from anyio import create_task_group, move_on_after, open_process
from anyio.abc import AnyByteReceiveStream, Process
from anyio.streams.text import TextReceiveStream
from fastmcp.server.dependencies import get_context
from fastmcp.utilities.logging import get_logger

from ..background import get_background_task_group
from ..mcp import mcp

__all__ = ("start_scrcpy", "stop_scrcpy")

# Keep track of background scrcpy processes
_background_processes: dict[int, Process] = {}


@mcp.tool("start_scrcpy")
async def start_scrcpy(serial: str = "", timeout: float = 5.0) -> int:
    """Startup scrcpy in background and returns process id.

    The scrcpy process will run in the background after successful startup.
    Use stop_scrcpy to terminate the process.

    Args:
        serial (str): Android device serialno. If empty string, connects to the unique device if only one device is connected.
        timeout (float): Seconds to wait for process to confirm startup.
            If process is still running after this time, startup is considered successful.

    Returns:
        int: process id (pid)
    """

    logger = get_logger(f"{__name__}.start_scrcpy")
    ctx = get_context()

    scrcpy_path = os.environ.get("SCRCPY", "scrcpy.exe" if os.name == "nt" else "scrcpy")
    command = [scrcpy_path]
    if serial := serial.strip():
        command.extend(["--serial", serial])

    logger.info("start scrcpy: %s", command)

    process = await open_process(command)
    pid = process.pid

    # Stream monitoring function
    async def receive(name: str, stream: AnyByteReceiveStream):
        logger.info("Starting to monitor %s for pid=%s", name, pid)
        async for line in TextReceiveStream(stream):
            logger.debug("Received %s line: %s", name, line.strip())
            match name:
                case "stdout":
                    await ctx.info(line)
                case "stderr":
                    await ctx.error(line)
                case _:
                    raise ValueError(f"Unknown stream name: {name}")
        logger.info("Finished monitoring %s for pid=%s", name, pid)

    # Monitor streams and auto-cleanup on process exit
    async def monitor_streams():
        if process.stdout is None:
            raise RuntimeError("stdout is None")
        if process.stderr is None:
            raise RuntimeError("stderr is None")
        try:
            async with create_task_group() as inner_tg:
                for name, handle in zip(("stdout", "stderr"), (process.stdout, process.stderr)):
                    inner_tg.start_soon(receive, name, handle)
        finally:
            # Cleanup only if we still own the process (i.e., not manually stopped)
            if _background_processes.pop(pid, None) is process:
                logger.info("scrcpy process exited naturally, cleaning up (pid=%s)", pid)
                await process.aclose()
            else:
                logger.info("scrcpy process was manually stopped, skipping cleanup (pid=%s)", pid)

    # Start monitoring immediately (before startup wait) to capture startup logs
    tg = get_background_task_group()
    if tg is None:
        raise RuntimeError("Monitor task group not initialized - server not started?")
    tg.start_soon(monitor_streams)

    # Store process
    _background_processes[pid] = process

    # Startup phase: wait for process exit with timeout
    with move_on_after(timeout) as timeout_scope:
        await process.wait()

    if timeout_scope.cancel_called:
        # Timeout reached, process is still running - success!
        logger.info("scrcpy started successfully in background (pid=%s)", pid)
    else:
        # Process exited before timeout - failure
        _background_processes.pop(pid, None)
        if process.returncode == 0:
            raise RuntimeError(f"scrcpy closed during startup (pid={pid}, return code 0)")
        else:
            raise RuntimeError(f"scrcpy exited during startup wait with code: {process.returncode} (pid={pid})")

    return pid


@mcp.tool("stop_scrcpy")
async def stop_scrcpy(pid: int, timeout: float = 5.0) -> None:
    """Stop a running scrcpy process by pid.

    Args:
        pid (int): Process id of the scrcpy process to stop
        timeout (float): Seconds to wait for process to terminate.

    Returns:
        None
    """

    logger = get_logger(f"{__name__}.stop_scrcpy")

    if pid not in _background_processes:
        raise ValueError(f"No scrcpy process found with pid: {pid}")

    process = _background_processes.pop(pid)
    process.kill()

    # Wait for process to exit with timeout
    with move_on_after(timeout) as timeout_scope:
        await process.wait()

    # Always close the process when manually stopping
    # The monitor task will detect we popped the process and skip cleanup
    await process.aclose()

    if timeout_scope.cancel_called:
        logger.warning("scrcpy process did not exit within %ss (pid=%s)", timeout, pid)
    else:
        logger.info("scrcpy process stopped (pid=%s)", pid)

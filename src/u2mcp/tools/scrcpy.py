from __future__ import annotations

import os

from anyio import create_task_group, move_on_after, open_process
from anyio.abc import AnyByteReceiveStream, Process
from anyio.streams.text import TextReceiveStream
from fastmcp.server.dependencies import get_context
from fastmcp.utilities.logging import get_logger

from ..mcp import mcp

__all__ = ("start_scrcpy", "stop_scrcpy")

# Keep track of background scrcpy processes
_background_processes: dict[int, Process] = {}


@mcp.tool("scrcpy")
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

    scrcpy_path = os.environ.get("SCRCPY", "scrcpy")
    command = [scrcpy_path]
    if serial := serial.strip():
        command.extend(["--serial", serial])

    logger.info("start scrcpy: %s", command)
    ctx = get_context()

    process = await open_process(command)
    pid = process.pid

    async def receive(name: str, stream: AnyByteReceiveStream):
        async for line in TextReceiveStream(stream):
            match name:
                case "stdout":
                    await ctx.info(line)
                case "stderr":
                    await ctx.error(line)
                case _:
                    raise ValueError(f"Unknown stream name: {name}")

    async def monitor_streams():
        if process.stdout is None:
            raise RuntimeError("stdout is None")
        if process.stderr is None:
            raise RuntimeError("stderr is None")
        async with create_task_group() as tg:
            for name, handle in zip(("stdout", "stderr"), (process.stdout, process.stderr)):
                tg.start_soon(receive, name, handle)

    # Startup phase: wait for process exit with timeout
    with move_on_after(timeout) as timeout_scope:
        await process.wait()

    if timeout_scope.cancel_called:
        # Timeout reached, process is still running - success!
        logger.info("scrcpy started successfully in background (pid=%s)", pid)
    else:
        # Process exited before timeout - failure
        raise RuntimeError(f"scrcpy exited during startup wait with code: {process.returncode}")

    # Start background monitoring (fire and forget)
    async def run_monitor():
        try:
            await monitor_streams()
        except Exception as e:
            logger.error("scrcpy stream monitor error: %s", e)
        finally:
            _background_processes.pop(pid, None)

    create_task_group().start_soon(run_monitor)
    _background_processes[pid] = process

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

    await process.aclose()

    if timeout_scope.cancel_called:
        raise TimeoutError(f"scrcpy process did not exit within {timeout}s")

    logger.info("scrcpy process stopped (pid=%s)", pid)

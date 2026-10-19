
import asyncio

from agentforge.core.config import settings


MAX_CODE_LENGTH = 4000


async def execute_python(code: str) -> dict:
    """Execute Python in a restricted Docker container."""

    if not code.strip() or len(code) > MAX_CODE_LENGTH:
        raise ValueError("Code must contain 1–4000 characters.")

    image = settings.python_sandbox_image

    command = [
        "docker", "run",
        "--rm",
        "-i",
        "--network", "none",
        "--read-only",
        "--memory", "128m",
        "--cpus", "0.5",
        "--pids-limit", "32",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--user", "65534:65534",
        "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
        image,
        "python", "-I", "-c", code,
    ]

    process = None

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        timeout = settings.python_sandbox_timeout_seconds

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout,
        )

    except FileNotFoundError as exc:
        raise RuntimeError(
            "Docker CLI not found. Install Docker Desktop and start it."
        ) from exc

    except asyncio.TimeoutError as exc:
        if process is not None and process.returncode is None:
            process.kill()
            await process.communicate()

        raise RuntimeError(
            "Python execution exceeded its time limit."
        ) from exc

    except OSError as exc:
        raise RuntimeError("Could not start Docker sandbox.") from exc

    output = stdout.decode("utf-8", errors="replace")[:8000]
    error = stderr.decode("utf-8", errors="replace")[:2000]

    if process.returncode != 0:
        return {
            "success": False,
            "output": output,
            "error": error or "Python execution failed.",
        }

    return {
        "success": True,
        "output": output,
        "error": "",
    }

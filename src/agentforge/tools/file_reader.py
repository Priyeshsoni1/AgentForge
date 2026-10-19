
from pathlib import Path

from agentforge.core.config import settings


MAX_FILE_BYTES = 100_000
MAX_PATH_LENGTH = 500


def read_file(relative_path: str) -> dict:
    """Read a small UTF-8 text file from the approved workspace."""

    if not relative_path or len(relative_path) > MAX_PATH_LENGTH:
        raise ValueError("Invalid file path.")

    relative = Path(relative_path)

    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Only relative workspace paths are allowed.")

    root = Path(settings.file_reader_root).resolve()
    candidate = root / relative

    # Check every component for symlinks before resolving.
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("Symbolic links are not allowed.")

    resolved = candidate.resolve()

    if not resolved.is_relative_to(root):
        raise ValueError("File path is outside the workspace.")

    if not resolved.is_file():
        raise ValueError("Requested file does not exist.")

    if resolved.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("File exceeds the 100 KB size limit.")

    try:
        content = resolved.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        raise ValueError("Could not read a UTF-8 text file.") from exc

    return {
        "path": relative.as_posix(),
        "content": content,
        "characters": len(content),
    }

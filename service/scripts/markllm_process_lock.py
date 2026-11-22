"""Cross-process serialization for memory-heavy MarkLLM model operations."""
from __future__ import annotations

import contextlib
import os
import threading
from pathlib import Path
from typing import Iterator

_LOCAL_LOCK = threading.Lock()
_LOCK_PATH = Path(os.environ.get("WATERMARKS_MARKLLM_LOCK_PATH", "/tmp/watermarks-markllm.lock"))


@contextlib.contextmanager
def markllm_process_lock() -> Iterator[None]:
    """Allow only one MarkLLM generation/detection worker at a time per container."""
    if os.name == "posix":
        import fcntl

        _LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _LOCAL_LOCK:
            with _LOCK_PATH.open("a+") as handle:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    else:
        with _LOCAL_LOCK:
            yield

#!/usr/bin/env python3
"""Short-lived MarkLLM generation worker for memory-constrained deployments."""
from __future__ import annotations

import json
import os
import sys

os.environ["WATERMARKS_MARKLLM_GENERATION_WORKER"] = "1"

from text_watermark import _watermark_local_markllm


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        result = _watermark_local_markllm(
            str(payload["text"]),
            str(payload["upstream_dir"]),
            keys=payload.get("keys"),
            options=payload.get("options") or {},
            timeout=payload.get("timeout"),
        )
        sys.stdout.write(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:
        sys.stderr.write(f"{type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

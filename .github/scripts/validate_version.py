#!/usr/bin/env python3

"""Validate a tag in GITHUB_REF against PEP 440 and write `version=...` to GITHUB_OUTPUT.

This script is intentionally small and dependency-free except for `packaging`, which the
workflow installs before calling this script.

Behavior:
- If GITHUB_REF is a tag (refs/tags/...): extract tag, strip a single leading 'v' if present.
- Use packaging.Version to validate PEP 440. If valid, write `version=<tag>` to GITHUB_OUTPUT.
- If invalid or no tag, write `version=` (empty) so downstream jobs can gate on it.
"""

from __future__ import annotations

import os
import sys

try:
    from packaging.version import InvalidVersion, Version
except Exception:  # pragma: no cover - packaging may be missing if not installed
    print("ERROR: packaging module is required to validate versions. Install packaging in CI.", file=sys.stderr)
    raise


def get_candidate_from_ref(ref: str) -> str:
    if not ref:
        return ""
    prefix = "refs/tags/"
    if not ref.startswith(prefix):
        return ""
    tag = ref[len(prefix) :].strip()
    if len(tag) > 1 and tag.startswith(("v", "V")):
        return tag[1:]
    return tag


def write_github_output(key: str, value: str):
    out_line = f"{key}={value}\n"
    g = os.environ.get("GITHUB_OUTPUT")
    if g:
        try:
            with open(g, "a", encoding="utf-8") as fh:
                fh.write(out_line)
            return
        except Exception:
            # Fallthrough to printing if file write fails
            pass
    # fallback: print to stdout so it's visible in logs
    sys.stdout.write(out_line)


def main():
    ref = os.environ.get("GITHUB_REF", "")
    cand = get_candidate_from_ref(ref)
    version = ""
    if cand:
        try:
            Version(cand)
            version = cand
        except InvalidVersion:
            version = ""
    print(f"GITHUB_REF={ref!r} -> version={version!r}")
    write_github_output("version", version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

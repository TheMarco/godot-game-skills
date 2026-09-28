#!/usr/bin/env python3
"""Compare declared equivalent timing samples; no FPS or significance claims."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import statistics
import sys


def load_series(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"metric", "unit", "context", "samples"}:
        raise ValueError("Expected metric, unit, context and samples fields only")
    for field in ("metric", "unit"):
        if not isinstance(data[field], str) or not data[field].strip():
            raise ValueError(f"{field} must be a nonempty string")
    if data["unit"] not in {"ns", "us", "ms", "s"}:
        raise ValueError("unit must be ns, us, ms or s")
    if not isinstance(data["context"], dict) or not data["context"]:
        raise ValueError("context must describe the measured environment and workload")
    values = data["samples"]
    if not isinstance(values, list) or not values:
        raise ValueError("samples must be a nonempty array")
    if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in values):
        raise ValueError("samples must contain finite nonnegative numbers, not booleans")
    return data


def summarize(values: list) -> dict:
    ordered = sorted(values)
    return {
        "count": len(values), "mean": statistics.mean(values),
        "median": statistics.median(values),
        "p95": ordered[math.ceil(len(values) * 0.95) - 1], "max": max(values),
    }


def compare(before: dict, after: dict) -> dict:
    for key in ("metric", "unit", "context"):
        if before[key] != after[key]:
            raise ValueError(f"Cannot compare: {key} differs")
    old, new = summarize(before["samples"]), summarize(after["samples"])
    delta = {
        key: {"absolute": new[key] - old[key],
              "percent": (new[key] / old[key] - 1) * 100 if old[key] else None}
        for key in ("mean", "median", "p95", "max")
    }
    warnings = ["Descriptive comparison only; not a significance test or a whole-game FPS claim."]
    if min(old["count"], new["count"]) < 20:
        warnings.append("Fewer than 20 samples: tail estimates are especially unstable.")
    return {"metric": before["metric"], "unit": before["unit"], "context": before["context"],
            "before": old, "after": new, "change": delta, "notes": warnings}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = compare(load_series(args.before), load_series(args.after))
        rendered = json.dumps(report, indent=2, allow_nan=False) + "\n"
        if args.output:
            # Never overwrite raw measurements or a previous report silently.
            with args.output.open("x", encoding="utf-8") as output:
                output.write(rendered)
        print(rendered, end="")
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Command line used by the API's job runner.

  python -m retentionlens.ingest inspect FILE
  python -m retentionlens.ingest validate FILE --mapping JSON [--date-order auto|dayfirst|monthfirst]
  python -m retentionlens.ingest score FILE --mapping JSON --out DIR [--date-order ...]

Prints one JSON object per line: progress lines {"stage", "pct"}, then {"result": ...} or {"error": ...}.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .pipeline import IngestError, inspect, score, validate


def emit(payload: dict) -> None:
    print(json.dumps(payload, default=str), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(prog="retentionlens.ingest")
    parser.add_argument("command", choices=["inspect", "validate", "score"])
    parser.add_argument("file", type=Path)
    parser.add_argument("--mapping", default="{}")
    parser.add_argument("--date-order", default="auto", choices=["auto", "dayfirst", "monthfirst"])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "inspect":
            result = inspect(args.file)
        elif args.command == "validate":
            result = validate(args.file, json.loads(args.mapping), args.date_order)
        else:
            if args.out is None:
                parser.error("--out is required for score")
            result = score(args.file, json.loads(args.mapping), args.out, args.date_order, lambda stage, pct: emit({"stage": stage, "pct": pct}))
    except IngestError as error:
        emit({"error": str(error)})
        return 2
    emit({"result": result})
    return 0


if __name__ == "__main__":
    sys.exit(main())

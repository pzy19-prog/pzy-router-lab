"""CLI for a single routing decision (no task/model execution)."""

import argparse
import json
from pathlib import Path

from .rules import route


def main() -> None:
    parser = argparse.ArgumentParser(description="Local-only rules Router baseline")
    parser.add_argument("command", choices=["route"])
    parser.add_argument("--input", required=True, type=Path, help="Path to sanitized JSON request")
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    print(json.dumps(route(payload), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

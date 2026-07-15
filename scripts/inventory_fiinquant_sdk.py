#!/usr/bin/env python3
"""Inventory local FiinQuant Python SDK surface (run where SDK is installed).

Usage:
  python scripts/inventory_fiinquant_sdk.py
  python scripts/inventory_fiinquant_sdk.py > plans/.../research/sdk-inventory.md
"""

from __future__ import annotations

import importlib
import inspect
import sys


CANDIDATES = ("fiinquant", "FiinQuantX", "fiinquantx")


def inventory_module(name: str) -> str:
    lines: list[str] = [f"# SDK inventory: `{name}`", ""]
    mod = importlib.import_module(name)
    lines.append(f"- file: `{getattr(mod, '__file__', '?')}`")
    lines.append(f"- version: `{getattr(mod, '__version__', 'n/a')}`")
    lines.append("")
    lines.append("## Public attributes")
    lines.append("")
    for attr in sorted(a for a in dir(mod) if not a.startswith("_")):
        obj = getattr(mod, attr)
        kind = type(obj).__name__
        if inspect.isclass(obj):
            lines.append(f"### class `{attr}`")
            methods = [
                m
                for m, _ in inspect.getmembers(obj, predicate=inspect.isfunction)
                if not m.startswith("_")
            ]
            methods += [
                m
                for m, _ in inspect.getmembers(obj, predicate=inspect.ismethod)
                if not m.startswith("_")
            ]
            # also unbound methods on class
            for m in sorted(set(dir(obj))):
                if m.startswith("_"):
                    continue
                member = getattr(obj, m, None)
                if callable(member):
                    try:
                        sig = str(inspect.signature(member))
                    except (TypeError, ValueError):
                        sig = "(...)"
                    lines.append(f"- `{m}{sig}`")
            lines.append("")
        elif callable(obj):
            try:
                sig = str(inspect.signature(obj))
            except (TypeError, ValueError):
                sig = "(...)"
            lines.append(f"- function `{attr}{sig}` ({kind})")
        else:
            lines.append(f"- `{attr}`: {kind}")
    return "\n".join(lines) + "\n"


def main() -> int:
    found = False
    for name in CANDIDATES:
        try:
            print(inventory_module(name))
            found = True
        except ImportError:
            print(f"# `{name}`: not importable", file=sys.stderr)
    if not found:
        print(
            "No FiinQuant SDK found. Install private wheel, then re-run.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

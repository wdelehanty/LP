#!/usr/bin/env python3
"""Inject the site version and deploy date into data-stamp elements.

Usage: python3 scripts/stamp.py <version> <file> [<file> ...]
The date is always today (local). Fails loudly if a file has no stamps,
so a page can never ship with a hard-coded footer by accident.
"""
import datetime
import re
import sys


def stamp(path: str, version: str, date: str) -> int:
    with open(path, encoding="utf-8") as f:
        html = f.read()
    count = 0

    def repl(m):
        nonlocal count
        count += 1
        value = version if m.group(2) == "version" else date
        return m.group(1) + value + m.group(3)

    html = re.sub(
        r'(<[^>]*data-stamp="(version|date)"[^>]*>)[^<]*(</)',
        repl,
        html,
    )
    if count == 0:
        raise SystemExit(f"{path}: no data-stamp elements found")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return count


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    version = sys.argv[1]
    if not re.fullmatch(r"v\d+\.\d+\.\d+", version):
        raise SystemExit(f"bad version {version!r}, expected vX.Y.Z")
    date = datetime.date.today().isoformat()
    for path in sys.argv[2:]:
        n = stamp(path, version, date)
        print(f"{path}: stamped {n} elements with {version} / {date}")


if __name__ == "__main__":
    main()

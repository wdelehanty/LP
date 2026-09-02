#!/usr/bin/env python3
"""Write live status rail values into the markup so the fallback is real.

Usage: python3 scripts/bake_status.py <file> [<file> ...]
Reads STATUS_URL (default https://wd-status.wdelehanty.workers.dev/api/status), then
replaces the text of every element carrying data-rail="<key>" with the
value of that key. Files without a rail are skipped. Exits non-zero if the
endpoint cannot be read, so a release never bakes stale values by mistake
without saying so.
"""
import json
import os
import re
import sys
import urllib.request

URL = os.environ.get("STATUS_URL", "https://wd-status.wdelehanty.workers.dev/api/status")
PATTERN = re.compile(r'(<[^>]*data-rail="([a-z_]+)"[^>]*>)[^<]*(</)')


def fetch() -> dict:
    req = urllib.request.Request(URL, headers={"User-Agent": "williamdelehanty.com release script", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        if r.status != 200:
            raise SystemExit(f"{URL}: HTTP {r.status}")
        return json.load(r)


def bake(path: str, status: dict) -> int:
    with open(path, encoding="utf-8") as f:
        html = f.read()
    count = 0

    def repl(m):
        nonlocal count
        value = status.get(m.group(2))
        if value is None:
            return m.group(0)
        count += 1
        return m.group(1) + str(value) + m.group(3)

    new = PATTERN.sub(repl, html)
    if new != html:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
    return count


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    status = fetch()
    for path in sys.argv[1:]:
        n = bake(path, status)
        if n:
            print(f"{path}: baked {n} rail values")


if __name__ == "__main__":
    main()

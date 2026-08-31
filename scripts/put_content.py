#!/usr/bin/env python3
"""Replace the CONTENT placeholder in a skeleton page with stdin."""
import sys

path = sys.argv[1]
content = sys.stdin.read().rstrip("\n")
with open(path, encoding="utf-8") as f:
    html = f.read()
if "<!-- CONTENT -->" not in html:
    raise SystemExit(f"{path}: no CONTENT placeholder (already filled?)")
html = html.replace("<!-- CONTENT -->", content)
with open(path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"{path}: content set")

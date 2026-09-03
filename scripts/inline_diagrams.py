#!/usr/bin/env python3
"""Inline diagram SVGs into pages at their placeholder comments.

A page marks a slot with <!-- diagram:slug -->. This script replaces the
slot with the SVG from assets/diagrams/<slug>.svg (or the HTML fragment
<slug>.html for callouts figures, passed through as is), wrapped in a scroll
container when the diagram is wider than the content column, and fenced
with markers so re-running replaces cleanly. Fails loudly on a missing
SVG so a page can never ship with an empty slot.

Usage: inline_diagrams.py <v2-dir>
"""
import os
import re
import sys

WIDE_AT = 920


def svg_for(slug, diagrams_dir):
    html_path = os.path.join(diagrams_dir, slug + ".html")
    if os.path.exists(html_path):
        # callouts figures are HTML fragments; pass them through untouched
        return open(html_path, encoding="utf-8").read().strip()
    path = os.path.join(diagrams_dir, slug + ".svg")
    if not os.path.exists(path):
        raise SystemExit(f"missing diagram: {path}")
    svg = open(path, encoding="utf-8").read().strip()
    m = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', svg)
    width = float(m.group(1)) if m else 0
    if width > WIDE_AT:
        minw = int(width * 0.72)
        svg = svg.replace("<svg ", f'<svg style="min-width:{minw}px" ', 1)
        svg = f'<div class="dg-scroll">{svg}</div>'
    return svg


def process(path, diagrams_dir):
    html = open(path, encoding="utf-8").read()
    html = re.sub(r"<!-- dg:(\S+):start -->.*?<!-- dg:\1:end -->",
                  lambda m: f"<!-- diagram:{m.group(1)} -->", html, flags=re.S)
    slugs = re.findall(r"<!-- diagram:(\S+) -->", html)
    for slug in slugs:
        block = f"<!-- dg:{slug}:start -->{svg_for(slug, diagrams_dir)}<!-- dg:{slug}:end -->"
        html = html.replace(f"<!-- diagram:{slug} -->", block)
    open(path, "w", encoding="utf-8").write(html)
    return slugs


def main():
    v2 = sys.argv[1]
    diagrams = os.path.join(v2, "assets", "diagrams")
    for root, _, files in os.walk(v2):
        if os.path.join(v2, "assets") in root:
            continue
        for f in files:
            if f.endswith(".html"):
                p = os.path.join(root, f)
                slugs = process(p, diagrams)
                if slugs:
                    print(f"{os.path.relpath(p, v2)}: {', '.join(slugs)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Write qa/diagrams.html: every figure in assets/diagrams with its grammar,
size, and the pages that use it. The qa folder is gitignored.

Usage: contact_sheet.py
"""
import glob
import os
import re

GRAMMAR = {
    "flow": ["demand-engine-full", "feedback-loop", "kit-visit-alert", "lifeos-captures",
             "prompt-patch-loop", "provisioner", "chat-provisioner", "nightly-backup", "error-alerting",
             "transcript-qa-digest", "live-booking", "morning-round-v2", "monday-report", "outcome-loop",
             "selfserve-sequence", "event-pacing"],
    "ledger": ["enterprise-program", "summit-program", "lifeos-hub"],
    "timeline": ["forbes8-lifecycle", "selfserve-timeline", "profiling-timeline", "ha-waves"],
    "layers": ["connect-cdp", "playbook-structure", "wardrobe-system"],
    "split": ["two-tier", "two-bucket"],
    "swimlanes": ["funnel", "morning-round-lanes", "live-booking-lanes", "outcome-lanes"],
    "callouts": ["connect-callouts", "monday-report-callouts"],
}
BY_SLUG = {s: g for g, slugs in GRAMMAR.items() for s in slugs}

pages = [p for p in glob.glob("**/index.html", recursive=True) if not p.startswith(("archive/", "qa/", "pitches/", "worker/"))]
usage = {}
for p in pages:
    html = open(p, encoding="utf-8").read()
    for slug in re.findall(r"<!-- dg:(\S+):start -->", html):
        usage.setdefault(slug, []).append(p.replace("/index.html", "/") if p != "index.html" else "/")

cards = []
for path in sorted(glob.glob("assets/diagrams/*")):
    slug, ext = os.path.splitext(os.path.basename(path))
    body = open(path, encoding="utf-8").read()
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', body)
    size = f"{m.group(1)} by {m.group(2)}" if m else "html"
    used = ", ".join(sorted(usage.get(slug, []))) or "not on a page"
    grammar = BY_SLUG.get(slug, "flow")
    cards.append(f'''<section class="card">
  <div class="meta"><span class="eyebrow">{slug}</span><span class="mono">{grammar} / {size} / {used}</span></div>
  <div class="fig">{body}</div>
</section>''')

html = f'''<!doctype html>
<meta charset="utf-8">
<title>QA diagrams</title>
<link rel="stylesheet" href="../site.css">
<style>
  body {{ padding: 40px; }}
  h1 {{ font-size: 1.5rem; margin-bottom: 8px; }}
  .lede {{ margin-bottom: 40px; max-width: 46em; }}
  .card {{ border-top: 1px solid var(--line-soft); padding: 24px 0 32px; }}
  .card .meta {{ display: flex; justify-content: space-between; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }}
  .card .fig {{ max-width: 1000px; }}
  .card .fig svg {{ width: 100%; height: auto; display: block; }}
  .card .fig .callouts {{ max-width: 520px; }}
</style>
<h1>Every figure, {len(cards)} of them</h1>
<p class="lede">Grammar, native size, and where it lives. Figures marked "not on a page" are rendered workflow exports kept for the record.</p>
{"".join(cards)}
'''
os.makedirs("qa", exist_ok=True)
open("qa/diagrams.html", "w", encoding="utf-8").write(html)
counts = {}
for slug in usage:
    counts[BY_SLUG.get(slug, "flow")] = counts.get(BY_SLUG.get(slug, "flow"), 0) + 1
print("qa/diagrams.html:", len(cards), "figures;", "on pages by grammar:", dict(sorted(counts.items())))

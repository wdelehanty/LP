#!/usr/bin/env python3
"""Write sitemap.xml from the public pages, lastmod from git. Stdlib only.
Usage: sitemap.py [repo root]. Run by release.sh; excludes pitches, archive, qa."""
import datetime, os, subprocess, sys
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
SITE = "https://williamdelehanty.com"
SKIP = ("pitches", "archive", "qa", "intake", "worker", "node_modules", "assets", "raw", "scripts")
pages = []
for dp, dn, fn in os.walk(ROOT):
    rel = os.path.relpath(dp, ROOT)
    if rel != "." and (rel.split(os.sep)[0] in SKIP or rel.startswith(".")): dn[:] = []; continue
    if "index.html" in fn:
        pages.append("/" if rel == "." else "/" + rel.replace(os.sep, "/") + "/")
    for f in fn:  # notes posts live as slug/index.html too; nothing else is a page
        pass
def lastmod(url):
    p = os.path.join(ROOT, ("index.html" if url == "/" else url.strip("/") + "/index.html"))
    d = subprocess.run(["git", "log", "-1", "--format=%cs", "--", p], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    return d or datetime.date.today().isoformat()
pages.sort(key=lambda u: (u.count("/"), u))
out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in pages:
    out.append(f"  <url><loc>{SITE}{u}</loc><lastmod>{lastmod(u)}</lastmod></url>")
out.append("</urlset>")
open(os.path.join(ROOT, "sitemap.xml"), "w").write("\n".join(out) + "\n")
print(f"sitemap.xml: {len(pages)} urls")

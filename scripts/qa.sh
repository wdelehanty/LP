#!/bin/sh
# QA gate, run before every ship. Exits non-zero on any failure.
# Checks: em-dashes in tracked files, banned client names, HTML parse of every
# public page, version stamp, referenced assets exist, no leftover slots,
# JSON-LD parses, canonical present, OG images exist, sitemap URLs resolve.
# Usage: sh scripts/qa.sh vX.Y.Z
cd "$(dirname "$0")/.."
v="$1"; fail=0; dash=$(printf '\342\200\224')  # U+2014, kept out of this file as a literal
if git ls-files | grep -v -E '^(raw/|intake/|assets/fonts/)' | xargs grep -l -- "$dash" 2>/dev/null | grep -q .; then
  echo "FAIL em-dash:"; git ls-files | grep -v -E '^(raw/|intake/|assets/fonts/)' | xargs grep -l -- "$dash"; fail=1
else echo "ok   em-dash grep"; fi
if grep -rn -E "T-Mobile|ServiceNow|Indeed" --include="*.html" --include="*.md" --include="*.svg" . 2>/dev/null | grep -v -E "^\./(qa|pitches|archive|intake|node_modules)/" | grep -v "CC_Brief" | grep -q .; then
  echo "FAIL banned names:"; grep -rn -E "T-Mobile|ServiceNow|Indeed" --include="*.html" --include="*.md" . | grep -v -E "^\./(qa|pitches|archive|intake)/" | grep -v CC_Brief; fail=1
else echo "ok   banned names"; fi
python3 - "$v" <<'PYEOF' || fail=1
import glob, html.parser, json, os, re, sys
v = sys.argv[1]; bad = 0
pages = [f for f in glob.glob("**/*.html", recursive=True) if not f.startswith(("qa/", "intake/", "pitches/", "archive/", "worker/", "node_modules/", "assets/", "scripts/"))]
for f in pages:
    s = open(f, encoding="utf-8").read()
    try: html.parser.HTMLParser().feed(s)
    except Exception as e: print("FAIL parse", f, e); bad += 1
    if v and f != "404.html" and f'data-stamp="version">{v}<' not in s: print("FAIL stamp", f); bad += 1
    if "<b>slot</b>" in s or 'class="slot' in s: print("FAIL slot left", f); bad += 1
    for m in re.finditer(r'(?:src|href|poster)="((?:\.\./|/)?assets/[^"#?]+)"', s):
        rel = m.group(1); path = rel.lstrip("/") if rel.startswith("/") else os.path.normpath(os.path.join(os.path.dirname(f), rel))
        if not os.path.exists(path): print("FAIL missing asset", f, rel); bad += 1
    for m in re.finditer(r'data-loop="([^"]+)"', s):
        base = os.path.normpath(os.path.join(os.path.dirname(f), m.group(1)))
        for ext in (".mp4", ".webm"):
            if not os.path.exists(base + ext): print("FAIL loop source missing", f, base + ext); bad += 1
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: json.loads(m.group(1))
        except Exception as e: print("FAIL json-ld", f, e); bad += 1
    if f != "404.html" and 'rel="canonical"' not in s: print("FAIL canonical", f); bad += 1
    for m in re.finditer(r'og:image" content="https://williamdelehanty.com/(assets/og/[^"]+)"', s):
        if not os.path.exists(m.group(1)): print("FAIL og image", f, m.group(1)); bad += 1
if os.path.exists("sitemap.xml"):
    for u in re.findall(r"<loc>https://williamdelehanty.com(/[^<]*)</loc>", open("sitemap.xml").read()):
        p = "index.html" if u == "/" else u.strip("/") + "/index.html"
        if not os.path.exists(p): print("FAIL sitemap url", u); bad += 1
print(("ok   " if not bad else "FAIL ") + f"{len(pages)} pages: parse, stamp, assets, loops, json-ld, canonical, og, sitemap")
sys.exit(1 if bad else 0)
PYEOF
[ "$fail" = 0 ] && echo "QA gate: pass" || { echo "QA gate: FAIL"; exit 1; }

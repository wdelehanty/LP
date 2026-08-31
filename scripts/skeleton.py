#!/usr/bin/env python3
"""Stamp out the shared page chrome for a new v2 page.

Usage: python3 scripts/skeleton.py <relpath-under-v2> <title> <description>
Writes v2/<relpath>/index.html with nav, rail, footer, beacon, and a
CONTENT placeholder to be replaced by hand. Refuses to overwrite.
"""
import os
import sys

TPL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<!-- Preview build. Remove noindex at cutover. -->
<meta name="robots" content="noindex">
<link rel="preload" href="{p}assets/fonts/barlow-600.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{p}assets/fonts/barlow-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{p}assets/fonts/barlow-condensed-600.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{p}assets/fonts/plex-mono-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{p}site.css">
</head>
<body>

<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <defs>
    <marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0.5 L7,4 L0,7.5" fill="none" stroke="#3A4046" stroke-width="1.2"/>
    </marker>
  </defs>
</svg>

<nav class="nav" aria-label="Site">
  <div class="wrap">
    <a class="name" href="{p}">William Delehanty</a>
    <ul>
      <li><a href="{p}work/">Work</a></li>
      <li><a href="{p}stedd/">Stedd</a></li>
      <li><a href="{p}lab/">Lab</a></li>
      <li><a href="{p}stack/">Stack</a></li>
      <li><a href="{p}how-i-work/">How I work</a></li>
      <li><a href="{p}about/">About</a></li>
    </ul>
  </div>
</nav>

<div class="rail" role="status" aria-label="System status">
  <div class="wrap">
    <span class="item"><span class="dot"></span><b id="st-workflows">52</b>&nbsp;workflows</span>
    <span class="item"><span class="dot"></span><b id="st-active">36</b>&nbsp;active</span>
    <span class="item"><span class="dot"></span>last run&nbsp;<b id="st-lastrun">07:50 ET</b></span>
    <span class="item"><span class="dot"></span>site&nbsp;<b id="st-version" data-stamp="version">v2.0.0</b></span>
  </div>
</div>

<main>

<!-- CONTENT -->

</main>

<footer>
  <div class="wrap">
    <span class="mono">Built by hand in Warwick, NY. <span data-stamp="version">v2.0.0</span>. Last deploy <span data-stamp="date">2026-08-31</span>.</span>
    <span class="links mono">
      <a href="https://github.com/wdelehanty">GitHub</a>
      <a href="https://www.linkedin.com/in/william-delehanty-18a01661">LinkedIn</a>
      <a href="mailto:wdelehanty@gmail.com">Email</a>
    </span>
  </div>
</footer>

<script>
(function(){{
  fetch('/status.json', {{cache: 'no-store'}})
    .then(function(r){{ return r.ok ? r.json() : null; }})
    .then(function(s){{
      if (!s) return;
      var map = {{ 'st-workflows': s.workflows, 'st-active': s.active, 'st-lastrun': s.last_run, 'st-version': s.site }};
      Object.keys(map).forEach(function(id){{
        var el = document.getElementById(id);
        if (el && map[id] != null) el.textContent = map[id];
      }});
    }})
    .catch(function(){{}});
}})();
</script>
<script>
(function(){{
  var c = new URLSearchParams(location.search).get('c') || '';
  if (!c || sessionStorage.getItem('b_' + c)) return;
  sessionStorage.setItem('b_' + c, '1');
  new Image().src = 'https://n8n.stedd.ai/webhook/kit-visit-p4n8t2'
    + '?token=vt7r3k9w2m5x&code=' + encodeURIComponent(c)
    + '&kit=' + encodeURIComponent(location.hostname.split('.')[0])
    + '&path=' + encodeURIComponent(location.pathname);
}})();
</script>
</body>
</html>
"""


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    rel, title, description = sys.argv[1:]
    depth = rel.count("/") + 1
    prefix = "../" * depth
    path = os.path.join(os.path.dirname(__file__), "..", "v2", rel, "index.html")
    path = os.path.normpath(path)
    if os.path.exists(path):
        raise SystemExit(f"{path} exists, not overwriting")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(TPL.format(title=title, description=description, p=prefix))
    print(path)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Notes: the index, the post template, and the RSS feed (Brief 8, item 7).

  notes.py new <slug> "<Title>" "<one-line description>"   writes notes/<slug>/index.html
  notes.py build                                            rewrites notes/index.html and notes/feed.xml

Posts are plain pages. The build reads each notes/<slug>/index.html for its
title (h1), date (<time datetime>), and description (meta), newest first.
Run from the repo root. Stdlib only.
"""
import datetime, email.utils, html, os, re, sys

SITE = "https://williamdelehanty.com"
NAV = """<nav class="nav" aria-label="Site">
  <div class="wrap">
    <a class="name" href="{root}">William Delehanty</a>
    <ul>
      <li><a href="{root}work/">Work</a></li>
      <li><a href="{root}stedd/">Stedd</a></li>
      <li><a href="{root}lab/">Lab</a></li>
      <li><a href="{root}notes/">Notes</a></li>
      <li><a href="{root}stack/">Stack</a></li>
      <li><a href="{root}how-i-work/">How I work</a></li>
      <li><a href="{root}about/">About</a></li>
    </ul>
  </div>
</nav>

<div class="rail" role="status" aria-label="Live status" data-status="https://wd-status.wdelehanty.workers.dev/api/status">
  <div class="wrap">
    <span class="item">workflows active: <b data-rail="workflows_active" data-count>41</b></span>
    <span class="dot" aria-hidden="true"></span>
    <span class="item">last morning round: <b data-rail="last_morning_round">Wed 07:00</b></span>
    <span class="dot" aria-hidden="true"></span>
    <span class="item">last deploy: <b data-stamp="date">2026-09-02</b></span>
  </div>
</div>
"""
FOOT = """<footer>
  <div class="wrap">
    <span class="mono">Built by hand in Warwick, NY. <span data-stamp="version">v2.6.2</span>. Last deploy <span data-stamp="date">2026-09-02</span>.</span>
    <span class="links mono">
      <a href="{root}notes/feed.xml">RSS</a>
      <a href="https://www.linkedin.com/in/williamdelehanty/">LinkedIn</a>
      <a href="mailto:wdelehanty@gmail.com">Email</a>
    </span>
  </div>
</footer>
"""
HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | William Delehanty</title>
<meta name="description" content="{description}">
<link rel="preload" href="{root}assets/fonts/barlow-600.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{root}assets/fonts/barlow-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{root}assets/fonts/barlow-condensed-600.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{root}assets/fonts/plex-mono-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="icon" type="image/svg+xml" href="/assets/img/favicon.svg">
<link rel="alternate" type="application/rss+xml" title="Notes, William Delehanty" href="/notes/feed.xml">
<meta property="og:title" content="{title} | William Delehanty">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{site}/assets/og/{og}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:url" content="{site}{url}">
<link rel="canonical" href="{site}{url}">
<meta property="og:type" content="{ogtype}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{site}/assets/og/{og}.png">
<link rel="stylesheet" href="{root}site.css">
<script defer src="{root}site.js"></script>
{ld}</head>
<body>

"""
POST = HEAD + NAV + """
<main>

<header class="cs-header">
  <div class="wrap">
    <div class="meta">
      <span class="eyebrow">Notes</span>
      <span class="mono"><time datetime="{iso}">{date}</time></span>
    </div>
    <h1>{title}</h1>
    <p class="outcome">{description}</p>
  </div>
</header>

<section class="cs-body">
  <div class="wrap">
    <div class="cs-main note-body">
{body}
    </div>
  </div>
</section>

<section class="cs-next">
  <div class="wrap">
    <a href="../">All notes</a>
  </div>
</section>

</main>

""" + FOOT + """
</body>
</html>
"""
INDEX = HEAD + NAV + """
<main>

<header class="cs-header">
  <div class="wrap">
    <div class="meta">
      <span class="eyebrow">Notes</span>
      <span class="mono">RSS at <a href="feed.xml">/notes/feed.xml</a></span>
    </div>
    <h1>Notes</h1>
    <p class="outcome">Short pieces on how the work actually gets done: attribution, lifecycle with a small team, and what changed with AI in the loop.</p>
  </div>
</header>

<section class="cs-body">
  <div class="wrap">
    <div class="cs-main">
{list}
    </div>
  </div>
</section>

</main>

""" + FOOT + """
</body>
</html>
"""
BODY_PLACEHOLDER = """      <p>First paragraph goes here. Body copy sits at the case study measure. One figure is allowed:</p>
      <figure class="fig">
        <div class="frame r43"><img src="../../assets/img/REPLACE.jpg" alt="" width="1400" height="1050" loading="lazy"></div>
        <figcaption class="mono caption">Caption.</figcaption>
      </figure>
      <p>Second paragraph.</p>"""

def posts():
    out = []
    for slug in sorted(os.listdir("notes")):
        p = os.path.join("notes", slug, "index.html")
        if not os.path.isfile(p): continue
        s = open(p, encoding="utf-8").read()
        title = html.unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S).group(1))).strip()
        iso = re.search(r'<time datetime="([^"]+)"', s).group(1)
        desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1))
        out.append((iso, slug, title, desc))
    return sorted(out, reverse=True)

def nice(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%B %-d, %Y")

def build():
    ps = posts()
    if ps:
        items = "\n".join(
            f'      <article class="note-row">\n        <span class="mono"><time datetime="{iso}">{nice(iso)}</time></span>\n        <h2><a href="{slug}/">{html.escape(title)}</a></h2>\n        <p>{html.escape(desc)}</p>\n      </article>'
            for iso, slug, title, desc in ps)
    else:
        items = '      <p class="mono">Three notes are in draft. The first lands with v2.7.1.</p>'
    ld = '<script type="application/ld+json">{"@context": "https://schema.org", "@type": "Blog", "name": "Notes", "url": "%s/notes/", "author": {"@type": "Person", "name": "William Delehanty", "url": "%s/"}}</script>\n' % (SITE, SITE)
    page = INDEX.format(root="../", site=SITE, title="Notes", description="Short pieces on attribution, lifecycle with a small team, and what changed with AI in the loop.", og="notes", url="/notes/", ogtype="website", ld=ld, list=items)
    open("notes/index.html", "w", encoding="utf-8").write(page)
    rss = ['<?xml version="1.0" encoding="UTF-8"?>', '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">', '<channel>',
           '<title>Notes, William Delehanty</title>', f'<link>{SITE}/notes/</link>',
           '<description>Short pieces on attribution, lifecycle with a small team, and what changed with AI in the loop.</description>',
           '<language>en-us</language>', f'<atom:link href="{SITE}/notes/feed.xml" rel="self" type="application/rss+xml"/>']
    for iso, slug, title, desc in ps:
        pub = email.utils.format_datetime(datetime.datetime.fromisoformat(iso + "T12:00:00+00:00"))
        rss += ['<item>', f'<title>{html.escape(title)}</title>', f'<link>{SITE}/notes/{slug}/</link>', f'<guid>{SITE}/notes/{slug}/</guid>',
                f'<pubDate>{pub}</pubDate>', f'<description>{html.escape(desc)}</description>', '</item>']
    rss += ['</channel>', '</rss>']
    open("notes/feed.xml", "w", encoding="utf-8").write("\n".join(rss) + "\n")
    print(f"notes: {len(ps)} posts, index and feed written")

def new(slug, title, desc):
    d = os.path.join("notes", slug); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "index.html")
    if os.path.exists(p): sys.exit(f"{p} exists")
    iso = datetime.date.today().isoformat()
    ld = '<script type="application/ld+json">{"@context": "https://schema.org", "@type": "BlogPosting", "headline": %s, "description": %s, "datePublished": "%s", "url": "%s/notes/%s/", "author": {"@type": "Person", "name": "William Delehanty", "url": "%s/"}}</script>\n' % (
        __import__("json").dumps(title), __import__("json").dumps(desc), iso, SITE, slug, SITE)
    page = POST.format(root="../../", site=SITE, title=html.escape(title), description=html.escape(desc), og="notes-" + slug, url=f"/notes/{slug}/", ogtype="article", ld=ld, iso=iso, date=nice(iso), body=BODY_PLACEHOLDER)
    open(p, "w", encoding="utf-8").write(page)
    print(f"wrote {p}; fill in the body, add the og entry to scripts/og.py PAGES, then notes.py build")

if __name__ == "__main__":
    os.makedirs("notes", exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "new": new(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    else: build()

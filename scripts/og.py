#!/usr/bin/env python3
"""Per-page Open Graph images in site tokens (Brief 8, item 6).

Reads each page's eyebrow and h1, draws a 1200 by 630 card on the site's
dark ground with the eyebrow in Barlow Condensed, the title in Barlow, and
a rail-style strip along the bottom with the site name. Writes
assets/og/<slug>.png. Fonts are the site's own woff2 files, converted to
TTF in a temp dir for Pillow (needs fonttools and brotli).

Usage: og.py [repo root]
"""
import html, os, re, sys, tempfile
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
BG, PANEL, LINE, SOFT, TEXT, MUTED, SIGNAL = "#15181B", "#1E2226", "#3A4046", "#2A2F34", "#E6E4DF", "#9AA0A6", "#F2C230"
W, H = 1200, 630
PAGES = [  # (path, slug, fallback eyebrow)
    ("index.html", "home", "Warwick, NY"),
    ("about/index.html", "about", "About"),
    ("work/index.html", "work", "Work"),
    ("stedd/index.html", "stedd", "Stedd"),
    ("lab/index.html", "lab", "Lab"),
    ("stack/index.html", "stack", "Stack"),
    ("how-i-work/index.html", "how-i-work", "How I work"),
    ("changelog/index.html", "changelog", "Changelog"),
    ("colophon/index.html", "colophon", "Colophon"),
    ("notes/index.html", "notes", "Notes"),
    ("work/forbes-demand-engine/index.html", "work-forbes-demand-engine", "Case study"),
    ("work/forbes-connect-cdp/index.html", "work-forbes-connect-cdp", "Case study"),
    ("work/dg-playbook-and-ai/index.html", "work-dg-playbook-and-ai", "Case study"),
    ("work/self-serve-advertising-lifecycle/index.html", "work-self-serve-advertising-lifecycle", "Case study"),
    ("work/enterprise-partner-programs/index.html", "work-enterprise-partner-programs", "Case study"),
    ("work/under-30-summit-2018/index.html", "work-under-30-summit-2018", "Case study"),
    ("work/forbes8-lifecycle/index.html", "work-forbes8-lifecycle", "Case study"),
]

def ttf(name, tmp):
    src = os.path.join(ROOT, "assets/fonts", name + ".woff2")
    out = os.path.join(tmp, name + ".ttf")
    if not os.path.exists(out):
        f = TTFont(src); f.flavor = None; f.save(out)
    return out

def text_of(fragment):
    return html.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()

def read(path, fallback):
    s = open(os.path.join(ROOT, path), encoding="utf-8").read()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
    title = re.sub(r"\s+", " ", text_of(m.group(1))) if m else fallback
    m = re.search(r'<meta name="description" content="([^"]*)"', s)
    desc = html.unescape(m.group(1)) if m else ""
    m = re.search(r'class="eyebrow"[^>]*>(.*?)</', s, re.S)
    eyebrow = text_of(m.group(1)) if m else fallback
    if path == "index.html": eyebrow = fallback  # the home hero carries no eyebrow; the first one is a section's
    lead = title.rstrip(".") + ": "
    if desc.startswith(lead): desc = desc[len(lead):].strip(); desc = desc[0].upper() + desc[1:]
    return eyebrow, title, desc

def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= width or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def card(eyebrow, title, desc, out, fonts):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    for x in range(0, W, 56): d.line([(x, 0), (x, H)], fill=SOFT, width=1)
    for y in range(0, H, 56): d.line([(0, y), (W, y)], fill=SOFT, width=1)
    d.rectangle([(0, 0), (W, H)], outline=LINE, width=2)
    # eyebrow with the short signal rule above it
    d.rectangle([(72, 84), (128, 86)], fill=SIGNAL)
    d.text((72, 104), eyebrow.upper(), font=fonts["eyebrow"], fill=SIGNAL)
    # title, wrapped, sized down if it runs long
    for size in (76, 68, 60, 52):
        f = ImageFont.truetype(fonts["title_path"], size)
        lines = wrap(d, title, f, W - 144)
        if len(lines) <= 3: break
    y = 172
    for ln in lines:
        d.text((72, y), ln, font=f, fill=TEXT); y += int(size * 1.12)
    # the page description, muted, under the title
    y += 18
    for ln in wrap(d, desc, fonts["desc"], W - 200)[:3]:
        if y > H - 78 - 48: break
        d.text((72, y), ln, font=fonts["desc"], fill=MUTED); y += 42
    # rail-style strip along the bottom
    d.rectangle([(0, H - 78), (W, H)], fill=PANEL)
    d.line([(0, H - 78), (W, H - 78)], fill=LINE, width=1)
    d.text((72, H - 52), "williamdelehanty.com", font=fonts["mono"], fill=MUTED)
    d.ellipse([(340, H - 44), (348, H - 36)], fill=SIGNAL)
    d.text((364, H - 52), "revenue systems, built by hand", font=fonts["mono"], fill=MUTED)
    name = "WILLIAM DELEHANTY"
    d.text((W - 72 - d.textlength(name, font=fonts["name"]), H - 54), name, font=fonts["name"], fill=TEXT)
    im.save(out, optimize=True)

def main():
    import glob
    for f in sorted(glob.glob(os.path.join(ROOT, "notes/*/index.html"))):  # notes posts
        slug = f.split(os.sep)[-2]; PAGES.append((os.path.relpath(f, ROOT), "notes-" + slug, "Notes"))
    tmp = os.path.join(tempfile.gettempdir(), "lp-og-fonts"); os.makedirs(tmp, exist_ok=True)
    fonts = {
        "eyebrow": ImageFont.truetype(ttf("barlow-condensed-600", tmp), 30),
        "name": ImageFont.truetype(ttf("barlow-condensed-600", tmp), 26),
        "mono": ImageFont.truetype(ttf("plex-mono-400", tmp), 20),
        "desc": ImageFont.truetype(ttf("barlow-400", tmp), 30),
        "title_path": ttf("barlow-600", tmp),
    }
    os.makedirs(os.path.join(ROOT, "assets/og"), exist_ok=True)
    for path, slug, fb in PAGES:
        if not os.path.exists(os.path.join(ROOT, path)): continue
        eyebrow, title, desc = read(path, fb)
        out = os.path.join(ROOT, "assets/og", slug + ".png")
        card(eyebrow, title, desc, out, fonts)
        print(f"{slug}: {eyebrow} / {title}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Draw the hand-designed diagrams in site tokens.

Seven grammars, all in the same fonts, strokes, and colors, so a page can
vary its figures without leaving the visual language:

  flow       boxes and arrows (box, arrow)      systems and pipelines
  ledger     a table with a signal total row    lists of numbers, before/after
  timeline   a rule with ticks, one yellow      flights, rollouts, sequences
  layers     stacked full-width bands           stacks, what sits on what
  split      two panels, muted left             how it was, how it is
  swimlanes  lanes with hand-off arrows         a human and a system taking turns
  bars       horizontal bars, longest yellow    inventory numbers only
  callouts   a real screenshot with pins        HTML, not SVG

Figures are authored here node by node and written to assets/diagrams/.
Usage: draw_architecture.py <out-dir>
"""
import os
import sys

BG_PANEL = "#1E2226"
BG = "#15181B"
LINE = "#3A4046"
LINE_SOFT = "#2A2F34"
TEXT = "#E6E4DF"
MUTED = "#9AA0A6"
SIGNAL = "#F2C230"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def head_style(size=13, tracking=".08em"):
    return f"font:600 {size}px 'Barlow Condensed',sans-serif;letter-spacing:{tracking};text-transform:uppercase"


def mono_style(size=10):
    return f"font:400 {size}px 'IBM Plex Mono',monospace"


def body_style(size=12):
    return f"font:400 {size}px Barlow,sans-serif"


def text(x, y, s, style, fill=TEXT, anchor=None):
    a = f' text-anchor="{anchor}"' if anchor else ""
    return f'<text x="{x}" y="{y}"{a} style="{style}" fill="{fill}">{esc(s)}</text>'


# ---------------------------------------------------------------- flow

def box(x, y, w, h, label, sub=None, own=False, size=0):
    """A node. size adds to the type sizes (the demand engine runs at +2)."""
    stroke = SIGNAL if own else LINE
    sw = 1.5 if own else 1
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{BG_PANEL}" stroke="{stroke}" stroke-width="{sw}"/>',
           text(x + 14, y + 24 + size, label, head_style(13 + size))]
    if sub:
        out.append(text(x + 14, y + 42 + size * 2, sub, mono_style(10 + size), MUTED))
    return "\n".join(out)


def arrow(x1, y1, x2, y2, mid, dashed=False):
    dash = ' stroke-dasharray="4 4"' if dashed else ""
    if abs(y1 - y2) < 1 or abs(x1 - x2) < 1:
        d = f"M{x1},{y1} L{x2},{y2}"
    else:
        mx = (x1 + x2) / 2
        d = f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}"
    return f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1"{dash} marker-end="url(#{mid})"/>'


def note(x, y, s, size=0):
    return text(x, y, s, mono_style(11 + size), MUTED)


def title_block(title, subtitle=None, x=20, y=22):
    out = [text(x, y, title, head_style(12))]
    if subtitle:
        out.append(text(x, y + 16, subtitle, mono_style(10), MUTED))
    return "\n".join(out)


def doc(name, inner, w, h, label, out_dir):
    mid = f"ar-{name}"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">\n'
           f'<defs><marker id="{mid}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           f'<path d="M0,0.5 L7,4 L0,7.5" fill="none" stroke="{LINE}" stroke-width="1.2"/></marker></defs>\n'
           + inner.replace("MID", mid) + "\n</svg>\n")
    open(os.path.join(out_dir, name + ".svg"), "w").write(svg)
    print(f"{name}.svg  {w}x{h}")


# ---------------------------------------------------------------- ledger

def ledger(name, title, subtitle, columns, rows, total, label, out_dir, w=900):
    """A two or three column table. Headers in condensed caps, values in
    mono, hairline rules, the total row in signal."""
    p = [title_block(title, subtitle)]
    top = 64
    row_h = 32
    ncol = len(columns)
    first_w = int(w * 0.46) if ncol > 2 else int(w * 0.5)
    xs = [20] + [first_w + (i - 1) * int((w - first_w - 20) / (ncol - 1)) + (w - 20 if i == ncol - 1 else 0) * 0 for i in range(1, ncol)]
    right = w - 20
    y = top
    for i, c in enumerate(columns):
        anchor = "end" if i == ncol - 1 else None
        x = right if i == ncol - 1 else xs[i]
        p.append(text(x, y, c, head_style(12), MUTED, anchor))
    y += 10
    p.append(f'<line x1="20" y1="{y}" x2="{right}" y2="{y}" stroke="{LINE}" stroke-width="1"/>')
    for r in rows:
        y += row_h
        for i, v in enumerate(r):
            anchor = "end" if i == ncol - 1 else None
            x = right if i == ncol - 1 else xs[i]
            style = body_style(13) if i == 0 else mono_style(11)
            p.append(text(x, y, v, style, TEXT if i == 0 else MUTED, anchor))
        p.append(f'<line x1="20" y1="{y + 11}" x2="{right}" y2="{y + 11}" stroke="{LINE_SOFT}" stroke-width="1"/>')
    y += row_h + 4
    p.append(f'<line x1="20" y1="{y - 22}" x2="{right}" y2="{y - 22}" stroke="{SIGNAL}" stroke-width="1"/>')
    for i, v in enumerate(total):
        anchor = "end" if i == ncol - 1 else None
        x = right if i == ncol - 1 else xs[i]
        style = head_style(13) if i == 0 else mono_style(12)
        p.append(text(x, y, v, style, SIGNAL, anchor))
    h = y + 26
    doc(name, "\n".join(p), w, h, label, out_dir)


# ---------------------------------------------------------------- timeline

def timeline(name, title, subtitle, events, label, out_dir, w=900, h=None, note_text=None):
    """events: (position 0..1, label, sublabel, side 'above'|'below', key).
    One yellow tick for the moment that matters."""
    p = [title_block(title, subtitle)]
    base_y = 132 if w > 600 else 168
    x0, x1 = 30, w - 30
    p.append(f'<line x1="{x0}" y1="{base_y}" x2="{x1}" y2="{base_y}" stroke="{LINE}" stroke-width="1"/>')
    for pos, lab, sub, side, key in events:
        x = x0 + (x1 - x0) * pos
        col = SIGNAL if key else LINE
        p.append(f'<line x1="{x}" y1="{base_y - 10}" x2="{x}" y2="{base_y + 10}" stroke="{col}" stroke-width="{2 if key else 1}"/>')
        if key:
            p.append(f'<circle cx="{x}" cy="{base_y}" r="4" fill="{SIGNAL}"/>')
        anchor = "middle"
        ax = min(max(x, 70), w - 70)
        if side == "above":
            p.append(text(ax, base_y - 36, lab, head_style(12), SIGNAL if key else TEXT, anchor))
            if sub:
                p.append(text(ax, base_y - 20, sub, mono_style(10), MUTED, anchor))
        else:
            p.append(text(ax, base_y + 30, lab, head_style(12), SIGNAL if key else TEXT, anchor))
            if sub:
                p.append(text(ax, base_y + 46, sub, mono_style(10), MUTED, anchor))
    hh = h or (base_y + 96)
    if note_text:
        p.append(note(20, hh - 16, note_text))
    doc(name, "\n".join(p), w, hh, label, out_dir)


# ---------------------------------------------------------------- layers

def layers(name, title, subtitle, bands, label, out_dir, w=900, note_text=None):
    """bands: (label, description, own) top to bottom. Full-width hairline
    rectangles, label left, description right, owned layers in signal."""
    p = [title_block(title, subtitle)]
    y = 56
    band_h = 52
    for lab, desc, own in bands:
        stroke = SIGNAL if own else LINE
        p.append(f'<rect x="20" y="{y}" width="{w - 40}" height="{band_h}" rx="2" fill="{BG_PANEL}" stroke="{stroke}" stroke-width="{1.5 if own else 1}"/>')
        p.append(text(36, y + 31, lab, head_style(13), TEXT))
        p.append(text(w - 36, y + 31, desc, mono_style(11), MUTED, "end"))
        y += band_h + 8
    h = y + 24 if note_text else y + 8
    if note_text:
        p.append(note(20, y + 12, note_text))
    doc(name, "\n".join(p), w, h, label, out_dir)


# ---------------------------------------------------------------- split

def split(name, title, subtitle, before, after, label, out_dir, w=480, h=320):
    """before, after: (heading, lines). Muted left, full strength right,
    a vertical hairline and a small arrow between them."""
    p = [title_block(title, subtitle)]
    mid = w // 2
    top, bottom = 80, h - 40
    p.append(f'<line x1="{mid}" y1="{top}" x2="{mid}" y2="{bottom}" stroke="{LINE}" stroke-width="1"/>')
    ay = (top + bottom) // 2
    p.append(f'<path d="M{mid - 14},{ay} L{mid + 13},{ay}" fill="none" stroke="{LINE}" stroke-width="1" marker-end="url(#MID)"/>')
    p.append(f'<rect x="{mid - 22}" y="{ay - 12}" width="44" height="24" fill="{BG_PANEL}"/>')
    p.append(f'<path d="M{mid - 12},{ay} L{mid + 11},{ay}" fill="none" stroke="{SIGNAL}" stroke-width="1" marker-end="url(#MID)"/>')
    for i, (heading, lines) in enumerate((before, after)):
        x = 24 if i == 0 else mid + 24
        col_head = MUTED if i == 0 else TEXT
        col_line = MUTED if i == 0 else TEXT
        p.append(text(x, top + 22, heading, head_style(13), col_head))
        yy = top + 48
        for ln in lines:
            p.append(text(x, yy, ln, mono_style(10), col_line if i else MUTED))
            yy += 16
    p.append(text(24, h - 14, "before", mono_style(10), MUTED))
    p.append(text(mid + 24, h - 14, "after", mono_style(10), SIGNAL))
    doc(name, "\n".join(p), w, h, label, out_dir)


# ---------------------------------------------------------------- swimlanes

def swimlanes(name, title, subtitle, lanes, steps, edges, label, out_dir, w=900, note_text=None):
    """lanes: names top to bottom. steps: (id, lane, column, label, sub).
    edges: (from_id, to_id, dashed). Hand-offs cross lanes as curves."""
    p = [title_block(title, subtitle)]
    lane_h = 86
    top = 56
    label_w = 118
    box_w, gap = 122, 30
    ncol = max(s[2] for s in steps) + 1
    for i, lane in enumerate(lanes):
        y = top + i * lane_h
        p.append(f'<rect x="20" y="{y}" width="{w - 40}" height="{lane_h}" fill="{BG_PANEL if i % 2 == 0 else BG}" stroke="{LINE_SOFT}" stroke-width="1"/>')
        p.append(text(34, y + lane_h / 2 + 5, lane, head_style(12), MUTED))
    pos = {}
    for sid, lane, col, lab, sub in steps:
        x = 20 + label_w + col * (box_w + gap)
        y = top + lane * lane_h + (lane_h - 50) / 2
        pos[sid] = (x, y)
        p.append(f'<rect x="{x}" y="{y}" width="{box_w}" height="50" rx="2" fill="{BG_PANEL}" stroke="{LINE}" stroke-width="1"/>')
        p.append(text(x + 10, y + 21, lab, head_style(11, ".06em"), TEXT))
        if sub:
            p.append(text(x + 10, y + 38, sub, mono_style(9), MUTED))
    for a, b, dashed in edges:
        ax, ay = pos[a]
        bx, by = pos[b]
        if abs(ay - by) < 1:
            p.append(arrow(ax + box_w, ay + 25, bx - 1, by + 25, "MID", dashed))
        elif bx > ax:
            p.append(arrow(ax + box_w, ay + 25, bx - 1, by + 25, "MID", dashed))
        else:
            sy = ay + (50 if by > ay else 0)
            ty = by + (0 if by > ay else 50)
            d = f"M{ax + box_w / 2},{sy} C{ax + box_w / 2},{(sy + ty) / 2} {bx + box_w / 2},{(sy + ty) / 2} {bx + box_w / 2},{ty}"
            dash = ' stroke-dasharray="4 4"' if dashed else ""
            p.append(f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1"{dash} marker-end="url(#MID)"/>')
    h = top + len(lanes) * lane_h + (36 if note_text else 12)
    if note_text:
        p.append(note(20, h - 12, note_text))
    doc(name, "\n".join(p), w, h, label, out_dir)


# ---------------------------------------------------------------- bars

def bars(name, title, subtitle, series, label, out_dir, w=900, note_text=None):
    """series: (label, value, display). Inventory numbers only. The longest
    bar is signal, the rest are line-colored."""
    p = [title_block(title, subtitle)]
    top = 60
    row_h = 34
    label_w = 190
    maxv = max(v for _, v, _ in series) or 1
    track = w - 40 - label_w - 90
    y = top
    for lab, v, disp in series:
        length = max(4, int(track * v / maxv))
        col = SIGNAL if v == maxv else LINE
        p.append(text(20, y + 15, lab, head_style(12), TEXT))
        p.append(f'<rect x="{20 + label_w}" y="{y + 3}" width="{length}" height="16" rx="1" fill="{col}"/>')
        p.append(text(20 + label_w + length + 10, y + 15, disp, mono_style(11), TEXT if v == maxv else MUTED))
        y += row_h
    h = y + (30 if note_text else 8)
    if note_text:
        p.append(note(20, h - 12, note_text))
    doc(name, "\n".join(p), w, h, label, out_dir)


# ---------------------------------------------------------------- callouts (HTML)

def callouts(name, img_src, alt, width, height, pins, out_dir):
    """A real screenshot with numbered signal pins and a mono key. Written
    as an HTML fragment; inline_diagrams.py passes it through untouched.
    pins: (x_pct, y_pct, key_text)."""
    parts = ['<div class="callouts">',
             f'  <div class="photo-frame frame auto grain"><img src="{img_src}" alt="{esc(alt)}" width="{width}" height="{height}" loading="lazy">']
    for i, (x, y, _) in enumerate(pins, 1):
        parts.append(f'    <span class="pin" style="left:{x}%;top:{y}%" aria-hidden="true">{i}</span>')
    parts.append('  </div>')
    parts.append('  <ol class="mono key">')
    for _, _, k in pins:
        parts.append(f'    <li>{esc(k)}</li>')
    parts.append('  </ol>')
    parts.append('</div>')
    open(os.path.join(out_dir, name + ".html"), "w").write("\n".join(parts) + "\n")
    print(f"{name}.html  callouts, {len(pins)} pins")


# ---------------------------------------------------------------- plates (3:2 flow cards)

def plate(name, title, subtitle, boxes, notes, label, out_dir, arrows=True, loop=False):
    """A 480 by 320 flow plate for the 3:2 frames."""
    W, H = 480, 320
    p = [title_block(title, subtitle, 20, 34)]
    n = len(boxes)
    w, gap = (132, 24) if n == 3 else (200, 32)
    x0 = (W - (n * w + (n - 1) * gap)) // 2
    y, h = 118, 52
    for i, (lab, subs, own) in enumerate(boxes):
        x = x0 + i * (w + gap)
        stroke = SIGNAL if own else LINE
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{BG_PANEL}" stroke="{stroke}" stroke-width="{1.5 if own else 1}"/>')
        p.append(text(x + 12, y + 31, lab, head_style(11, ".06em"), TEXT))
        for j, sub in enumerate(subs or []):
            p.append(text(x + w / 2, y + h + 20 + j * 14, sub, mono_style(10), MUTED, "middle"))
        if arrows and i < n - 1:
            p.append(arrow(x + w, y + h / 2, x + w + gap - 1, y + h / 2, "MID"))
    for k, t in enumerate(notes):
        p.append(text(20, 282 + k * 18, t, mono_style(10.5), MUTED))
    doc(name, "\n".join(p), W, H, label, out_dir)


def loop_plate(name, title, subtitle, nodes, notes, label, out_dir):
    """Three nodes on a circle with arrows running around it. For a loop
    that is actually a loop."""
    import math
    W, H = 480, 320
    p = [title_block(title, subtitle, 20, 34)]
    cx, cy, r = 250, 178, 88
    bw, bh = 116, 42
    angles = [-90, 30, 150]
    centers = []
    for (lab, sub, own), ang in zip(nodes, angles):
        a = math.radians(ang)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        centers.append((x, y))
        stroke = SIGNAL if own else LINE
        p.append(f'<rect x="{x - bw / 2:.1f}" y="{y - bh / 2:.1f}" width="{bw}" height="{bh}" rx="2" fill="{BG_PANEL}" stroke="{stroke}" stroke-width="{1.5 if own else 1}"/>')
        p.append(text(x, y - 3, lab, head_style(11, ".06em"), TEXT, "middle"))
        if sub:
            p.append(text(x, y + 12, sub, mono_style(9), MUTED, "middle"))
    for i in range(3):
        a1 = math.radians(angles[i] + 24)
        a2 = math.radians(angles[(i + 1) % 3] - 24)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
        p.append(f'<path d="M{x1:.1f},{y1:.1f} A{r},{r} 0 0 1 {x2:.1f},{y2:.1f}" fill="none" stroke="{LINE}" stroke-width="1" stroke-dasharray="4 4" marker-end="url(#MID)"/>')
    for k, t in enumerate(notes):
        p.append(text(20, 282 + k * 18, t, mono_style(10.5), MUTED))
    doc(name, "\n".join(p), W, H, label, out_dir)


# ================================================================ figures

def demand_engine_full(out_dir):
    """The one place the flow grammar earns it. Type runs 2px larger."""
    p = []
    xs = [10, 190, 370, 550, 730]
    labels = [
        ("Acquisition", "paid / content / partner", True),
        ("CDP", "18m+ profiles", True),
        ("Lifecycle", "nurture / reengage", True),
        ("CRM routing", "speed to lead", True),
        ("Sales", "outreach library", False),
    ]
    for x, (l, s, own) in zip(xs, labels):
        p.append(box(x, 10, 160, 60, l, s, own, size=2))
        if x != xs[-1]:
            p.append(arrow(x + 160, 40, x + 180, 40, "MID"))
    p.append(box(10, 124, 880, 56, "Measurement", "performance console / qbr frameworks / contact-role attribution", True, size=2))
    for x in xs:
        p.append(arrow(x + 80, 124, x + 80, 70, "MID", dashed=True))
    p.append(note(10, 214, "dashed: every stage reports into the same measurement layer, which is where the influenced-revenue number comes from", size=2))
    p.append(note(10, 236, "yellow outline: the parts I own", size=2))
    doc("demand-engine-full", "\n".join(p), 900, 250,
        "The full demand engine: acquisition feeds the CDP, then lifecycle, then CRM routing, then sales, with a shared measurement layer of the performance console, QBR frameworks, and contact-role attribution underneath all stages.", out_dir)


def funnel(out_dir):
    swimlanes("funnel", "The mechanism behind the ~2.5x", "forbes b2b / who does what, in order",
              ["Marketing", "Sales"],
              [("cap", 0, 0, "Capture", "forms and pages"),
               ("nur", 0, 1, "Nurture", "onboard, reengage"),
               ("route", 0, 2, "Route", "speed to lead"),
               ("work", 1, 3, "Work the lead", "outreach library"),
               ("close", 1, 4, "Close", "contact role logged"),
               ("attr", 0, 5, "Attribute", "conservative count")],
              [("cap", "nur", False), ("nur", "route", False), ("route", "work", False),
               ("work", "close", False), ("close", "attr", True)],
              "The funnel as two lanes: marketing captures, nurtures, and routes; sales works the lead from the outreach library and closes; the closed opportunity's contact roles come back as attribution. About 2.5x conversion improvement across capture, nurture, and routing.",
              out_dir, w=1040, note_text="~2.5x conversion improvement across capture, nurture, and routing; dashed: attribution reads the closed opportunity")


def connect_cdp(out_dir):
    layers("connect-cdp", "Forbes Connect, what sits on what", "the conversion layer on the cdp",
           [("Forbes.com", "dialogues and progressive profiling, targeted by what the reader has read and done", False),
            ("BlueConic CDP", "18m+ profiles, behavioral segments, predictive ltv, third-party enrichment", True),
            ("Pardot", "nurture programs; a new profile lands here without anyone touching it", False),
            ("Salesforce", "routing to sellers, contact-role attribution", False)],
           "Forbes Connect as layers: the site's dialogues and progressive profiling on top, the BlueConic CDP beneath with 18 million plus profiles, then Pardot for nurture and Salesforce for routing and attribution.",
           out_dir, note_text="yellow outline: the layer I own end to end; anonymous readers become identified profiles on site and route down")


def profiling_timeline(out_dir):
    timeline("profiling-timeline", "Progressive profiling", "forbes connect / one ask per visit",
             [(0.08, "First visit", "one field", "above", False),
              (0.5, "Next visit", "one more field", "below", False),
              (0.92, "Known profile", "segmented, routed", "above", True)],
             "Progressive profiling on a timeline: one field on the first visit, one more on the next, until the reader is a known profile that gets segmented and routed.",
             out_dir, w=480, h=320, note_text="the profile fills in over a few visits; nobody ever sees a long form")


def connect_callouts(out_dir):
    callouts("connect-callouts", "/assets/img/forbes-landing.jpg",
             "A Forbes partner landing page on a phone with numbered pins on the Connect with Us button, the audience eyebrow, and the audience numbers",
             595, 1100,
             [(46, 7, "The ask. One prompt, targeted by what the reader has read and done."),
              (50, 21.5, "The segment the page is built for."),
              (50, 92, "The audience numbers the page trades on.")],
             out_dir)


def forbes8_lifecycle(out_dir):
    timeline("forbes8-lifecycle", "Forbes8 lifecycle", "signup to lifetime value",
             [(0.03, "Signup", "day zero", "above", False),
              (0.24, "Activation", "the first few days, the sequence to first value", "below", True),
              (0.5, "Engagement", "programs across the base", "above", False),
              (0.74, "Retention", "keep them around", "below", False),
              (0.97, "LTV", "what it all points at", "above", False)],
             "The Forbes8 lifecycle as a timeline: signup, the activation sequence in the first few days, engagement, retention, and lifetime value, with every program tuned on incremental sales.",
             out_dir, note_text="the incremental-sales feedback loop tuned every program on sales effect")


def selfserve_timeline(out_dir):
    timeline("selfserve-timeline", "Self-serve lifecycle", "danads / no account manager, so all of it is built in",
             [(0.03, "Account created", "onboarding sequence starts", "above", False),
              (0.28, "First live campaign", "the onboarding goal", "below", True),
              (0.52, "Second campaign", "activation pushes the behaviors that predict it", "above", False),
              (0.76, "Stalled", "retention sequence", "below", False),
              (0.97, "Lapsed", "reengagement sequence", "above", False)],
             "The self-serve advertising lifecycle as a timeline: account creation starts onboarding toward a first live campaign, activation pushes toward a second, and retention and reengagement sequences catch stalled and lapsed advertisers.",
             out_dir, note_text="8 programs, 29 emails, written and built by one person, staged for launch")


def two_tier(out_dir):
    split("two-tier", "Two-tier product structure", "pitched to a national wireless carrier",
          ("One tier", ["one buyer depth", "one price point"]),
          ("Two tiers", ["a lighter buyer and a deeper one", "two price points", "one architecture underneath"]),
          "Two-tier product structure as a before and after: one buyer depth at one price point becomes two tiers at two price points on one architecture.",
          out_dir)


def two_bucket(out_dir):
    split("two-bucket", "The two-bucket model", "operating playbook / who does what",
          ("One bucket", ["contractor work,", "undifferentiated"]),
          ("Two buckets", ["trainable execution:", "custom gpts, one operator", "real expertise:", "outside rates"]),
          "The two-bucket contractor model as a before and after: undifferentiated contractor work becomes trainable execution through custom GPTs and one operator, with real expertise bought at outside rates.",
          out_dir)


def enterprise_program(out_dir):
    ledger("enterprise-program", "Enterprise partner programs", "the components, and where they stopped",
           ["Component", "Count"],
           [("Advertisers pitched", "3"),
            ("Channels per program", "3: content, research, retargeting"),
            ("Flagship deliverable", "1: a year-end insight report"),
            ("Product tiers, carrier pitch", "2"),
            ("Delivery", "CRM-ready, workable the same week")],
           ("Programs that ran", "0: all three stopped at the pitch"),
           "A ledger of the enterprise partner program: three advertisers pitched, three channels per program, one flagship year-end report, two product tiers in the carrier pitch, CRM-ready delivery, and zero programs run because all three stopped at the pitch stage.",
           out_dir)


def summit_program(out_dir):
    ledger("summit-program", "Under 30 Summit 2018", "the audience program by the numbers",
           ["Line", "Figure"],
           [("Budget", "~$500K"),
            ("Duration", "6 months, weekly pacing"),
            ("Team", "3"),
            ("Channels", "paid media, radio, out-of-home, startup hub"),
            ("International markets", "Nigeria, Ghana")],
           ("Attendees", "10,000+"),
           "A ledger of the 2018 Under 30 Summit audience program: roughly five hundred thousand dollars over six months, a team of three, paid media plus radio and out-of-home in Nigeria and Ghana and a startup hub, producing over ten thousand attendees.",
           out_dir)


def playbook_structure(out_dir):
    layers("playbook-structure", "The operating playbook", "what runs on what",
           [("10+ concurrent programs", "run by a team of two", False),
            ("Custom GPTs", "the trainable work runs through them; specialists keep the judgment calls", True),
            ("Standards", "what a program is, what every email has to contain, what counts as launch-ready", False),
            ("Prompt libraries", "the recurring work, versioned like anything else we ship", False),
            ("QA checklists", "gate everything before it ships, human or machine made", False),
            ("Governance", "what AI may touch, what needs human review, who owns the output", False)],
           "The operating playbook as layers: ten plus concurrent programs run on custom GPTs, which run on standards, prompt libraries, QA checklists, and governance.",
           out_dir, note_text="yellow outline: the layer the trainable work runs through")


def feedback_loop(out_dir):
    loop_plate("feedback-loop", "The incremental-sales loop", "forbes8 / how programs got tuned",
               [("Send", "lifecycle program", False),
                ("Sales effect", "incremental, measured", True),
                ("Tune", "adjust the program", False)],
               ["dashed: around again, every program judged on sales"],
               "The incremental-sales feedback loop drawn as a loop: a lifecycle send, its measured sales effect, a tuned program, and around again.",
               out_dir)


def morning_round_lanes(out_dir):
    swimlanes("morning-round-lanes", "The morning round", "job search / n8n, gmail, and me, taking turns",
              ["n8n", "Gmail", "Will"],
              [("sched", 0, 0, "8am schedule", "every day"),
               ("drafts", 1, 1, "Labeled drafts", "labeled only"),
               ("digest", 0, 2, "Build and send", "one digest"),
               ("approve", 2, 3, "Approve and send", "one tap"),
               ("send", 0, 4, "Send the draft", "as written, logged")],
              [("sched", "drafts", False), ("drafts", "digest", False), ("digest", "approve", False), ("approve", "send", False)],
              "The morning round as swimlanes: an n8n schedule collects labeled Gmail drafts, builds one digest, Will approves with one tap, and n8n sends the draft as written and logs it.",
              out_dir, note_text="fails closed if the label is missing: no label, no send button")


def live_booking_lanes(out_dir):
    swimlanes("live-booking-lanes", "Live booking", "stedd / the caller never waits on a callback",
              ["Caller", "Voice agent", "n8n + calendar"],
              [("call", 0, 0, "Calls in", "after hours too"),
               ("ask", 1, 1, "Proposes a time", "caller still on"),
               ("check", 2, 2, "Checks calendar", "live"),
               ("book", 2, 3, "Books or declines", "booked or busy"),
               ("confirm", 1, 4, "Confirms live", "or another time")],
              [("call", "ask", False), ("ask", "check", False), ("check", "book", False), ("book", "confirm", False)],
              "Live booking as swimlanes: a caller calls in, the voice agent proposes a time, n8n checks the calendar live and books or declines, and the agent confirms on the same call.",
              out_dir, note_text="nightly transcript QA reviews every completed call against the founder checklist")


def outcome_lanes(out_dir):
    swimlanes("outcome-lanes", "The outcome confirmation loop", "stedd / a weekly reply grammar",
              ["n8n", "Client"],
              [("sun", 0, 0, "Sunday 6pm email", "open leads, quotes"),
               ("reply", 1, 1, "Replies", "won, lost, pending"),
               ("parse", 0, 2, "Parse the reply", "outcomes applied"),
               ("wed", 0, 3, "Wednesday nudge", "skips who answered"),
               ("flag", 0, 4, "Flag the odd ones", "odd replies, to me")],
              [("sun", "reply", False), ("reply", "parse", False), ("sun", "wed", True), ("parse", "flag", True)],
              "The outcome confirmation loop as swimlanes: a Sunday email lists open leads and quotes, the client replies in a short grammar, n8n parses the reply onto the records, reminds on Wednesday, and flags anything it cannot read.",
              out_dir)


def monday_report_callouts(out_dir):
    callouts("monday-report-callouts", "/assets/img/stedd-monday-report.jpg",
             "The Stedd Monday Report sample with numbered pins on the recovered-this-week tile, the quotes-rescued tile, and the per-touch receipts",
             1320, 1240,
             [(26, 29, "Recovered this week: the number the report exists for."),
              (26, 58, "Quotes chased and won back, with the dollars."),
              (8, 74, "Numbered per-touch receipts: what happened and what it was worth.")],
             out_dir)


def lifeos_hub(out_dir):
    ledger("lifeos-hub", "Life OS hub", "notion / one page runs it; family surfaces left off on purpose",
           ["Surface", "What it holds"],
           [("Now", "project queue, stalest on top"),
            ("Capture inbox", "title only, keep moving"),
            ("Weekly review", "sundays, 15 minutes"),
            ("Knowledge base", "decisions and lessons"),
            ("Money and direction", "monthly, not weekly"),
            ("Logs", "maintenance, dog, builds"),
            ("Parked", "nothing gets deleted"),
            ("Operating manual", "read when away")],
           ("Capture hooks", "email label, home assistant, webhook, all through n8n"),
           "A ledger of the Life OS hub in Notion: a now queue, capture inbox, weekly review, knowledge base, money and direction, logs, parked items, and the operating manual, with email, Home Assistant, and webhook capture hooks feeding in through n8n.",
           out_dir)


def ha_waves(out_dir):
    timeline("ha-waves", "Home Assistant, three waves", "the cleanup, in order",
             [(0.1, "Wave 2", "naming: one scheme, every device", "above", False),
              (0.45, "Wave 3", "integrations consolidated, old gear retired", "below", False),
              (0.82, "Wave 4", "automations: goodnight lockdown, doorbell chime", "above", True)],
             "The Home Assistant cleanup as a timeline: wave two naming, wave three consolidated integrations with old hardware retired, wave four automations including the goodnight lockdown and doorbell chime.",
             out_dir, note_text="maintenance events post themselves to Notion through the n8n webhook; the dashboard stays in the house")


def wardrobe_system(out_dir):
    layers("wardrobe-system", "The wardrobe system", "what sits on what",
           [("iOS app", "testflight; reads and writes through the worker", False),
            ("Worker API", "cloudflare", True),
            ("Notion databases", "closet / his: 289 items, closet / hers, outfits: 14 use contexts", False),
            ("AI cataloguing", "photo in, item out", False)],
           "The wardrobe system as layers: an iOS app on TestFlight, a Cloudflare Worker API beneath it, his-and-hers closet databases and an outfits database in Notion, and AI photo cataloguing at the bottom.",
           out_dir, note_text="item count queried from the live database, 2026-08-31")


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    demand_engine_full(out)
    funnel(out)
    connect_cdp(out)
    profiling_timeline(out)
    connect_callouts(out)
    forbes8_lifecycle(out)
    selfserve_timeline(out)
    two_tier(out)
    two_bucket(out)
    enterprise_program(out)
    summit_program(out)
    playbook_structure(out)
    feedback_loop(out)
    morning_round_lanes(out)
    live_booking_lanes(out)
    outcome_lanes(out)
    monday_report_callouts(out)
    lifeos_hub(out)
    ha_waves(out)
    wardrobe_system(out)


if __name__ == "__main__":
    main()

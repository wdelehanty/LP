#!/usr/bin/env python3
"""Draw the hand-designed architecture diagrams in site tokens.

These are authored here, node by node, and written to v2/assets/diagrams/.
Same visual language as the rendered workflow diagrams, larger boxes.

Usage: draw_architecture.py <out-dir>
"""
import os
import sys

BG_PANEL = "#1E2226"
LINE = "#3A4046"
TEXT = "#E6E4DF"
MUTED = "#9AA0A6"
SIGNAL = "#F2C230"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, w, h, label, sub=None, own=False):
    stroke = SIGNAL if own else LINE
    sw = 1.5 if own else 1
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{BG_PANEL}" stroke="{stroke}" stroke-width="{sw}"/>',
           f'<text x="{x+14}" y="{y+24}" style="font:600 13px \'Barlow Condensed\',sans-serif;letter-spacing:.08em;text-transform:uppercase" fill="{TEXT}">{esc(label)}</text>']
    if sub:
        out.append(f'<text x="{x+14}" y="{y+42}" style="font:400 10px \'IBM Plex Mono\',monospace" fill="{MUTED}">{esc(sub)}</text>')
    return "\n".join(out)


def arrow(x1, y1, x2, y2, mid, dashed=False):
    dash = ' stroke-dasharray="4 4"' if dashed else ""
    if abs(y1 - y2) < 1 or abs(x1 - x2) < 1:
        d = f"M{x1},{y1} L{x2},{y2}"
    else:
        mx = (x1 + x2) / 2
        d = f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}"
    return f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1"{dash} marker-end="url(#{mid})"/>'


def note(x, y, text):
    return f'<text x="{x}" y="{y}" style="font:400 11px \'IBM Plex Mono\',monospace" fill="{MUTED}">{esc(text)}</text>'


def doc(name, inner, w, h, label, out_dir):
    mid = f"ar-{name}"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">\n'
           f'<defs><marker id="{mid}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           f'<path d="M0,0.5 L7,4 L0,7.5" fill="none" stroke="{LINE}" stroke-width="1.2"/></marker></defs>\n'
           + inner.replace("MID", mid) + "\n</svg>\n")
    open(os.path.join(out_dir, name + ".svg"), "w").write(svg)
    print(f"{name}.svg  {w}x{h}")


def demand_engine_full(out_dir):
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
        p.append(box(x, 10, 160, 56, l, s, own))
        if x != xs[-1]:
            p.append(arrow(x + 160, 38, x + 190 - 160 + 150, 38, "MID"))
    p.append(box(10, 120, 880, 52, "Measurement", "performance console / qbr frameworks / contact-role attribution", True))
    for x in xs:
        p.append(arrow(x + 80, 120, x + 80, 66, "MID", dashed=True))
    p.append(note(10, 204, "dashed: every stage reports into the same measurement layer, which is where the influenced-revenue number comes from"))
    p.append(note(10, 224, "yellow outline: the parts I own"))
    doc("demand-engine-full", "\n".join(p), 900, 236,
        "The full demand engine: acquisition feeds the CDP, then lifecycle, then CRM routing, then sales, with a shared measurement layer of the performance console, QBR frameworks, and contact-role attribution underneath all stages.", out_dir)


def funnel(out_dir):
    """The mechanism behind the ~2.5x, with what actually sits in each stage."""
    p = []
    stages = [
        ("Capture", "forms, pages, tracking"),
        ("Nurture", "onboarding, reengagement"),
        ("Route", "speed to lead, contact roles"),
        ("Sales handoff", "one-click outreach library"),
    ]
    gap, w = 28, 200
    x, y = 10, 10
    for i, (l, sub) in enumerate(stages):
        p.append(box(x, y, w, 56, l, sub))
        if i < len(stages) - 1:
            p.append(arrow(x + w, y + 28, x + w + gap, y + 28, "MID"))
        x += w + gap
    total = x - gap
    p.append(f'<path d="M10,96 L10,106 L{total},106 L{total},96" fill="none" stroke="{SIGNAL}" stroke-width="1"/>')
    p.append(f'<text x="{total/2}" y="126" text-anchor="middle" style="font:400 12px \'IBM Plex Mono\',monospace" fill="{TEXT}">~2.5x conversion improvement across capture, nurture, and routing</text>')
    doc("funnel", "\n".join(p), 900, 138,
        "The funnel from capture through nurture and routing to the sales handoff, with what runs in each stage and a bracket marking the roughly 2.5x conversion improvement across them.", out_dir)


def connect_cdp(out_dir):
    p = []
    p.append(box(10, 40, 190, 66, "Forbes.com", "dialogues / profiling", False))
    p.append(box(280, 40, 220, 66, "BlueConic CDP", "18m+ profiles / segments / ltv", True))
    p.append(box(280, 150, 220, 50, "Third-party enrichment", None, False))
    p.append(box(580, 10, 190, 56, "Pardot", "nurture programs", False))
    p.append(box(580, 90, 190, 56, "Salesforce", "routing / attribution", False))
    p.append(arrow(200, 73, 280, 73, "MID"))
    p.append(arrow(390, 150, 390, 106, "MID", dashed=True))
    p.append(arrow(500, 60, 580, 38, "MID"))
    p.append(arrow(500, 86, 580, 118, "MID"))
    p.append(note(10, 232, "anonymous readers become identified profiles on site; identified profiles route into nurture and sales"))
    doc("connect-cdp", "\n".join(p), 900, 244,
        "Forbes Connect architecture: the site's dialogues and progressive profiling feed the BlueConic CDP, enriched by third-party data, which routes profiles into Pardot for nurture and Salesforce for routing and attribution.", out_dir)


def forbes8_lifecycle(out_dir):
    p = []
    xs = [10, 190, 370, 550, 730]
    labels = [("Signup", None), ("Activation", "first value"), ("Engagement", None), ("Retention", None), ("LTV", None)]
    for x, (l, s) in zip(xs, labels):
        p.append(box(x, 10, 160, 56, l, s, l == "Activation"))
        if x != xs[-1]:
            p.append(arrow(x + 160, 38, x + 180, 38, "MID"))
    p.append(f'<path d="M810,66 C810,130 90,130 90,70" fill="none" stroke="{LINE}" stroke-width="1" stroke-dasharray="4 4" marker-end="url(#MID)"/>')
    p.append(note(310, 122, "incremental-sales feedback loop: programs tuned on sales effect"))
    doc("forbes8-lifecycle", "\n".join(p), 900, 148,
        "The Forbes8 lifecycle: signup to activation to engagement to retention to lifetime value, with a dashed feedback loop carrying incremental sales data back into the programs.", out_dir)


def selfserve_sequence(out_dir):
    p = []
    groups = [
        (10, "Onboarding", "signup to first live campaign"),
        (310, "Activation", "behaviors that predict a second"),
        (610, "Retention + revive", "stalled and lapsed advertisers"),
    ]
    for x, l, s in groups:
        p.append(box(x, 10, 280, 66, l, s, False))
        if x != 610:
            p.append(arrow(x + 280, 43, x + 300, 43, "MID"))
    p.append(box(10, 120, 880, 50, "8 programs / 29 emails", "written, built, and wired end to end by one person; staged for launch", True))
    for x, _, _ in groups:
        p.append(arrow(x + 140, 120, x + 140, 76, "MID", dashed=True))
    doc("selfserve-sequence", "\n".join(p), 900, 182,
        "The self-serve lifecycle map: onboarding, activation, and retention groups, all drawing on eight programs and twenty-nine emails staged for launch.", out_dir)


def enterprise_program(out_dir):
    p = []
    p.append(box(10, 46, 170, 56, "Partner goal", None, False))
    p.append(box(260, 10, 200, 50, "Content", None, False))
    p.append(box(260, 72, 200, 50, "Research", None, False))
    p.append(box(260, 134, 200, 50, "Retargeting", None, False))
    p.append(box(540, 46, 170, 66, "Flagship deliverable", "year-end insight report", True))
    p.append(box(540, 134, 170, 50, "Leads, CRM-ready", None, False))
    p.append(box(780, 88, 110, 56, "Partner CRM", "and sellers", False))
    p.append(arrow(180, 74, 260, 35, "MID"))
    p.append(arrow(180, 74, 260, 97, "MID"))
    p.append(arrow(180, 74, 260, 159, "MID"))
    p.append(arrow(460, 35, 540, 70, "MID"))
    p.append(arrow(460, 97, 540, 85, "MID"))
    p.append(arrow(460, 159, 540, 159, "MID"))
    p.append(arrow(710, 79, 780, 108, "MID"))
    p.append(arrow(710, 159, 780, 130, "MID"))
    p.append(note(10, 216, "the architecture pitched to three enterprise advertisers; it stopped at the pitch stage"))
    doc("enterprise-program", "\n".join(p), 900, 228,
        "Enterprise partner program architecture: the partner's pipeline goal drives content, research, and retargeting channels, converging on a flagship year-end insight report and CRM-ready lead delivery into the partner's CRM and sellers.", out_dir)


def summit_program(out_dir):
    p = []
    p.append(box(10, 88, 180, 66, "~$500K / 6 months", "team of three", True))
    chans = [("Paid media", None, 10), ("Radio", "nigeria + ghana", 72), ("Out-of-home", "nigeria + ghana", 134), ("Startup hub", "built from scratch", 196)]
    for l, s, y in chans:
        p.append(box(280, y, 220, 50, l, s, False))
        p.append(arrow(190, 121, 280, y + 25, "MID"))
    p.append(box(590, 88, 220, 66, "10,000+ attendees", "2018 under 30 summit", True))
    for _, _, y in chans:
        p.append(arrow(500, y + 25, 590, 121, "MID"))
    doc("summit-program", "\n".join(p), 900, 258,
        "Under 30 Summit audience program: a roughly $500K budget over six months, run by a team of three, deployed across paid media, radio and out-of-home in Nigeria and Ghana, and a startup hub, producing over ten thousand attendees.", out_dir)


def playbook_structure(out_dir):
    p = []
    pillars = [("Standards", 10), ("Prompt libraries", 232), ("QA checklists", 454), ("Governance", 676)]
    for l, x in pillars:
        p.append(box(x, 10, 214, 50, l, None, False))
        p.append(arrow(x + 107, 60, x + 107, 96, "MID"))
    p.append(box(10, 100, 880, 56, "Custom GPTs", "the trainable work runs through them; specialists keep the judgment calls", True))
    p.append(arrow(450, 156, 450, 192, "MID"))
    p.append(box(10, 196, 880, 52, "10+ concurrent programs", "run by a team of two", False))
    doc("playbook-structure", "\n".join(p), 900, 262,
        "The operating playbook structure: standards, prompt libraries, QA checklists, and governance feed custom GPTs that carry the trainable work, which is how a team of two runs more than ten concurrent programs.", out_dir)


def plate(name, title, subtitle, boxes, notes, label, out_dir, arrows=True, loop=False):
    """A 480 by 320 plate for the 3:2 frames: a title line, two or three
    boxes in a row, sub-labels beneath each, notes at the foot. Type is set
    denser than the full-width diagrams because these render small."""
    W, H = 480, 320
    p = [f'<text x="20" y="34" style="font:600 12px \'Barlow Condensed\',sans-serif;letter-spacing:.08em;text-transform:uppercase" fill="{TEXT}">{esc(title)}</text>']
    if subtitle:
        p.append(f'<text x="20" y="50" style="font:400 10px \'IBM Plex Mono\',monospace" fill="{MUTED}">{esc(subtitle)}</text>')
    n = len(boxes)
    w, gap = (132, 24) if n == 3 else (200, 32)
    x0 = (W - (n * w + (n - 1) * gap)) // 2
    y, h = 118, 52
    for i, (lab, subs, own) in enumerate(boxes):
        x = x0 + i * (w + gap)
        stroke = SIGNAL if own else LINE
        sw = 1.5 if own else 1
        p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{BG_PANEL}" stroke="{stroke}" stroke-width="{sw}"/>')
        p.append(f'<text x="{x+12}" y="{y+31}" style="font:600 11px \'Barlow Condensed\',sans-serif;letter-spacing:.06em;text-transform:uppercase" fill="{TEXT}">{esc(lab)}</text>')
        for j, sub in enumerate(subs or []):
            p.append(f'<text x="{x + w/2}" y="{y+h+20+j*14}" text-anchor="middle" style="font:400 10px \'IBM Plex Mono\',monospace" fill="{MUTED}">{esc(sub)}</text>')
        if arrows and i < n - 1:
            p.append(arrow(x + w, y + h/2, x + w + gap - 1, y + h/2, "MID"))
    if loop:
        x1 = x0 + (n - 1) * (w + gap) + w/2
        x2 = x0 + w/2
        p.append(f'<path d="M{x1},{y} C{x1},{y-52} {x2},{y-52} {x2},{y-1}" fill="none" stroke="{LINE}" stroke-width="1" stroke-dasharray="4 4" marker-end="url(#MID)"/>')
    for k, t in enumerate(notes):
        p.append(f'<text x="20" y="{282 + k*18}" style="font:400 10.5px \'IBM Plex Mono\',monospace" fill="{MUTED}">{esc(t)}</text>')
    doc(name, "\n".join(p), W, H, label, out_dir)


def plates(out_dir):
    plate("profiling-plate", "Progressive profiling", "forbes connect / one ask per visit",
          [("First visit", ["one field"], False),
           ("Next visit", ["one more field"], False),
           ("Known profile", ["segmented, routed"], True)],
          ["the profile fills in over a few visits", "nobody ever sees a long form"],
          "Progressive profiling: one field on the first visit, one more on the next, until the reader is a known profile that gets segmented and routed.", out_dir)
    plate("dialogue-plate", "On-site dialogues", "forbes connect / targeted by behavior",
          [("First-timer", ["one ask"], False),
           ("Three stories deep", ["a different ask"], True)],
          ["an on-site prompt targeted by what the reader has read and done"],
          "On-site dialogues: a first-time reader sees one ask, somebody three stories deep into a topic sees a different one, targeted by behavior.", out_dir, arrows=False)
    plate("two-bucket", "The two-bucket model", "operating playbook / who does what",
          [("Trainable execution", ["custom gpts and", "one operator"], True),
           ("Real expertise", ["outside rates,", "judgment calls"], False)],
          ["outside rates only get paid for the second bucket"],
          "The two-bucket contractor model: trainable execution runs through custom GPTs and one operator, real expertise is bought at outside rates.", out_dir, arrows=False)
    plate("selfserve-onboarding", "Onboarding into activation", "self-serve / no account manager",
          [("Account created", ["onboarding", "sequence starts"], False),
           ("First campaign", ["the onboarding goal"], True),
           ("Second campaign", ["activation pushes", "the behaviors", "that predict it"], False)],
          ["what an account manager would do, built in before launch"],
          "Self-serve onboarding: account creation starts the onboarding sequence toward a first live campaign, then activation programs push the behaviors that predict a second campaign.", out_dir)
    plate("two-tier", "Two-tier product structure", "pitched to a national wireless carrier",
          [("Tier one", ["one buyer depth,", "one price point"], False),
           ("Tier two", ["a deeper buyer,", "a higher price point"], True)],
          ["one program serving two buyer depths at two price points"],
          "Two-tier product structure: one program serving two buyer depths at two price points.", out_dir, arrows=False)
    plate("feedback-loop", "The incremental-sales loop", "forbes8 / how programs got tuned",
          [("Send", ["lifecycle program"], False),
           ("Sales effect", ["incremental sales,", "measured"], True),
           ("Tune", ["adjust the program"], False)],
          ["dashed: the loop that let us judge programs on sales"],
          "The incremental-sales feedback loop: a lifecycle send, its measured sales effect, a tuned program, and back around.", out_dir, loop=True)


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    demand_engine_full(out)
    funnel(out)
    connect_cdp(out)
    forbes8_lifecycle(out)
    selfserve_sequence(out)
    enterprise_program(out)
    summit_program(out)
    playbook_structure(out)
    plates(out)


if __name__ == "__main__":
    main()

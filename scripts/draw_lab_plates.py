#!/usr/bin/env python3
"""Draw the lab-page event pacing wireframe. The Life OS hub ledger, the
wardrobe layers, and the Home Assistant timeline live in draw_architecture.py.
Family names and personal finance/health surfaces are deliberately
excluded or genericized.

Usage: draw_lab_plates.py <out-dir>
"""
import sys

from draw_architecture import arrow, box, doc, note


def event_pacing(out_dir):
    p = []
    tiles = [(10, "Registrations"), (232, "Revenue pacing"), (454, "Vs goal")]
    for x, l in tiles:
        p.append(box(x, 10, 214, 88, l, None, False))
        p.append('<rect x="%d" y="52" width="130" height="18" rx="2" fill="#2A2F34"/>' % (x + 14))
        p.append('<rect x="%d" y="78" width="90" height="8" rx="2" fill="#2A2F34"/>' % (x + 14))
    p.append(box(10, 122, 658, 106, "Events needing attention", None, False))
    for i in range(3):
        y = 158 + i * 22
        p.append('<circle cx="30" cy="%d" r="3" fill="#F2C230"/>' % y)
        p.append('<rect x="44" y="%d" width="220" height="9" rx="2" fill="#2A2F34"/>' % (y - 5))
        p.append('<rect x="290" y="%d" width="90" height="9" rx="2" fill="#2A2F34"/>' % (y - 5))
        p.append('<rect x="400" y="%d" width="140" height="9" rx="2" fill="#2A2F34"/>' % (y - 5))
    p.append(box(700, 122, 190, 106, "Ask the analyst", "pacing, channels, revenue", True))
    p.append(note(10, 262, "drawn from the real interface; the live numbers stay internal on purpose"))
    doc("event-pacing", "\n".join(p), 900, 274,
        "Wireframe of the event pacing dashboard: registration, revenue, and goal tiles, an events-needing-attention list, and the ask-the-analyst panel, drawn without the internal numbers.", out_dir)

def main():
    out = sys.argv[1]
    event_pacing(out)


if __name__ == "__main__":
    main()

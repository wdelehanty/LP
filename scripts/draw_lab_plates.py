#!/usr/bin/env python3
"""Draw the lab-page system plates: Life OS hub map (from the live
workspace structure), the wardrobe system, and the Home Assistant waves.
Family names and personal finance/health surfaces are deliberately
excluded or genericized.

Usage: draw_lab_plates.py <out-dir>
"""
import sys

from draw_architecture import arrow, box, doc, note


def lifeos_hub(out_dir):
    p = []
    p.append(box(280, 10, 340, 50, "Life OS hub", "notion, one page runs it", True))
    sections = [
        (10, 100, "Now", "project queue, stalest on top"),
        (232, 100, "Capture inbox", "title only, keep moving"),
        (454, 100, "Weekly review", "sundays, 15 minutes"),
        (676, 100, "Knowledge base", "decisions + lessons"),
        (10, 190, "Money + direction", "monthly, not weekly"),
        (232, 190, "Logs", "maintenance / dog / builds"),
        (454, 190, "Parked", "nothing gets deleted"),
        (676, 190, "Operating manual", "read when away"),
    ]
    for x, y, l, s in sections:
        p.append(box(x, y, 214, 62, l, s, False))
        if y == 100:
            p.append(arrow(x + 107, 100, x + 107, 64, "MID", dashed=True))
    hooks = [
        (10, "Email label", "to the inbox", 339, 162),
        (330, "Home Assistant", "to the maintenance log", 339, 252),
        (650, "Webhook", "to the knowledge base", 783, 162),
    ]
    for x, l, s, tx, ty in hooks:
        p.append(box(x, 310, 240, 52, l, s, False))
        p.append(arrow(x + 120, 310, tx, ty, "MID", dashed=True))
    p.append(note(10, 396, "capture hooks run through n8n; mapped from the live workspace, family surfaces left off on purpose"))
    doc("lifeos-hub", "\n".join(x for x in p if x), 900, 408,
        "Map of the Life OS hub in Notion: a now queue, capture inbox, weekly review, and knowledge base on the active row; money, logs, parked items, and the operating manual behind them; email, Home Assistant, and webhook capture hooks feeding in through n8n.", out_dir)


def wardrobe_system(out_dir):
    p = []
    p.append(box(10, 64, 190, 60, "AI cataloguing", "photo in, item out", False))
    p.append(box(280, 10, 200, 56, "Closet / his", "289 items, live count", False))
    p.append(box(280, 78, 200, 56, "Closet / hers", None, False))
    p.append(box(280, 146, 200, 56, "Outfits", "14 use contexts", False))
    p.append(box(560, 64, 170, 60, "Worker API", "cloudflare", True))
    p.append(box(790, 64, 100, 60, "iOS app", "testflight", False))
    p.append(arrow(200, 94, 280, 38, "MID"))
    p.append(arrow(200, 94, 280, 106, "MID"))
    p.append(arrow(200, 94, 280, 174, "MID"))
    p.append(arrow(480, 38, 560, 84, "MID"))
    p.append(arrow(480, 106, 560, 94, "MID"))
    p.append(arrow(480, 174, 560, 104, "MID"))
    p.append(arrow(730, 94, 790, 94, "MID"))
    p.append(note(10, 236, "notion holds the databases; the app reads and writes through the worker; item count queried live 2026-08-31"))
    doc("wardrobe-system", "\n".join(p), 900, 248,
        "The wardrobe system: AI photo cataloguing feeds his-and-hers closet databases and an outfits database in Notion, a Cloudflare Worker API sits in front, and the iOS app on TestFlight reads and writes through it.", out_dir)


def ha_waves(out_dir):
    p = []
    waves = [
        (10, "Wave 2 / naming", "one scheme, every device"),
        (232, "Wave 3 / integrations", "consolidated, old gear retired"),
        (454, "Wave 4 / automations", "goodnight lockdown, doorbell chime"),
    ]
    for x, l, s in waves:
        p.append(box(x, 10, 214, 62, l, s, l.startswith("Wave 4")))
        if x != 454:
            p.append(arrow(x + 214, 41, x + 222, 41, "MID"))
    p.append(box(700, 10, 190, 62, "Notion log", "maintenance events", False))
    p.append(arrow(668, 41, 700, 41, "MID", dashed=True))
    p.append(note(10, 106, "dashed: maintenance events post themselves through the n8n webhook; the dashboard stays in the house"))
    doc("ha-waves", "\n".join(p), 900, 118,
        "The Home Assistant cleanup in three waves: naming conventions, consolidated integrations with old hardware retired, and automations including the goodnight lockdown and doorbell chime, with maintenance events posting to Notion through a webhook.", out_dir)




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
    lifeos_hub(out)
    wardrobe_system(out)
    ha_waves(out)
    event_pacing(out)


if __name__ == "__main__":
    main()

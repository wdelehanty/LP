#!/usr/bin/env python3
"""Render n8n workflow exports as SVG diagrams in the site tokens.

Reads trimmed exports (nodes: name/type/position, connections) from a source
directory, writes SVGs to v2/assets/diagrams/. Sticky notes are dropped.
Workflows over TRUNK_AT real nodes render as their trunk path (longest chain
from the trigger) with a note saying how many nodes are shown, per the
collapse-for-readability rule in the brief. Loop-back edges from
splitInBatches nodes are ignored for layout and drawn dashed.

Usage: render_workflows.py <src-dir> <out-dir>
"""
import json
import os
import re
import sys

BG_PANEL = "#1E2226"
LINE = "#3A4046"
TEXT = "#E6E4DF"
MUTED = "#9AA0A6"
SIGNAL = "#F2C230"

BOX_W, BOX_H = 150, 58
COL_W, ROW_H = 178, 80
MARGIN = 8
TRUNK_AT = 11
WRAP_COLS = 5

TYPE_LABELS = {
    "webhook": "webhook", "scheduleTrigger": "schedule", "gmailTrigger": "gmail trigger",
    "gmail": "gmail", "code": "code", "postgres": "postgres", "httpRequest": "http",
    "if": "if", "switch": "switch", "set": "set", "twilio": "twilio", "notion": "notion",
    "googleCalendar": "calendar", "respondToWebhook": "respond", "splitInBatches": "loop",
    "form": "form", "formTrigger": "form trigger", "errorTrigger": "error trigger",
    "googleSheets": "sheets", "anthropic": "claude",
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def type_label(t):
    suffix = t.split(".")[-1]
    return TYPE_LABELS.get(suffix, re.sub(r"([a-z])([A-Z])", r"\1 \2", suffix).lower())


def wrap_name(name, max_chars=23):
    if len(name) <= max_chars:
        return [name]
    words, lines, cur = name.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    if len(lines) > 2:
        lines = [lines[0], " ".join(lines[1:])]
        if len(lines[1]) > max_chars:
            lines[1] = lines[1][: max_chars - 1] + "…"
    return lines


def load(path):
    d = json.load(open(path))
    nodes = [n for n in d["nodes"] if "stickyNote" not in n["type"]]
    names = {n["name"] for n in nodes}
    edges = []
    for src, outs in d.get("connections", {}).items():
        if src not in names:
            continue
        for group in outs.get("main", []) or []:
            for tgt in group or []:
                if tgt.get("node") in names:
                    edges.append((src, tgt["node"]))
    return nodes, edges


def classify_edges(nodes, edges):
    """DFS back-edge detection so loops do not break the layout."""
    adj = {}
    for s, t in edges:
        adj.setdefault(s, []).append(t)
    state = {n["name"]: 0 for n in nodes}
    back = set()

    def dfs(u):
        state[u] = 1
        for v in adj.get(u, []):
            if state[v] == 0:
                dfs(v)
            elif state[v] == 1:
                back.add((u, v))
        state[u] = 2

    indeg = {n["name"]: 0 for n in nodes}
    for s, t in edges:
        indeg[t] += 1
    roots = [n["name"] for n in nodes if indeg[n["name"]] == 0] or [nodes[0]["name"]]
    sys.setrecursionlimit(10000)
    for r in roots:
        if state[r] == 0:
            dfs(r)
    for n in nodes:
        if state[n["name"]] == 0:
            dfs(n["name"])
    return [e for e in edges if e not in back], sorted(back)


def depths(nodes, fwd):
    d = {n["name"]: 0 for n in nodes}
    changed = True
    while changed:
        changed = False
        for s, t in fwd:
            if d[t] < d[s] + 1:
                d[t] = d[s] + 1
                changed = True
    return d


def is_trigger(node, indeg):
    t = node["type"]
    return indeg.get(node["name"], 0) == 0 or t.endswith("Trigger") or t.endswith(".webhook")


def node_svg(x, y, node, trigger):
    stroke = SIGNAL if trigger else LINE
    sw = 1.5 if trigger else 1
    lines = wrap_name(node["name"])
    out = [f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="2" fill="{BG_PANEL}" stroke="{stroke}" stroke-width="{sw}"/>']
    out.append(f'<text x="{x+10}" y="{y+16}" style="font:600 9px \'Barlow Condensed\',sans-serif;letter-spacing:.08em;text-transform:uppercase" fill="{MUTED}">{esc(type_label(node["type"]).upper())}</text>')
    ny = y + 33
    for ln in lines:
        out.append(f'<text x="{x+10}" y="{ny}" style="font:400 12px Barlow,sans-serif" fill="{TEXT}">{esc(ln)}</text>')
        ny += 14
    return "\n".join(out)


def edge_path(x1, y1, x2, y2, marker, dashed=False):
    dash = ' stroke-dasharray="4 4"' if dashed else ""
    if x2 > x1:
        mx = (x1 + x2) / 2
        d = f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}"
    else:
        drop = max(y1, y2) + ROW_H * 0.42
        d = f"M{x1},{y1} C{x1+30},{drop} {x2-30},{drop} {x2},{y2}"
    return f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="1"{dash} marker-end="url(#{marker})"/>'


def layout_full(nodes, edges, marker):
    fwd, back = classify_edges(nodes, edges)
    dep = depths(nodes, fwd)
    indeg = {}
    for s, t in fwd:
        indeg[t] = indeg.get(t, 0) + 1
    cols = {}
    for n in sorted(nodes, key=lambda n: (n.get("position") or [0, 0])[1]):
        cols.setdefault(dep[n["name"]], []).append(n)
    pos = {}
    parts = []
    for c, col_nodes in cols.items():
        for r, n in enumerate(col_nodes):
            x = MARGIN + c * COL_W
            y = MARGIN + r * ROW_H
            pos[n["name"]] = (x, y)
            parts.append(node_svg(x, y, n, is_trigger(n, indeg)))
    for s, t in fwd:
        sx, sy = pos[s]
        tx, ty = pos[t]
        parts.append(edge_path(sx + BOX_W, sy + BOX_H / 2, tx, ty + BOX_H / 2, marker))
    for s, t in back:
        sx, sy = pos[s]
        tx, ty = pos[t]
        parts.append(edge_path(sx + BOX_W / 2, sy + BOX_H, tx + BOX_W / 2, ty + BOX_H, marker, dashed=True))
    w = MARGIN * 2 + (max(dep.values()) + 1) * COL_W - (COL_W - BOX_W)
    h = MARGIN * 2 + max(len(v) for v in cols.values()) * ROW_H - (ROW_H - BOX_H)
    return "\n".join(parts), w, h


def trunk(nodes, edges):
    fwd, _ = classify_edges(nodes, edges)
    adj = {}
    for s, t in fwd:
        adj.setdefault(s, []).append(t)
    indeg = {}
    for s, t in fwd:
        indeg[t] = indeg.get(t, 0) + 1
    starts = [n["name"] for n in nodes if indeg.get(n["name"], 0) == 0]
    best = []

    def walk(u, path, seen):
        nonlocal best
        nxt = [v for v in adj.get(u, []) if v not in seen]
        if not nxt:
            if len(path) > len(best):
                best = list(path)
            return
        for v in nxt:
            walk(v, path + [v], seen | {v})

    for s in starts or [nodes[0]["name"]]:
        walk(s, [s], {s})
    byname = {n["name"]: n for n in nodes}
    return [byname[n] for n in best]


def layout_trunk(nodes, edges, marker):
    chain = trunk(nodes, edges)
    total = len(nodes)
    parts = []
    pos = []
    for i, n in enumerate(chain):
        row, idx = divmod(i, WRAP_COLS)
        col = idx if row % 2 == 0 else WRAP_COLS - 1 - idx
        x = MARGIN + col * COL_W
        y = MARGIN + row * ROW_H
        pos.append((x, y))
        parts.append(node_svg(x, y, n, i == 0))
    for i in range(len(chain) - 1):
        x1, y1 = pos[i]
        x2, y2 = pos[i + 1]
        if y1 == y2:
            if x2 > x1:
                parts.append(edge_path(x1 + BOX_W, y1 + BOX_H / 2, x2, y2 + BOX_H / 2, marker))
            else:
                parts.append(edge_path(x1, y1 + BOX_H / 2, x2 + BOX_W, y2 + BOX_H / 2, marker))
        else:
            parts.append(edge_path(x1 + BOX_W / 2, y1 + BOX_H, x2 + BOX_W / 2, y2, marker))
    rows = (len(chain) + WRAP_COLS - 1) // WRAP_COLS
    w = MARGIN * 2 + min(len(chain), WRAP_COLS) * COL_W - (COL_W - BOX_W)
    h = MARGIN * 2 + rows * ROW_H - (ROW_H - BOX_H)
    note = None
    if len(chain) < total:
        note = f"trunk path shown: {len(chain)} of {total} nodes"
    return "\n".join(parts), w, h, note


def render_workflow(slug, src_dir, mode=None):
    nodes, edges = load(os.path.join(src_dir, slug + ".json"))
    marker = f"arr-{slug}"
    if mode is None:
        mode = "trunk" if len(nodes) > TRUNK_AT else "full"
    if mode == "full":
        body, w, h = layout_full(nodes, edges, marker)
        note = None
    else:
        body, w, h, note = layout_trunk(nodes, edges, marker)
    return body, w, h, note, marker


def marker_def(mid):
    return (f'<marker id="{mid}" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0.5 L7,4 L0,7.5" fill="none" stroke="{LINE}" stroke-width="1.2"/></marker>')


def svg_doc(inner, w, h, markers, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">\n'
            f'<defs>{"".join(marker_def(m) for m in markers)}</defs>\n{inner}\n</svg>\n')


def write_single(slug, src_dir, out_dir, label, mode=None):
    body, w, h, note, marker = render_workflow(slug, src_dir, mode)
    if note:
        body += f'\n<text x="{MARGIN}" y="{h + 16}" style="font:400 11px \'IBM Plex Mono\',monospace" fill="{MUTED}">{esc(note)}</text>'
        h += 26
    doc = svg_doc(body, w, h, [marker], label)
    open(os.path.join(out_dir, slug + ".svg"), "w").write(doc)
    print(f"{slug}.svg  {w}x{h}")


def write_lanes(out_slug, lanes, src_dir, out_dir, label):
    """lanes: list of (lane_title, slug, mode or None)"""
    parts, markers = [], []
    y_off, max_w = 0, 0
    for title, slug, mode in lanes:
        body, w, h, note, marker = render_workflow(slug, src_dir, mode)
        markers.append(marker)
        title_txt = title + (f"  ({note})" if note else "")
        parts.append(f'<g transform="translate(0,{y_off})">'
                     f'<text x="{MARGIN}" y="14" style="font:600 12px \'Barlow Condensed\',sans-serif;letter-spacing:.08em;text-transform:uppercase" fill="{MUTED}">{esc(title_txt)}</text>'
                     f'<g transform="translate(0,24)">{body}</g></g>')
        y_off += h + 24 + 34
        max_w = max(max_w, w)
    doc = svg_doc("\n".join(parts), max_w, y_off - 34 + MARGIN, markers, label)
    open(os.path.join(out_dir, out_slug + ".svg"), "w").write(doc)
    print(f"{out_slug}.svg  {max_w}x{y_off - 34 + MARGIN}")


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    singles = {
        "live-booking": "Live booking workflow: a webhook receives the proposed time, the calendar is checked, the call is booked or declined, and the agent gets an answer while the caller waits.",
        "kit-visit-alert": "Kit visit alert workflow: the beacon webhook verifies a token, throttles repeat visits, and sends an alert.",
        "morning-round-v2": "Morning round workflow: a daily schedule collects labeled Gmail drafts and follow-ups and sends one digest with approve buttons.",
        "transcript-qa-digest": "Nightly transcript QA workflow: every completed call is reviewed by Claude against a checklist and a digest is emailed.",
        "provisioner": "Provisioner workflow: one request buys a number, creates the voice agent, and imports the number.",
        "chat-provisioner": "Chat provisioner workflow: clones the reference chat agent for a new client with a fresh webhook.",
        "nightly-backup": "Nightly backup workflow: a schedule exports every Postgres table and emails the backup.",
        "error-alerting": "Error alerting workflow: any workflow failure triggers a diagnostic email.",
        "monday-report": "Monday report workflow: a weekly schedule assembles each client's recovered revenue receipts and sends the report.",
    }
    modes = {"morning-round-v2": "trunk", "monday-report": "trunk"}
    for slug, label in singles.items():
        write_single(slug, src, out, label, modes.get(slug))
    write_lanes("prompt-patch-loop", [
        ("Stage 1 / propose (nightly)", "prompt-patch-proposer", "trunk"),
        ("Stage 2 / decide (apply or reject)", "prompt-patch-decision", "trunk"),
        ("Stage 3 / rollback (one click)", "prompt-rollback", "trunk"),
        ("Stage 4 / consolidate (monthly)", "prompt-consolidation-review", "trunk"),
    ], src, out, "The prompt patch loop in four stages: a nightly proposer drafts the smallest fix, a decision webhook applies or rejects it with a single-use token, a rollback webhook restores the previous prompt in one click, and a monthly consolidation review keeps the prompt coherent.")
    write_lanes("outcome-loop", [
        ("Send (sunday, reminder wednesday)", "outcome-confirmation-sender", "trunk"),
        ("Parse replies", "outcome-reply-parser", "trunk"),
    ], src, out, "The outcome confirmation loop: a weekly email asks each client to confirm outcomes with a short reply grammar, and a parser applies the confirmations to leads and quotes.")
    write_lanes("lifeos-captures", [
        ("Email to inbox", "capture-email-inbox", None),
        ("Home maintenance (home assistant)", "capture-home-maintenance", None),
        ("Knowledge base webhook", "capture-knowledge-base", None),
    ], src, out, "The three Life OS capture workflows: labeled email lands in the Notion inbox, Home Assistant posts maintenance events, and a webhook writes to the knowledge base.")


if __name__ == "__main__":
    main()

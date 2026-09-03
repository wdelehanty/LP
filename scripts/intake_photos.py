#!/usr/bin/env python3
"""Photo intake for the site (Brief 7). Finds candidate photos in the Mac
Photos library or a Google Takeout folder, downscales them into a gitignored
cache, tags them with Claude, scores them per slot, and writes a review
sheet at qa/intake.html. Will ticks; the ticked picks come back as
intake/picks.json and `apply` wires them in.

Usage:
  intake_photos.py scan  [--source apple | --source takeout <dir>] [--years 4] [--limit N]
  intake_photos.py tag   [--concurrency 4]           needs ANTHROPIC_API_KEY (or an ant profile)
  intake_photos.py sheet                              writes qa/intake.html from the tags
  intake_photos.py apply intake/picks.json            processes the ticked picks into assets/img

Originals never enter the repo. intake/ and raw/ are gitignored.
"""
import argparse
import base64
import concurrent.futures
import datetime as dt
import hashlib
import io
import json
import os
import sys

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTAKE = os.path.join(ROOT, "intake")
CACHE_DIR = os.path.join(INTAKE, "cache")
INDEX = os.path.join(INTAKE, "index.json")
TAGS = os.path.join(INTAKE, "tags.json")
SHEET = os.path.join(ROOT, "qa", "intake.html")

SUBJECTS = ["shop", "coop", "farm", "snowmobile", "ski", "fish", "boat", "dog", "fireworks", "tractor", "cars", "kids", "food", "other"]
SLOTS = {
    "shop": {"title": "The shop slot", "subjects": ["shop"], "want": "clean, wide from the door, lights on", "ratio": "square"},
    "carousel": {"title": "About carousel slides", "subjects": ["ski", "fish", "boat", "dog", "snowmobile", "tractor", "cars", "fireworks"], "want": "outside, seasons, machines", "ratio": "4:3"},
    "strip": {"title": "Strip replacements", "subjects": ["coop", "farm", "shop", "snowmobile", "fireworks"], "want": "home, weekends", "ratio": "square"},
}

TAG_SCHEMA = {
    "type": "object",
    "properties": {
        "images": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer"},
                    "subjects": {"type": "array", "items": {"type": "string", "enum": SUBJECTS}},
                    "orientation": {"type": "string", "enum": ["landscape", "portrait", "square"]},
                    "identifiable_face": {"type": "boolean"},
                    "children_present": {"type": "boolean"},
                    "children_from_behind_only": {"type": "boolean"},
                    "plate_or_address_legible": {"type": "boolean"},
                    "clutter": {"type": "integer", "minimum": 1, "maximum": 5},
                    "exposure": {"type": "integer", "minimum": 1, "maximum": 5},
                    "caption": {"type": "string"},
                },
                "required": ["index", "subjects", "orientation", "identifiable_face", "children_present",
                             "children_from_behind_only", "plate_or_address_legible", "clutter", "exposure", "caption"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["images"],
    "additionalProperties": False,
}

TAG_PROMPT = (
    "Tag each photo for a personal website's photo slots. For every image, return one object with its index, "
    "subject tags from the fixed list, orientation, whether any identifiable face is present, whether children "
    "are present and whether they appear only from behind, whether any license plate or street address is "
    "legible, a clutter score (1 clean to 5 chaotic), an exposure score (1 poor to 5 excellent), and a one-line "
    "caption in plain words naming the place and what it is, no dates, no names. Be strict about faces: a face "
    "that a friend could recognize counts."
)


# ---------------------------------------------------------------- helpers

def hash_file(path, size=None, mtime=None):
    h = hashlib.sha1()
    h.update(path.encode())
    st = os.stat(path)
    h.update(str(size or st.st_size).encode())
    h.update(str(mtime or int(st.st_mtime)).encode())
    return h.hexdigest()[:16]


def load_json(path, default):
    if os.path.exists(path):
        return json.load(open(path))
    return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, "w"), indent=1)


def open_image(path):
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except ImportError:
        pass
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    return im.convert("RGB")


def downscale(path, out_path, long_edge=1024):
    im = open_image(path)
    im.thumbnail((long_edge, long_edge), Image.LANCZOS)
    im.save(out_path, quality=84, optimize=True)
    return im.size


def exif_date(path):
    try:
        im = Image.open(path)
        exif = im.getexif()
        raw = exif.get(36867) or exif.get(306)
        if raw:
            return dt.datetime.strptime(str(raw)[:19], "%Y:%m:%d %H:%M:%S")
        model = exif.get(272)
        return None if model is None else dt.datetime.fromtimestamp(os.path.getmtime(path))
    except Exception:
        return None


def has_camera_model(path):
    try:
        return bool(Image.open(path).getexif().get(272))
    except Exception:
        return False


# ---------------------------------------------------------------- scan

def scan_takeout(src_dir, since, limit):
    out = []
    for root, _, files in os.walk(src_dir):
        for f in files:
            ext = f.lower().rsplit(".", 1)[-1] if "." in f else ""
            if ext not in ("heic", "jpg", "jpeg", "png"):
                continue
            path = os.path.join(root, f)
            if ext == "png":
                try:
                    w, h = Image.open(path).size
                except Exception:
                    continue
                if w * h < 3_000_000 and not has_camera_model(path):
                    continue  # a screenshot
            when = exif_date(path)
            if when is None or when < since:
                continue
            out.append({"path": path, "date": when.isoformat(), "screenshot": False})
            if limit and len(out) >= limit:
                return out
    return out


LABEL_WORDS = ["dog", "boat", "snow", "ski", "fish", "garage", "workshop", "tractor", "firework", "lake",
               "tool", "truck", "barn", "chicken", "coop", "motorcycle", "snowmobile", "frozen", "winter",
               "beach", "pond", "water body", "machine", "vehicle", "farm", "workbench", "hardware"]


def label_hit(labels):
    """Apple's own classification labels, used as a free pre-filter so the
    paid tagging pass only sees photos that could fit a slot."""
    return [l for l in labels if any(w in l for w in LABEL_WORDS)]


def scan_apple(since, limit, use_labels=True):
    import osxphotos
    db = osxphotos.PhotosDB()
    out = []
    for p in db.photos(movies=False, from_date=since):
        if p.screenshot or p.hidden or p.intrash:
            continue
        if p.uti and ("png" in p.uti.lower()) and (p.width or 0) * (p.height or 0) < 3_000_000:
            continue
        labels = list(p.labels_normalized or [])
        hits = label_hit(labels)
        if use_labels and not hits:
            continue
        path = p.path or (max(p.path_derivatives, key=lambda x: os.path.getsize(x)) if p.path_derivatives else None)
        if not path or not os.path.exists(path):
            continue
        out.append({"path": path, "date": p.date.replace(tzinfo=None).isoformat(), "screenshot": False,
                    "uuid": p.uuid, "original": p.original_filename, "place": (p.place.name if p.place else None),
                    "labels": labels, "label_hits": hits})
        if limit and len(out) >= limit:
            break
    return out


def cmd_scan(args):
    since = dt.datetime.now() - dt.timedelta(days=365 * args.years)
    if args.source == "takeout":
        if not args.dir:
            sys.exit("takeout needs a directory")
        items = scan_takeout(args.dir, since, args.limit)
    elif args.source == "apple":
        items = scan_apple(since, args.limit, use_labels=not args.all_labels)
    else:
        sys.exit("pick a source: --source apple, or --source takeout <dir>")
    print(f"{len(items)} candidates since {since.date()}")
    if args.count_only:
        return
    os.makedirs(CACHE_DIR, exist_ok=True)
    index = load_json(INDEX, {})
    for i, it in enumerate(items, 1):
        key = hash_file(it["path"])
        cached = os.path.join(CACHE_DIR, key + ".jpg")
        if not os.path.exists(cached):
            try:
                downscale(it["path"], cached)
            except Exception as e:
                print(f"skip {it['path']}: {e}")
                continue
        it["key"] = key
        it["cached"] = cached
        index[key] = it
        if i % 100 == 0:
            print(f"  {i} of {len(items)}")
    save_json(INDEX, index)
    print(f"index: {len(index)} entries in {INTAKE}")


# ---------------------------------------------------------------- tag

def b64(path):
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode()


def tag_batch(client, keys, index):
    content = []
    for i, k in enumerate(keys):
        content.append({"type": "text", "text": f"Image {i}:"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64(index[k]["cached"])}})
    content.append({"type": "text", "text": TAG_PROMPT + f" There are {len(keys)} images, indexed 0 to {len(keys) - 1}."})
    kwargs = dict(model="claude-opus-5", max_tokens=16000, messages=[{"role": "user", "content": content}],
                  output_config={"format": {"type": "json_schema", "schema": TAG_SCHEMA}})
    try:
        response = client.beta.messages.create(betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs)
    except TypeError:
        response = client.messages.create(**kwargs)
    if response.stop_reason == "refusal":
        raise RuntimeError("the model declined a batch: " + str(getattr(response, "stop_details", "")))
    text = next(b.text for b in response.content if b.type == "text")
    data = json.loads(text)
    out = {}
    for item in data["images"]:
        idx = item["index"]
        if 0 <= idx < len(keys):
            out[keys[idx]] = item
    return out


def cmd_tag(args):
    import anthropic
    index = load_json(INDEX, {})
    tags = load_json(TAGS, {})
    todo = [k for k in index if k not in tags]
    print(f"{len(index)} indexed, {len(tags)} tagged, {len(todo)} to tag")
    if not todo:
        return
    client = anthropic.Anthropic()
    batches = [todo[i:i + 10] for i in range(0, len(todo), 10)]
    done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = {ex.submit(tag_batch, client, b, index): b for b in batches}
        for fut in concurrent.futures.as_completed(futures):
            try:
                result = fut.result()
            except Exception as e:
                print(f"batch failed: {e}")
                continue
            tags.update(result)
            done += len(result)
            save_json(TAGS, tags)
            print(f"  tagged {done} of {len(todo)}")
    print(f"tags: {len(tags)} in {TAGS}")


# ---------------------------------------------------------------- score and sheet

def score(t):
    s = t["exposure"] * 2 - t["clutter"]
    if not t["identifiable_face"]:
        s += 3
    if t["children_present"] and not t["children_from_behind_only"]:
        s -= 10
    if t["plate_or_address_legible"]:
        s -= 10
    return s


def season(date_iso):
    m = int(date_iso[5:7])
    y = date_iso[:4]
    return y + ("-winter" if m in (12, 1, 2) else "-spring" if m in (3, 4, 5) else "-summer" if m in (6, 7, 8) else "-fall")


def pick_for_slot(slot, index, tags, top=8):
    cands = []
    for k, t in tags.items():
        if k not in index:
            continue
        if not set(t["subjects"]) & set(slot["subjects"]):
            continue
        if t["children_present"] and not t["children_from_behind_only"]:
            continue
        if slot["ratio"] == "4:3" and t["orientation"] == "portrait":
            continue
        cands.append((score(t), k))
    cands.sort(reverse=True)
    out, seen = [], set()
    for sc, k in cands:
        t = tags[k]
        sig = (t["subjects"][0] if t["subjects"] else "other", season(index[k]["date"]))
        if sig in seen:
            continue
        seen.add(sig)
        out.append((sc, k))
        if len(out) >= top:
            break
    return out


SLOT_LABELS = {
    "shop": ["garage", "workshop", "workbench", "hardware"],
    "carousel": ["ski", "snowmobile", "snow", "frozen", "boat", "fish", "dog", "lake", "beach", "tractor", "motorcycle", "firework", "truck"],
    "strip": ["coop", "chicken", "barn", "farm", "pond", "garage", "workshop"],
}


def pick_untagged(slot_id, index, top=12):
    """Before tagging: newest first among photos whose Apple labels fit the slot."""
    words = SLOT_LABELS[slot_id]
    cands = [(it["date"], k) for k, it in index.items() if any(any(w in l for w in words) for l in it.get("labels", []))]
    cands.sort(reverse=True)
    return [(0, k) for _, k in cands[:top]]


def cmd_sheet(args):
    index = load_json(INDEX, {})
    tags = load_json(TAGS, {})
    sections = []
    for slot_id, slot in SLOTS.items():
        picks = pick_for_slot(slot, index, tags, top=12 if slot_id == "carousel" else 8) if tags else pick_untagged(slot_id, index)
        cards = []
        for sc, k in picks:
            it = index[k]
            t = tags.get(k) or {"subjects": it.get("label_hits", [])[:3], "orientation": "", "clutter": "?", "exposure": "?",
                                "identifiable_face": "people" in it.get("labels", []), "children_present": "child" in it.get("labels", []),
                                "children_from_behind_only": False, "caption": "untagged: " + ", ".join(it.get("label_hits", [])[:4])}
            rel = os.path.relpath(it["cached"], os.path.dirname(SHEET))
            flags = []
            if t["identifiable_face"]:
                flags.append("face")
            if t["children_present"]:
                flags.append("children, from behind" if t["children_from_behind_only"] else "children")
            if t.get("plate_or_address_legible"):
                flags.append("plate visible")
            cards.append(f'''<label class="card">
  <input type="checkbox" name="pick" value="{slot_id}:{k}">
  <img src="{rel}" alt="" loading="lazy">
  <span class="mono">{", ".join(t["subjects"])} / {t["orientation"]} / clutter {t["clutter"]} / exposure {t["exposure"]}{" / " + ", ".join(flags) if flags else ""}</span>
  <span class="cap">{t["caption"]}</span>
  <span class="mono dim">{it["date"][:10]}{" / " + it["place"] if it.get("place") else ""}</span>
</label>''')
        sections.append(f'''<section>
  <div class="head"><span class="eyebrow">{slot["title"]}</span><span class="mono">{slot["want"]} / {slot["ratio"]}</span></div>
  <div class="grid">{"".join(cards) or '<p class="mono">no candidates matched</p>'}</div>
</section>''')
    untagged = len([k for k in index if k not in tags])
    html = f'''<!doctype html>
<meta charset="utf-8">
<title>QA intake</title>
<link rel="stylesheet" href="../site.css">
<style>
  body {{ padding: 40px; }}
  h1 {{ font-size: 1.5rem; margin-bottom: 8px; }}
  .lede {{ max-width: 46em; margin-bottom: 32px; }}
  section {{ border-top: 1px solid var(--line-soft); padding: 24px 0 32px; }}
  .head {{ display: flex; justify-content: space-between; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }}
  .grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }}
  .card {{ display: grid; gap: 6px; cursor: pointer; border: 1px solid var(--line-soft); border-radius: 4px; padding: 10px; }}
  .card:has(input:checked) {{ border-color: var(--signal); }}
  .card img {{ width: 100%; aspect-ratio: 4 / 3; object-fit: cover; border-radius: 2px; display: block; }}
  .card .cap {{ font-size: .9375rem; }}
  .dim {{ opacity: .7; }}
  .bar {{ position: sticky; bottom: 0; background: var(--bg); border-top: 1px solid var(--line); padding: 14px 0; display: flex; gap: 16px; align-items: center; }}
  .bar button {{ border: 1px solid var(--signal); background: transparent; color: var(--text); padding: 10px 16px; border-radius: 2px; font: 600 .8125rem/1 'Barlow Condensed', sans-serif; letter-spacing: .08em; text-transform: uppercase; cursor: pointer; }}
  textarea {{ width: 100%; min-height: 80px; background: var(--bg-panel); color: var(--text); border: 1px solid var(--line-soft); font: 400 .8125rem/1.5 'IBM Plex Mono', monospace; padding: 8px; }}
  @media (max-width: 900px) {{ .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
</style>
<h1>Photo intake</h1>
<p class="lede">Top candidates per slot, scored on exposure, clutter, and whether a face is in frame. Tick what should ship, then save the picks: the button downloads <code>picks.json</code>, which goes to <code>intake/picks.json</code>. {len(index)} indexed, {len(tags)} tagged, {untagged} untagged.</p>
<form id="picks">{"".join(sections)}</form>
<div class="bar">
  <button type="button" id="save">Download picks.json</button>
  <button type="button" id="copy">Copy JSON</button>
  <span class="mono" id="count">0 ticked</span>
</div>
<textarea id="out" readonly aria-label="Picks as JSON"></textarea>
<script>
(function () {{
  var form = document.getElementById('picks'), out = document.getElementById('out'), count = document.getElementById('count');
  function picks() {{
    var by = {{}};
    form.querySelectorAll('input[name=pick]:checked').forEach(function (i) {{
      var parts = i.value.split(':'); (by[parts[0]] = by[parts[0]] || []).push(parts[1]);
    }});
    return by;
  }}
  function render() {{
    var p = picks(); var n = Object.keys(p).reduce(function (a, k) {{ return a + p[k].length; }}, 0);
    out.value = JSON.stringify(p, null, 2); count.textContent = n + ' ticked';
  }}
  form.addEventListener('change', render); render();
  document.getElementById('save').addEventListener('click', function () {{
    var blob = new Blob([out.value], {{type: 'application/json'}});
    var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'picks.json'; a.click();
  }});
  document.getElementById('copy').addEventListener('click', function () {{ out.select(); document.execCommand('copy'); }});
}})();
</script>
'''
    os.makedirs(os.path.dirname(SHEET), exist_ok=True)
    open(SHEET, "w", encoding="utf-8").write(html)
    print(f"wrote {SHEET}")


# ---------------------------------------------------------------- apply

def crop_ratio(im, ratio):
    w, h = im.size
    if ratio == "square":
        s = min(w, h)
        box = ((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2)
    else:
        tw, th = 4, 3
        if w / h > tw / th:
            nw = int(h * tw / th)
            box = ((w - nw) // 2, 0, (w + nw) // 2, h)
        else:
            nh = int(w * th / tw)
            box = (0, (h - nh) // 2, w, (h + nh) // 2)
    return im.crop(box)


def cmd_apply(args):
    picks = json.load(open(args.picks))
    index = load_json(INDEX, {})
    tags = load_json(TAGS, {})
    img_dir = os.path.join(ROOT, "assets", "img")
    raw_dir = os.path.join(ROOT, "raw")
    slides = []
    counts = {}
    for slot_id, keys in picks.items():
        slot = SLOTS[slot_id]
        for k in keys:
            it = index[k]
            t = tags.get(k, {})
            subject = (t.get("subjects") or ["photo"])[0]
            counts[subject] = counts.get(subject, 0) + 1
            name = "shop" if slot_id == "shop" else f"{subject}-{counts[subject]}"
            im = open_image(it["path"])
            im = crop_ratio(im, slot["ratio"])
            big = (1400, 1400) if slot["ratio"] == "square" else (1400, 1050)
            small = (800, 800) if slot["ratio"] == "square" else (800, 600)
            im.resize(big, Image.LANCZOS).save(os.path.join(img_dir, name + ".jpg"), quality=86, optimize=True)
            im.resize(small, Image.LANCZOS).save(os.path.join(img_dir, name + "-800.jpg"), quality=84, optimize=True)
            os.makedirs(raw_dir, exist_ok=True)
            try:
                import shutil
                shutil.copy2(it["path"], os.path.join(raw_dir, os.path.basename(it["path"])))
            except Exception:
                pass
            print(f"{slot_id}: {name}.jpg from {os.path.basename(it['path'])}")
            if slot_id == "carousel":
                slides.append((name, t.get("caption", "")))
    if slides:
        p = os.path.join(ROOT, "about", "index.html")
        s = open(p, encoding="utf-8").read()
        marker = '      </div>\n      <div class="dots" aria-hidden="true"></div>'
        add = ""
        for name, cap in slides:
            add += f'''        <figure class="slide">
          <div class="frame r43"><img src="../assets/img/{name}.jpg" srcset="../assets/img/{name}-800.jpg 800w, ../assets/img/{name}.jpg 1400w" sizes="(max-width: 720px) 86vw, 500px" alt="{cap}" width="1400" height="1050" loading="lazy"></div>
          <figcaption class="mono">{cap}</figcaption>
        </figure>
'''
        if marker in s:
            s = s.replace(marker, add + marker)
            open(p, "w", encoding="utf-8").write(s)
            print(f"about carousel: {len(slides)} slides added")
    if "shop" in picks and picks["shop"]:
        p = os.path.join(ROOT, "index.html")
        s = open(p, encoding="utf-8").read()
        if "coop-run.jpg" in s:
            s = s.replace('<img src="assets/img/coop-run.jpg" srcset="assets/img/coop-run-800.jpg 800w, assets/img/coop-run.jpg 1400w"',
                          '<img src="assets/img/shop.jpg" srcset="assets/img/shop-800.jpg 800w, assets/img/shop.jpg 1400w"')
            s = s.replace('alt="The finished coop run, screened in, with hanging baskets along the top rail" width="1400" height="1050"',
                          'alt="The shop, wide from the door, lights on" width="1400" height="1400"')
            open(p, "w", encoding="utf-8").write(s)
            print("strip: shop slot rewired to shop.jpg")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--source", choices=["apple", "takeout"])
    s.add_argument("dir", nargs="?")
    s.add_argument("--years", type=int, default=4)
    s.add_argument("--limit", type=int, default=0)
    s.add_argument("--count-only", action="store_true")
    s.add_argument("--all-labels", action="store_true", help="skip the Apple label pre-filter and take everything")
    t = sub.add_parser("tag")
    t.add_argument("--concurrency", type=int, default=4)
    sub.add_parser("sheet")
    a = sub.add_parser("apply")
    a.add_argument("picks")
    args = ap.parse_args()
    if args.cmd == "scan" and not args.source:
        if args.dir and os.path.isdir(args.dir):
            args.source = "takeout"
        else:
            try:
                import osxphotos  # noqa: F401
                args.source = "apple"
            except ImportError:
                sys.exit("no source found: pass --source takeout <dir>, or pip install osxphotos for the Mac Photos library")
    {"scan": cmd_scan, "tag": cmd_tag, "sheet": cmd_sheet, "apply": cmd_apply}[args.cmd](args)


if __name__ == "__main__":
    main()

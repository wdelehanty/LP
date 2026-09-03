#!/usr/bin/env python3
"""Mask the studio headshot onto the site's dark ground (Brief 7, item 4).

Flood-fills the light backdrop from the top edge, erodes the subject mask
2px and feathers it, darkens the 8px band just outside the subject to kill
the light rim, then composites onto a 920 by 1150 gunmetal gradient with
the top of the hair at 14% from the top and the shoulders running off the
bottom. The studio watermark is painted over with the jacket around it.

Needs Pillow and numpy (pip install pillow numpy).
Usage: mask_headshot.py <source.jpg> <out-dir>
Writes headshot-dark.jpg (920x1150) and headshot-dark-600.jpg (600x750).
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CANVAS_W, CANVAS_H = 920, 1150
HAIR_TOP = 0.14
GROUND_CENTER = (0x2A, 0x2F, 0x34)
GROUND_EDGE = (0x15, 0x18, 0x1B)


def boxmean(x, r=3):
    p = np.pad(x, ((r + 1, r), (r + 1, r)), mode="edge")
    c = p.cumsum(0).cumsum(1)
    n = (2 * r + 1) ** 2
    k = 2 * r + 1
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / n


def subject_mask(a):
    """1.0 on the subject, 0.0 on the backdrop, from a flood fill off the top edge."""
    H, W = a.shape[:2]
    L = a.max(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    gray = a.mean(axis=2).astype(np.float64)
    m = boxmean(gray)
    m2 = boxmean(gray ** 2)
    std = np.sqrt(np.clip(m2 - m * m, 0, None))
    seeds = [(3, 3), (W - 4, 3), (W // 2, 3), (3, H // 3), (W - 4, H // 3), (3, H // 2), (W - 4, H // 2)]
    Lmin = min(int(L[y, x]) for x, y in seeds[:3]) - 40
    smax = max(int(sat[y, x]) for x, y in seeds[:3]) + 10
    cand = (L > Lmin) & (sat < smax) & (std < 8)
    mask = Image.fromarray((cand * 255).astype(np.uint8)).copy()
    for seed in seeds:
        if mask.getpixel(seed) == 255:
            ImageDraw.floodfill(mask, seed, 128, thresh=0)
    bg = (np.asarray(mask) == 128)
    return Image.fromarray(((~bg) * 255).astype(np.uint8)).copy()


def erase_watermark(a, cx, cy, r):
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    ring = (d > r) & (d < r + 14)
    fill = a[ring].mean(axis=0)
    inside = d <= r
    noise = np.random.default_rng(1).normal(0, 2.0, size=(int(inside.sum()), 3))
    a[inside] = np.clip(fill + noise, 0, 255).astype(np.int16)


def main():
    src, out_dir = sys.argv[1], sys.argv[2]
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    H, W = a.shape[:2]

    # the studio watermark sits on the jacket at the bottom right: paint it
    # with the jacket around it before anything else looks at the pixels
    erase_watermark(a, cx=int(W * 0.935), cy=int(H * 0.94), r=34)
    subject = subject_mask(a)
    # erode 2px, then feather 3px
    eroded = subject.filter(ImageFilter.MinFilter(5))
    soft = eroded.filter(ImageFilter.GaussianBlur(3))
    alpha = np.asarray(soft).astype(np.float64) / 255.0
    # the 8px band just outside the eroded subject carries the light rim: darken it
    band = np.asarray(eroded.filter(ImageFilter.MaxFilter(17))).astype(bool) & ~np.asarray(eroded).astype(bool)
    rgb = a.astype(np.float64)
    rgb[band] *= 0.85

    # where does the hair start
    rows = np.where(np.asarray(eroded).astype(bool).any(axis=1))[0]
    y_top = int(rows[0]) if len(rows) else 0
    # scale so the hair top lands at 14% and the source bottom runs past the canvas
    target_top = HAIR_TOP * CANVAS_H
    s = max(CANVAS_W / W, (CANVAS_H - target_top) / (H - y_top))
    sw, sh = int(round(W * s)), int(round(H * s))
    subj_img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).resize((sw, sh), Image.LANCZOS)
    alpha_img = Image.fromarray((alpha * 255).astype(np.uint8)).resize((sw, sh), Image.LANCZOS)
    ox = (CANVAS_W - sw) // 2
    oy = int(round(target_top - y_top * s))

    # gunmetal radial ground across the whole canvas
    yy, xx = np.mgrid[0:CANVAS_H, 0:CANVAS_W]
    r = np.sqrt(((xx - CANVAS_W * 0.5) / (CANVAS_W * 0.62)) ** 2 + ((yy - CANVAS_H * 0.36) / (CANVAS_H * 0.62)) ** 2)
    t = np.clip(r, 0, 1)[..., None]
    ground = np.array(GROUND_CENTER, float) * (1 - t) + np.array(GROUND_EDGE, float) * t
    canvas = Image.fromarray(ground.astype(np.uint8))
    canvas.paste(subj_img, (ox, oy), alpha_img)

    canvas.save(f"{out_dir}/headshot-dark.jpg", quality=88, optimize=True)
    canvas.resize((600, 750), Image.LANCZOS).save(f"{out_dir}/headshot-dark-600.jpg", quality=86, optimize=True)
    print(f"hair top at source row {y_top}, scale {s:.3f}, placed at ({ox}, {oy}); wrote {CANVAS_W}x{CANVAS_H} and 600x750")


if __name__ == "__main__":
    main()

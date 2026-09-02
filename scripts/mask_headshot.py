#!/usr/bin/env python3
"""Mask the studio headshot onto the site's dark ground (Brief 6, item 8).

Flood-fills the light backdrop from the top edge, feathers the edge, and
composites the subject over a gunmetal gradient, then crops the watermark
corner. Needs Pillow and numpy (pip install pillow numpy).

Usage: mask_headshot.py <source.jpg> <out-dir>
Writes headshot-dark.jpg (920px) and headshot-dark-600.jpg.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
src, out_dir = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
a = np.asarray(im).astype(np.int16)
H, W = a.shape[:2]
L = a.max(axis=2); sat = a.max(axis=2) - a.min(axis=2)
gray = a.mean(axis=2).astype(np.float64)
def boxmean(x, r=3):
    p = np.pad(x, ((r+1, r), (r+1, r)), mode="edge"); c = p.cumsum(0).cumsum(1)
    n = (2*r+1)**2; k = 2*r+1
    return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / n
m = boxmean(gray); m2 = boxmean(gray**2); std = np.sqrt(np.clip(m2 - m*m, 0, None))
seeds = [(3,3),(W-4,3),(W//2,3),(3,H//3),(W-4,H//3),(3,H//2),(W-4,H//2)]
Lmin = min(int(L[y,x]) for x,y in seeds[:3]) - 40
smax = max(int(sat[y,x]) for x,y in seeds[:3]) + 10
cand = (L > Lmin) & (sat < smax) & (std < 8)
mask = Image.fromarray((cand*255).astype(np.uint8)).copy()
for seed in seeds:
    if mask.getpixel(seed) == 255:
        ImageDraw.floodfill(mask, seed, 128, thresh=0)
bg = (np.asarray(mask) == 128).astype(np.uint8)*255
bgm = Image.fromarray(bg).copy().filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.6))
mf = np.asarray(bgm).astype(np.float64)/255.0
print("background share:", round(float(mf.mean()),3))
yy, xx = np.mgrid[0:H, 0:W]
r = np.sqrt(((xx-W*0.5)/(W*0.62))**2 + ((yy-H*0.36)/(H*0.62))**2)
t = np.clip(r, 0, 1)[..., None]
c0 = np.array([0x2A,0x2F,0x34], float); c1 = np.array([0x15,0x18,0x1B], float)
ground = c0*(1-t) + c1*t
out = a.astype(np.float64)*(1-mf[...,None]) + ground*mf[...,None]
res = Image.fromarray(np.clip(out,0,255).astype(np.uint8))
crop = res.crop((40, 0, 960, 920))
crop.save(f"{out_dir}/headshot-dark.jpg", quality=88, optimize=True)
crop.resize((600, 600), Image.LANCZOS).save(f"{out_dir}/headshot-dark-600.jpg", quality=86, optimize=True)
Image.fromarray(bg).save(f"{out_dir}/headshot-mask.png")
print("wrote", crop.size)

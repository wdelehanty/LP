#!/usr/bin/env python3
"""Mask the studio headshot onto the site's dark ground (Brief 7, item 4, v2).

Replaces the flood-fill approach with a matting model (rembg, isnet) so hair
edges come out clean, then composites onto a 920x1150 gunmetal gradient with
headroom, despills the partial-alpha fringe toward a dark hair tone, and
kills the watermark corner.

pip install rembg onnxruntime pillow numpy
Usage: mask_headshot.py <source.jpg> <out-dir>
Writes headshot-dark.jpg (920x1150) and headshot-dark-600.jpg (600x750).
"""
import sys
import numpy as np
from PIL import Image, ImageFilter
from rembg import remove, new_session

src_path, out_dir = sys.argv[1], sys.argv[2]
src = Image.open(src_path).convert("RGB")
cut = remove(src, session=new_session("isnet-general-use"))
cn = np.asarray(cut).astype(np.float64)
alpha = cn[..., 3]
alpha[900:, 880:] = 0  # watermark corner on the 1000x1000 source
alpha = np.asarray(Image.fromarray(alpha.astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))).astype(np.float64) / 255.0
fg = cn[..., :3]

W, H = 920, 1150
yy, xx = np.mgrid[0:H, 0:W]
r = np.sqrt(((xx - W * 0.5) / (W * 0.62)) ** 2 + ((yy - H * 0.32) / (H * 0.62)) ** 2)
t = np.clip(r, 0, 1)[..., None]
c0 = np.array([0x2A, 0x2F, 0x34], float); c1 = np.array([0x15, 0x18, 0x1B], float)
ground = c0 * (1 - t) + c1 * t

s = 1.02
sub = Image.fromarray(np.dstack([fg, alpha[..., None] * 255]).astype(np.uint8)).resize((int(1000 * s), int(1000 * s)), Image.LANCZOS)
sn = np.asarray(sub).astype(np.float64); sa = sn[..., 3:4] / 255.0; sf = sn[..., :3]
fringe = ((sa > 0.03) & (sa < 0.97)).astype(float)
sf = sf * (1 - 0.45 * fringe) + np.array([0x20, 0x1C, 0x18]) * (0.45 * fringe)
sw, sh = sub.size
ox = (W - sw) // 2
oy = int(H * 0.13) - int(35 * s)  # hair top in the source sits at y=35
out = ground.copy()
y0, y1 = max(oy, 0), min(oy + sh, H); x0, x1 = max(ox, 0), min(ox + sw, W)
sy0, sx0 = y0 - oy, x0 - ox
al = sa[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
out[y0:y1, x0:x1] = sf[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)] * al + out[y0:y1, x0:x1] * (1 - al)
res = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
res.save(f"{out_dir}/headshot-dark.jpg", quality=90, optimize=True)
res.resize((600, 750), Image.LANCZOS).save(f"{out_dir}/headshot-dark-600.jpg", quality=88, optimize=True)
print("wrote", res.size)

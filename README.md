# LP

williamdelehanty.com. Hand-written HTML and CSS, no framework, hosted on
GitHub Pages. DESIGN.md is the reference for every page that ships.

## Scripts

Python 3 with Pillow and numpy for the image work. Two scripts need more:

- `scripts/mask_headshot.py` uses `rembg` with the isnet-general-use model
  and `onnxruntime`. The first run downloads about 180MB to `~/.rembg/`.
- `scripts/intake_photos.py` uses `osxphotos` to read the Mac Photos
  library, `pillow-heif` for HEIC, and `anthropic` for the tagging pass.

```
pip install pillow numpy rembg onnxruntime osxphotos pillow-heif anthropic
```

Other scripts: `scripts/og.py` draws the per-page Open Graph cards (needs
`fonttools` and `brotli` on top of Pillow); `scripts/notes.py new|build`
creates a note and rebuilds the Notes index and feed; `scripts/render_loop.js`
renders a loop source page in `scripts/loops/` to frames through headless
Chrome (`NODE_PATH` pointing at a puppeteer-core install) and
`scripts/encode_loop.sh` encodes them; `scripts/prep_demo_call.sh` and
`scripts/prep_loop.sh` prepare a recording for the site; `scripts/qa.sh`
is the gate before a ship.

Release: `sh scripts/release.sh vX.Y.Z` stamps every page, bakes the
status rail values, and rewrites the sitemap. The status Worker lives in
`worker/`.

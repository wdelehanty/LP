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

Release: `sh scripts/release.sh vX.Y.Z` stamps every page and bakes the
status rail values. The status Worker lives in `worker/`.

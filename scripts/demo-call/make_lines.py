#!/usr/bin/env python3
"""Synthesize the caller's lines for the demo call harness with the Mac voice.
Reads lines.json, writes lines/<key>.wav (48 kHz mono). Run from the repo root."""
import json, os, subprocess
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(here, "lines"), exist_ok=True)
for k, t in json.load(open(os.path.join(here, "lines.json"))).items():
    aiff = os.path.join(here, "lines", k + ".aiff"); wav = os.path.join(here, "lines", k + ".wav")
    subprocess.run(["say", "-v", "Samantha", "-r", "178", "-o", aiff, t], check=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", aiff, "-ar", "48000", "-ac", "1", wav], check=True)
    os.remove(aiff)
print("lines written to", os.path.join(here, "lines"))

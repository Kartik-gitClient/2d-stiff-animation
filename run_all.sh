#!/bin/bash
# Full pipeline: Sarvam voiceover -> real timing -> 1080p render -> SFX + mix
# Needs: python3, ffmpeg, pip install pycairo numpy pillow requests   (+ libraqm for Hindi shaping: PIL must report raqm=True)
set -e
export SARVAM_API_KEY="${SARVAM_API_KEY:?export SARVAM_API_KEY=your_key first}"
python3 make_voice.py          # line_XX.wav + voice.wav + timing.json (real durations)
python3 horror.py qc           # check qc.jpg if you want
python3 horror.py full         # video_silent.mp4 + sfx.wav
python3 horror.py mix          # final.mp4 (voice + sfx, -14 LUFS)

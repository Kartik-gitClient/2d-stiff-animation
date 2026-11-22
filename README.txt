ROOM 13 - Rahul & Vinni (Hindi horror, GrowKaz cutout style)

Files
  story.py        Hindi script + Sarvam voice map (edit text / speakers / pace here)
  make_voice.py   calls Sarvam Bulbul v3 per line, builds voice.wav + timing.json
  horror.py       shot list, renderer, SFX, final mix      (qc | full | mix)
  horror_sets.py  characters, horror sets, Hindi text renderer
  engine.py       GrowKaz cutout engine (from the plugin)
  run_all.sh      one-shot pipeline

Run:  export SARVAM_API_KEY=...   &&   ./run_all.sh
Tip:  SCALE=0.667 python3 horror.py full   -> fast 720p preview

# -*- coding: utf-8 -*-
"""Generate Sarvam Bulbul v3 voiceover, timing.json, and master voice.wav for Portrait Horror."""
import os, sys, json, base64, wave, subprocess, time
import numpy as np
from story import LINES, VOICES, MODEL, GAP

dry = '--dry' in sys.argv
KEY = os.environ.get('SARVAM_API_KEY')
if not KEY and os.path.exists('.env'):
    for line in open('.env'):
        if line.strip().startswith('SARVAM_API_KEY='):
            KEY = line.strip().split('=', 1)[1].strip()
            os.environ['SARVAM_API_KEY'] = KEY
            break

SR = 44100
os.makedirs('voice', exist_ok=True)
if not dry:
    import requests
    if not KEY: sys.exit("Set SARVAM_API_KEY first (or pass via .env)")

def est(text): return len(text.split()) / 2.9 + 0.3

def wav_dur(path):
    with wave.open(path) as w: return w.getnframes() / w.getframerate()

TIM, cur, clips = [], 0.0, []
for i, (spk, text, pad) in enumerate(LINES):
    raw, out = f'voice/raw_{i:02d}', f'voice/line_{i:02d}.wav'
    if dry:
        dur = est(text)
    elif os.path.exists(out) and os.path.getsize(out) > 1000:
        dur = wav_dur(out); clips.append((cur + 0.12, out))
    else:
        v = VOICES[spk]
        print(f"Synthesizing [{i}/{len(LINES)}] {spk} ({v['speaker']}): {text[:35]}...")
        success = False
        for attempt in range(4):
            try:
                r = requests.post(
                    'https://api.sarvam.ai/text-to-speech',
                    headers={'api-subscription-key': KEY, 'Content-Type': 'application/json'},
                    json=dict(text=text, target_language_code='hi-IN', speaker=v['speaker'],
                              model=MODEL, pace=v['pace'], speech_sample_rate=24000),
                    timeout=90
                )
                r.raise_for_status()
                open(raw, 'wb').write(base64.b64decode(''.join(r.json()['audios'])))
                subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw, '-ar', str(SR), '-ac', '1', '-c:a', 'pcm_s16le', out], check=True)
                dur = wav_dur(out); clips.append((cur + 0.12, out))
                success = True
                break
            except Exception as e:
                print(f"  Attempt {attempt+1} failed: {e}. Retrying in 2s...")
                time.sleep(2)
        if not success:
            sys.exit(f"Failed to synthesize line {i}")

    t1 = cur + 0.12 + dur + GAP + pad
    TIM.append(dict(t0=round(cur, 2), t1=round(t1, 2), spk=spk, text=text, dur=round(dur, 2)))
    cur = t1

json.dump(dict(lines=TIM, total=round(cur, 2), dry=dry), open('timing.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if not dry:
    track = np.zeros(int((cur + 1) * SR), dtype=np.float32)
    for t0, f in clips:
        with wave.open(f) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        s = int(t0 * SR)
        track[s:s + len(a)] += a[:len(track) - s]
    with wave.open('voice.wav', 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(track, -1, 1) * 32767).astype(np.int16).tobytes())

print(f"Generated {len(TIM)} lines, total duration: {round(cur, 1)}s")

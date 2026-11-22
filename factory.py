# -*- coding: utf-8 -*-
"""
HORROR SHORTS FACTORY — 10 Vertical Hindi Horror Episodes + 1 Movie
Master builder: writes all stories, generates Sarvam voices, builds scenes, renders.
Run from D:\2d-stiff-animation
"""
import os, sys, json, base64, wave, subprocess, time, math, shutil, traceback
import numpy as np

PYTHON = r"C:\Users\karti\AppData\Local\Python\bin\python.exe"
ROOT = r"D:\2d-stiff-animation"
os.chdir(ROOT)

# Load API key
KEY = None
if os.path.exists('.env'):
    for line in open('.env'):
        if line.strip().startswith('SARVAM_API_KEY='):
            KEY = line.strip().split('=', 1)[1].strip()
if not KEY:
    sys.exit("No SARVAM_API_KEY in .env")

import requests

MODEL = "bulbul:v3"
SR = 44100

# ============================================================
# ALL 10 HORROR STORY SCRIPTS
# ============================================================

STORIES = {
    "ep01_aaina": {
        "title": "आइना",
        "title_en": "The Mirror",
        "lines": [
            ("N", "नीता ने अपने नए घर में एक पुराना आइना लगाया। पुराना, भारी, सोने के फ्रेम वाला।", 0.3),
            ("N", "पहली रात, उसने शीशे में अपना चेहरा देखा। सब कुछ सामान्य था।", 0.2),
            ("N", "दूसरी रात, शीशे में उसका reflection एक सेकंड देर से हिला।", 0.5),
            ("F", "नीता... ये शीशा अजीब है। इसमें मेरी परछाई अलग दिखती है।", 0.3),
            ("N", "तीसरी रात, शीशे में नीता मुस्कुरा रही थी... लेकिन असली नीता नहीं।", 0.6),
            ("N", "और फिर, शीशे वाली नीता ने धीरे से हाथ बढ़ाया... शीशे के बाहर।", 0.8),
            ("N", "अब फ़ैसला तुम्हारा है। नीता क्या करे? कमेंट में बताओ!", 3.0),
        ],
        "voices": {"N": ("shubh", 0.92), "F": ("priya", 1.0)},
    },
    "ep02_antim_bus": {
        "title": "अंतिम बस",
        "title_en": "The Last Bus",
        "lines": [
            ("N", "रात के ग्यारह बजे, अमन आख़िरी बस में चढ़ा। बस पूरी तरह ख़ाली थी।", 0.3),
            ("N", "ड्राइवर ने बिना मुड़े कहा...", 0.2),
            ("D", "पीछे मत बैठना। और किसी से बात मत करना।", 0.5),
            ("N", "बस चलने लगी। अचानक, एक-एक करके सीटों पर लोग दिखने लगे।", 0.4),
            ("N", "एक बुढ़िया, एक बच्चा, एक आदमी... सब चुपचाप, सब स्थिर।", 0.4),
            ("N", "और सबके चेहरे एक जैसे थे... बिल्कुल अमन जैसे।", 0.7),
            ("N", "तभी पीछे से एक आवाज़ आई।", 0.3),
            ("X", "तुम भी हमारे जैसे हो, अमन। बस अभी तुम्हें पता नहीं।", 0.6),
            ("N", "कमेंट में बताओ, अमन को क्या करना चाहिए?", 3.0),
        ],
        "voices": {"N": ("shubh", 0.92), "D": ("kabir", 0.82), "X": ("priya", 0.78)},
    },
    "ep03_gudiya": {
        "title": "गुड़िया",
        "title_en": "The Doll",
        "lines": [
            ("N", "शालू को अपनी नानी की पुरानी गुड़िया मिली। चीनी मिट्टी की, टूटी आँखों वाली।", 0.3),
            ("N", "रात को शालू ने गुड़िया को शेल्फ़ पर रखा और सो गई।", 0.2),
            ("N", "सुबह, गुड़िया बिस्तर पर थी। उसके बगल में।", 0.5),
            ("F", "माँ, मैंने गुड़िया शेल्फ़ पर रखी थी! ये यहाँ कैसे आई?", 0.3),
            ("N", "अगली रात, शालू ने गुड़िया को ताले में बंद कर दिया।", 0.3),
            ("N", "सुबह, ताला खुला था। गुड़िया उसकी तकिये के नीचे थी।", 0.5),
            ("N", "और इस बार, गुड़िया की दोनों आँखें ठीक हो गई थीं। और वो शालू की तरफ़ देख रही थी।", 0.8),
            ("N", "शालू को क्या करना चाहिए? कमेंट में बताओ!", 3.0),
        ],
        "voices": {"N": ("shubh", 0.92), "F": ("priya", 1.0)},
    },
    "ep04_chhaaya": {
        "title": "छाया",
        "title_en": "The Shadow",
        "lines": [
            ("N", "रोहन की छाया ने उसकी नक़ल करना बंद कर दिया।", 0.4),
            ("N", "पहले सिर्फ़ एक सेकंड की देरी थी। फिर दो। फिर पाँच।", 0.3),
            ("N", "एक दिन, जब रोहन बैठा था... उसकी छाया खड़ी थी।", 0.5),
            ("R", "ये... ये क्या हो रहा है? मेरी छाया... मेरी बात नहीं मान रही!", 0.4),
            ("N", "रात को, रोहन ने बत्ती जलाई। छाया दीवार पर थी। लेकिन रोहन की तरफ़ देख रही थी।", 0.5),
            ("N", "और फिर छाया ने मुँह खोला और कहा...", 0.4),
            ("S", "अब मेरी बारी है बाहर आने की।", 0.7),
            ("N", "रोहन क्या करे? कमेंट में बताओ!", 3.0),
        ],
        "voices": {"N": ("shubh", 0.92), "R": ("rahul", 1.0), "S": ("kabir", 0.76)},
    },
    "ep05_phone_call": {
        "title": "फ़ोन कॉल",
        "title_en": "The Phone Call",
        "lines": [
            ("N", "रात के दो बजे, सिमरन के फ़ोन पर कॉल आई। नंबर उसका अपना था।", 0.4),
            ("N", "उसने हिचकिचाते हुए उठाया।", 0.2),
            ("X", "सिमरन, दरवाज़ा मत खोलना। वो आ रही है।", 0.5),
            ("F", "कौन बोल रहा है? ये मेरा नंबर कैसे?", 0.3),
            ("X", "मैं तू ही हूँ। कल की तू। सुन, जो भी हो, बत्ती मत बुझाना।", 0.5),
            ("N", "तभी बत्ती गुल हो गई। और सामने, अंधेरे में, कोई खड़ा था।", 0.6),
            ("N", "सिमरन को क्या करना चाहिए? कमेंट में लिखो!", 3.0),
        ],
        "voices": {"N": ("shubh", 0.92), "F": ("priya", 1.0), "X": ("priya", 0.78)},
    },
    "ep06_kuan": {
        "title": "कुआँ",
        "title_en": "The Well",
        "lines": [
            ("N", "गाँव के बाहर एक सूखा कुआँ था। सब कहते थे, उसमें मत झाँको।", 0.3),
            ("N", "लेकिन आर्यन ने झाँका।", 0.3),
            ("N", "नीचे अँधेरा था। फिर, अँधेरे से एक आवाज़ आई।", 0.4),
            ("K", "मदद करो... मैं यहाँ फँसा हूँ... बहुत दिनों से।", 0.5),
            ("R", "कौन है वहाँ? तुम कौन हो?", 0.3),
            ("K", "मैं... मैं आर्यन हूँ।", 0.6),
            ("N", "आर्यन ने फिर नीचे झाँका। और नीचे से, उसका अपना चेहरा उसे देख रहा था।", 0.7),
            ("N", "आर्यन क्या करे? कमेंट में बताओ!", 3.0),
        ],
        "voices": {"N": ("shubh", 0.92), "R": ("rahul", 1.0), "K": ("kabir", 0.78)},
    },
    "ep07_train": {
        "title": "रात की ट्रेन",
        "title_en": "The Night Train",
        "lines": [
            ("N", "रात की आख़िरी ट्रेन। डिब्बा पूरा ख़ाली। सिर्फ़ मीरा बैठी थी।", 0.3),
            ("N", "ट्रेन एक अनजान स्टेशन पर रुकी। बोर्ड पर कोई नाम नहीं था।", 0.4),
            ("N", "एक आदमी चढ़ा। पुराने कपड़ों में। उसने सामने बैठकर कहा...", 0.3),
            ("A", "तुम भी ग़लत ट्रेन में बैठ गई हो।", 0.5),
            ("F", "ग़लत ट्रेन? ये तो दिल्ली जा रही है।", 0.3),
            ("A", "दिल्ली तो पच्चीस साल पहले जा रही थी। अब ये कहीं और जाती है।", 0.6),
            ("N", "मीरा ने खिड़की से बाहर देखा। बाहर सिर्फ़ अंधेरा था। और ट्रेन तेज़ होती जा रही थी।", 0.7),
            ("N", "मीरा को क्या करना चाहिए? कमेंट में लिखो!", 3.0),
        ],
        "voices": {"N": ("shubh", 0.92), "F": ("priya", 1.0), "A": ("kabir", 0.80)},
    },
    "ep08_tasveer": {
        "title": "तस्वीर",
        "title_en": "The Photograph",
        "lines": [
            ("N", "विकास को एक पुरानी फ़ोटो मिली। उसके दादा की शादी की। उन्नीस सौ बयालीस।", 0.3),
            ("N", "फ़ोटो में पीछे, भीड़ में, एक चेहरा था। जो बिल्कुल विकास जैसा दिखता था।", 0.5),
            ("R", "ये मैं कैसे हो सकता हूँ? ये तो अस्सी साल पुरानी फ़ोटो है!", 0.3),
            ("N", "विकास ने और पुरानी फ़ोटो देखीं। हर फ़ोटो में, हर दशक में, वही चेहरा था।", 0.5),
            ("N", "और सबसे पुरानी फ़ोटो में, वो चेहरा सीधा कैमरे की तरफ़ देख रहा था।", 0.5),
            ("N", "और मुस्कुरा रहा था।", 0.7),
            ("N", "विकास को क्या करना चाहिए? कमेंट में बताओ!", 3.0),
        ],
        "voices": {"N": ("shubh", 0.92), "R": ("rahul", 1.0)},
    },
    "ep09_pustakalaya": {
        "title": "पुस्तकालय",
        "title_en": "The Library",
        "lines": [
            ("N", "शहर के सबसे पुराने पुस्तकालय में, आधी रात को किताबें अपने आप खुलती हैं।", 0.3),
            ("N", "लाइब्रेरियन ने देव को चेतावनी दी थी।", 0.2),
            ("L", "बारह बजे के बाद, section C में मत जाना।", 0.4),
            ("N", "लेकिन देव गया। और वहाँ एक किताब खुली पड़ी थी।", 0.3),
            ("N", "किताब में लिखा था: 'देव, अगला पन्ना मत पलटना।'", 0.5),
            ("N", "देव ने पन्ना पलटा। अगले पन्ने पर लिखा था: 'अब बहुत देर हो गई।'", 0.5),
            ("N", "और किताब की स्याही से दो हाथ बाहर निकलने लगे।", 0.7),
            ("N", "देव को बचने के लिए क्या करना चाहिए? कमेंट में लिखो!", 3.0),
        ],
        "voices": {"N": ("shubh", 0.92), "L": ("kabir", 0.82)},
    },
    "ep10_manzil": {
        "title": "मंज़िल",
        "title_en": "The Floor",
        "lines": [
            ("N", "प्रिया की नई बिल्डिंग में सात मंज़िलें थीं। लेकिन लिफ़्ट में आठ बटन थे।", 0.4),
            ("N", "सबने कहा, आठवीं मंज़िल मत जाना। वो exist नहीं करती।", 0.3),
            ("N", "एक रात, प्रिया ने गलती से आठ दबा दिया।", 0.3),
            ("N", "लिफ़्ट खुली। एक लंबा, अंधेरा गलियारा था। और हर दरवाज़े पर उसका नाम लिखा था।", 0.5),
            ("N", "प्रिया ने पहला दरवाज़ा खोला। अंदर, वही कमरा था जहाँ वो अभी रहती है।", 0.4),
            ("N", "लेकिन बिस्तर पर कोई सो रहा था... और वो प्रिया ही थी।", 0.5),
            ("N", "और सोई हुई प्रिया ने आँखें खोलीं और कहा...", 0.3),
            ("P", "तुम बहुत देर से यहाँ आने वाली थीं।", 0.7),
            ("N", "प्रिया क्या करे? कमेंट में बताओ!", 3.0),
        ],
        "voices": {"N": ("shubh", 0.92), "P": ("priya", 0.78)},
    },
}

GAP = 0.32

# ============================================================
# STEP 1: Generate all Sarvam voices
# ============================================================

def synthesize_line(text, speaker, pace, out_path, raw_path):
    """Synthesize one line via Sarvam API"""
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        with wave.open(out_path) as w:
            return w.getnframes() / w.getframerate()
    for attempt in range(4):
        try:
            r = requests.post(
                'https://api.sarvam.ai/text-to-speech',
                headers={'api-subscription-key': KEY, 'Content-Type': 'application/json'},
                json=dict(text=text, target_language_code='hi-IN', speaker=speaker,
                          model=MODEL, pace=pace, speech_sample_rate=24000),
                timeout=90
            )
            r.raise_for_status()
            open(raw_path, 'wb').write(base64.b64decode(''.join(r.json()['audios'])))
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', raw_path, '-ar', str(SR),
                            '-ac', '1', '-c:a', 'pcm_s16le', out_path], check=True)
            with wave.open(out_path) as w:
                return w.getnframes() / w.getframerate()
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(1.5)
    raise RuntimeError(f"Failed to synthesize: {text[:40]}")

def generate_voices_for_episode(ep_id, story):
    """Generate all voice lines and timing.json for one episode"""
    ep_dir = os.path.join(ROOT, "shorts", ep_id)
    voice_dir = os.path.join(ep_dir, "voice")
    os.makedirs(voice_dir, exist_ok=True)

    TIM, cur, clips = [], 0.0, []
    for i, (spk, text, pad) in enumerate(story["lines"]):
        raw = os.path.join(voice_dir, f"raw_{i:02d}")
        out = os.path.join(voice_dir, f"line_{i:02d}.wav")
        speaker, pace = story["voices"][spk]
        print(f"  [{ep_id}] Line {i}: {spk} ({speaker}): {text[:30]}...")
        dur = synthesize_line(text, speaker, pace, out, raw)
        clips.append((cur + 0.12, out))
        t1 = cur + 0.12 + dur + GAP + pad
        TIM.append(dict(t0=round(cur, 2), t1=round(t1, 2), spk=spk, text=text, dur=round(dur, 2)))
        cur = t1

    # Build master voice.wav
    total = round(cur, 2)
    track = np.zeros(int((cur + 1) * SR), dtype=np.float32)
    for t0, f in clips:
        with wave.open(f) as w:
            a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        s = int(t0 * SR)
        track[s:s + len(a)] += a[:len(track) - s]
    voice_path = os.path.join(ep_dir, "voice.wav")
    with wave.open(voice_path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(track, -1, 1) * 32767).astype(np.int16).tobytes())

    # Write timing.json
    timing_path = os.path.join(ep_dir, "timing.json")
    json.dump(dict(lines=TIM, total=total, dry=False, title=story["title"], title_en=story["title_en"]),
              open(timing_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"  [{ep_id}] Done: {len(TIM)} lines, {total}s")
    return total

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "voices"

    if mode == "voices":
        print("=" * 60)
        print("GENERATING SARVAM AI VOICES FOR ALL 10 EPISODES")
        print("=" * 60)
        totals = {}
        for ep_id, story in STORIES.items():
            try:
                t = generate_voices_for_episode(ep_id, story)
                totals[ep_id] = t
                print(f"  ✓ {ep_id}: {t}s")
            except Exception as e:
                print(f"  ✗ {ep_id}: {e}")
                traceback.print_exc()
        print("\nAll voice generation complete:")
        for k, v in totals.items():
            print(f"  {k}: {v}s")
        json.dump(totals, open(os.path.join(ROOT, "shorts", "voice_summary.json"), 'w'), indent=2)

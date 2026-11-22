# 2D Stiff Animation (Cutout & Puppet Animation Engine)

A 2D cutout/puppet-style animation studio built in Python with **PyCairo**, **Pillow**, **uharfbuzz**, **Sarvam AI Hindi TTS**, and **FFmpeg**. Characters are parametric flat-vector rigs with smooth easing, blinking, speaking mouth shapes, dynamic camera choreography, and layered atmospheric sets rendered directly from code.

---

## 🎬 Projects Included

### 1. Room 13 (*कमरा नंबर 13*)
- **Format**: 1920x1080 (16:9 Landscape), 30 FPS
- **Story**: Rahul and Vinni stranded at an eerie mountain hotel at midnight. Room 13 key given with a strict warning. At 3:00 AM, knocks on the door with duplicate voices outside.
- **Audio**: Sarvam AI `bulbul:v3` Hindi multi-speaker voiceover + procedural sound effects.
- **Run**: `run_all.bat` or `python make_voice.py && python horror.py qc && python horror.py full && python horror.py mix`

### 2. Lift Ka Niyam (*लिफ़्ट का नियम* — The 2:00 AM Elevator)
- **Directory**: `portrait_horror/`
- **Format**: 1080x1920 (9:16 Portrait for YouTube Shorts, Instagram Reels, TikTok), 30 FPS
- **Story**: Kabir working late in an empty IT building at 2:00 AM. Warned by the old security guard never to take the midnight elevator. Inside, a woman in red stands facing the wall. Sudden stop between floors reveals her horrifying grin in the mirror.
- **Audio**: Multi-speaker cast (Narrator, Guard, Kabir, Woman in Red) + procedural elevator hum, bell DING, brake thuds, heartbeat, and stingers.
- **Interactive Ending**: 3-button choice cards encouraging comments (`1. इमरजेंसी घंटी बजाओ`, `2. शीशा तोड़कर भागो`, `3. छत का वेंट खोलो`).
- **Run**: `cd portrait_horror && run_all.bat`

---

## 🚀 Quick Setup

### Requirements
- Python 3.10+
- FFmpeg installed and available on PATH
- Hindi font (e.g., `Nirmala UI` on Windows or `FreeSansBold` on Linux)

```bash
pip install pycairo numpy pillow uharfbuzz requests
```

### Environment Configuration
Create a `.env` file in the project root:
```env
SARVAM_API_KEY=your_sarvam_api_key_here
```

### Running Pipeline
```bash
# Generate voiceover, timing, render contact sheets, full video, and master mix:
run_all.bat
```

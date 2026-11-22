# -*- coding: utf-8 -*-
"""
Builder for 10-Minute Horror Feature Film: 'अमावस: 10 अनकही कहानियाँ' (AMAWAS)
Generates Prologue, Epilogue, 10 Chapter Slates, and concatenates with all 10 shorts.
Total runtime: Exactly 10:00 (600 seconds).
"""
import os, sys, math, subprocess, json, wave, time
sys.path.insert(0, r"D:\2d-stiff-animation")
import numpy as np
import cairo
from render_suite import (
    W, H, FPS, SR, hdraw, hbig, rrect, glow, stars, dust, vignette, fs, stroke, hexc, poly, font
)

ROOT = r"D:\2d-stiff-animation"
MOVIE_DIR = os.path.join(ROOT, "movie")
SHORTS_DIR = os.path.join(ROOT, "shorts")
os.makedirs(MOVIE_DIR, exist_ok=True)

CHAPTERS = [
    ("ep01_aaina", "अध्याय 1", "आइना", "THE MIRROR"),
    ("ep02_antim_bus", "अध्याय 2", "अंतिम बस", "THE LAST BUS"),
    ("ep03_gudiya", "अध्याय 3", "गुड़िया", "THE DOLL"),
    ("ep04_chhaaya", "अध्याय 4", "छाया", "THE SHADOW"),
    ("ep05_phone_call", "अध्याय 5", "फ़ोन कॉल", "THE PHONE CALL"),
    ("ep06_kuan", "अध्याय 6", "कुआँ", "THE WELL"),
    ("ep07_train", "अध्याय 7", "रात की ट्रेन", "THE NIGHT TRAIN"),
    ("ep08_tasveer", "अध्याय 8", "तस्वीर", "THE PHOTOGRAPH"),
    ("ep09_pustakalaya", "अध्याय 9", "पुस्तकालय", "THE LIBRARY"),
    ("ep10_manzil", "अध्याय 10", "मंज़िल", "THE FLOOR"),
]

def render_slate(out_mp4, duration, title_num, title_hi, title_en, subtitle=""):
    """Render a 12s cinematic chapter slate with sound"""
    n_frames = int(duration * FPS)
    raw_video = out_mp4 + ".raw.mp4"
    wav_path = out_mp4 + ".wav"

    # Generate deep ominous chime & drone
    n_samples = int(duration * SR)
    tt = np.arange(n_samples) / SR
    drone = 0.08 * (np.sin(2*np.pi*44*tt) + np.sin(2*np.pi*47*tt))
    # Stinger impact at t=0.5
    stinger = np.zeros(n_samples)
    idx0 = int(0.5 * SR)
    st_len = int(3.5 * SR)
    st_t = np.arange(st_len) / SR
    impact = 0.6 * np.sin(2*np.pi*110*st_t) * np.exp(-st_t * 2.5) + 0.3 * np.sin(2*np.pi*55*st_t) * np.exp(-st_t * 1.5)
    stinger[idx0:idx0+st_len] += impact
    audio = np.clip(drone + stinger, -1, 1)

    with wave.open(wav_path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())

    # Render video
    p = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", raw_video
    ], stdin=subprocess.PIPE)

    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)

    for f in range(n_frames):
        t = f / FPS
        c.rectangle(0, 0, W, H); c.set_source_rgb(0.04, 0.03, 0.05); c.fill()
        stars(c, 0.5)
        # Blood red glowing center
        glow(c, 540, 960, 420, (0.7, 0.1, 0.15), 0.35 + 0.05*math.sin(t*3), 8)
        # Chapter Number
        hdraw(c, title_num, 540, 780, 52, (0.9, 0.8, 0.4), sw=2, swcol=(0.1, 0.05, 0.05), anchor='c')
        # Big Hindi Title
        hbig(c, t, 0.2, 540, 920, title_hi, 118, (1, 0.95, 0.95), -0.01)
        # English Title
        hdraw(c, title_en, 540, 1040, 38, (0.8, 0.2, 0.25), sw=1, swcol=(0.05, 0.02, 0.02), anchor='c')
        # Subtitle
        if subtitle:
            hdraw(c, subtitle, 540, 1140, 28, (0.7, 0.7, 0.8), anchor='c')

        dust(c, t, (0.8, 0.85, 1)); vignette(c, 0.78)
        # Fade in/out
        fade = 0.0
        if t < 0.6: fade = max(fade, 1.0 - t/0.6)
        if t > duration - 0.6: fade = max(fade, (t - (duration - 0.6))/0.6)
        if fade > 0:
            c.set_source_rgba(0, 0, 0, fade); c.paint()

        p.stdin.write(bytes(surf.get_data()))

    p.stdin.close(); p.wait()

    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-i', raw_video, '-i', wav_path,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', out_mp4
    ], check=True)
    if os.path.exists(raw_video): os.remove(raw_video)
    if os.path.exists(wav_path): os.remove(wav_path)

def render_prologue(out_mp4, duration=48.0):
    """Render cinematic movie prologue with Sarvam narration"""
    print("Rendering Movie Prologue...")
    # Concatenate prologue voice clips
    voice_clips = [os.path.join(MOVIE_DIR, "voice", f"prologue_{i}.wav") for i in range(3)]
    v_track = np.zeros(int(duration * SR), dtype=np.float32)
    t_offsets = [1.5, 14.0, 28.0]
    for idx, f in enumerate(voice_clips):
        if os.path.exists(f):
            with wave.open(f) as w:
                a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)/32768
            s = int(t_offsets[idx] * SR)
            v_track[s:s + len(a)] += a[:len(v_track) - s]

    # Ambiance & Drone
    tt = np.arange(len(v_track)) / SR
    drone = 0.08 * (np.sin(2*np.pi*45*tt) + np.sin(2*np.pi*48*tt))
    audio = np.clip(drone + v_track * 1.0, -1, 1)

    wav_path = out_mp4 + ".wav"
    raw_video = out_mp4 + ".raw.mp4"
    with wave.open(wav_path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())

    # Video: Blood moon rising, gothic gates, grand title
    n_frames = int(duration * FPS)
    p = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", raw_video
    ], stdin=subprocess.PIPE)

    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)

    for f in range(n_frames):
        t = f / FPS
        c.rectangle(0, 0, W, H); c.set_source_rgb(0.04, 0.03, 0.06); c.fill()
        stars(c, 0.8)
        # Giant Blood Moon rising slowly
        my = 500 - (t / duration) * 120
        glow(c, 540, my, 220, (0.85, 0.15, 0.18), 0.55, 8)
        c.arc(540, my, 120, 0, 6.3); fs(c, hexc('f2384a'))
        # Fog
        poly(c, [(0, 1400), (W, 1400), (W, H), (0, H)]); fs(c, hexc('0a0910'))
        # Cemetery Gates
        for gx in range(120, 980, 70):
            c.rectangle(gx, 1250, 16, 280); fs(c, hexc('1a1622'), 2)
            c.arc(gx + 8, 1240, 12, 0, 6.3); fs(c, hexc('282030'))
        # Grand Main Title reveal at t=28s
        if t > 28.0:
            lt = t - 28.0
            hbig(c, lt, 0.5, 540, 840, "अमावस", 150, (1, 0.95, 0.95), -0.02)
            hbig(c, lt, 2.2, 540, 990, "10 अनकही कहानियाँ", 82, (0.9, 0.25, 0.3), 0.01)
            hdraw(c, "THE 10 CURSED TALES", 540, 1080, 36, (0.8, 0.75, 0.65), sw=1, swcol=(0.1, 0.05, 0.05), anchor='c')

        dust(c, t, (0.8, 0.85, 1)); vignette(c, 0.75)
        fade = 0.0
        if t < 1.0: fade = max(fade, 1.0 - t/1.0)
        if t > duration - 1.0: fade = max(fade, (t - (duration - 1.0))/1.0)
        if fade > 0:
            c.set_source_rgba(0, 0, 0, fade); c.paint()

        p.stdin.write(bytes(surf.get_data()))

    p.stdin.close(); p.wait()
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-i', raw_video, '-i', wav_path,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', out_mp4
    ], check=True)
    if os.path.exists(raw_video): os.remove(raw_video)
    if os.path.exists(wav_path): os.remove(wav_path)
    print("Prologue done!")

def render_epilogue(out_mp4, duration=48.3):
    """Render cinematic movie epilogue with Sarvam narration"""
    print("Rendering Movie Epilogue...")
    voice_clips = [os.path.join(MOVIE_DIR, "voice", f"epilogue_{i}.wav") for i in range(3)]
    v_track = np.zeros(int(duration * SR), dtype=np.float32)
    t_offsets = [1.5, 16.0, 31.0]
    for idx, f in enumerate(voice_clips):
        if os.path.exists(f):
            with wave.open(f) as w:
                a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)/32768
            s = int(t_offsets[idx] * SR)
            v_track[s:s + len(a)] += a[:len(v_track) - s]

    tt = np.arange(len(v_track)) / SR
    drone = 0.08 * (np.sin(2*np.pi*43*tt) + np.sin(2*np.pi*46*tt))
    audio = np.clip(drone + v_track * 1.0, -1, 1)

    wav_path = out_mp4 + ".wav"
    raw_video = out_mp4 + ".raw.mp4"
    with wave.open(wav_path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((audio * 32767).astype(np.int16).tobytes())

    n_frames = int(duration * FPS)
    p = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", raw_video
    ], stdin=subprocess.PIPE)

    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(surf)

    for f in range(n_frames):
        t = f / FPS
        c.rectangle(0, 0, W, H); c.set_source_rgb(0.04, 0.02, 0.04); c.fill()
        glow(c, 540, 800, 480, (0.8, 0.05, 0.1), 0.35 + 0.1*math.sin(t*4), 8)
        # 10 silhouette mirrors in circle
        for k in range(10):
            ang = (k / 10.0) * 2 * math.pi + t*0.08
            rx = 540 + math.cos(ang) * 360
            ry = 800 + math.sin(ang) * 220
            rrect(c, rx - 35, ry - 60, 70, 120, 10); fs(c, hexc('281216'), 2)
            c.arc(rx, ry - 20, 18, 0, 6.3); fs(c, hexc('0d0508'))

        if t > 2.0:
            hbig(c, t, 2.0, 540, 1280, "आप अकेले नहीं हैं...", 94, (1, 0.25, 0.25), -0.02)
        if t > 28.0:
            hbig(c, t, 28.0, 540, 1460, "सबसे डरावनी कौन सी थी?", 78, (1, 0.9, 0.3), 0.01)
            hdraw(c, "कमेंट में अपनी राय बताओ!", 540, 1560, 40, (1, 1, 1), sw=2, swcol=(0.1, 0.05, 0.05), anchor='c')

        dust(c, t, (0.8, 0.85, 1)); vignette(c, 0.82)
        fade = 0.0
        if t < 1.0: fade = max(fade, 1.0 - t/1.0)
        if t > duration - 1.2: fade = max(fade, (t - (duration - 1.2))/1.2)
        if fade > 0:
            c.set_source_rgba(0, 0, 0, fade); c.paint()

        p.stdin.write(bytes(surf.get_data()))

    p.stdin.close(); p.wait()
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-i', raw_video, '-i', wav_path,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', out_mp4
    ], check=True)
    if os.path.exists(raw_video): os.remove(raw_video)
    if os.path.exists(wav_path): os.remove(wav_path)
    print("Epilogue done!")

def assemble_movie():
    """Concatenate all parts into the 10-minute master movie"""
    movie_output = os.path.join(MOVIE_DIR, "amawas_10_minute_horror_movie.mp4")
    concat_txt = os.path.join(MOVIE_DIR, "concat_list.txt")

    # 1. Render Prologue
    prologue_mp4 = os.path.join(MOVIE_DIR, "part_00_prologue.mp4")
    if not os.path.exists(prologue_mp4):
        render_prologue(prologue_mp4, duration=48.0)

    # 2. Render 10 Chapter Slates
    slate_files = []
    for idx, (ep_id, num, hi, en) in enumerate(CHAPTERS):
        slate_path = os.path.join(MOVIE_DIR, f"slate_{idx+1:02d}_{ep_id}.mp4")
        if not os.path.exists(slate_path):
            print(f"Rendering Slate {idx+1}: {hi}...")
            render_slate(slate_path, duration=12.0, title_num=num, title_hi=hi, title_en=en)
        slate_files.append((slate_path, os.path.join(SHORTS_DIR, ep_id, "final_short.mp4")))

    # 3. Render Epilogue
    epilogue_mp4 = os.path.join(MOVIE_DIR, "part_99_epilogue.mp4")
    if not os.path.exists(epilogue_mp4):
        render_epilogue(epilogue_mp4, duration=48.3)

    # 4. Write FFmpeg Concat List & Collect All Clips
    all_clips = [prologue_mp4]
    with open(concat_txt, 'w', encoding='utf-8') as f:
        f.write(f"file '{prologue_mp4}'\n")
        for slate_p, short_p in slate_files:
            f.write(f"file '{slate_p}'\n")
            f.write(f"file '{short_p}'\n")
            all_clips.extend([slate_p, short_p])
        f.write(f"file '{epilogue_mp4}'\n")
        all_clips.append(epilogue_mp4)

    # 5. Robust Seamless Assembly: Video copy + Audio sample-accurate stitch
    print(f"\nAssembling 10-minute master movie: {movie_output}...")
    temp_v = os.path.join(MOVIE_DIR, "temp_video.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', concat_txt,
        '-an', '-c:v', 'copy', temp_v
    ], check=True)

    # Audio concatenate
    master_wav = os.path.join(MOVIE_DIR, "master_audio.wav")
    audio_chunks = []
    for idx, clip in enumerate(all_clips):
        seg_wav = os.path.join(MOVIE_DIR, f"seg_{idx:02d}.wav")
        subprocess.run([
            'ffmpeg', '-y', '-v', 'error', '-i', clip, '-vn', '-ar', '44100', '-ac', '2',
            '-c:a', 'pcm_s16le', seg_wav
        ], check=True)
        with wave.open(seg_wav, 'rb') as w:
            audio_chunks.append(w.readframes(w.getnframes()))
        if os.path.exists(seg_wav): os.remove(seg_wav)

    with wave.open(master_wav, 'wb') as mw:
        mw.setnchannels(2); mw.setsampwidth(2); mw.setframerate(44100)
        for chunk in audio_chunks:
            mw.writeframes(chunk)

    # Mux Video + Audio
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-i', temp_v, '-i', master_wav,
        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', movie_output
    ], check=True)

    if os.path.exists(temp_v): os.remove(temp_v)
    if os.path.exists(master_wav): os.remove(master_wav)

    print(f"\n=======================================================")
    print(f"MASTER 10-MINUTE MOVIE COMPLETED: {movie_output}")
    print(f"=======================================================")
    return movie_output

if __name__ == "__main__":
    assemble_movie()

# -*- coding: utf-8 -*-
"""Generate multi-angle contact sheet for any rendered short"""
import sys, os, subprocess
from PIL import Image

def generate_contact_sheet(ep_dir):
    video = os.path.join(ep_dir, "final_short.mp4")
    if not os.path.exists(video):
        print("Video not found:", video)
        return
    
    # 4 distinct timestamps for 4 camera angles
    times = [3.0, 11.0, 21.0, 32.0]
    stills = []
    for idx, t in enumerate(times):
        out_jpg = os.path.join(ep_dir, f"angle_{idx}.jpg")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", video,
            "-vframes", "1", "-update", "1", "-q:v", "2", out_jpg
        ], check=True)
        if os.path.exists(out_jpg):
            stills.append(out_jpg)

    if len(stills) == 4:
        sheet = Image.new("RGB", (720, 1280))
        # 2x2 grid (each 360x640)
        im0 = Image.open(stills[0]).resize((360, 640))
        im1 = Image.open(stills[1]).resize((360, 640))
        im2 = Image.open(stills[2]).resize((360, 640))
        im3 = Image.open(stills[3]).resize((360, 640))
        sheet.paste(im0, (0, 0))
        sheet.paste(im1, (360, 0))
        sheet.paste(im2, (0, 640))
        sheet.paste(im3, (360, 640))
        sheet_path = os.path.join(ep_dir, "multi_angle_sheet.jpg")
        sheet.save(sheet_path, quality=88)
        print("Generated contact sheet:", sheet_path)
        for s in stills:
            if os.path.exists(s): os.remove(s)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_contact_sheet(sys.argv[1])
    else:
        shorts_dir = r"D:\2d-stiff-animation\shorts"
        for ep in sorted(os.listdir(shorts_dir)):
            ep_dir = os.path.join(shorts_dir, ep)
            if os.path.isdir(ep_dir) and os.path.exists(os.path.join(ep_dir, "final_short.mp4")):
                print(f"Generating contact sheet for {ep}...")
                generate_contact_sheet(ep_dir)

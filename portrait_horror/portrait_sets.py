# -*- coding: utf-8 -*-
"""Portrait 9:16 Sets, Character Cast, and Hindi Text Helpers for 'Lift Ka Niyam' (2:00 AM Elevator)."""
import math, cairo, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, features
from engine import *

# Overwrite engine canvas dimensions to 9:16 portrait
W, H = 1080, 1920
FPS = 30

# ------------------------------------------------------------------ Cast
SKINS['p'] = hexc('d6cfc4')  # pale ghostly
SKINS['g'] = hexc('8c6b54')  # weathered guard skin

CAST['kabir'] = dict(skin='b', hair='short', hair_col=hexc('1a1615'), shirt=hexc('d4d0c8'),
                     jacket=hexc('2b3548'), pants=hexc('1a1f2c'), shoes=hexc('252323'),
                     stubble=True, glasses=True)

CAST['guard'] = dict(skin='g', hair='bald', hair_col=hexc('706c68'), shirt=hexc('4a4235'),
                     jacket=hexc('322c22'), pants=hexc('26221b'), shoes=hexc('161412'),
                     mustache=True)

CAST['woman'] = dict(skin='p', hair='long', hair_col=hexc('100c0c'), shirt=hexc('8a1218'),
                     jacket=hexc('6e0c10'), pants=hexc('42080a'), shoes=hexc('180304'),
                     female=True)

# ------------------------------------------------------------------ Hindi Typography
_FONT_CANDIDATES = [
    r'C:\Windows\Fonts\NirmalaB.ttf',
    r'C:\Windows\Fonts\Nirmala.ttf',
    r'C:\Windows\Fonts\arialbd.ttf',
    r'C:\Windows\Fonts\mangal.ttf',
    '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
]
HF = next((f for f in _FONT_CANDIDATES if os.path.exists(f)), 'arial.ttf')
_has_raqm = features.check('raqm')
_layout_engine = ImageFont.Layout.RAQM if _has_raqm else ImageFont.Layout.BASIC
_fonts, _cache = {}, {}

def _pf(sz):
    k = int(sz)
    if k not in _fonts: _fonts[k] = ImageFont.truetype(HF, k, layout_engine=_layout_engine)
    return _fonts[k]

def hw(txt, size): return _pf(size).getlength(txt)

def hwrap(txt, size, maxw):
    words, lines, cur = txt.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if hw(t, size) > maxw and cur: lines.append(cur); cur = w_
        else: cur = t
    if cur: lines.append(cur)
    return lines

def hsurf(txt, size, col, sw, swcol):
    key = (txt, int(size), tuple(col), sw, tuple(swcol))
    if key in _cache: return _cache[key]
    f = _pf(size); pad = sw + 14
    asc, desc = f.getmetrics()
    w = int(f.getlength(txt)) + 2*pad; h = asc + desc + 2*pad
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rgb = tuple(int(x*255) for x in col[:3]); sc = tuple(int(x*255) for x in swcol[:3])
    d.text((pad, pad), txt, font=f, fill=rgb + (255,), stroke_width=sw, stroke_fill=sc + (255,), anchor='la')
    a = np.array(im).astype(np.float32); al = a[..., 3:4] / 255
    a[..., :3] *= al; bgra = a[..., [2, 1, 0, 3]].astype(np.uint8)
    buf = bytearray(bgra.tobytes()); surf = cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_ARGB32, w, h, w*4)
    _cache[key] = (surf, buf, w, h, pad); return _cache[key]

def hdraw(c, txt, x, y, size, col=(1, 1, 1), sw=0, swcol=(0, 0, 0), alpha=1.0, anchor='c'):
    surf, buf, w, h, pad = hsurf(txt, size, col, sw, swcol)
    c.save(); c.translate(x - (w/2 if anchor == 'c' else pad), y - h/2)
    c.set_source_surface(surf, 0, 0); c.paint_with_alpha(alpha); c.restore()

def hbig(c, t, t0, x, y, txt, size=96, col=(1, 1, 1), rot=-0.02, t1=None, shake=0):
    if t < t0 or (t1 and t > t1): return
    s = pop(t, t0)
    if t1: s *= 1 - ease((t - (t1 - 0.2))/0.2)
    jx = math.sin(t*60)*shake; jy = math.cos(t*47)*shake
    c.save(); c.translate(x + jx, y + jy); c.rotate(rot); c.scale(S(s), S(s))
    hdraw(c, txt, 0, 0, size, col, sw=max(4, size//14), swcol=(0.04, 0.02, 0.03)); c.restore()

def hsub(c, t, t0, t1, txt, y=1700, size=48):
    if t < t0 or t > t1: return
    k = clamp((t - t0)/0.25) * (1 - clamp((t - (t1 - 0.2))/0.2))
    lines = hwrap(txt, size, 940); lh = size*1.45; h = len(lines)*lh + 28
    lw = max(hw(l, size) for l in lines)
    c.save(); c.translate(W/2, y)
    rrect(c, -lw/2 - 30, -h/2, lw + 60, h, 18); c.set_source_rgba(0.04, 0.02, 0.05, 0.78*k); c.fill()
    for i, l in enumerate(lines):
        hdraw(c, l, 0, -h/2 + 14 + lh*(i + 0.5), size, (1, 1, 1), sw=2, swcol=(0, 0, 0), alpha=k)
    c.restore()

def hbubble(c, lt, t0, t1, x, y, txt, tip=None, size=42, maxw=780, bg=(0.99, 0.99, 0.97), fg=LINE, ol=LINE, rot=-0.02):
    if lt < t0 or lt > t1 + 0.01: return
    s = pop(lt, t0, 0.3) * (1 - ease((lt - (t1 - 0.2))/0.2))
    lines = hwrap(txt, size, maxw); lh = size*1.45
    lw = max(hw(l, size) for l in lines); w = lw + 70; h = len(lines)*lh + 36
    words = txt.split(); nshow = int(len(words)*clamp((lt - t0)/max(0.5, min(1.8, (t1 - t0)*0.65))) + 0.999)
    c.save(); c.translate(x, y); c.scale(S(s), S(s)); c.rotate(rot)
    shadow_rect(c, -w/2, -h/2, w, h, min(h/2, 36), 0.28)
    if tip:
        bx = clamp(tip[0]*0.3, -w/2 + 50, w/2 - 70)
        c.move_to(bx - 24, h/2 - 5); c.line_to(tip[0], tip[1]); c.line_to(bx + 24, h/2 - 5); c.close_path()
        c.set_source_rgb(*bg); c.fill_preserve(); stroke(c, 4, ol)
    rrect(c, -w/2, -h/2, w, h, min(h/2, 36)); c.set_source_rgb(*bg); c.fill_preserve(); stroke(c, 4, ol)
    if tip:
        c.move_to(bx - 20, h/2 - 2); c.line_to(bx + 20, h/2 - 2); c.set_source_rgb(*bg); c.set_line_width(8); c.stroke()
    shown = 0
    for i, l in enumerate(lines):
        ws = l.split(); k = max(0, min(len(ws), nshow - shown)); shown += len(ws)
        if k: hdraw(c, " ".join(ws[:k]), -lw/2, -h/2 + 18 + lh*(i + 0.5), size, fg, anchor='l')
    c.restore()

def tagt(c, lt, t0, t1, x, y, title, sub=None, rot=-0.04):
    if lt < t0 or lt > t1: return
    k = 1 - ease((lt - (t1 - 0.25))/0.25)
    c.save(); c.translate(x, y); c.scale(S(k), S(k)); c.translate(-x, -y); tag(c, lt, t0, x, y, title, sub, rot); c.restore()

def stampt(c, lt, t0, t1, *a, **k):
    if lt > t1: return
    stamp(c, lt, t0, *a, **k)

def hstamp(c, lt, t0, x, y, txt, rot=-0.06, size=42, col=(0.85, 0.15, 0.15)):
    if lt < t0: return
    s = pop(lt, t0, 0.22); w = hw(txt, size) + 60; h = size*2.2
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(S(s), S(s))
    rrect(c, -w/2, -h/2, w, h, 10); c.set_source_rgba(col[0], col[1], col[2], 0.15); c.fill_preserve()
    stroke(c, 4, col)
    rrect(c, -w/2 + 6, -h/2 + 6, w - 12, h - 12, 8); stroke(c, 1.8, col)
    hdraw(c, txt, 0, 0, size, col, anchor='c'); c.restore()

def hstampt(c, lt, t0, t1, *a, **k):
    if lt > t1: return
    hstamp(c, lt, t0, *a, **k)

# ------------------------------------------------------------------ SETS (9:16 Portrait)

def set_office_hallway(c, t):
    """Late night empty IT office corridor"""
    # Background wall
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.06, 0.08, 0.12); c.fill()
    # Floor perspective
    poly(c, [(0, 1200), (W, 1200), (W, H), (0, H)]); fs(c, hexc('141824'))
    for x in (180, 420, 660, 900):
        c.move_to(x, 1200); c.line_to(x*1.4 - 200, H); stroke(c, 2, hexc('1a2233'))
    # Ceiling tiles
    for y in range(0, 500, 100):
        c.move_to(0, y); c.line_to(W, y); stroke(c, 1.5, hexc('0e131d'))
    # Flickering fluorescent light
    f = 0.3 if math.sin(t*14)*math.cos(t*6) < -0.4 else 1.0
    c.rectangle(340, 60, 400, 30); c.set_source_rgba(0.85, 0.92, 1, 0.85*f); c.fill()
    glow(c, 540, 120, 220, (0.7, 0.85, 1), 0.35*f, 6)
    # Green exit sign
    rrect(c, 840, 80, 160, 60, 10); fs(c, hexc('0d2a14'), 2)
    font(c, 26); c.move_to(875, 120); c.set_source_rgb(0.3, 1, 0.4); c.show_text("EXIT")
    # Wall clock at 2:00 AM
    clock_face(c, 200, 320, 75, hr=2, mn=0)

def clock_face(c, cx, cy, r, hr=2, mn=0):
    c.arc(cx, cy, r, 0, 6.3); fs(c, hexc('1e2430'), 4)
    c.arc(cx, cy, r - 6, 0, 6.3); c.set_source_rgb(0.88, 0.86, 0.82); c.fill()
    c.arc(cx, cy, 4, 0, 6.3); c.set_source_rgb(0.1, 0.1, 0.1); c.fill()
    # Hands
    ang_m = (mn / 60) * 2 * math.pi - math.pi/2
    ang_h = ((hr % 12 + mn/60) / 12) * 2 * math.pi - math.pi/2
    c.move_to(cx, cy); c.line_to(cx + math.cos(ang_h)*(r*0.55), cy + math.sin(ang_h)*(r*0.55)); stroke(c, 5, hexc('111111'))
    c.move_to(cx, cy); c.line_to(cx + math.cos(ang_m)*(r*0.8), cy + math.sin(ang_m)*(r*0.8)); stroke(c, 3, hexc('992222'))

def set_guard_hallway(c, t):
    """Guard corner with flashlight beam"""
    set_office_hallway(c, t)
    # Flashlight beam cone
    c.save()
    g = cairo.LinearGradient(300, 1100, 950, 1400)
    g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.6)
    g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
    poly(c, [(320, 1120), (980, 900), (1050, 1600), (330, 1160)])
    c.set_source(g); c.fill(); c.restore()

def set_elevator_doors(c, t, open_ratio=0.0):
    """Elevator lobby with sliding metal doors"""
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.08, 0.09, 0.13); c.fill()
    # Floor
    poly(c, [(0, 1400), (W, 1400), (W, H), (0, H)]); fs(c, hexc('1a1c22'))
    # Wall panels
    c.rectangle(120, 200, 840, 1200); fs(c, hexc('222630'), 5)
    # Floor indicator
    rrect(c, 440, 260, 200, 90, 12); fs(c, hexc('0a0b0e'), 3)
    glow(c, 540, 305, 70, (1, 0.2, 0.2), 0.4, 4)
    font(c, 54); c.move_to(505, 325); c.set_source_rgb(1, 0.25, 0.25); c.show_text("13")
    # Doors
    dw = 380; split = dw * open_ratio
    # Left door
    c.rectangle(160 - split, 380, dw, 1020); fs(c, hexc('3a4050'), 4)
    # Right door
    c.rectangle(540 + split, 380, dw, 1020); fs(c, hexc('3a4050'), 4)
    # Interior void behind open doors
    if open_ratio > 0.05:
        c.save(); c.rectangle(160 + dw - split, 380, split*2, 1020); c.clip()
        c.rectangle(0, 380, W, 1020); c.set_source_rgb(0.04, 0.04, 0.06); c.fill()
        # Red ambient light in void
        glow(c, 540, 800, 300, (0.7, 0.1, 0.15), 0.45, 6)
        c.restore()

def set_elevator_inside(c, t, floor_num=14, flicker=False):
    """Inside elevator cabin with metal panels and rear mirror"""
    # Cabin walls
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.12, 0.14, 0.18); c.fill()
    # Rear large mirror
    rrect(c, 140, 280, 800, 1150, 16); fs(c, hexc('252c38'), 5)
    # Mirror reflection glass tint
    rrect(c, 155, 295, 770, 1120, 10)
    g = cairo.LinearGradient(155, 295, 925, 1415)
    g.add_color_stop_rgba(0, 0.22, 0.32, 0.42, 0.85)
    g.add_color_stop_rgba(1, 0.10, 0.14, 0.20, 0.95)
    c.set_source(g); c.fill()
    # Mirror bevel shine
    c.move_to(180, 310); c.line_to(900, 310); stroke(c, 2, hexc('5a7290'))
    # Handrail
    rrect(c, 80, 1180, 920, 24, 12); fs(c, hexc('808e9b'), 3)
    # Elevator control panel & digital display
    rrect(c, 880, 480, 140, 520, 14); fs(c, hexc('1c202a'), 3)
    rrect(c, 900, 505, 100, 65, 8); fs(c, hexc('06070a'))
    f = 0.2 if flicker and (int(t*18) % 3 == 0) else 1.0
    font(c, 42); c.move_to(922, 552); c.set_source_rgba(1, 0.2, 0.2, f); c.show_text(f"{floor_num:02d}")
    # Cabin ceiling light
    c.rectangle(260, 40, 560, 50); fs(c, hexc('eef4f8'), 3)
    glow(c, 540, 80, 320, (0.85, 0.92, 1), 0.38*f, 6)
    # Cabin floor
    poly(c, [(0, 1430), (W, 1430), (W, H), (0, H)]); fs(c, hexc('14161d'))

def set_mirror_climax(c, t):
    """Dramatic close up on mirror with glitching reflections"""
    set_elevator_inside(c, t, floor_num=16, flicker=True)
    # Blood red vignette / distortion pulse
    pulse = 0.4 + 0.3*math.sin(t*12)
    glow(c, 540, 750, 450, (0.8, 0.05, 0.1), pulse, 8)
    # Ghostly handprint silhouette on mirror glass
    c.save(); c.translate(620, 680); c.scale(0.8, 0.8)
    c.arc(0, 0, 40, 0, 6.3); c.set_source_rgba(0.6, 0.05, 0.1, 0.45); c.fill()
    for dx in (-30, -10, 12, 32):
        rrect(c, dx, -80, 14, 65, 7); c.set_source_rgba(0.6, 0.05, 0.1, 0.45); c.fill()
    c.restore()

def set_choice_portrait(c, t):
    """Interactive 9:16 vertical choice cards for Reels/Shorts"""
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.06, 0.04, 0.07); c.fill()
    glow(c, 540, 300, 400, (0.8, 0.2, 0.3), 0.25, 8)
    # 3 Choice Buttons
    options = [
        ("1", "इमरजेंसी घंटी बजाओ", "🚨 ALERT SECURITY", (0.9, 0.2, 0.25)),
        ("2", "शीशा तोड़कर भागो", "🔨 SMASH MIRROR", (0.25, 0.65, 0.95)),
        ("3", "छत का वेंट खोलो", "🕳️ CLIMB AIR VENT", (0.95, 0.75, 0.25))
    ]
    for idx, (num, hin, eng, col) in enumerate(options):
        by = 640 + idx*260
        rrect(c, 100, by, 880, 200, 28); fs(c, hexc('181b24'), 4)
        # Number badge
        c.arc(190, by + 100, 52, 0, 6.3); fs(c, col)
        font(c, 52); c.move_to(176, by + 118); c.set_source_rgb(1, 1, 1); c.show_text(num)
        # Hindi option text
        hdraw(c, hin, 490, by + 75, 48, (1, 1, 1), anchor='c')
        # English subtext
        font(c, 28); c.move_to(360, by + 145); c.set_source_rgba(col[0], col[1], col[2], 0.9); c.show_text(eng)

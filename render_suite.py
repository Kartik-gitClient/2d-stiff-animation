# -*- coding: utf-8 -*-
"""
UNIVERSAL 2D HORROR SHORTS & MOVIE RENDER ENGINE
Renders all 10 vertical 9:16 horror shorts + builds the 10-minute feature film.
"""
import os, sys, json, math, subprocess, wave, time
import numpy as np
import cairo
from PIL import Image, ImageDraw, ImageFont, features
from engine import (
    hexc, clamp, ease, back_out, lerp, S, rrect, poly, stroke, fs, shade, darker,
    font, text_c, SKINS, CAST, POSES, EXPR, arm, head, character,
    glow, stars, sky, MOODS, dust, vignette, shadow_rect, pop
)

# 9:16 Portrait Canvas
W, H = 1080, 1920
FPS = 30
LINE = (0.17, 0.11, 0.09)

# ------------------------------------------------------------------ Hindi Typography
_FONT_CANDIDATES = [
    r'C:\Windows\Fonts\NirmalaB.ttf',
    r'C:\Windows\Fonts\Nirmala.ttf',
    r'C:\Windows\Fonts\arialbd.ttf',
    r'C:\Windows\Fonts\mangal.ttf',
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

def hsub(c, t, t0, t1, txt, y=1700, size=46):
    if t < t0 or t > t1: return
    k = clamp((t - t0)/0.25) * (1 - clamp((t - (t1 - 0.2))/0.2))
    lines = hwrap(txt, size, 940); lh = size*1.45; h = len(lines)*lh + 28
    lw = max(hw(l, size) for l in lines)
    c.save(); c.translate(W/2, y)
    rrect(c, -lw/2 - 30, -h/2, lw + 60, h, 18); c.set_source_rgba(0.04, 0.02, 0.05, 0.82*k); c.fill()
    for i, l in enumerate(lines):
        hdraw(c, l, 0, -h/2 + 14 + lh*(i + 0.5), size, (1, 1, 1), sw=2, swcol=(0, 0, 0), alpha=k)
    c.restore()

def hbubble(c, lt, t0, t1, x, y, txt, tip=None, size=40, maxw=780, bg=(0.99, 0.99, 0.97), fg=LINE, ol=LINE, rot=-0.02):
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

def hstamp(c, lt, t0, x, y, txt, rot=-0.06, size=42, col=(0.85, 0.15, 0.15)):
    if lt < t0: return
    s = pop(lt, t0, 0.22); w = hw(txt, size) + 60; h = size*2.2
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(S(s), S(s))
    rrect(c, -w/2, -h/2, w, h, 10); c.set_source_rgba(col[0], col[1], col[2], 0.18); c.fill_preserve()
    stroke(c, 4, col)
    rrect(c, -w/2 + 6, -h/2 + 6, w - 12, h - 12, 8); stroke(c, 1.8, col)
    hdraw(c, txt, 0, 0, size, col, anchor='c'); c.restore()

def hstampt(c, lt, t0, t1, *a, **k):
    if lt > t1: return
    hstamp(c, lt, t0, *a, **k)

def choice_screen_portrait(c, t, title, opt1, opt2, opt3):
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.05, 0.03, 0.07); c.fill()
    glow(c, 540, 320, 380, (0.8, 0.15, 0.25), 0.3, 8)
    hbig(c, t, 0.1, 540, 320, title, 110, (1, 0.9, 0.3), -0.02)
    options = [("1", opt1, (0.9, 0.2, 0.25)), ("2", opt2, (0.25, 0.65, 0.95)), ("3", opt3, (0.95, 0.75, 0.25))]
    for idx, (num, hin, col) in enumerate(options):
        by = 640 + idx*260
        rrect(c, 100, by, 880, 200, 26); fs(c, hexc('181b24'), 4)
        c.arc(190, by + 100, 52, 0, 6.3); fs(c, col)
        font(c, 52); c.move_to(176, by + 118); c.set_source_rgb(1, 1, 1); c.show_text(num)
        hdraw(c, hin, 540, by + 100, 48, (1, 1, 1), anchor='c')
    hbig(c, t, 1.8, 540, 1550, "कमेंट में 1, 2 या 3 लिखो!", 66, (1, 1, 1), 0.0, shake=2)

# ------------------------------------------------------------------ Cast Extension
SKINS['p'] = hexc('d6cfc4')
SKINS['ghost'] = hexc('b8c2cc')

CAST['neeta'] = dict(skin='a', hair='long', hair_col=hexc('1c1512'), shirt=hexc('d48b7a'), jacket=hexc('4a2d34'), pants=hexc('2a2228'), shoes=hexc('e8e0d0'), female=True)
CAST['aman'] = dict(skin='b', hair='short', hair_col=hexc('1a1615'), shirt=hexc('e0dbd0'), jacket=hexc('2b3e58'), pants=hexc('1f242e'), shoes=hexc('252323'))
CAST['shalu'] = dict(skin='a', hair='short', hair_col=hexc('2b1f1a'), shirt=hexc('f2d06b'), pants=hexc('3a5a8a'), shoes=hexc('d84a3a'), chibi=True)
CAST['rohan'] = dict(skin='b', hair='short', hair_col=hexc('1a1615'), shirt=hexc('d8d4cc'), jacket=hexc('324a3e'), pants=hexc('222e28'), shoes=hexc('1e2220'), glasses=True)
CAST['simran'] = dict(skin='a', hair='long', hair_col=hexc('221815'), shirt=hexc('a84e68'), jacket=hexc('3a1e28'), pants=hexc('241820'), shoes=hexc('d8d0c8'), female=True)
CAST['aryan'] = dict(skin='c', hair='short', hair_col=hexc('181412'), shirt=hexc('d0a860'), jacket=hexc('5a4028'), pants=hexc('3a2818'), shoes=hexc('2a1e12'), stubble=True)
CAST['meera'] = dict(skin='b', hair='bun', hair_col=hexc('201814'), shirt=hexc('5c788a'), jacket=hexc('253540'), pants=hexc('1b252c'), shoes=hexc('182025'), female=True)
CAST['vikas'] = dict(skin='b', hair='short', hair_col=hexc('241d1a'), shirt=hexc('e2ddcf'), jacket=hexc('544236'), pants=hexc('30251e'), shoes=hexc('221a15'), stubble=True)
CAST['dev'] = dict(skin='b', hair='short', hair_col=hexc('1b1715'), shirt=hexc('d4cebe'), jacket=hexc('3e3450'), pants=hexc('262030'), shoes=hexc('1a1620'), glasses=True)
CAST['priya_k'] = dict(skin='a', hair='long', hair_col=hexc('181310'), shirt=hexc('c46860'), jacket=hexc('422020'), pants=hexc('281618'), shoes=hexc('dcd4c8'), female=True)
CAST['shadow_man'] = dict(skin='ghost', hair='bald', hair_col=hexc('111115'), shirt=hexc('151520'), jacket=hexc('0d0d14'), pants=hexc('08080c'), shoes=hexc('040406'))
CAST['bus_driver'] = dict(skin='ghost', hair='short', hair_col=hexc('606060'), shirt=hexc('354035'), jacket=hexc('202820'), pants=hexc('182018'), shoes=hexc('101410'), cap=hexc('202820'))

# ------------------------------------------------------------------ Visual Sets for 10 Episodes

def set_aaina(c, t, mirror_glitch=False):
    """Bedroom with ornate golden mirror"""
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.07, 0.06, 0.09); c.fill()
    poly(c, [(0, 1350), (W, 1350), (W, H), (0, H)]); fs(c, hexc('14121a'))
    # Mirror frame
    rrect(c, 160, 240, 760, 1100, 24); fs(c, hexc('8a6d2b'), 8)
    rrect(c, 180, 260, 720, 1060, 16)
    g = cairo.LinearGradient(180, 260, 900, 1320)
    g.add_color_stop_rgba(0, 0.25, 0.32, 0.45, 0.9)
    g.add_color_stop_rgba(1, 0.12, 0.15, 0.24, 0.95)
    c.set_source(g); c.fill()
    # Mirror bevel
    c.move_to(220, 280); c.line_to(860, 280); stroke(c, 2.5, hexc('c2a85e'))
    # Candle on dresser
    rrect(c, 80, 1280, 120, 70, 8); fs(c, hexc('403020'), 3)
    c.rectangle(125, 1210, 30, 70); fs(c, hexc('e8e0c8'), 2)
    flk = 0.8 + 0.2*math.sin(t*18)
    glow(c, 140, 1190, 80, (1, 0.8, 0.3), 0.6*flk, 6)
    if mirror_glitch:
        pulse = 0.4 + 0.3*math.sin(t*14)
        glow(c, 540, 790, 420, (0.8, 0.1, 0.2), pulse, 8)

def set_bus(c, t, seats_full=False):
    """Empty night bus with streetlights moving outside"""
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.08, 0.1, 0.14); c.fill()
    # Windows
    for i in range(3):
        wy = 320 + i*320
        rrect(c, 80, wy, 920, 240, 14); fs(c, hexc('152030'), 4)
        # Passing streetlight streak
        sx = (int(t*600 + i*300) % 1800) - 200
        glow(c, sx, wy + 120, 90, (1, 0.85, 0.4), 0.35, 4)
    # Bus aisle & seats
    poly(c, [(0, 1350), (W, 1350), (W, H), (0, H)]); fs(c, hexc('10141d'))
    # Bus seats
    for sy in (800, 1080, 1340):
        rrect(c, 120, sy, 320, 180, 18); fs(c, hexc('28453a'), 4)
        rrect(c, 640, sy, 320, 180, 18); fs(c, hexc('28453a'), 4)
        if seats_full:
            c.arc(280, sy + 60, 40, 0, 6.3); fs(c, hexc('151820'))
            c.arc(800, sy + 60, 40, 0, 6.3); fs(c, hexc('151820'))

def set_doll(c, t, eyes_glowing=False):
    """Child's room with shelf, moonlight window, antique doll"""
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.06, 0.06, 0.1); c.fill()
    # Moonbeam window
    rrect(c, 680, 220, 300, 500, 12); fs(c, hexc('1a2840'), 4)
    c.move_to(830, 220); c.line_to(830, 720); stroke(c, 3, hexc('101a2c'))
    c.move_to(680, 470); c.line_to(980, 470); stroke(c, 3, hexc('101a2c'))
    # Light shaft
    poly(c, [(680, 220), (980, 220), (600, 1500), (100, 1500)])
    c.set_source_rgba(0.7, 0.82, 1, 0.1); c.fill()
    # Wooden shelf
    rrect(c, 140, 700, 500, 35, 6); fs(c, hexc('482e18'), 3)
    # Floor
    poly(c, [(0, 1400), (W, 1400), (W, H), (0, H)]); fs(c, hexc('14121a'))
    if eyes_glowing:
        glow(c, 380, 600, 60, (0.9, 0.1, 0.2), 0.7, 5)

def set_shadow(c, t, detached=False):
    """Minimalist room with single overhead bulb and ominous wall shadow"""
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.12, 0.12, 0.14); c.fill()
    poly(c, [(0, 1400), (W, 1400), (W, H), (0, H)]); fs(c, hexc('1c1c20'))
    # Overhead hanging bulb
    c.move_to(540, 0); c.line_to(540, 220); stroke(c, 3, hexc('111111'))
    c.arc(540, 240, 25, 0, 6.3); fs(c, hexc('fff8d0'))
    fl = 0.85 + 0.15*math.sin(t*22)*math.sin(t*9)
    glow(c, 540, 260, 450, (1, 0.92, 0.65), 0.45*fl, 8)
    if detached:
        # Shadow figure stands tall against the wall looking directly
        c.save(); c.translate(760, 1000); c.scale(1.5, 1.5)
        c.arc(0, -220, 55, 0, 6.3); fs(c, hexc('050508'))
        rrect(c, -45, -160, 90, 220, 20); fs(c, hexc('050508'))
        # Red glowing eyes on shadow!
        c.arc(-18, -225, 6, 0, 6.3); c.set_source_rgb(1, 0.1, 0.2); c.fill()
        c.arc(18, -225, 6, 0, 6.3); c.set_source_rgb(1, 0.1, 0.2); c.fill()
        c.restore()

def set_phone(c, t, blackout=False):
    """Dark bedroom at 2:00 AM with glowing phone screen"""
    bg = (0.02, 0.02, 0.03) if blackout else (0.06, 0.07, 0.1)
    c.rectangle(0, 0, W, H); c.set_source_rgb(*bg); c.fill()
    poly(c, [(0, 1400), (W, 1400), (W, H), (0, H)]); fs(c, hexc('12141a') if not blackout else hexc('060608'))
    # Glowing Phone
    rrect(c, 340, 620, 400, 700, 28); fs(c, hexc('1a1f28'), 5)
    rrect(c, 360, 640, 360, 660, 16); fs(c, hexc('0b1420'))
    glow(c, 540, 970, 280, (0.3, 0.6, 0.95), 0.4, 6)
    font(c, 38); c.move_to(440, 780); c.set_source_rgb(1, 1, 1); c.show_text("INCOMING CALL")
    font(c, 54); c.move_to(420, 890); c.set_source_rgb(0.4, 0.9, 1); c.show_text("MY NUMBER")
    if blackout:
        glow(c, 540, 960, 500, (0.8, 0.05, 0.1), 0.45, 8)

def set_kuan(c, t, reflection_up=False):
    """Old stone well in desolate village at midnight"""
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.04, 0.05, 0.09); c.fill()
    stars(c, 0.7)
    # Moon
    glow(c, 860, 240, 90, (0.8, 0.88, 1), 0.4, 6)
    c.arc(860, 240, 50, 0, 6.3); fs(c, hexc('eef4ff'))
    # Ground
    poly(c, [(0, 1300), (W, 1300), (W, H), (0, H)]); fs(c, hexc('0d1218'))
    # Stone well
    rrect(c, 240, 1150, 600, 450, 24); fs(c, hexc('282c35'), 6)
    c.arc(540, 1150, 280, 0, math.pi); stroke(c, 5, hexc('181b22'))
    # Void inside well
    c.save(); c.arc(540, 1150, 260, 0, math.pi); c.clip()
    c.rectangle(260, 1150, 560, 300); fs(c, hexc('040508'))
    if reflection_up:
        glow(c, 540, 1260, 160, (0.2, 0.5, 0.8), 0.6, 6)
        c.arc(540, 1240, 48, 0, 6.3); fs(c, hexc('b8c2cc'))
    c.restore()

def set_train(c, t, speed_dark=False):
    """Vintage railway coach interior at midnight"""
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.08, 0.1, 0.12); c.fill()
    # Large train window
    rrect(c, 140, 340, 800, 700, 20); fs(c, hexc('080a10'), 5)
    if not speed_dark:
        # Faint passing station lamp
        sx = (int(t*450) % 1500) - 200
        glow(c, sx, 640, 120, (1, 0.8, 0.4), 0.35, 4)
    # Luggage rack
    rrect(c, 80, 200, 920, 40, 6); fs(c, hexc('5a6878'), 3)
    # Floor & Berth
    poly(c, [(0, 1380), (W, 1380), (W, H), (0, H)]); fs(c, hexc('141820'))
    rrect(c, 100, 1280, 880, 180, 16); fs(c, hexc('1f3d32'), 4)

def set_tasveer(c, t, zoom_photo=False):
    """Vintage study desk with 1942 antique sepia photo"""
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.09, 0.08, 0.07); c.fill()
    poly(c, [(0, 1350), (W, 1350), (W, H), (0, H)]); fs(c, hexc('281a14'))
    # Antique Photo Frame
    fw, fh = (720, 980) if zoom_photo else (540, 740)
    fx, fy = 540, 750
    rrect(c, fx - fw/2, fy - fh/2, fw, fh, 22); fs(c, hexc('5a3e28'), 7)
    # Sepia photo inside
    rrect(c, fx - fw/2 + 25, fy - fh/2 + 25, fw - 50, fh - 50, 12)
    fs(c, hexc('d8c4a0'))
    # Silhouette people in vintage 1942 wedding photo
    for px in (-160, -70, 20, 110, 200):
        c.arc(fx + px*(fw/600), fy - 60, 36, 0, 6.3); fs(c, hexc('403024'))
        rrect(c, fx + px*(fw/600) - 30, fy - 20, 60, 160, 12); fs(c, hexc('322418'))
    # Red marker ring around the double face
    c.arc(fx + 20*(fw/600), fy - 60, 46, 0, 6.3); stroke(c, 4, hexc('b82020'))

def set_pustakalaya(c, t, ink_rising=False):
    """Gothic library with Section C bookshelves and open cursed book"""
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.06, 0.05, 0.08); c.fill()
    # Bookshelves on left and right
    for bx in (60, 840):
        rrect(c, bx, 180, 180, 1200, 12); fs(c, hexc('281c16'), 4)
        for by in range(240, 1350, 180):
            rrect(c, bx + 10, by, 160, 20, 4); fs(c, hexc('402a20'))
            # Book spines
            for sx in range(bx + 15, bx + 150, 28):
                c.rectangle(sx, by - 120, 22, 120); fs(c, (0.3 + (sx%5)*0.1, 0.15, 0.2))
    # Section C sign
    rrect(c, 440, 220, 200, 70, 10); fs(c, hexc('141418'), 3)
    font(c, 36); c.move_to(475, 270); c.set_source_rgb(0.9, 0.8, 0.4); c.show_text("SEC - C")
    # Reading pedestal & open book
    poly(c, [(0, 1400), (W, 1400), (W, H), (0, H)]); fs(c, hexc('121016'))
    rrect(c, 340, 1100, 400, 220, 16); fs(c, hexc('35251c'), 4)
    # Open book pages
    poly(c, [(380, 1140), (530, 1155), (530, 1260), (380, 1240)]); fs(c, hexc('eee6d4'), 2)
    poly(c, [(550, 1155), (700, 1140), (700, 1240), (550, 1260)]); fs(c, hexc('eee6d4'), 2)
    if ink_rising:
        glow(c, 540, 1100, 260, (0.8, 0.1, 0.2), 0.55, 6)

def set_manzil_eight(c, t, door_open=False):
    """Endless apartment hallway on 8th floor with numbered doors"""
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.08, 0.08, 0.12); c.fill()
    poly(c, [(0, 1300), (W, 1300), (W, H), (0, H)]); fs(c, hexc('141620'))
    # Hallway perspective lines
    for x in (200, 450, 630, 880):
        c.move_to(x, 1300); c.line_to(x*1.4 - 200, H); stroke(c, 2, hexc('1a1e2c'))
    # Elevator frame behind
    rrect(c, 360, 220, 360, 120, 14); fs(c, hexc('0e1018'), 3)
    font(c, 64); c.move_to(515, 305); c.set_source_rgb(1, 0.2, 0.25); c.show_text("08")
    # Doors along hallway
    for dx in (140, 720):
        rrect(c, dx, 480, 220, 820, 12); fs(c, hexc('282e3c'), 4)
        font(c, 32); c.move_to(dx + 80, 560); c.set_source_rgb(0.9, 0.8, 0.4); c.show_text("801" if dx < 500 else "802")
    if door_open:
        rrect(c, 160, 500, 180, 800, 8); fs(c, hexc('05060a'))
        glow(c, 250, 900, 200, (0.8, 0.1, 0.2), 0.5, 6)

SETS_MAP = {
    "ep01_aaina": (set_aaina, "neeta", "आइना", "1. शीशा तोड़ दो", "2. घर से भागो", "3. हाथ पकड़ लो"),
    "ep02_antim_bus": (set_bus, "aman", "अंतिम बस", "1. खिड़की से कूदो", "2. आगे भागो", "3. शांत बैठो"),
    "ep03_gudiya": (set_doll, "shalu", "गुड़िया", "1. गुड़िया जला दो", "2. घर छोड़ दो", "3. उससे बात करो"),
    "ep04_chhaaya": (set_shadow, "rohan", "छाया", "1. बत्ती बुझा दो", "2. आईने में देखो", "3. बाहर भागो"),
    "ep05_phone_call": (set_phone, "simran", "फ़ोन कॉल", "1. फ़ोन फेंक दो", "2. मोमबत्ती जलाओ", "3. इंतज़ार करो"),
    "ep06_kuan": (set_kuan, "aryan", "कुआँ", "1. रस्सी फेंको", "2. भाग जाओ", "3. पत्थर गिराओ"),
    "ep07_train": (set_train, "meera", "रात की ट्रेन", "1. चेन खींचो", "2. दूसरे डिब्बे में भागो", "3. कूद जाओ"),
    "ep08_tasveer": (set_tasveer, "vikas", "तस्वीर", "1. फ़ोटो फाड़ दो", "2. दादाजी से पूछो", "3. घर से निकलो"),
    "ep09_pustakalaya": (set_pustakalaya, "dev", "पुस्तकालय", "1. किताब बंद करो", "2. आग लगाओ", "3. दौड़ लगाओ"),
    "ep10_manzil": (set_manzil_eight, "priya_k", "मंज़िल", "1. लिफ़्ट में घुसो", "2. सीढ़ियों से भागो", "3. दरवाज़ा बंद करो"),
}

# ------------------------------------------------------------------ Shot Class
class Shot:
    def __init__(self, t0, t1, set_fn, chars=(), set_kwargs=None, ov_fn=None, subs=True, text="",
                 zoom=(1.0, 1.1), focus=None, rot=0.0, shakes=(), dark=0.0):
        self.t0, self.t1 = t0, t1
        self.set_fn = set_fn
        self.chars = list(chars)
        self.set_kwargs = set_kwargs or {}
        self.ov_fn = ov_fn
        self.subs = subs
        self.text = text
        self.zoom = zoom
        self.focus = focus or (W/2, H*0.55)
        self.rot = rot
        self.shakes = list(shakes)
        self.dark = dark

    def render(self, c, t):
        lt = t - self.t0; dur = max(0.1, self.t1 - self.t0)
        z = lerp(self.zoom[0], self.zoom[1], ease(lt/dur))
        fx, fy = self.focus

        # Screen shakes
        sx = sy = 0
        for kt in self.shakes:
            if 0 <= lt - kt < 0.35:
                a = 26 * (1 - (lt - kt)/0.35)
                sx += math.sin(lt*93)*a
                sy += math.cos(lt*79)*a

        c.save()
        c.translate(fx + sx, fy + sy)
        c.scale(z, z)
        if self.rot:
            c.rotate(self.rot)
        c.translate(-fx, -fy)

        self.set_fn(c, t, **self.set_kwargs)
        for ch in self.chars:
            cx, cy = ch.get('x', 540), ch.get('y', 1480)
            cs = ch.get('s', 1.35)
            c.save(); c.translate(cx, cy); c.scale(cs, cs)
            character(c, ch['name'], t, ch.get('pose', 'idle'), ch.get('expr', 'neutral'),
                      ((t*1.2) % 3.6) < 0.12, ch.get('flip', False), None, 0, ch.get('seed', 1))
            c.restore()
        c.restore()

        dust(c, t, (0.8, 0.85, 1)); vignette(c, 0.72)
        if self.dark > 0:
            c.set_source_rgba(0, 0, 0, self.dark); c.paint()
        if self.ov_fn:
            self.ov_fn(c, lt)
        if self.subs and self.text:
            hsub(c, t, self.t0 + 0.1, self.t1 - 0.2, self.text)

# ------------------------------------------------------------------ Build Episode Timeline with Dynamic Multi-Angle Cinematography
def build_episode_shots(ep_id, data):
    set_fn, char_name, title, opt1, opt2, opt3 = SETS_MAP[ep_id]
    lines = data['lines']
    n_lines = len(lines)
    shots = []

    # Camera directors angles for each shot in a horror narrative
    CAMERA_DIRECTOR = [
        # Shot 0: Wide establishing shot (the room/setting, character at side, title)
        dict(zoom=(1.0, 1.1), focus=(540, 1050), rot=0.0, char_x=380, char_s=1.35, pose='idle', expr='neutral'),
        # Shot 1: Over-The-Shoulder / Medium shot (approaching/interacting)
        dict(zoom=(1.25, 1.35), focus=(540, 950), rot=0.02, char_x=680, char_s=1.55, pose='think', expr='neutral'),
        # Shot 2: POV / Reaction Reverse Shot (focus on the anomaly/mirror/book/clock)
        dict(zoom=(1.5, 1.7), focus=(540, 750), rot=-0.03, char_x=540, char_s=1.65, pose='hold', expr='worried'),
        # Shot 3: Dutch Angle Close-Up on character (dialogue, speech bubble)
        dict(zoom=(1.75, 1.95), focus=(480, 880), rot=-0.06, char_x=480, char_s=1.85, pose='think', expr='worried'),
        # Shot 4: Macro Close-Up on the supernatural horror event
        dict(zoom=(2.1, 2.4), focus=(540, 700), rot=0.05, char_x=540, char_s=2.1, pose='up', expr='shock'),
        # Shot 5: High-intensity Climax (screen shake, jump, monster reveal)
        dict(zoom=(1.8, 2.1), focus=(540, 850), rot=-0.04, char_x=540, char_s=1.75, pose='up', expr='shock', shakes=[0.15, 0.45]),
        # Shot 6: Suspense beat / Cliffhanger
        dict(zoom=(1.4, 1.55), focus=(540, 950), rot=0.02, char_x=540, char_s=1.5, pose='sad', expr='shock'),
        # Shot 7: Shock reveal
        dict(zoom=(2.0, 2.2), focus=(540, 800), rot=-0.05, char_x=540, char_s=1.9, pose='up', expr='shock', shakes=[0.2]),
        # Shot 8: Extreme climax
        dict(zoom=(1.6, 1.8), focus=(540, 900), rot=0.03, char_x=540, char_s=1.6, pose='up', expr='shock'),
    ]

    for i, line in enumerate(lines):
        t0, t1 = line['t0'], line['t1']
        spk, text = line['spk'], line['text']
        is_choice = (i == n_lines - 1)
        is_climax = (i >= n_lines - 3 and not is_choice)

        cam = CAMERA_DIRECTOR[min(i, len(CAMERA_DIRECTOR)-1)]

        kwargs = {}
        if ep_id == "ep01_aaina" and is_climax: kwargs['mirror_glitch'] = True
        elif ep_id == "ep02_antim_bus" and i >= 3: kwargs['seats_full'] = True
        elif ep_id == "ep03_gudiya" and is_climax: kwargs['eyes_glowing'] = True
        elif ep_id == "ep04_chhaaya" and is_climax: kwargs['detached'] = True
        elif ep_id == "ep05_phone_call" and is_climax: kwargs['blackout'] = True
        elif ep_id == "ep06_kuan" and is_climax: kwargs['reflection_up'] = True
        elif ep_id == "ep07_train" and is_climax: kwargs['speed_dark'] = True
        elif ep_id == "ep08_tasveer" and is_climax: kwargs['zoom_photo'] = True
        elif ep_id == "ep09_pustakalaya" and is_climax: kwargs['ink_rising'] = True
        elif ep_id == "ep10_manzil" and is_climax: kwargs['door_open'] = True

        chars = []
        if not is_choice:
            cx = cam.get('char_x', 540)
            cs = cam.get('char_s', 1.35)
            expr = cam.get('expr', 'neutral')
            pose = cam.get('pose', 'idle')
            chars.append(dict(name=char_name, x=cx, y=1480, s=cs, expr=expr, pose=pose))

        def make_ov(shot_idx, s_spk, s_text, is_ch):
            def ov(c, lt):
                if shot_idx == 0:
                    hbig(c, lt, 0.3, 540, 280, title, 108, (1, 0.28, 0.25), -0.02, t1=3.8)
                    hstampt(c, lt, 4.0, 7.5, 540, 420, "NEW HOUSE" if ep_id=="ep01_aaina" else "12:00 AM", rot=0.04, size=40)
                elif is_ch:
                    choice_screen_portrait(c, lt, "आपका फ़ैसला?", opt1, opt2, opt3)
                elif s_spk != 'N':
                    hbubble(c, lt, 0.1, (t1 - t0) - 0.2, 540, 480, s_text, tip=(0, 220), size=44, maxw=820)
            return ov

        ov_fn = make_ov(i, spk, text, is_choice)
        z = (1.0, 1.02) if is_choice else cam.get('zoom', (1.0, 1.1))
        foc = (540, 960) if is_choice else cam.get('focus', (540, 1000))
        rot = 0.0 if is_choice else cam.get('rot', 0.0)
        shk = () if is_choice else cam.get('shakes', ())

        shots.append(Shot(
            t0, t1, set_fn, chars, kwargs, ov_fn,
            subs=(spk == 'N' and not is_choice), text=text,
            zoom=z, focus=foc, rot=rot, shakes=shk
        ))

    return shots

# ------------------------------------------------------------------ Procedural SFX Builder
SR = 44100
def build_horror_sfx(total_sec):
    n = int((total_sec + 1)*SR); tr = np.zeros(n); tt = np.arange(n)/SR
    # Ambient sub-bass drone
    tr += 0.07*(np.sin(2*np.pi*46*tt) + np.sin(2*np.pi*49.5*tt))*(0.7 + 0.3*np.sin(2*np.pi*0.09*tt))
    # Wind turbulence
    rng = np.random.default_rng(13)
    w = np.convolve(rng.standard_normal(n), np.ones(90)/90, 'same')
    tr += 0.35*w*(0.04 + 0.03*np.sin(2*np.pi*0.11*tt))
    # Heartbeat in second half
    half = total_sec * 0.45
    t_h = half
    while t_h < total_sec - 1.5:
        idx = int(t_h*SR)
        m_ = int(0.25*SR); x = np.arange(m_)/SR
        hb = 0.55*np.sin(2*np.pi*56*x)*np.minimum(1, x/0.004)*np.exp(-x*22)
        if idx + len(hb) < n: tr[idx:idx + len(hb)] += hb
        # second thud
        idx2 = idx + int(0.2*SR)
        if idx2 + len(hb) < n: tr[idx2:idx2 + len(hb)] += hb*0.75
        t_h += 0.82
    tr = np.clip(tr, -1, 1)
    return tr

# ------------------------------------------------------------------ Renderer
def render_episode(ep_id):
    ep_dir = os.path.join(r"D:\2d-stiff-animation\shorts", ep_id)
    timing_path = os.path.join(ep_dir, "timing.json")
    voice_path = os.path.join(ep_dir, "voice.wav")
    out_video = os.path.join(ep_dir, "final_short.mp4")
    raw_video = os.path.join(ep_dir, "video_silent.mp4")
    sfx_path = os.path.join(ep_dir, "sfx.wav")

    print(f"\n==========================================")
    print(f"RENDERING: {ep_id}")
    print(f"==========================================")

    data = json.load(open(timing_path, encoding='utf-8'))
    total_sec = data['total']
    shots = build_episode_shots(ep_id, data)

    # 1. Build SFX
    sfx_arr = build_horror_sfx(total_sec)
    with wave.open(sfx_path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(sfx_arr, -1, 1)*32767).astype(np.int16).tobytes())

    # 2. Render Frames Pipe
    fps = 30
    n_frames = int(total_sec * fps)
    p = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
        "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", raw_video
    ], stdin=subprocess.PIPE)

    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)

    t0_render = time.time()
    for f in range(n_frames):
        t = f / fps
        sh = next((s for s in shots if s.t0 <= t < s.t1), shots[-1])
        sh.render(ctx, t)
        # Smooth fades at head and tail
        fade = 0.0
        if t < 0.6: fade = max(fade, 1.0 - t/0.6)
        if t > total_sec - 0.7: fade = max(fade, (t - (total_sec - 0.7))/0.7)
        if fade > 0:
            ctx.set_source_rgba(0, 0, 0, fade); ctx.paint()

        p.stdin.write(bytes(surf.get_data()))
        if f % 180 == 0:
            pct = round(f / n_frames * 100)
            elapsed = round(time.time() - t0_render, 1)
            print(f"  [{ep_id}] Frame {f}/{n_frames} ({pct}%) in {elapsed}s", flush=True)

    p.stdin.close()
    p.wait()

    # 3. Audio Mix with Voice
    mix_raw = os.path.join(ep_dir, "mix_raw.wav")
    sfx_data = np.frombuffer(wave.open(sfx_path).readframes(10**9), dtype=np.int16).astype(np.float32)/32768
    out_audio = sfx_data * 0.45
    if os.path.exists(voice_path):
        v = np.frombuffer(wave.open(voice_path).readframes(10**9), dtype=np.int16).astype(np.float32)/32768
        mlen = max(len(v), len(out_audio))
        o = np.zeros(mlen, dtype=np.float32)
        o[:len(out_audio)] += out_audio; o[:len(v)] += v * 1.0
        out_audio = o
    with wave.open(mix_raw, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(out_audio, -1, 1)*32767).astype(np.int16).tobytes())

    # 4. Final Mux
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-i', raw_video, '-i', mix_raw,
        '-af', 'loudnorm=I=-14:TP=-1.5', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', out_video
    ], check=True)

    print(f"  ✓ [{ep_id}] Rendered: {out_video}")
    return out_video

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target == "all":
        for ep in SETS_MAP.keys():
            render_episode(ep)
    else:
        render_episode(target)

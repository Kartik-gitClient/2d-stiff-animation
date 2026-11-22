# -*- coding: utf-8 -*-
"""Horror sets + Hindi text helpers for the GrowKaz cutout engine."""
import math, cairo, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from engine import *

# ------------------------------------------------------------------ cast
SKINS['p'] = hexc('d6cfc4')           # pale (manager)
CAST['rahul'] = dict(skin='b', hair='short', hair_col=hexc('1e1715'), shirt=hexc('d8d4cc'), jacket=hexc('b8452e'),
                     pants=hexc('2e3548'), shoes=hexc('2d2a2a'), stubble=True)
CAST['vinni'] = dict(skin='a', hair='long', hair_col=hexc('2a1a14'), shirt=hexc('e4c46a'), jacket=hexc('2f7a82'),
                     pants=hexc('3a3a48'), shoes=hexc('e8e0d0'), female=True)
CAST['manager'] = dict(skin='p', hair='bald', hair_col=hexc('8a8a88'), shirt=hexc('3a3a30'), jacket=hexc('26231f'),
                       tie=hexc('6a1e1e'), pants=hexc('26231f'), shoes=hexc('141210'), mustache=True, glasses=True)

# ------------------------------------------------------------------ Hindi text (PIL + RAQM shaping -> cairo)
from PIL import features
_FONT_CANDIDATES = [
    r'C:\Windows\Fonts\NirmalaB.ttf',
    r'C:\Windows\Fonts\Nirmala.ttf',
    r'C:\Windows\Fonts\arialbd.ttf',
    r'C:\Windows\Fonts\mangal.ttf',
    '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
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
    f = _pf(size); pad = sw + 12
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

def hbig(c, t, t0, x, y, txt, size=96, col=(1, 1, 1), rot=-0.03, t1=None, shake=0):
    if t < t0 or (t1 and t > t1): return
    s = pop(t, t0)
    if t1: s *= 1 - ease((t - (t1 - 0.2))/0.2)
    jx = math.sin(t*60)*shake; jy = math.cos(t*47)*shake
    c.save(); c.translate(x + jx, y + jy); c.rotate(rot); c.scale(S(s), S(s))
    hdraw(c, txt, 0, 0, size, col, sw=max(4, size//14), swcol=(0.05, 0.02, 0.04)); c.restore()

def hsub(c, t, t0, t1, txt, y=972, size=46):
    if t < t0 or t > t1: return
    k = clamp((t - t0)/0.25) * (1 - clamp((t - (t1 - 0.2))/0.2))
    lines = hwrap(txt, size, 1500); lh = size*1.5; h = len(lines)*lh + 22
    lw = max(hw(l, size) for l in lines)
    c.save(); c.translate(W/2, y)
    rrect(c, -lw/2 - 34, -h/2, lw + 68, h, 16); c.set_source_rgba(0.04, 0.02, 0.05, 0.72*k); c.fill()
    for i, l in enumerate(lines): hdraw(c, l, 0, -h/2 + 11 + lh*(i + 0.5), size, (1, 1, 1), sw=2, swcol=(0, 0, 0), alpha=k)
    c.restore()

def hbubble(c, lt, t0, t1, x, y, txt, tip=None, size=40, maxw=620, bg=(0.99, 0.99, 0.97), fg=LINE, ol=LINE, rot=-0.02):
    if lt < t0 or lt > t1 + 0.01: return
    s = pop(lt, t0, 0.3) * (1 - ease((lt - (t1 - 0.2))/0.2))
    lines = hwrap(txt, size, maxw); lh = size*1.5
    lw = max(hw(l, size) for l in lines); w = lw + 80; h = len(lines)*lh + 36
    words = txt.split(); nshow = int(len(words)*clamp((lt - t0)/max(0.5, min(1.8, (t1 - t0)*0.65))) + 0.999)
    c.save(); c.translate(x, y); c.scale(S(s), S(s)); c.rotate(rot)
    shadow_rect(c, -w/2, -h/2, w, h, min(h/2, 40), 0.25)
    if tip:
        bx = clamp(tip[0]*0.3, -w/2 + 60, w/2 - 90)
        c.move_to(bx - 28, h/2 - 6); c.line_to(tip[0], tip[1]); c.line_to(bx + 28, h/2 - 6); c.close_path()
        c.set_source_rgb(*bg); c.fill_preserve(); stroke(c, 4, ol)
    rrect(c, -w/2, -h/2, w, h, min(h/2, 40)); c.set_source_rgb(*bg); c.fill_preserve(); stroke(c, 4, ol)
    if tip:
        c.move_to(bx - 24, h/2 - 2); c.line_to(bx + 24, h/2 - 2); c.set_source_rgb(*bg); c.set_line_width(8); c.stroke()
    shown = 0
    for i, l in enumerate(lines):
        ws = l.split(); k = max(0, min(len(ws), nshow - shown)); shown += len(ws)
        if k: hdraw(c, " ".join(ws[:k]), -lw/2, -h/2 + 18 + lh*(i + 0.5), size, fg, anchor='l')
    c.restore()

def tagt(c, lt, t0, t1, x, y, title, sub=None, rot=-0.05):
    """name tag that pops in and shrinks out"""
    if lt < t0 or lt > t1: return
    k = 1 - ease((lt - (t1 - 0.25))/0.25)
    c.save(); c.translate(x, y); c.scale(S(k), S(k)); c.translate(-x, -y); tag(c, lt, t0, x, y, title, sub, rot); c.restore()

def stampt(c, lt, t0, t1, *a, **k):
    if lt > t1: return
    stamp(c, lt, t0, *a, **k)

# ------------------------------------------------------------------ night helpers
def flick(t, seed=0.0):
    v = math.sin(t*11 + seed)*math.sin(t*3.7 + seed*2)
    return 0.3 if v < -0.55 else 1.0

def moon(c, x, y, r):
    glow(c, x, y, r, (0.75, 0.82, 1.0), 0.5, 6)
    c.arc(x, y, r, 0, 6.3); c.set_source_rgba(0.92, 0.94, 1, 1); c.fill()
    for dx, dy, rr in ((-20, -14, 16), (22, 18, 12), (6, -30, 9), (-26, 24, 8)):
        c.arc(x + dx*r/70, y + dy*r/70, rr*r/70, 0, 6.3); c.set_source_rgba(0.72, 0.78, 0.92, 0.7); c.fill()

def fog(c, t, y, a=0.16, col=(0.72, 0.8, 0.92), n=7, sp=14, sc=2.6, ry=0.5):
    for i in range(n):
        x = ((i*(W + 700)/n) + t*sp*(1 + 0.3*(i % 3))) % (W + 700) - 350
        yy = y + math.sin(t*0.4 + i)*14
        c.save(); c.translate(x, yy); c.scale(sc, ry)
        g = cairo.RadialGradient(0, 0, 0, 0, 0, 260)
        g.add_color_stop_rgba(0, col[0], col[1], col[2], a); g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
        c.set_source(g); c.arc(0, 0, 260, 0, 6.3); c.fill(); c.restore()

def ridge(c, base, amp, col, seed, off=0.0, scale=1.0):
    c.move_to(-50, H)
    for x in range(-50, W + 100, 40):
        xx = x + off
        y = base - amp*(0.5 + 0.3*math.sin(xx*0.004*scale + seed) + 0.2*math.sin(xx*0.011*scale + seed*2.3) + 0.06*math.sin(xx*0.03 + seed))
        c.line_to(x, y)
    c.line_to(W + 100, H); c.close_path(); c.set_source_rgba(*col); c.fill()

def pine(c, x, y, s, col):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.rectangle(-8, -50, 16, 50); c.set_source_rgba(*col); c.fill()
    for k in range(4):
        yb = -40 - k*62; hw_ = 74 - k*14
        poly(c, [(-hw_, yb), (hw_, yb), (0, yb - 110)]); c.set_source_rgba(*col); c.fill()
    c.restore()

def night_sky(c, t, moon_xy=(1450, 210), r=70):
    sky(c, MOODS['night']); stars(c, 0.7); moon(c, *moon_xy, r)

# ------------------------------------------------------------------ SET: road, car side view
def car_side(c, t):
    c.save(); c.translate(0, math.sin(t*9)*2.2)
    # headlight beam
    g = cairo.LinearGradient(260, -85, 1000, -85); g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.55); g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
    poly(c, [(258, -86), (1000, -10), (1000, -200)]); c.set_source(g); c.fill()
    body = hexc('8a2a2a')
    rrect(c, -260, -122, 520, 82, 30); fs(c, body)
    poly(c, [(-140, -122), (-96, -196), (74, -196), (150, -122)]); fs(c, body)
    for pts in ([(-118, -128), (-84, -184), (-8, -184), (-8, -128)], [(8, -128), (8, -184), (66, -184), (126, -128)]):
        poly(c, pts); fs(c, hexc('2a3e5a'), 3)
    c.arc(-52, -154, 19, 0, 6.3); c.set_source_rgba(0.04, 0.03, 0.06, 0.95); c.fill()      # Vinni (passenger)
    c.arc(44, -154, 20, 0, 6.3); c.fill()                                                     # Rahul (driver)
    c.arc(-56, -125, 30, math.pi, 0); c.fill(); c.arc(40, -125, 30, math.pi, 0); c.fill()
    glow(c, 258, -88, 14, (1, 0.95, 0.7), 0.9, 4); c.arc(258, -88, 14, 0, 6.3); c.set_source_rgb(1, 0.97, 0.8); c.fill()
    glow(c, -258, -92, 10, (1, 0.1, 0.1), 0.8, 4); c.arc(-258, -92, 8, 0, 6.3); c.set_source_rgb(1, 0.2, 0.2); c.fill()
    for wx in (-150, 150):
        c.save(); c.translate(wx, -42); c.arc(0, 0, 44, 0, 6.3); fs(c, hexc('16161c'))
        c.arc(0, 0, 22, 0, 6.3); fs(c, hexc('9aa0ac'), 2.5)
        c.rotate(-t*9)
        for i in range(5): c.move_to(0, 0); c.line_to(0, -22); c.rotate(6.2832/5); stroke(c, 3, hexc('5a606c'))
        c.restore()
    c.restore()

def set_road(c, t, **kw):
    night_sky(c, t)
    ridge(c, 700, 300, hexc('141a3a'), 1.0, off=t*4); ridge(c, 790, 240, hexc('0d1230'), 3.1, off=t*10)
    fog(c, 700, 0.18)
    for i in range(14):
        x = (i*190 - t*150) % (W + 400) - 200; pine(c, x, 800, 0.9 + (i % 3)*0.18, hexc('080b1c'))
    g = cairo.LinearGradient(0, 800, 0, H); g.add_color_stop_rgba(0, *hexc('23232d')); g.add_color_stop_rgba(1, *hexc('0e0e14'))
    c.rectangle(0, 800, W, H); c.set_source(g); c.fill(); c.move_to(0, 800); c.line_to(W, 800); stroke(c, 3, hexc('0a0a10'))
    for k in range(12):
        x = (k*220 - t*430) % (W + 220) - 220; rrect(c, x, 962, 120, 12, 4); c.set_source_rgba(0.85, 0.78, 0.4, 0.8); c.fill()
    c.save(); c.translate(780, 905); c.scale(1.25, 1.25); car_side(c, t); c.restore()
    fog(c, 900, 0.14, n=5, sp=30)

# ------------------------------------------------------------------ SET: inside the car
def set_car(c, t, **kw):
    night_sky(c, t, (1050, 330), 55)
    hz = 520
    ridge(c, hz + 20, 200, hexc('141a3a'), 2.0, off=t*3); fog(c, hz + 10, 0.2)
    c.rectangle(0, hz, W, H); c.set_source_rgba(*hexc('0c0f1c')); c.fill()
    half = lambda z: 30 + z**2.2*760
    yy = lambda z: hz + (H - hz)*z**2.2
    poly(c, [(960 - 30, hz), (960 + 30, hz), (960 + 790, H), (960 - 790, H)]); c.set_source_rgba(*hexc('26262f')); c.fill()
    g = cairo.LinearGradient(0, hz, 0, H); g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.0); g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0.28)
    poly(c, [(960 - 30, hz), (960 + 30, hz), (960 + 790, H), (960 - 790, H)]); c.set_source(g); c.fill()
    for k in range(14):
        z0 = ((k/14) + t*0.45) % 1.0; z1 = z0 + 0.035
        poly(c, [(960 - 2 - z0**2.2*20, yy(z0)), (960 + 2 + z0**2.2*20, yy(z0)), (960 + 2 + z1**2.2*20, yy(z1)), (960 - 2 - z1**2.2*20, yy(z1))])
        c.set_source_rgba(0.9, 0.82, 0.45, 0.85); c.fill()
    for i in range(12):
        z = ((i/12) + t*0.17) % 1.0
        for sd in (-1, 1):
            pine(c, 960 + sd*(half(z)*1.35 + 40), yy(z), 0.05 + z**2.2*1.5, hexc('06081a'))
    fog(c, hz + 30, 0.22, n=5, sp=20)

def car_fg(c, t, **kw):
    dark = hexc('0d0d12')
    rrect(c, -20, -20, W + 40, 100, 0); c.set_source_rgba(*dark); c.fill()
    poly(c, [(-10, 0), (200, 0), (80, 830), (-10, 830)]); c.set_source_rgba(*dark); c.fill()
    poly(c, [(W + 10, 0), (W - 200, 0), (W - 80, 830), (W + 10, 830)]); c.set_source_rgba(*dark); c.fill()
    c.move_to(-10, 830); c.curve_to(500, 770, 1400, 770, W + 10, 830); c.line_to(W + 10, H + 10); c.line_to(-10, H + 10); c.close_path()
    g = cairo.LinearGradient(0, 780, 0, H); g.add_color_stop_rgba(0, *hexc('1c1c24')); g.add_color_stop_rgba(1, *hexc('08080c'))
    c.set_source(g); c.fill()
    rrect(c, 900, 90, 120, 50, 12); fs(c, hexc('15151b'))                                  # rear-view mirror
    c.set_source_rgba(0.5, 0.7, 1, 0.12); rrect(c, 906, 96, 108, 38, 8); c.fill()
    # steering wheel (driver on the right, India)
    c.save(); c.translate(1300, 960); c.scale(1, 0.5); c.arc(0, 0, 150, 0, 6.3); c.restore(); stroke(c, 22, hexc('101014'))
    # dash glow
    glow(c, 960, 900, 40, (0.4, 0.8, 1.0), 0.18, 5)
    c.arc(1100, 880, 7, 0, 6.3); c.set_source_rgba(1, 0.2, 0.2, 0.5 + 0.5*math.sin(t*5)); c.fill()

# ------------------------------------------------------------------ SET: hotel exterior
def branch(c, x, y, ang, ln, d, t):
    if d == 0: return
    x2 = x + math.cos(ang)*ln; y2 = y + math.sin(ang)*ln
    c.move_to(x, y); c.line_to(x2, y2); stroke(c, 3 + d*2.4, hexc('07070f'))
    sw = math.sin(t*0.8 + d)*0.04
    branch(c, x2, y2, ang - 0.5 + sw, ln*0.72, d - 1, t); branch(c, x2, y2, ang + 0.45 + sw, ln*0.72, d - 1, t)

def set_hotel(c, t, **kw):
    night_sky(c, t, (420, 190), 80)
    ridge(c, 760, 330, hexc('141a3a'), 0.4, off=t*2); ridge(c, 830, 230, hexc('0d1230'), 2.2, off=t*5)
    fog(c, 780, 0.2)
    g = cairo.LinearGradient(0, 820, 0, H); g.add_color_stop_rgba(0, *hexc('151c2a')); g.add_color_stop_rgba(1, *hexc('06080e'))
    c.rectangle(0, 820, W, H); c.set_source(g); c.fill()
    poly(c, [(1290, 830), (1390, 830), (1720, H), (640, H)]); c.set_source_rgba(*hexc('22222c')); c.fill()
    hx = 1040
    poly(c, [(hx - 40, 300), (hx + 260, 150), (hx + 560, 300)]); fs(c, hexc('17121e'))
    rrect(c, hx + 410, 130, 50, 110, 4); fs(c, hexc('17121e'))
    rrect(c, hx, 300, 520, 530, 6); fs(c, hexc('2a2430'))
    lit = {(0, 1), (1, 0), (2, 2)}
    for r in range(3):
        for k in range(3):
            x, y = hx + 46 + k*158, 346 + r*128
            rrect(c, x, y, 100, 88, 4)
            if (r, k) in lit:
                fl = flick(t, r*3 + k); c.set_source_rgba(0.96, 0.77, 0.43, 0.9*fl); c.fill_preserve(); stroke(c, 3.5)
                glow(c, x + 50, y + 44, 30, (1, 0.8, 0.45), 0.2*fl, 4)
            else: c.set_source_rgba(*hexc('0b0912')); c.fill_preserve(); stroke(c, 3.5)
            c.move_to(x + 50, y); c.line_to(x + 50, y + 88); c.move_to(x, y + 44); c.line_to(x + 100, y + 44); stroke(c, 2.5)
    if math.sin(t*0.7) > 0.1:                                                              # a face in the empty window
        x, y = hx + 46 + 2*158, 346 + 0*128
        c.save(); rrect(c, x, y, 100, 88, 4); c.clip()
        c.arc(x + 50, y + 44, 15, 0, 6.3); c.set_source_rgba(0.85, 0.85, 0.9, 0.75); c.fill()
        c.arc(x + 50, y + 100, 34, math.pi, 0); c.fill(); c.restore()
    rrect(c, hx + 200, 700, 120, 130, 6); fs(c, hexc('f2c46d')); glow(c, hx + 260, 770, 40, (1, 0.8, 0.45), 0.35, 5)
    c.move_to(hx + 215, 700); c.line_to(hx + 215, 830); stroke(c, 3)
    rrect(c, hx + 170, 690, 180, 14, 3); fs(c, hexc('120e18'))
    c.move_to(hx + 150, 640); c.line_to(hx + 150, 700); stroke(c, 5, hexc('120e18'))
    rrect(c, hx + 40, 600, 230, 70, 8); fs(c, hexc('1b1620')); fl = flick(t, 4.0)
    text_c(c, "H TEL", hx + 155, 650, 46, (1, 0.35, 0.25, 0.85*fl))
    branch(c, 520, 840, -1.55, 140, 6, t)
    rrect(c, 800 - 6, 560, 12, 280, 3); fs(c, hexc('0b0a12'))                               # broken lamp post
    fl = flick(t, 9.0); glow(c, 800, 560, 14, (1, 0.85, 0.5), 0.3*fl, 5); c.arc(800, 556, 11, 0, 6.3); c.set_source_rgba(1, 0.9, 0.6, fl); c.fill()
    for i in range(7):
        x = 120 + i*70; c.rectangle(x, 800, 10, 90); c.set_source_rgba(*hexc('0b0a12')); c.fill()
    fog(c, 860, 0.22, n=6, sp=22)

# ------------------------------------------------------------------ SET: lobby
def set_lobby(c, t, **kw):
    wall(c, hexc('4a4636'), hexc('3a2a22'), fy=780)
    for x in range(0, W, 70): c.rectangle(x, 0, 24, 630); c.set_source_rgba(0, 0, 0, 0.12); c.fill()
    # grandfather clock
    rrect(c, 120, 220, 170, 560, 10); fs(c, hexc('3a2418')); rrect(c, 140, 250, 130, 130, 65); fs(c, hexc('d8ccb0'))
    c.save(); c.translate(205, 315); c.move_to(0, 0); c.line_to(0, -42); c.move_to(0, 0); c.line_to(36, 0); stroke(c, 5); c.restore()
    c.save(); c.translate(205, 440); c.rotate(math.sin(t*3)*0.25); c.move_to(0, 0); c.line_to(0, 240); stroke(c, 4, hexc('9a8a4a')); c.arc(0, 250, 22, 0, 6.3); fs(c, hexc('c8a24a')); c.restore()
    # portrait with moving eyes
    frame_pic(c, 560, 150, 230, 300, hexc('1e1a22'))
    for ex in (-30, 30):
        c.save(); c.translate(675 + ex, 280); c.scale(1.3, 1); c.arc(0, 0, 14, 0, 6.3); c.restore(); c.set_source_rgb(0.92, 0.92, 0.85); c.fill()
        c.arc(675 + ex + math.sin(t*0.8)*6, 280, 5.5, 0, 6.3); c.set_source_rgb(0.05, 0.02, 0.02); c.fill()
    # key board
    rrect(c, 1180, 190, 560, 360, 8); fs(c, hexc('3a2a1e'))
    for r in range(3):
        for k in range(5):
            x, y = 1230 + k*100, 250 + r*95
            c.arc(x, y, 5, 0, 6.3); c.set_source_rgb(0.7, 0.6, 0.3); c.fill()
            if (r, k) != (1, 2): c.move_to(x, y + 6); c.line_to(x, y + 42); stroke(c, 4, hexc('b8944a')); c.arc(x, y + 50, 10, 0, 6.3); fs(c, hexc('b8944a'), 2.5)
    text_c(c, "13", 1480, 335, 34, (0.9, 0.3, 0.25, 0.75))
    # cobweb
    for i in range(6): c.move_to(W, 0); c.line_to(W - 260*math.cos(i*0.3), 260*math.sin(i*0.3)); stroke(c, 1.5, (0.85, 0.85, 0.9, 0.5))
    fl = flick(t, 2.0); c.move_to(960, 0); c.line_to(960, 150); stroke(c, 3)
    glow(c, 960, 170, 30, (1, 0.82, 0.45), 0.55*fl, 7); c.arc(960, 170, 22, 0, 6.3); c.set_source_rgba(1, 0.92, 0.65, fl); c.fill()
    c.set_source_rgba(0, 0, 0, 0.32); c.paint()

def lobby_fg(c, t, **kw):
    rrect(c, 1100, 790, 760, 400, 6); fs(c, hexc('5a3a24')); rrect(c, 1080, 760, 800, 44, 8); fs(c, hexc('7a4e30'))
    c.arc(1250, 750, 22, math.pi, 0); fs(c, hexc('c8a24a'))
    rrect(c, 1560, 730, 150, 30, 4); fs(c, hexc('2a1a14'))

# ------------------------------------------------------------------ SET: room 13
def set_room(c, t, tick=False, **kw):
    wall(c, hexc('3c4456'), hexc('2c2230'), fy=800)
    window(c, 300, 170, 360, 420, MOODS['night'], t, city=False)
    for sx in (260, 640):
        poly(c, [(sx - 60 if sx < 400 else sx - 10, 140), (sx + 60 if sx < 400 else sx + 70, 140), (sx + 70 if sx < 400 else sx + 90, 640), (sx - 70 if sx < 400 else sx - 30, 640)])
        c.set_source_rgba(*hexc('6a2a3a', 0.85)); c.fill()
    c.arc(960, 150, 70, 0, 6.3); fs(c, hexc('d8ccb0'))
    for i in range(12):
        a = i*math.pi/6; c.move_to(960 + 56*math.sin(a), 150 - 56*math.cos(a)); c.line_to(960 + 64*math.sin(a), 150 - 64*math.cos(a)); stroke(c, 3)
    c.move_to(960, 150); c.line_to(960, 100); c.move_to(960, 150); c.line_to(1004, 150); stroke(c, 5)   # 3:00
    rrect(c, 1500, 210, 300, 610, 10); fs(c, hexc('4e3424'))
    for r in range(2):
        for k in range(2): rrect(c, 1530 + k*130, 250 + r*260, 112, 210, 6); stroke(c, 3, hexc('2e1c12'))
    c.arc(1530, 540, 14, 0, 6.3); fs(c, hexc('d8b45a'), 2.5)
    c.rectangle(1500, 814, 300, 10); c.set_source_rgba(1, 0.9, 0.62, 0.95); c.fill()
    glow(c, 1650, 824, 20, (1, 0.8, 0.45), 0.25, 8)
    rrect(c, 360, 480, 900, 340, 12); fs(c, hexc('3a2230'))                                        # headboard
    fl = flick(t, 5.0); lamp(c, 1380, 810, on=fl > 0.5)
    c.set_source_rgba(0.02, 0.02, 0.08, 0.38); c.paint()
    if fl < 0.5: c.set_source_rgba(0, 0, 0, 0.35); c.paint()

def room_fg(c, t, **kw):
    rrect(c, 300, 905, 1000, 220, 20); fs(c, hexc('7a4a5e'))
    rrect(c, 300, 905, 1000, 60, 20); fs(c, hexc('9a6a7e'))
    rrect(c, 340, 860, 240, 70, 24); fs(c, hexc('d8d0c8')); rrect(c, 1020, 860, 240, 70, 24); fs(c, hexc('d8d0c8'))

# ------------------------------------------------------------------ SET: door close-up
def set_door(c, t, pairs=1, tint=(1, 0.15, 0.1), **kw):
    c.set_source_rgba(*hexc('0a0810')); c.paint()
    g = cairo.RadialGradient(960, 900, 40, 960, 700, 900)
    g.add_color_stop_rgba(0, tint[0], tint[1], tint[2], 0.35); g.add_color_stop_rgba(1, 0, 0, 0, 0); c.set_source(g); c.paint()
    rrect(c, 520, 20, 880, 1100, 14); fs(c, hexc('4a2e20'), 5)
    for r in range(2):
        for k in range(2): rrect(c, 580 + k*400, 80 + r*480, 360, 400, 10); c.set_source_rgba(0.1, 0.05, 0.03, 0.35); c.fill_preserve(); stroke(c, 4, hexc('2a180f'))
    jx = math.sin(t*38)*3 if int(t*2) % 5 == 4 else 0
    c.save(); c.translate(1280 + jx, 600); c.arc(0, 0, 28, 0, 6.3); fs(c, hexc('d8b45a')); c.arc(-8, -8, 8, 0, 6.3); c.set_source_rgba(1, 1, 1, 0.5); c.fill(); c.restore()
    rrect(c, 520, 1008, 880, 18, 0); c.set_source_rgba(1, 0.9, 0.6, 0.95); c.fill()
    glow(c, 960, 1016, 30, (1, 0.8, 0.45), 0.22, 14)
    for p in range(pairs):
        ox = (-90 if pairs == 2 and p == 0 else 90 if pairs == 2 else 0) + math.sin(t*1.3 + p)*10
        for fx in (-46, 46):
            c.save(); c.translate(960 + ox + fx, 1016); c.scale(1, 0.22); c.arc(0, 0, 34, 0, 6.3); c.restore(); c.set_source_rgba(0.02, 0.01, 0.03, 0.95); c.fill()
    fog(c, 1020, 0.2, col=(0.9, 0.5, 0.5), n=4, sp=18, sc=2.2, ry=0.25)

# ------------------------------------------------------------------ SET: choice screen
def set_choice(c, t, **kw):
    g = cairo.RadialGradient(960, 500, 80, 960, 540, 1200)
    g.add_color_stop_rgba(0, *hexc('3a0c16')); g.add_color_stop_rgba(1, *hexc('07040a')); c.set_source(g); c.paint()
    fog(c, 800, 0.16, col=(0.9, 0.4, 0.45), n=6, sp=16)
    for (ex, ey, ph) in ((260, 330, 0.0), (1660, 420, 1.7), (420, 820, 3.1)):
        a = max(0, math.sin(t*0.9 + ph))**2
        for sx in (-22, 22):
            c.save(); c.translate(ex + sx, ey); c.scale(1.6, 0.8); c.arc(0, 0, 9, 0, 6.3); c.restore(); c.set_source_rgba(1, 0.25, 0.2, a); c.fill()
            glow(c, ex + sx, ey, 8, (1, 0.2, 0.15), 0.35*a, 5)

def choice_buttons(c, lt, t0):
    items = [("1", "दरवाज़ा खोलो", hexc('d8452e')), ("2", "पुलिस को बुलाओ", hexc('3a7ad8')), ("3", "खिड़की से भागो", hexc('e8b83a'))]
    for i, (n, label, col) in enumerate(items):
        tt = t0 + i*0.55
        if lt < tt: continue
        s = pop(lt, tt, 0.35); pulse = 1 + 0.015*math.sin(lt*3 + i)
        c.save(); c.translate(960, 480 + i*165); c.rotate(-0.012 + i*0.012); c.scale(S(s*pulse), S(s*pulse))
        shadow_rect(c, -470, -66, 940, 132, 30, 0.4)
        rrect(c, -470, -66, 940, 132, 30); c.set_source_rgb(0.98, 0.96, 0.92); c.fill_preserve(); stroke(c, 5)
        c.arc(-390, 0, 46, 0, 6.3); fs(c, col, 4); text_c(c, n, -390, 18, 52, (1, 1, 1))
        hdraw(c, label, -300, 0, 64, LINE, anchor='l'); c.restore()

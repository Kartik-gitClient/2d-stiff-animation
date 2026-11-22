# -*- coding: utf-8 -*-
"""Rahul & Vinni - Room 13  (GrowKaz cutout style, Hindi horror, interactive ending)
usage:  python3 horror.py qc | full | mix        env: SCALE=0.667 (preview res), FPSX=30
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from horror_sets import *

SCALE = float(os.environ.get('SCALE', '1'))
OW, OH = int(W*SCALE) // 2 * 2, int(H*SCALE) // 2 * 2
TJ = json.load(open('timing.json')); TIM = TJ['lines']; TOTAL = TJ['total']
FEET = 1035

SETS = dict(road=set_road, car=set_car, hotel=set_hotel, lobby=set_lobby, room=set_room, door=set_door, choice=set_choice)

def C(n, x, s=1.2, pose='idle', expr='neutral', flip=False, g=(), e=(), talk=(), y=FEET):
    return dict(n=n, x=x, s=s, pose=pose, expr=expr, flip=flip, g=list(g), e=list(e), talk=list(talk), y=y)
def head_y(ch): return ch['y'] - 470*ch['s']
def pose_at(ch, lt):
    cur = ch['pose']
    for tt, p in ch['g']:
        if lt >= tt:
            kk = ease((lt - tt)/0.45)
            if kk < 1: return cur, p, kk
            cur = p
    return cur, None, 0
def expr_at(ch, lt):
    ex = ch['expr']
    for tt, x in ch['e']:
        if lt >= tt: ex = x
    return ex
def draw_char(c, ch, t, lt, seed):
    c.save(); c.translate(ch['x'], ch['y']); c.scale(ch['s'], ch['s'])
    c.save(); c.scale(1, 0.16); c.arc(0, 0, 110, 0, 6.3); c.set_source_rgba(0, 0, 0, 0.25); c.fill(); c.restore()
    p1, p2, k = pose_at(ch, lt); ex = expr_at(ch, lt)
    blink = ((t + seed*1.37) % 3.6) < 0.13
    if any(a <= lt <= b for a, b in ch['talk']) and int(lt*8) % 2 == 0:
        EXPR['_talk'] = dict(EXPR[ex]); EXPR['_talk']['mouth_o'] = True; ex = '_talk'
    character(c, ch['n'], t, p1, ex, blink, ch['flip'], p2, k, seed)
    c.restore()

class Shot:
    def __init__(self, i0, i1, bg, chars=(), ov=None, fg=None, zoom=(1.0, 1.12), focus=None, bgargs=None, subs=True, shakes=(), dark=0.0):
        self.i0, self.i1 = i0, i1
        self.t0 = TIM[i0]['t0']; self.t1 = TIM[i1]['t1']
        self.bg, self.chars, self.ov, self.fg = bg, list(chars), ov, fg
        self.zoom, self.focus, self.bgargs, self.subs, self.shakes, self.dark = zoom, focus, bgargs or {}, subs, shakes, dark
    def render(self, c, t):
        lt = t - self.t0; dur = self.t1 - self.t0
        z = lerp(self.zoom[0], self.zoom[1], ease(lt/dur)); fx, fy = self.focus or (W/2, H*0.55)
        sx = sy = 0
        for kt in self.shakes:
            if 0 <= lt - kt < 0.3:
                a = 16*(1 - (lt - kt)/0.3); sx += math.sin(lt*91)*a; sy += math.cos(lt*77)*a
        def cam(depth):
            zz = 1 + (z - 1)*depth; c.translate(fx + sx*depth, fy + sy*depth); c.scale(zz, zz); c.translate(-fx - lt*4*depth, -fy)
        c.save(); cam(0.6); SETS[self.bg](c, t, **self.bgargs); c.restore()
        c.save(); cam(1.0)
        for i, ch in enumerate(self.chars): draw_char(c, ch, t, lt, i + int(ch['x']))
        if self.fg: self.fg(c, t)
        c.restore()
        dust(c, t, (0.8, 0.85, 1)); vignette(c, 0.78)
        if self.dark: c.set_source_rgba(0, 0, 0, self.dark); c.paint()
        if self.ov: c.save(); cam(0.85); self.ov(c, lt); c.restore()
        if self.subs:
            for i in range(self.i0, self.i1 + 1):
                if TIM[i]['spk'] == 'N': hsub(c, t, TIM[i]['t0'] + 0.1, TIM[i]['t1'] - 0.25, TIM[i]['text'])

def rel(i, base): return TIM[i]['t0'] - TIM[base]['t0'] + 0.1, TIM[i]['t1'] - TIM[base]['t0'] - 0.2
def speech(c, lt, ch, a, b, txt, dx=0, dy=-170, **kw):
    hx, hy = ch['x'], head_y(ch); bx, by = clamp(hx + dx, 380, W - 380), max(170, hy + dy)
    hbubble(c, lt, a, b, bx, by, txt, tip=(hx - bx, hy - by - 36), **kw)
RED = dict(bg=(0.16, 0.03, 0.05), fg=(1, 0.82, 0.82), ol=(0.85, 0.12, 0.14))
BLU = dict(bg=(0.05, 0.08, 0.2), fg=(0.82, 0.92, 1), ol=(0.3, 0.55, 0.95))
DRK = dict(bg=(0.12, 0.1, 0.09), fg=(0.95, 0.9, 0.8), ol=(0.5, 0.4, 0.3))

def build():
    L = []; T = TIM
    # 1 - the drive
    def o1(c, lt):
        hbig(c, lt, 0.5, 960, 190, "कमरा नंबर 13", 120, (1, 0.28, 0.25), -0.03, t1=4.2)
        stampt(c, lt, 4.4, 8.8, 330, 150, "12:00 AM", rot=-0.06, size=34)
    L.append(Shot(0, 0, 'road', [], o1, zoom=(1.0, 1.1), focus=(900, 800)))
    # 2 - inside the car
    vin = C('vinni', 560, 1.6, y=1190, expr='worried', talk=[rel(1, 1)], e=[(rel(2, 1)[0], 'worried')])
    rah = C('rahul', 1330, 1.6, y=1190, expr='neutral', talk=[rel(2, 1)], e=[(rel(2, 1)[0], 'happy')])
    a1, b1 = rel(1, 1); a2, b2 = rel(2, 1)
    def o2(c, lt):
        tagt(c, lt, 0.3, 3.2, 330, 620, "VINNI", "co-pilot"); tagt(c, lt, 0.8, 3.7, 1590, 620, "RAHUL", "the driver", rot=0.04)
        icon(c, lt, a1 + 0.4, 960, 600, 'phone', 0.8, t1=b1 + 1.0); stampt(c, lt, a1 + 1.0, b1 + 1.2, 960, 720, "NO NETWORK", rot=-0.05, size=30)
        speech(c, lt, vin, a1, b1, T[1]['text'], dx=60, **DRK); speech(c, lt, rah, a2, b2, T[2]['text'], dx=-40, **DRK)
    L.append(Shot(1, 2, 'car', [vin, rah], o2, fg=car_fg, zoom=(1.0, 1.08), subs=False))
    # 3 - the hotel
    r3 = C('rahul', 470, 0.95, expr='worried'); v3 = C('vinni', 660, 0.95, expr='shock')
    def o3(c, lt):
        d = T[3]['t1'] - T[3]['t0']
        hbig(c, lt, d*0.5, 470, 300, "ना कोई दुकान", 78, (1, 0.45, 0.4), -0.04, t1=d - 0.2)
        hbig(c, lt, d*0.62, 500, 400, "ना कोई मकान", 78, (1, 0.45, 0.4), 0.03, t1=d - 0.2)
        stampt(c, lt, d*0.78, d + 5, 1720, 440, "सिर्फ़ यही होटल", rot=0.05, size=34)
    L.append(Shot(3, 3, 'hotel', [r3, v3], o3, zoom=(1.0, 1.16), focus=(1300, 560)))
    # 4 - lobby
    r4 = C('rahul', 420, 1.1, expr='worried'); v4 = C('vinni', 650, 1.1, expr='worried', flip=False)
    m4 = C('manager', 1480, 1.2, expr='neutral', pose='hips')
    def o4(c, lt):
        d = T[4]['t1'] - T[4]['t0']
        tagt(c, lt, 0.8, 4.5, 1480, 330, "MANAGER", "?????", rot=0.03); stampt(c, lt, d*0.62, d + 6, 960, 330, "ROOM 13", rot=-0.07, size=48)
    L.append(Shot(4, 4, 'lobby', [r4, v4, m4], o4, fg=lobby_fg, zoom=(1.0, 1.14), focus=(1300, 560)))
    # 5 - manager warning
    m5 = C('manager', 960, 1.75, expr='angry', y=1330, talk=[rel(5, 5)])
    a5, b5 = rel(5, 5)
    def o5(c, lt):
        speech(c, lt, m5, a5, b5, T[5]['text'], dy=-300, size=46, maxw=760, **RED)
    L.append(Shot(5, 5, 'lobby', [m5], o5, fg=lobby_fg, zoom=(1.0, 1.2), focus=(960, 520), subs=False))
    # 6 - 3 AM knock
    r6 = C('rahul', 560, 1.15, expr='worried', y=1010); v6 = C('vinni', 810, 1.15, expr='worried', y=1010)
    kn = [T[6]['t1'] - T[6]['t0'] - 1.7, T[6]['t1'] - T[6]['t0'] - 1.15, T[6]['t1'] - T[6]['t0'] - 0.6]
    def o6(c, lt):
        stampt(c, lt, 0.5, 9, 960, 300, "3:00 AM", rot=-0.05, size=56)
        for i, k in enumerate(kn): hbig(c, lt, k, 1180 + i*70, 330 + i*120, "टक!", 96, (1, 0.35, 0.3), 0.05*(i - 1), shake=5)
    L.append(Shot(6, 6, 'room', [r6, v6], o6, fg=room_fg, zoom=(1.0, 1.15), focus=(1100, 600), shakes=[k for k in kn]))
    # 7 - voice outside (Vinni's voice)
    a7, b7 = rel(7, 7)
    def o7(c, lt): hbubble(c, lt, a7, b7, 960, 250, T[7]['text'], tip=(0, 330), size=50, maxw=760, **RED)
    L.append(Shot(7, 7, 'door', [], o7, zoom=(1.0, 1.1), focus=(960, 800), subs=False, bgargs=dict(pairs=1), shakes=[0.05]))
    # 8 - but Vinni is next to him
    r8 = C('rahul', 560, 1.15, expr='shock', y=1010); v8 = C('vinni', 810, 1.15, expr='shock', y=1010)
    def o8(c, lt): pass
    L.append(Shot(8, 8, 'room', [r8, v8], o8, fg=room_fg, zoom=(1.0, 1.22), focus=(700, 560)))
    # 9 - Vinni: that's my voice
    r9 = C('rahul', 560, 1.15, expr='shock', y=1010); v9 = C('vinni', 810, 1.15, expr='shock', y=1010, talk=[rel(9, 9)])
    a9, b9 = rel(9, 9)
    def o9(c, lt): speech(c, lt, v9, a9, b9, T[9]['text'], dy=-190, **DRK)
    L.append(Shot(9, 9, 'room', [r9, v9], o9, fg=room_fg, zoom=(1.0, 1.12), focus=(700, 620), subs=False))
    # 10-11 - the second voice (Rahul's)
    a11, b11 = rel(11, 10)
    def o10(c, lt): hbubble(c, lt, a11, b11, 960, 250, T[11]['text'], tip=(0, 330), size=50, maxw=800, **BLU)
    L.append(Shot(10, 11, 'door', [], o10, zoom=(1.0, 1.16), focus=(960, 800), bgargs=dict(pairs=2, tint=(0.2, 0.4, 1.0)), shakes=[a11]))
    # 12 - who is real?
    r12 = C('rahul', 600, 1.2, expr='shock', y=1010); v12 = C('vinni', 840, 1.2, expr='shock', y=1010)
    d12 = T[12]['t1'] - T[12]['t0']
    def o12(c, lt):
        hbig(c, lt, d12*0.55, 1300, 330, "असली कौन?", 130, (1, 0.3, 0.3), -0.04, shake=3)
        hbig(c, lt, d12*0.78, 1360, 500, "नक़ली कौन?", 130, (0.55, 0.8, 1), 0.04, shake=3)
    L.append(Shot(12, 12, 'room', [r12, v12], o12, fg=room_fg, zoom=(1.0, 1.28), focus=(720, 600)))
    # 13 - your choice
    def o13(c, lt):
        hbig(c, lt, 0.2, 960, 170, "आपका फ़ैसला?", 128, (1, 0.9, 0.35), -0.02)
        choice_buttons(c, lt, 1.6)
        hbig(c, lt, 4.4, 960, 960, "कमेंट में 1, 2 या 3 लिखो", 62, (1, 1, 1), 0.0)
    L.append(Shot(13, 13, 'choice', [], o13, zoom=(1.0, 1.04), subs=False))
    return L

def render(shots, out=None, stills=None):
    def frame(t):
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, OW, OH); c = cairo.Context(surf); c.scale(OW/W, OH/H)
        sh = next((s for s in shots if s.t0 <= t < s.t1), shots[-1]); sh.render(c, t)
        f = 0
        if sh is not shots[0]: f = max(f, 1 - ease((t - sh.t0)/0.3))
        if sh is not shots[-1]: f = max(f, ease((t - (sh.t1 - 0.25))/0.25))
        f = max(f, 1 - ease(t/0.8), ease((t - (TOTAL - 0.9))/0.9))
        if f > 0: c.set_source_rgba(0, 0, 0, f); c.paint()
        return surf
    if stills: return [frame(t) for t in stills]
    fps = int(os.environ.get('FPSX', FPS))
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{OW}x{OH}", "-r", str(fps), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    n = int(TOTAL*fps)
    for i in range(n):
        p.stdin.write(bytes(frame(i/fps).get_data()))
        if i % 150 == 0: print(f'frame {i}/{n}', flush=True)
    p.stdin.close(); p.wait()

# ------------------------------------------------------------------ SFX
SR = 44100
def build_sfx(shots):
    rng = np.random.default_rng(3); n = int((TOTAL + 1)*SR); tr = np.zeros(n); tt = np.arange(n)/SR
    def put(t, s, g=1.0):
        i = int(t*SR)
        if i < 0 or i >= n: return
        tr[i:i + len(s)] += g*s[:n - i]
    def env(m, a=0.003, dec=8): x = np.arange(m)/SR; return np.minimum(1, x/a)*np.exp(-x*dec)
    # drone + wind
    tr += 0.05*(np.sin(2*np.pi*49*tt) + np.sin(2*np.pi*52.5*tt))*(0.7 + 0.3*np.sin(2*np.pi*0.1*tt))
    w = np.convolve(rng.standard_normal(n), np.ones(60)/60, 'same'); tr += 0.5*w*(0.04 + 0.03*np.sin(2*np.pi*0.13*tt))
    # car engine + road under the first two shots
    ce = shots[1].t1
    m = tt < ce; eng = (np.sin(2*np.pi*(62 + 3*np.sin(tt*1.7))*tt) + 0.5*np.sin(2*np.pi*124*tt))*0.07
    tr += eng*m*np.clip((ce - tt)/1.0, 0, 1)
    # door creak at lobby, stinger + heartbeat late
    def stinger(t, g=0.28):
        m_ = int(1.6*SR); x = np.arange(m_)/SR
        put(t, g*(np.sin(2*np.pi*622*x) + np.sin(2*np.pi*659*x) + 0.6*np.sin(2*np.pi*933*x))*(1 + 0.4*np.sin(2*np.pi*7*x))*env(m_, 0.01, 2.2))
    def thump(t, g=0.9):
        m_ = int(0.35*SR); x = np.arange(m_)/SR; put(t, g*np.sin(2*np.pi*(150*np.exp(-x*14) + 45)*x)*env(m_, 0.001, 14) + 0.25*rng.standard_normal(m_)*env(m_, 0.001, 60))
    def creak(t):
        m_ = int(1.1*SR); x = np.arange(m_)/SR; f = 300 + 180*np.sin(2*np.pi*3.3*x) + 220*x
        put(t, 0.09*np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*np.sin(np.pi*x/1.1))
    def heart(t):
        for d in (0, 0.22): m_ = int(0.25*SR); x = np.arange(m_)/SR; put(t + d, 0.55*np.sin(2*np.pi*58*x)*env(m_, 0.004, 22))
    creak(shots[3].t1 - 0.6); stinger(shots[4].t0 + 0.2, 0.12)
    for k in shots[6].shakes: thump(shots[6].t0 + k, 1.0)
    stinger(shots[7].t0, 0.32); stinger(shots[9].t0 + 0.05, 0.28); stinger(shots[10].t0 + 0.25, 0.3)
    stinger(shots[11].t0 + 0.5, 0.34)
    t = shots[8].t0
    while t < shots[11].t1 - 0.4: heart(t); t += 0.95 - 0.35*(t - shots[8].t0)/(shots[11].t1 - shots[8].t0)
    for sh in shots[1:]:
        m_ = int(0.4*SR); x = rng.standard_normal(m_); y = x - np.convolve(x, np.ones(20)/20, 'same')
        put(sh.t0 - 0.12, 0.05*y*np.sin(np.pi*np.arange(m_)/m_)**2)
    tr = np.clip(tr, -1, 1); return tr

def write_wav(path, a):
    with wave.open(path, 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1)*32767).astype(np.int16).tobytes())

def mix():
    sfx = np.frombuffer(wave.open('sfx.wav').readframes(10**9), dtype=np.int16).astype(np.float32)/32768
    out = sfx*0.55
    if os.path.exists('voice.wav') and not TJ.get('dry'):
        v = np.frombuffer(wave.open('voice.wav').readframes(10**9), dtype=np.int16).astype(np.float32)/32768
        m_ = max(len(v), len(out)); o = np.zeros(m_, dtype=np.float32); o[:len(out)] += out; o[:len(v)] += v*1.0; out = o
    write_wav('mix_raw.wav', out)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'video_silent.mp4', '-i', 'mix_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', 'final.mp4'], check=True)
    print('final.mp4 done')

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'qc'; shots = build()
    if mode == 'qc':
        from PIL import Image
        ts = [s.t0 + (s.t1 - s.t0)*(0.82 if i not in (13 - 1,) else 0.75) for i, s in enumerate(shots)]
        ims = render(shots, stills=ts); cols = 4; rows = math.ceil(len(ims)/cols); tw, th = 640, 360
        sheet = Image.new('RGB', (cols*tw, rows*th))
        for i, s in enumerate(ims):
            s.write_to_png('q_temp.png'); sheet.paste(Image.open('q_temp.png').resize((tw, th)), ((i % cols)*tw, (i//cols)*th))
        if os.path.exists('q_temp.png'): os.remove('q_temp.png')
        sheet.save('qc.jpg', quality=88); print('qc.jpg', len(ims))
    elif mode == 'full':
        write_wav('sfx.wav', build_sfx(shots)); render(shots, 'video_silent.mp4')
    elif mode == 'mix':
        mix()

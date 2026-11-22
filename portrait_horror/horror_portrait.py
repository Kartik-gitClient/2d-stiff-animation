# -*- coding: utf-8 -*-
"""Portrait 9:16 Hindi Horror Film: 'Lift Ka Niyam' (The 2:00 AM Elevator).
Usage: python horror_portrait.py qc | full | mix
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from portrait_sets import *

SCALE = float(os.environ.get('SCALE', '1'))
OW, OH = int(W*SCALE) // 2 * 2, int(H*SCALE) // 2 * 2
TJ = json.load(open('timing.json', encoding='utf-8'))
TIM = TJ['lines']
TOTAL = TJ['total']
FEET = 1520

SETS = dict(
    office=set_office_hallway,
    guard=set_guard_hallway,
    doors=set_elevator_doors,
    inside=set_elevator_inside,
    mirror=set_mirror_climax,
    choice=set_choice_portrait
)

def C(n, x, s=1.35, pose='idle', expr='neutral', flip=False, g=(), e=(), talk=(), y=FEET):
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
    c.save(); c.scale(1, 0.16); c.arc(0, 0, 110, 0, 6.3); c.set_source_rgba(0, 0, 0, 0.3); c.fill(); c.restore()
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
        lt = t - self.t0; dur = max(0.1, self.t1 - self.t0)
        z = lerp(self.zoom[0], self.zoom[1], ease(lt/dur)); fx, fy = self.focus or (W/2, H*0.55)
        sx = sy = 0
        for kt in self.shakes:
            if 0 <= lt - kt < 0.35:
                a = 22*(1 - (lt - kt)/0.35); sx += math.sin(lt*91)*a; sy += math.cos(lt*77)*a
        def cam(depth):
            zz = 1 + (z - 1)*depth; c.translate(fx + sx*depth, fy + sy*depth); c.scale(zz, zz); c.translate(-fx - lt*3*depth, -fy)
        c.save(); cam(0.6); SETS[self.bg](c, t, **self.bgargs); c.restore()
        c.save(); cam(1.0)
        for i, ch in enumerate(self.chars): draw_char(c, ch, t, lt, i + int(ch['x']))
        if self.fg: self.fg(c, t)
        c.restore()
        dust(c, t, (0.8, 0.85, 1)); vignette(c, 0.72)
        if self.dark: c.set_source_rgba(0, 0, 0, self.dark); c.paint()
        if self.ov: c.save(); cam(0.85); self.ov(c, lt); c.restore()
        if self.subs:
            for i in range(self.i0, self.i1 + 1):
                if TIM[i]['spk'] == 'N': hsub(c, t, TIM[i]['t0'] + 0.1, TIM[i]['t1'] - 0.25, TIM[i]['text'])

def rel(i, base): return TIM[i]['t0'] - TIM[base]['t0'] + 0.1, TIM[i]['t1'] - TIM[base]['t0'] - 0.2

RED = dict(bg=(0.18, 0.03, 0.06), fg=(1, 0.85, 0.85), ol=(0.85, 0.15, 0.18))
BLU = dict(bg=(0.06, 0.1, 0.22), fg=(0.85, 0.94, 1), ol=(0.35, 0.6, 0.95))
DRK = dict(bg=(0.12, 0.11, 0.13), fg=(0.95, 0.92, 0.88), ol=(0.55, 0.45, 0.4))

def build():
    L = []; T = TIM

    # Shot 0: Office corridor at 2:00 AM
    k0 = C('kabir', 540, 1.45, expr='neutral')
    def o0(c, lt):
        hbig(c, lt, 0.4, 540, 280, "लिफ़्ट का नियम", 108, (1, 0.3, 0.3), -0.02, t1=4.2)
        stampt(c, lt, 4.4, 8.8, 540, 420, "2:00 AM", rot=-0.04, size=46)
    L.append(Shot(0, 0, 'office', [k0], o0, zoom=(1.0, 1.1), focus=(540, 1100)))

    # Shot 1: Old Guard warning
    g1 = C('guard', 540, 1.55, expr='angry', talk=[rel(1, 1)])
    a1, b1 = rel(1, 1)
    def o1(c, lt):
        tagt(c, lt, 0.4, 3.5, 320, 680, "SECURITY", "night shift", rot=-0.03)
        hbubble(c, lt, a1, b1, 540, 480, T[1]['text'], tip=(0, 240), size=44, maxw=820, **RED)
    L.append(Shot(1, 1, 'guard', [g1], o1, zoom=(1.0, 1.14), focus=(540, 1050), subs=False))

    # Shot 2: Kabir dismisses warning
    k2 = C('kabir', 540, 1.5, expr='happy', talk=[rel(2, 2)])
    a2, b2 = rel(2, 2)
    def o2(c, lt):
        tagt(c, lt, 0.3, 3.2, 780, 680, "KABIR", "exhausted", rot=0.03)
        hbubble(c, lt, a2, b2, 540, 480, T[2]['text'], tip=(0, 240), size=44, maxw=820, **DRK)
    L.append(Shot(2, 2, 'office', [k2], o2, zoom=(1.0, 1.1), focus=(540, 1050), subs=False))

    # Shot 3: Elevator lobby, button pressed, doors slide open
    k3 = C('kabir', 320, 1.35, expr='neutral')
    def o3(c, lt):
        d = T[3]['t1'] - T[3]['t0']
        stampt(c, lt, 1.2, d, 820, 780, "DING!", rot=0.05, size=48)
    # Open ratio animates
    L.append(Shot(3, 3, 'doors', [k3], o3, zoom=(1.0, 1.16), focus=(540, 950), bgargs=dict(open_ratio=0.75)))

    # Shot 4: Inside elevator, woman in red facing wall
    w4 = C('woman', 680, 1.45, expr='neutral', flip=True)
    def o4(c, lt):
        hstampt(c, lt, 0.8, 6.0, 360, 420, "अकेली औरत", rot=-0.05, size=46)
        hbig(c, lt, 2.2, 540, 260, "लाल लिबास", 90, (0.9, 0.15, 0.2), -0.02)
    L.append(Shot(4, 4, 'inside', [w4], o4, zoom=(1.0, 1.18), focus=(540, 950)))

    # Shot 5: Kabir enters and speaks
    k5 = C('kabir', 360, 1.45, expr='worried', talk=[rel(5, 5)])
    w5 = C('woman', 720, 1.45, expr='neutral', flip=True)
    a5, b5 = rel(5, 5)
    def o5(c, lt):
        hbubble(c, lt, a5, b5, 420, 480, T[5]['text'], tip=(0, 220), size=42, maxw=700, **BLU)
    L.append(Shot(5, 5, 'inside', [k5, w5], o5, zoom=(1.0, 1.1), focus=(540, 950), subs=False))

    # Shot 6: Elevator accelerates upwards rapidly
    k6 = C('kabir', 360, 1.45, expr='shock')
    w6 = C('woman', 720, 1.45, expr='neutral', flip=True)
    shk6 = [1.0, 2.0, 3.2]
    def o6(c, lt):
        hbig(c, lt, 1.0, 540, 300, "14... 15... 16!", 110, (1, 0.25, 0.25), -0.03, shake=6)
    L.append(Shot(6, 6, 'inside', [k6, w6], o6, zoom=(1.0, 1.22), focus=(540, 950), shakes=shk6, bgargs=dict(floor_num=16, flicker=True)))

    # Shot 7: Sudden violent brake halt!
    k7 = C('kabir', 360, 1.45, expr='shock')
    w7 = C('woman', 720, 1.45, expr='neutral', flip=True)
    def o7(c, lt):
        hstampt(c, lt, 0.2, 5.0, 540, 380, "धड़ाम!", rot=-0.08, size=68)
    L.append(Shot(7, 7, 'inside', [k7, w7], o7, zoom=(1.0, 1.25), focus=(540, 950), shakes=[0.1, 0.35], bgargs=dict(floor_num=16, flicker=True)))

    # Shot 8: Kabir looks into the mirror
    k8 = C('kabir', 540, 1.55, expr='shock')
    def o8(c, lt): pass
    L.append(Shot(8, 8, 'mirror', [k8], o8, zoom=(1.0, 1.2), focus=(540, 850)))

    # Shot 9: Mirror reveals horrifying face turned around
    w9 = C('woman', 540, 1.6, expr='shock')
    def o9(c, lt):
        hbig(c, lt, 0.8, 540, 280, "चेहरा मुड़ा हुआ था!", 98, (1, 0.2, 0.2), 0.03, shake=5)
    L.append(Shot(9, 9, 'mirror', [w9], o9, zoom=(1.0, 1.28), focus=(540, 850)))

    # Shot 10: Woman speaks chilling final curse
    w10 = C('woman', 540, 1.6, expr='shock', talk=[rel(10, 10)])
    a10, b10 = rel(10, 10)
    def o10(c, lt):
        hbubble(c, lt, a10, b10, 540, 380, T[10]['text'], tip=(0, 240), size=46, maxw=820, **RED)
    L.append(Shot(10, 10, 'mirror', [w10], o10, zoom=(1.0, 1.15), focus=(540, 850), subs=False))

    # Shot 11: Who will survive?
    def o11(c, lt):
        hbig(c, lt, 0.3, 540, 360, "फ़ैसला आपका!", 124, (1, 0.9, 0.3), -0.02)
    L.append(Shot(11, 11, 'choice', [], o11, zoom=(1.0, 1.05), focus=(540, 960)))

    # Shot 12: Interactive mobile ending screen
    def o12(c, lt):
        hbig(c, lt, 0.2, 540, 320, "कबीर क्या करे?", 110, (1, 0.95, 0.3), -0.02)
        hbig(c, lt, 3.2, 540, 1550, "कमेंट में 1, 2 या 3 लिखो!", 66, (1, 1, 1), 0.0, shake=2)
    L.append(Shot(12, 12, 'choice', [], o12, zoom=(1.0, 1.02), focus=(540, 960), subs=False))

    return L

def render(shots, out=None, stills=None):
    def frame(t):
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, OW, OH)
        c = cairo.Context(surf)
        c.scale(OW/W, OH/H)
        sh = next((s for s in shots if s.t0 <= t < s.t1), shots[-1])
        sh.render(c, t)
        f = 0
        if sh is not shots[0]: f = max(f, 1 - ease((t - sh.t0)/0.3))
        if sh is not shots[-1]: f = max(f, ease((t - (sh.t1 - 0.25))/0.25))
        f = max(f, 1 - ease(t/0.8), ease((t - (TOTAL - 0.9))/0.9))
        if f > 0: c.set_source_rgba(0, 0, 0, f); c.paint()
        return surf

    if stills: return [frame(t) for t in stills]

    fps = int(os.environ.get('FPSX', FPS))
    p = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
        "-s", f"{OW}x{OH}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out
    ], stdin=subprocess.PIPE)
    n = int(TOTAL*fps)
    for i in range(n):
        p.stdin.write(bytes(frame(i/fps).get_data()))
        if i % 150 == 0: print(f'frame {i}/{n}', flush=True)
    p.stdin.close()
    p.wait()

SR = 44100
def build_sfx(shots):
    rng = np.random.default_rng(7); n = int((TOTAL + 1)*SR); tr = np.zeros(n); tt = np.arange(n)/SR
    def put(t, s, g=1.0):
        i = int(t*SR)
        if i < 0 or i >= n: return
        tr[i:i + len(s)] += g*s[:n - i]
    def env(m, a=0.003, dec=8): x = np.arange(m)/SR; return np.minimum(1, x/a)*np.exp(-x*dec)
    
    # Eerie ambient drone + low ventilation hum
    tr += 0.06*(np.sin(2*np.pi*48*tt) + np.sin(2*np.pi*51.5*tt))*(0.7 + 0.3*np.sin(2*np.pi*0.08*tt))
    w = np.convolve(rng.standard_normal(n), np.ones(80)/80, 'same')
    tr += 0.4*w*(0.04 + 0.03*np.sin(2*np.pi*0.12*tt))
    
    # Elevator bell DING! at shot 3
    t_ding = shots[3].t0 + 1.2
    m_ding = int(1.8*SR); x_d = np.arange(m_ding)/SR
    ding = (np.sin(2*np.pi*880*x_d) + 0.5*np.sin(2*np.pi*1760*x_d))*env(m_ding, 0.002, 3.5)
    put(t_ding, ding, 0.4)
    
    # Metal door sliding scrape
    t_door = shots[3].t0 + 1.6
    m_door = int(1.4*SR); x_dr = np.arange(m_door)/SR
    put(t_door, 0.08*np.convolve(rng.standard_normal(m_door), np.ones(30)/30, 'same')*np.sin(np.pi*x_dr/1.4))
    
    # Heavy violent brake screech and thump at shot 7
    t_halt = shots[7].t0 + 0.1
    m_thump = int(0.5*SR); x_th = np.arange(m_thump)/SR
    put(t_halt, 0.9*np.sin(2*np.pi*(180*np.exp(-x_th*12) + 40)*x_th)*env(m_thump, 0.001, 10))
    
    # Heartbeat throbs during climax
    def heart(t):
        for d in (0, 0.22):
            m_ = int(0.25*SR); x = np.arange(m_)/SR
            put(t + d, 0.55*np.sin(2*np.pi*55*x)*env(m_, 0.004, 22))
    
    t_h = shots[8].t0
    while t_h < shots[10].t1:
        heart(t_h)
        t_h += 0.85
    
    # Eerie strings stinger at mirror reveal
    def stinger(t, g=0.35):
        m_ = int(2.0*SR); x = np.arange(m_)/SR
        put(t, g*(np.sin(2*np.pi*622*x) + np.sin(2*np.pi*659*x) + 0.7*np.sin(2*np.pi*933*x))*(1 + 0.4*np.sin(2*np.pi*7*x))*env(m_, 0.01, 1.8))
    
    stinger(shots[1].t0 + 0.2, 0.18)
    stinger(shots[4].t0 + 0.3, 0.25)
    stinger(shots[9].t0 + 0.4, 0.42)
    stinger(shots[10].t0 + 0.2, 0.38)
    
    tr = np.clip(tr, -1, 1)
    return tr

def write_wav(path, a):
    with wave.open(path, 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(a, -1, 1)*32767).astype(np.int16).tobytes())

def mix():
    sfx = np.frombuffer(wave.open('sfx.wav').readframes(10**9), dtype=np.int16).astype(np.float32)/32768
    out = sfx*0.5
    if os.path.exists('voice.wav') and not TJ.get('dry'):
        v = np.frombuffer(wave.open('voice.wav').readframes(10**9), dtype=np.int16).astype(np.float32)/32768
        m_ = max(len(v), len(out)); o = np.zeros(m_, dtype=np.float32)
        o[:len(out)] += out; o[:len(v)] += v*1.0; out = o
    write_wav('mix_raw.wav', out)
    subprocess.run([
        'ffmpeg', '-y', '-v', 'error', '-i', 'video_silent.mp4', '-i', 'mix_raw.wav',
        '-af', 'loudnorm=I=-14:TP=-1.5', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
        '-shortest', 'final_portrait.mp4'
    ], check=True)
    print('final_portrait.mp4 done')

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'qc'
    shots = build()
    if mode == 'qc':
        from PIL import Image
        ts = [s.t0 + (s.t1 - s.t0)*0.75 for s in shots]
        ims = render(shots, stills=ts)
        cols = 4; rows = math.ceil(len(ims)/cols); tw, th = 360, 640
        sheet = Image.new('RGB', (cols*tw, rows*th))
        for i, s in enumerate(ims):
            s.write_to_png('q_temp.png')
            sheet.paste(Image.open('q_temp.png').resize((tw, th)), ((i % cols)*tw, (i//cols)*th))
        if os.path.exists('q_temp.png'): os.remove('q_temp.png')
        sheet.save('qc_portrait.jpg', quality=88)
        print('qc_portrait.jpg done', len(ims))
    elif mode == 'full':
        write_wav('sfx.wav', build_sfx(shots))
        render(shots, 'video_silent.mp4')
    elif mode == 'mix':
        mix()

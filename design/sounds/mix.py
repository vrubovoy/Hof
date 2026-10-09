# Сведение звуков Hof: громкость к одному плану, полосы частот, петля фонтана, порывы ветра.
# Нужны macOS afconvert (декодирование и AAC) и Python с numpy.
# usage: python3 mix.py <папка> [<папка> ...]   — где искать скачанные записи (обычно ~/Downloads)
#
# План громкости (LUFS по BS.1770; «кратко» — максимум по окну 0,1–0,4 с):
#   музыка          −30 интегрально, вырез −3 дБ на 2–5 кГц: там живут звуки интерфейса
#   интерфейс       −26 кратко, срез ниже 120 Гц, пик не выше −6 dBFS
#   ветер в листве  −34 кратко, полоса 150 Гц–7 кГц, мягкие вход и выход
#   фонтан          −40 интегрально, полоса 200 Гц–5 кГц, бесшовная петля 12 с (несколько, по очереди заходов)
#   кот             −28 кратко (чуть тише интерфейса), полоса 250 Гц–8 кГц; мурчание −32
# Во время звука интерфейса музыка приглушается на 4 дБ (это делает fx.js, не файл).
import glob
import os
import subprocess
import sys
import tempfile
import wave
import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES = [os.path.expanduser(p) for p in (sys.argv[1:] or ['~/Downloads'])]
KENNEY = os.path.join(HERE, 'kenney-rpg-audio')
TMP = tempfile.mkdtemp()


def load(path):
    out = os.path.join(TMP, 'in.wav')
    subprocess.run(['afconvert', '-f', 'WAVE', '-d', 'LEI16@44100', path, out], check=True)
    w = wave.open(out)
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, w.getnchannels()) / 32768
    return a if a.shape[1] == 2 else np.repeat(a, 2, 1)


def save(a, name, kbps=64):
    wav = os.path.join(TMP, 'out.wav')
    with wave.open(wav, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run(['afconvert', '-f', 'm4af', '-d', 'aac', '-b', str(kbps * 1000), wav, os.path.join(HERE, name + '.m4a')], check=True)


def shape(a, hp=None, lp=None, dip=None):
    """Полосы частот через спектр (без сдвига фазы): срезы с плавным краем и вырез dip=(f1, f2, дБ)."""
    n = len(a); f = np.fft.rfftfreq(n, 1 / SR); g = np.ones_like(f)
    if hp: g *= 1 / np.sqrt(1 + (hp / np.maximum(f, 1)) ** 4)
    if lp: g *= 1 / np.sqrt(1 + (f / lp) ** 4)
    if dip:
        f1, f2, db = dip
        g *= 10 ** (db / 20 * np.exp(-0.5 * (np.log(np.maximum(f, 1) / np.sqrt(f1 * f2)) / np.log(f2 / f1) * 2.4) ** 2))
    return np.stack([np.fft.irfft(np.fft.rfft(a[:, c]) * g, n) for c in range(2)], 1)


def kweighted_power(a):
    n = len(a); f = np.fft.rfftfreq(n, 1 / SR); s = 2j * np.pi * f
    w0, gs, q = 2 * np.pi * 1681.97, 10 ** (3.99984 / 20), 0.7071752
    w1, q1 = 2 * np.pi * 38.1355, 0.5003270
    H = np.abs((gs * s**2 + np.sqrt(gs) * w0 / q * s + w0**2) / (s**2 + w0 / q * s + w0**2) * s**2 / (s**2 + w1 / q1 * s + w1**2))
    k = np.stack([np.fft.irfft(np.fft.rfft(a[:, c]) * H, n) for c in range(2)], 1)
    return (k ** 2).sum(1)


def short_max(a, win):
    p = kweighted_power(a); w = max(1, int(SR * win))
    c = np.convolve(p, np.ones(w) / w, 'valid') if len(p) > w else [p.mean()]
    return -0.691 + 10 * np.log10(np.max(c) + 1e-12)


def integrated(a):
    p = kweighted_power(a); w, h = int(SR * 0.4), int(SR * 0.1)
    s = np.array([-0.691 + 10 * np.log10(p[i:i + w].mean() + 1e-12) for i in range(0, len(p) - w, h)])
    s = s[s > -70]; s = s[s > 10 * np.log10(np.mean(10 ** (s / 10))) - 10]
    return 10 * np.log10(np.mean(10 ** (s / 10)))


def to_level(a, now, target, peak_db=-6):
    a = a * 10 ** ((target - now) / 20)
    pk = np.abs(a).max()
    return a * min(1, 10 ** (peak_db / 20) / pk) if pk > 0 else a


def fades(a, fin, fout):
    n = len(a); e = np.ones(n)
    i, o = int(SR * fin), int(SR * fout)
    if i: e[:i] = np.sin(np.linspace(0, np.pi / 2, i)) ** 2
    if o: e[-o:] = np.cos(np.linspace(0, np.pi / 2, o)) ** 2
    return a * e[:, None]


def trim(a, thr_db=-55):
    m = np.abs(a).max(1); idx = np.where(m > 10 ** (thr_db / 20))[0]
    return a[max(0, idx[0] - int(SR * 0.01)): idx[-1] + int(SR * 0.05)] if len(idx) else a


def ui(name, src, cap=None):
    """Звук интерфейса; cap — не длиннее стольких секунд (хвост плавно гаснет), чтобы звук
    кончался вместе со своей анимацией."""
    a = trim(shape(load(os.path.join(KENNEY, src + '.ogg')), hp=120))
    if cap and len(a) > SR * cap:
        a = fades(a[:int(SR * cap)], 0, 0.25)
    a = fades(a, 0.003, 0.03)
    save(to_level(a, short_max(a, 0.1), -26), name)


def loudest(a, dur, count):
    """Начала самых громких окон длиной dur, не пересекающихся."""
    p = kweighted_power(a); w = int(SR * dur)
    c = np.convolve(p, np.ones(w) / w, 'valid')
    picks = []
    for i in np.argsort(c)[::-1]:
        if all(abs(i - j) > w for j in picks):
            picks.append(i)
        if len(picks) == count:
            break
    return picks


def wind(names, src, count, dur=2.4):
    path = find(src)
    if not path:
        return
    a = shape(load(path), hp=150, lp=7000)
    if len(a) < SR * dur:
        a = np.concatenate([a, np.zeros((int(SR * dur) - len(a), 2))])
    for name, start in zip(names, loudest(a, dur, count)):
        seg = fades(a[start:start + int(SR * dur)], 0.35, 1.0)
        save(to_level(seg, short_max(seg, 0.4), -34), name)


def find(src):
    hits = sorted(h for d in SOURCES for h in glob.glob(os.path.join(d, src + '*')))
    if not hits:
        print('нет исходника, пропуск:', src)
    return hits[0] if hits else None


def fountain(name, src, length=12.0, xfade=1.5):
    path = find(src)
    if not path:
        return
    a = shape(load(path), hp=200, lp=5000)
    # самый ровный кусок: наименьший разброс кратковременной громкости
    p = kweighted_power(a); w = int(SR * 0.4)
    s = 10 * np.log10(np.convolve(p, np.ones(w) / w, 'valid')[::int(SR * 0.1)] + 1e-12)
    n = int((length + xfade) / 0.1)
    best = min(range(0, len(s) - n), key=lambda i: s[i:i + n].std())
    seg = a[best * int(SR * 0.1): best * int(SR * 0.1) + int(SR * (length + xfade))]
    L, X = int(SR * length), int(SR * xfade)
    t = np.linspace(0, np.pi / 2, X)[:, None]
    loop = seg[:L].copy()
    loop[:X] = seg[:X] * np.sin(t) + seg[L:L + X] * np.cos(t)    # конец переходит в начало без шва
    save(to_level(loop, integrated(loop), -40, peak_db=-12), name, kbps=96)


def meow(name, src):
    path = find(src)
    if not path:
        return
    a = fades(trim(shape(load(path), hp=250, lp=8000)), 0.005, 0.06)
    save(to_level(a, short_max(a, 0.1), -28), name)


def meows(names, src, cap=1.4):
    """Несколько мяуканий из одной записи: вокруг самых громких мест, от начала звука до спада
    (граница — 25 дБ ниже пика), не длиннее cap секунд."""
    path = find(src)
    if not path:
        return
    a = shape(load(path), hp=250, lp=8000)
    hop = int(SR * 0.02)
    env = 10 * np.log10(np.array([(a[i:i + hop] ** 2).mean() for i in range(0, len(a) - hop, hop)]) + 1e-12)
    picks = []
    for i in np.argsort(env)[::-1]:
        if all(abs(i - j) * hop > SR * cap for j in picks):
            picks.append(i)
        if len(picks) == len(names):
            break
    for name, p in zip(names, sorted(picks)):
        lo, hi = p, p
        while lo > 0 and env[lo - 1] > env[p] - 25 and (p - lo) * hop < SR * cap / 2:
            lo -= 1
        while hi < len(env) - 1 and env[hi + 1] > env[p] - 25 and (hi - lo) * hop < SR * cap:
            hi += 1
        seg = fades(a[lo * hop: (hi + 3) * hop], 0.01, 0.08)
        save(to_level(seg, short_max(seg, 0.1), -28), name)


def sniff(name, src, dur=1.2):
    """Кот нюхает: самый громкий кусок в dur секунд (два-три «фырк»), мягкие края, −30 LUFS кратко."""
    path = find(src)
    if not path:
        return
    a = shape(load(path), hp=250, lp=9000)
    start = loudest(a, dur, 1)[0]
    seg = fades(a[start:start + int(SR * dur)], 0.03, 0.15)
    save(to_level(seg, short_max(seg, 0.4), -30), name)


def purr(name, src, dur=3.2):
    path = find(src)
    if not path:
        return
    a = shape(load(path), hp=60, lp=4000)
    start = loudest(a, dur, 1)[0]
    seg = fades(a[start:start + int(SR * dur)], 0.4, 0.9)
    save(to_level(seg, short_max(seg, 0.4), -32), name)


def music(name, src, start=0):
    """Фоновая музыка: −30 LUFS, вырез 2–5 кГц под звуки интерфейса, мягкие вход и выход.
    start — с какой секунды брать запись (тихое вступление отрезается)."""
    path = find(src)
    if not path:
        return
    a = fades(shape(load(path)[int(SR * start):], hp=40, dip=(2000, 5000, -3)), 2.0, 3.0)
    os.makedirs(os.path.join(HERE, 'music'), exist_ok=True)
    save(to_level(a, integrated(a), -30, peak_db=-8), os.path.join('music', name), kbps=80)
    print(name, round(len(a) / SR), 'с')


# длительности подогнаны к анимациям: дверь открывается 0,75 с, крышка сундука 0,55 с,
# лист перелистывается 0,75 с, знамя разворачивается 1,2 с (два шороха ткани подряд)
for i, src in enumerate(['doorOpen_1', 'doorOpen_2', 'doorClose_1', 'doorClose_2', 'doorClose_3', 'doorClose_4'], 1):
    ui(f'door-{i}', src, cap=0.95)
for i, src in enumerate(['creak1', 'creak2', 'creak3'], 1):
    ui(f'chest-{i}', src, cap=0.7)
for i, src in enumerate(['handleCoins', 'handleCoins2'], 1):
    ui(f'coins-{i}', src)
for i, src in enumerate(['cloth1', 'cloth2', 'cloth3', 'cloth4'], 1):
    ui(f'banner-{i}', src)
for i, src in enumerate(['bookFlip1', 'bookFlip2'], 1):
    ui(f'page-{i}', src)
wind(['wind-1'], '146932__crashoverride6__wind-gust', 1)
wind(['wind-2', 'wind-3'], '457318__stek59__autumn-wind-and-dry-leaves', 2)
wind(['wind-4'], '347557__kinoton__rustling-leaves', 1)
wind(['wind-5'], '443065__amberdemeillon__leaves_rustling_edited', 1)
wind(['wind-6'], '178615__montacue__the-rustle-of-a-bush', 1)
fountain('fountain-1', '415027__roman_cgr__small-fountain')
fountain('fountain-2', '169250__skyko__fountain_1')
fountain('fountain-3', '193784__jhumbucker__water-fountain')
for i, src in enumerate(['fs-436541', 'fs-362652', 'fs-163286', 'fs-333916', 'fs-412017', 'fs-110011'], 1):
    meow(f'meow-{i}', src)
meows(['meow-7', 'meow-8'], 'fs-120160')       # «кот просит есть»: два мяуканья
meows(['meow-9'], 'fs-196251')                 # котёнок
purr('purr-1', 'fs-260881')
# кот нюхает мешки («Мешков пока нет»): freesound 848385 RavenWolfProds, 801809 Sadiquecat, 418161 14FPanskaZummer_Jakub
for i, src in enumerate(['fs-848385', 'fs-801809', 'fs-418161'], 1):
    sniff(f'sniff-{i}', src)
# музыка: один общий список на все экраны, играет по очереди и продолжается при переходах;
# 20 пьес, лютня и арфа вперемешку с более бодрыми, чтобы похожие не шли подряд
MUSIC = ['Loop_The_Bards_Tale', 'Loop_Kings_Feast', '769807__soundsandrebounds', 'oga-Market_Day', 'harvestseason',
         'Loop_Minstrel_Dance', 'fs-574485', 'oga-Komiku', 'oga-Exploration', 'Loop_Rejoicing', 'fs-608915', 'oga-Dowland',
         'Loop_The_Old_Tower_Inn', 'oga-HarpsiChordFlurry', 'fs-676787', 'fs-646460', 'oga-Serenade', 'oga-peasantry',
         'oga-Lament', 'fs-362288']
TRIM = {'fs-362288': 47}          # Kevzog: первые 47 с почти не слышны (на 20 дБ тише остального)
for i, src in enumerate(MUSIC, 1):
    music(f'music-{i}', src, TRIM.get(src, 0))
print('ok')

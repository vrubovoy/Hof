# Перьевые элементы интерфейса: рамки полей, сообщений и плашек (заливка — по тому же неровному
# контуру), закладки, линейки, подчёркивание, флажок, кольцо, ползунок. Кнопки и сургучные печати —
# нарисованные картинки (generated/btn-*, seal-*); прежние кнопки и печати пером — в _reserve/design/pen.
# Линия как от руки: длинные стороны плавно гуляют (несколько пологих волн), мелкая дрожь,
# лёгкий прогиб; одна линия, без второго «призрачного» штриха.
# Каждая рамка нарисована примерно в размер своего элемента: border-image тянет только середину,
# и если тянуть короткий рисунок на длинное поле, волна распрямляется в линейку.
# usage: python3 pen.py   → *.svg рядом с этим файлом. Случайность с зерном: результат всегда тот же.
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
INK = '#1B2E52'


def smooth_noise(n, rng, amp, k=1):
    v = [rng.uniform(-amp, amp) for _ in range(n + 1)]
    for _ in range(k):
        v = [(v[max(0, i - 1)] + v[i] + v[min(n, i + 1)]) / 3 for i in range(n + 1)]
    return v


def hand_line(p, q, rng, bow=0.8, jitter=0.22, step=3.0):
    """Точки линии от p к q: пологие волны по всей длине, прогиб и дрожь; концы — точно в p и q."""
    (x0, y0), (x1, y1) = p, q
    L = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(L / step))
    nx, ny = -(y1 - y0) / (L or 1), (x1 - x0) / (L or 1)
    b = rng.uniform(-bow, bow)
    waves = [(rng.uniform(140, 320), rng.uniform(0, 6.3), min(0.55, 0.12 + L / 1600) * rng.uniform(0.5, 1)) for _ in range(2)]
    noise = smooth_noise(n, rng, jitter, 2)
    pts = []
    for i in range(n + 1):
        t = i / n
        env = math.sin(math.pi * t) ** 0.6
        wave = sum(a * math.sin(2 * math.pi * t * L / wl + ph) for wl, ph, a in waves)
        off = b * math.sin(math.pi * t) + env * (wave + noise[i])
        pts.append((x0 + (x1 - x0) * t + nx * off, y0 + (y1 - y0) * t + ny * off))
    return pts


def d(pts, close=False):
    s = 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in pts)
    return s + (' Z' if close else '')


def box(rng, x0, y0, x1, y1):
    c = [(x0 + rng.uniform(-0.8, 0.8), y0 + rng.uniform(-0.8, 0.8)), (x1 + rng.uniform(-0.8, 0.8), y0 + rng.uniform(-0.8, 0.8)),
         (x1 + rng.uniform(-0.8, 0.8), y1 + rng.uniform(-0.8, 0.8)), (x0 + rng.uniform(-0.8, 0.8), y1 + rng.uniform(-0.8, 0.8))]
    pts = []
    for i in range(4):
        pts += hand_line(c[i], c[(i + 1) % 4], rng)[:-1]
    return pts


def svg(w, h, body, aspect=''):
    pa = f' preserveAspectRatio="{aspect}"' if aspect else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"{pa}>\n{body}</svg>\n'


def write(name, text):
    with open(os.path.join(HERE, name), 'w') as f:
        f.write(text)


def framed(name, w, h, seed, fill, fill_op, stroke, sw=1.7):
    """Прямоугольник пером w×h для border-image (срез 16): одна линия, заливка — по тому же контуру."""
    rng = random.Random(seed)
    pd = d(box(rng, 4.5, 4.5, w - 4.5, h - 4.5), True)
    body = f'<path d="{pd}" fill="{fill}" fill-opacity="{fill_op}"/>\n'
    body += f'<path d="{pd}" fill="none" stroke="{stroke}" stroke-opacity="0.92" stroke-width="{sw}" stroke-linejoin="round"/>\n'
    write(name, svg(w, h, body))


def tab(name, w, h, seed, fill, fill_op, stroke, sw=1.7):
    """Закладка: открыта снизу, верхние углы скруглены. border-image со срезом 16 16 0 16."""
    rng = random.Random(seed)
    r = 7
    left = hand_line((4.5, h), (4.8, 5 + r), rng, 0.4, 0.2)
    corner_l = [(4.8 + r * (1 - math.cos(a)), 5 + r - r * math.sin(a)) for a in [i * math.pi / 12 for i in range(7)]]
    top = hand_line((4.8 + r, 5), (w - 4.8 - r, 5.3), rng, 0.6, 0.25)
    corner_r = [(w - 4.8 - r + r * math.sin(a), 5.3 + r * (1 - math.cos(a))) for a in [i * math.pi / 12 for i in range(7)]]
    right = hand_line((w - 4.8, 5.3 + r), (w - 4.5, h), rng, 0.4, 0.2)
    pts = left + corner_l + top + corner_r + right
    body = f'<path d="{d(pts + [(w - 4.5, h), (4.5, h)], True)}" fill="{fill}" fill-opacity="{fill_op}"/>\n'
    body += f'<path d="{d(pts)}" fill="none" stroke="{stroke}" stroke-opacity="0.92" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>\n'
    write(name, svg(w, h, body))


def rule(name, seed, stroke, sw=1.2, op=0.9, length=1200, vertical=False):
    """Линейка length×6: растягивается по длине (preserveAspectRatio none), показывать толщиной 6 px."""
    rng = random.Random(seed)
    waves = [(rng.uniform(160, 380), rng.uniform(0, 6.3), rng.uniform(0.25, 0.5)) for _ in range(2)]
    noise = smooth_noise(length // 4, rng, 0.18, 2)
    pts = [(i * 4, 3 + sum(a * math.sin(2 * math.pi * i * 4 / wl + ph) for wl, ph, a in waves) * 0.75 + noise[i]) for i in range(length // 4 + 1)]
    if vertical:
        pts = [(y, x) for x, y in pts]
    body = f'<path d="{d(pts)}" fill="none" stroke="{stroke}" stroke-opacity="{op}" stroke-width="{sw}" stroke-linecap="round"/>\n'
    write(name, svg(6, length, body, 'none') if vertical else svg(length, 6, body, 'none'))


def check(name, seed, ticked):
    rng = random.Random(seed)
    body = f'<path d="{d(box(rng, 2.5, 2.5, 21.5, 21.5), True)}" fill="#FFFCF4" fill-opacity="0.8" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round"/>\n'
    if ticked:
        t = hand_line((6, 12.5), (10, 17), rng, 0.3, 0.1, 1.5) + hand_line((10, 17), (19.5, 4.5), rng, 0.6, 0.15, 1.5)[1:]
        body += f'<path d="{d(t)}" fill="none" stroke="{INK}" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/>\n'
    write(name, svg(24, 24, body))


def blob(rng, cx, cy, r, lobes=0.07):
    ph = [rng.uniform(0, 6.3) for _ in range(3)]
    pts = []
    for i in range(0, 361, 6):
        t = math.radians(i)
        rr = r * (1 + lobes * math.sin(3 * t + ph[0]) + lobes * 0.6 * math.sin(5 * t + ph[1]) + lobes * 0.4 * math.sin(8 * t + ph[2]))
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    return pts


def knob(name, seed):
    """Ручка ползунка: маленькая охристая печать пером."""
    rng = random.Random(seed)
    body = (f'<path d="{d(blob(rng, 13, 13, 9.5, 0.05), True)}" fill="#D7A64E" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round"/>\n'
            f'<path d="{d(blob(rng, 13, 13, 4.5, 0.05), True)}" fill="none" stroke="{INK}" stroke-width="1" stroke-opacity="0.6"/>\n')
    write(name, svg(26, 26, body))


def ring(name, seed, stroke):
    rng = random.Random(seed)
    pts = []
    for i in range(0, 400, 8):
        t = math.radians(i) - 0.4
        r = 1 + 0.02 * math.sin(3 * t) + (i / 360) * 0.03
        pts.append((40 + 34 * r * math.cos(t) + rng.uniform(-0.4, 0.4), 40 + 30 * r * math.sin(t) + rng.uniform(-0.4, 0.4)))
    write(name, svg(80, 80, f'<path d="{d(pts)}" fill="none" stroke="{stroke}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>\n'))


def chevron(name, seed, stroke):
    rng = random.Random(seed)
    pts = hand_line((3, 5), (7, 9.2), rng, 0.2, 0.1, 1) + hand_line((7, 9.2), (11, 5), rng, 0.2, 0.1, 1)[1:]
    write(name, svg(14, 14, f'<path d="{d(pts)}" fill="none" stroke="{stroke}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>\n'))


framed('pen-field.svg', 480, 48, 3, '#FFFCF4', 0.78, INK)
framed('pen-field-err.svg', 480, 48, 5, '#FFFCF4', 0.78, '#A83224')
# поле в фокусе: тот же контур (то же зерно), линия синяя и жирнее — вместо прямоугольной рамки браузера
framed('pen-field-focus.svg', 480, 48, 3, '#FFFCF4', 0.92, '#1F4E9E', sw=2.6)
framed('pen-field-err-focus.svg', 480, 48, 5, '#FFFCF4', 0.92, '#A83224', sw=2.6)
framed('pen-note-info.svg', 1000, 60, 23, '#FFFCF4', 0.7, '#1F4E9E')
framed('pen-note-error.svg', 1000, 60, 29, '#FFF6F2', 0.75, '#A83224')
framed('pen-panel.svg', 900, 84, 31, '#FFFDF8', 0.55, '#8F7E62', sw=1.3)
framed('pen-badge.svg', 120, 30, 33, '#FFFDF8', 0.6, '#8F7E62', sw=1.2)
framed('pen-pick.svg', 380, 62, 37, '#F3E3C2', 0.8, '#B98935', sw=1.5)
tab('pen-tab.svg', 140, 46, 41, '#FFFCF4', 0.6, INK)
tab('pen-tab-on.svg', 140, 46, 43, '#D7A64E', 1, INK)
rule('pen-rule.svg', 47, INK, 1.2)
rule('pen-rule-light.svg', 53, '#A8977A', 1.0, 0.75)
rule('pen-rule-ochre.svg', 59, '#B98935', 2.0, 0.95)
rule('pen-vrule-light.svg', 61, '#A8977A', 1.0, 0.75, vertical=True)
rule('pen-underline.svg', 67, '#1F4E9E', 1.3, length=240)
check('pen-check.svg', 71, False)
check('pen-check-on.svg', 71, True)
knob('pen-knob.svg', 89)
ring('pen-ring.svg', 17, '#B98935')
chevron('pen-chevron.svg', 23, INK)
print('ok')

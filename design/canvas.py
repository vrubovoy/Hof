# Генератор экранов Hof: доски холста «Hof — экраны MVP» (claude.ai Design) и живой прототип.
# Картинки, стили и звуки — локальные пути от папки design/. Для холста пути заменяются адресами
# загруженных копий из canvas-assets.json ({путь: {id, sha}}).
#
#   python3 canvas.py check              — какие файлы ещё не загружены на холст или изменились
#   python3 canvas.py record <путь> <id> — записать загруженный файл (sha берётся сейчас)
#   python3 canvas.py css <файл> <выход> — screens.css/demo.css с адресами холста (загрузить под тем же именем)
#   python3 canvas.py boards <project>   — доски *.dc.html и canvas.json для холста
#   python3 canvas.py preview            — живой прототип в design/preview/: ссылки, fx.js, звуки, музыка
#                                          (открыть design/preview/index.html в браузере)
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE_PATH = os.path.join(HERE, 'canvas-assets.json')
TABLE = json.load(open(TABLE_PATH, encoding='utf-8')) if os.path.exists(TABLE_PATH) else {}
MODE = sys.argv[1] if len(sys.argv) > 1 else 'check'
PREVIEW = MODE == 'preview'
USED = set()


def sha(path):
    return hashlib.sha256(open(os.path.join(HERE, path), 'rb').read()).hexdigest()[:16]


def U(path):
    """Адрес файла из design/ для текущего режима."""
    USED.add(path)
    if PREVIEW:
        return '../' + path
    rec = TABLE.get(path)
    return f'/_blob/{rec["id"]}' if rec else f'/_blob/MISSING:{path}'


def H(page):
    """Ссылка на другой экран: в прототипе — настоящая, на холсте — «#»."""
    return f'{page}.html' if PREVIEW else '#'


def css_for_canvas(name):
    src = open(os.path.join(HERE, name), encoding='utf-8').read()
    return re.sub(r'url\(([^)]+)\)', lambda m: f'url({U(m.group(1))})', src)


A = {k: U(v) for k, v in dict(
    login='generated/login-desktop-v2.webp', login2='generated/login-desktop-v2@2x.webp', login_m='generated/login-mobile-v2@2x.webp',
    map='generated/scene-courtyard-map.webp', map2='generated/scene-courtyard-map@2x.webp',
    residents='generated/scene-residents-panel.webp', residents2='generated/scene-residents-panel@2x.webp',
    treasury='generated/scene-treasury-band.webp', treasury2='generated/scene-treasury-band@2x.webp',
    chambers='generated/scene-chambers-panel.webp', chambers2='generated/scene-chambers-panel@2x.webp',
    empty_sk='generated/empty-saeckel.webp', empty_hist='generated/empty-history-closed.webp',
    sniff_1='generated/empty-saeckel-sniff-1.webp', sniff_2='generated/empty-saeckel-sniff-2.webp',
    empty_res='generated/empty-residents.webp',
    setup='generated/scene-setup.webp', setup2='generated/scene-setup@2x.webp', gate_open='generated/setup-gate-open.webp',
    e404='generated/error-404.webp', e4042='generated/error-404@2x.webp', e403='generated/error-403.webp', e4032='generated/error-403@2x.webp',
    e500='generated/error-500.webp', e5002='generated/error-500@2x.webp',
    sprig='generated/sprig-divider.webp', corner='generated/sprig-corner.webp',
    door_treasury='generated/map-treasury-door.webp', door_tower='generated/map-tower-door.webp', window_gate='generated/map-gatehouse-window.webp',
    mark='logo/hof-mark.svg', mark_w='logo/hof-mark-white.svg', pouch='generated/emblem-saeckel-small.webp',
    fountain='generated/emblem-fountain-small.webp', keys='generated/emblem-keys-small.webp', candle='generated/emblem-candle-small.webp',
    door_s='generated/emblem-door-small.webp', door_cs='generated/emblem-door-closed-small.webp',
    chest='generated/emblem-chest.webp', chest_c='generated/emblem-chest-closed.webp',
    key='generated/key-tag.webp', hook='generated/hook-empty.webp',
    lv_olive='generated/fx-leaves-olive.webp', lv_bush_l='generated/fx-leaves-bush-l.webp',
    lv_bush_r='generated/fx-leaves-bush-r.webp', lv_tree='generated/fx-leaves-tree.webp',
    bn_l='generated/fx-banner-gate-l.webp', bn_r='generated/fx-banner-gate-r.webp', bn_t='generated/fx-banner-tower.webp',
    map_cat='generated/map-cat.webp', chambers_cat='generated/chambers-cat.webp',
    pose_login='generated/pose-login.webp', pose_login2='generated/pose-login@2x.webp', pose_login_m='generated/pose-login-m.webp',
    pose_setup='generated/pose-setup.webp', pose_setup2='generated/pose-setup@2x.webp',
    pose_500='generated/pose-500.webp', pose_5002='generated/pose-500@2x.webp',
    blot_m='generated/ink-blot-medium.webp', blot_s='generated/ink-blot-small.webp',
    spl_a='generated/ink-splatter-a.webp', spl_b='generated/ink-splatter-b.webp', drip='generated/ink-drip.webp', ring='generated/ink-ring.webp',
).items()}
ICONS = {k: (U(f'generated/icon-{k}.webp') if k != 'pouch' else A['pouch'], label) for k, label in [  # знак мешка: ключ → (адрес, подпись)
    ('pouch', 'мешок'), ('cart', 'повозка'), ('basket', 'корзина'), ('hearth', 'очаг'), ('jug', 'кувшин'), ('mortar', 'ступка'),
    ('needle', 'игла'), ('lute', 'лютня'), ('bundle', 'свёрток'), ('scroll', 'свиток'), ('pot', 'кубышка'), ('toyhorse', 'лошадка'),
    ('bowl', 'миска'), ('hammer', 'молоток'), ('books', 'книги'), ('bag', 'котомка'), ('comb', 'гребень')]}
FONTS = 'https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,500;1,600&amp;display=swap'


def page(title, w, h, body, demo=False):
    if PREVIEW:
        return f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{title}</title>
<script src="../fx-head.js"></script>
<link href="{FONTS}" rel="stylesheet"><link rel="stylesheet" href="../screens.css">{'<link rel="stylesheet" href="../demo.css">' if demo else ''}
<style>html, body {{ height: 100%; margin: 0; overflow: hidden; background: #2E2A24; }} body {{ display: grid; place-items: center; }}</style></head>
<body>
{body}
<script>/* прототип: экран нарисован под {w}×{h} — вписать его в окно целиком */
(() => {{ const s = document.querySelector('.hof'); const fit = () => {{ s.style.zoom = Math.min(innerWidth / {w}, innerHeight / {h}); }}; fit(); addEventListener('resize', fit); }})();</script>
<script src="../fx.js" data-base="../"></script>
</body></html>
'''
    links = ''.join(f'<link rel="stylesheet" href="/_blob/{TABLE[c]["id"]}">\n' if c in TABLE else f'<link rel="stylesheet" href="/_blob/MISSING:{c}">\n'
                    for c in (['screens.css', 'demo.css'] if demo else ['screens.css']))
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
{links}</head>
<body>
<x-dc>
<helmet>
<link href="{FONTS}" rel="stylesheet">
<style>body{{margin:0}}</style>
</helmet>
{body}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
  renderVals() {{
    return {{}};
  }}
}}
</script>
</body>
</html>
'''


def blots(*items):
    return '\n  '.join(f'<img class="blot" src="{A[src]}" alt="" aria-hidden="true" style="left: {x}px; top: {y}px; width: {w}px; opacity: {op}; transform: rotate({rot}deg)">'
                       for src, x, y, w, rot, op in items)


def img2(key, alt, cls='scene', style=''):
    st = f' style="{style}"' if style else ''
    return f'<img class="{cls}" src="{A[key]}" srcset="{A[key]} 1x, {A[key + "2"]} 2x" alt="{alt}"{st}>'


def door(size):
    return f'<span class="frames" style="width: {size}px; height: {size}px"><img src="{A["door_cs"]}" alt=""><img src="{A["door_s"]}" alt=""></span>'


def vstack(key, frames, alt, width, inner='', extra=''):
    """Виньетка с кадрами сценки: кадры лежат поверх основы, показываются по классу на обёртке;
    нажимают на то, что внутри (кот). Без кадров — просто виньетка."""
    imgs = ''.join(f'<img class="f{i}" src="{A[k]}" alt="">' for i, k in enumerate(frames, 1))
    return f'<span class="vstack{extra}" style="width: {width}px"><img src="{A[key]}" alt="{alt}">{imgs}{inner}</span>'


def back(label, target, extra=''):
    """«Назад» маникулой: лист книги переворачивается назад."""
    return f'<a class="back{extra}" href="{H(target)}" data-fx="flip-back"><span>{label}</span></a>'


def select(sid, options, cls='input'):
    opts = ''.join(f'<option>{o}</option>' for o in options)
    return f'<span class="select"><select id="{sid}" class="{cls}">{opts}</select></span>'


def rel(pose, btn):
    """Кадр позы (x, y, w, h в px исходника) относительно кнопки-кота (тоже в px исходника) — в процентах."""
    (px, py, pw, ph), (bx, by, bw, bh) = pose, btn
    return f'left: {(px - bx) / bw * 100:.2f}%; top: {(py - by) / bh * 100:.2f}%; width: {pw / bw * 100:.2f}%; height: {ph / bh * 100:.2f}%'


def cat(style, label='Кот', pose='', attrs=''):
    """Кот на картинке — прозрачная кнопка; pose — (ключ кадра, его место относительно кнопки)."""
    k = pose[0] if pose else ''
    srcset = f' srcset="{A[k]} 1x, {A[k + "2"]} 2x"' if k + '2' in A else ''   # кадр в разрешении фона, иначе на Retina мутный
    img = f'<img class="pose" src="{A[k]}"{srcset} alt="" style="{pose[1]}">' if pose else ''
    return f'<button type="button" class="cat" aria-label="{label}" style="{style}"{attrs}>{img}</button>'


SNIFF_CAT = cat('left: 39%; top: 7%; width: 52%; height: 51%', attrs=' data-act="sniff"')   # кот у пустых мешков: нюхает


MENU = ['home', 'saeckel', 'users', 'account']   # порядок пунктов знамени: вниз — сцена уезжает влево, вверх — вправо


def banner(active):
    def item(key, label, icon, target):
        cur = ' active" aria-current="page' if key == active else ''
        fx = 'left' if MENU.index(key) > MENU.index(active) else 'right'
        keep = '' if key == 'saeckel' else ' data-keep'          # у службы своя шапка, знамя уезжает вместе со сценой
        return f'<a class="nav{cur}" href="{H(target)}" data-fx="{fx}"{keep}><img src="{A[icon]}" alt="">{label}</a>'
    return f'''<nav class="banner" aria-label="Hof">
      <a class="logo" href="{H('Home')}"><img src="{A['mark_w']}" width="44" height="44" alt=""><span><b>Hof</b><small>Ваш личный двор</small></span></a>
      {item('home', 'Двор', 'fountain', 'Home')}
      <div class="nav-label">Службы двора</div>
      {item('saeckel', 'Säckel', 'pouch', 'Saeckel')}
      <div class="nav-label">Хозяйство</div>
      {item('users', 'Приближённые', 'keys', 'Users')}
      <div class="banner-foot">
        {item('account', '<span class="stack" style="line-height: 1.2"><span>Мои покои</span><span class="small" style="opacity: 0.8">admin · хозяин</span></span>', 'candle', 'Account')}
        <button type="button" class="nav" data-go="{H('Main')}" data-sound="door" data-fx="right">{door(28)}Покинуть двор</button>
      </div>
    </nav>'''


def pct(x, y, w=None, h=None):  # координаты в исходнике карты 1536×1024 → проценты
    s = f'left: {x / 1536 * 100:.2f}%; top: {y / 1024 * 100:.2f}%'
    if w:
        s += f'; width: {w / 1536 * 100:.2f}%; height: {h / 1024 * 100:.2f}%'
    return s


def sc(x, y, w=None, h=None):
    """Координаты в сцене 1536×1024, показанной на весь экран 1440×900 (cover, слева по центру) → px."""
    k = 1440 / 1536
    s = f'left: {x * k:.0f}px; top: {y * k - 30:.0f}px'
    if w:
        s += f'; width: {w * k:.0f}px; height: {h * k:.0f}px'
    return s


def place(label, target, sign_xy, frame, box, cls='', pid=''):
    """Место на карте — одна ссылка: вывеска + кадр «открыто» (дверь или окно); нажать можно на любое.
    sign_xy=None — без вывески (телефон: вывески списком под картой)."""
    sign = f'<span class="sign on-map" style="{pct(*sign_xy)}"><span>{label}</span></span>' if sign_xy else ''
    i = f' id="{pid}"' if pid else ''
    aria = '' if sign_xy else f' aria-label="{label}"'
    return f'<a class="place {cls}"{i} href="{H(target)}"{aria}><img class="lit" src="{A[frame]}" alt="" style="{pct(*box)}">{sign}</a>'


MAP_ALT = 'Двор замка: ворота со сторожкой, казначейская, башня с покоями, фонтан посередине'
MAP_CAT = cat(pct(826, 680, 54, 72), pose=('map_cat', 'left: -62.96%; top: -79.17%; width: 287.04%; height: 211.11%'))
FOUNTAIN = f'<div class="fx fx-fountain" aria-hidden="true" style="{pct(610, 570, 340, 200)}"></div>'
LEAVES = ''.join(f'<div class="fx fx-leaves{" demo" if not PREVIEW else ""}" aria-hidden="true" style="{pct(x, y, w, h)}; background-image: url({A[k]}); --cycle: {c}s; --delay: {d}s"></div>'
                 for k, (x, y, w, h), c, d in [('lv_olive', (0, 620, 570, 270), 11, 2), ('lv_bush_l', (540, 592, 160, 140), 13, 5.5),
                                                ('lv_bush_r', (880, 598, 182, 144), 13, 9), ('lv_tree', (400, 226, 166, 204), 17, 0.6)])
BANNERS = ''.join(f'<div class="fx fx-banner" aria-hidden="true" style="{pct(*box)}; background-image: url({A[k]}); --cycle: {c}s"></div>'
                  for k, box, c in [('bn_l', (50, 384, 72, 134), 2.6), ('bn_r', (308, 384, 68, 131), 3.1), ('bn_t', (1442, 308, 88, 202), 3.5)])
BIRDS = (f'<div class="fx fx-birds" aria-hidden="true" style="top: 7%; height: 12%">'
         '<i style="left: 4%; top: 30%; --w: 2.6%; --flap: 0.66s"></i><i style="left: 8.5%; top: 6%; --w: 2.2%; --flap: 0.72s; --d: -0.3s"></i>'
         '<i style="left: 0.5%; top: 62%; --w: 2%; --flap: 0.7s; --d: -0.5s"></i></div>')
SMOKE = f'<div class="fx fx-smoke" aria-hidden="true" style="{pct(712, 100, 32, 80)}"><i></i><i></i><i></i></div>'
MAP_FX = FOUNTAIN + LEAVES + BANNERS + SMOKE + BIRDS
PW = 'Не короче [N] символов.'


def map_block(demo=False):
    inner = ' style="margin-top: -34px; transform-origin: 461px 376px; --cycle: 12s; --delay: 4s"' if demo else ' style="margin-top: -34px"'
    return f'''<div class="map fade-lb" style="height: 610px; flex: none">
        <div class="map-inner zoom"{inner}>
          {img2('map', MAP_ALT, cls='')}
          {MAP_FX}
          {place('Приближённые', 'Users', (215, 298), 'window_gate', (449, 476, 48, 63), 'p1')}
          {place('Säckel', 'Saeckel', (612, 346), 'door_treasury', (579, 429, 72, 145), 'p2')}
          {place('Мои покои', 'Account', (1330, 318), 'door_tower', (1334, 459, 84, 227), 'p3')}
          {MAP_CAT}
        </div>
        <h1 class="ribbon" style="position: absolute; left: 30px; top: 22px; margin: 0"><span>Добрый день!</span></h1>
      </div>'''


# ---------- Hof, компьютер ----------

def login_page(demo=False):
    veil = '<div class="veil" style="--cycle: 6s; --delay: 1s"></div>' if demo else ''
    zoom = ' style="position: absolute; inset: 0; transform-origin: 521px 532px; --cycle: 6s; --delay: 1s"' if demo else ' style="position: absolute; inset: 0"'
    return f'''<div class="hof{" demo" if demo else ""}" style="width: 1440px; height: 900px">
  <div class="zoom"{zoom}>
    <img class="scene" src="{A['login']}" srcset="{A['login']} 1x, {A['login2']} 2x" alt="Открытые ворота замка, кот смотрит во двор" style="position: absolute; inset: 0; object-position: left center">
    <i class="spot" id="gate" style="{sc(556, 600)}"></i>
    {cat(sc(656, 770, 124, 126), pose=('pose_login', rel((576, 696, 258, 245), (656, 770, 124, 126))))}
  </div>
  <div style="position: absolute; top: 0; right: 0; bottom: 0; width: 560px; display: flex; align-items: center; padding: 0 56px 0 24px">
    <form class="framed stack" style="gap: 22px; width: 100%">
      <div class="logo"><img src="{A['mark']}" width="78" height="78" alt=""><span><b style="font-size: 54px">Hof</b><small style="font-size: 11px">Ваш личный двор</small></span></div>
      <h1 class="title t-2">С возвращением во двор!</h1>
      <div class="field"><label for="l-login">Логин</label><input id="l-login" class="input" type="text" autocomplete="username"></div>
      <div class="field"><label for="l-pass">Пароль</label><input id="l-pass" class="input" type="password" autocomplete="current-password"></div>
      <button type="button" class="btn btn-blue btn-wide{" press" if demo else ""}" data-go="{H('Home')}" data-spot="#gate" data-unroll>Войти во двор</button>
      <p class="small muted">Нет ключа или забыли пароль? Обратитесь к хозяину двора.</p>
    </form>
  </div>
  {veil}
  {blots(('blot_s', 1360, 64, 46, 0, 0.7), ('spl_b', 1290, 800, 92, 14, 0.55), ('drip', 1405, 470, 22, 0, 0.75))}
</div>'''


def setup_page(demo=False):
    veil = '<div class="veil" style="--cycle: 7s; --delay: 1.4s"></div>' if demo else ''
    zoom = ' style="position: absolute; inset: 0; transform-origin: 521px 532px; --cycle: 7s; --delay: 1.4s"' if demo else ' style="position: absolute; inset: 0"'
    return f'''<div class="hof{" demo" if demo else ""}" style="width: 1440px; height: 900px">
  <div class="zoom"{zoom}>
    {img2('setup', 'Ворота замка закрыты, в замке ключ, кот ждёт у ворот', style='position: absolute; inset: 0; object-position: left center')}
    <img class="gate-open" id="gate-open" src="{A['gate_open']}" alt="" style="{sc(424, 440, 264, 350)}">
    <i class="spot" id="gate" style="{sc(556, 600)}"></i>
    {cat(sc(574, 740, 100, 124), pose=('pose_setup', rel((514, 680, 225, 215), (574, 740, 100, 124))))}
  </div>
  <div style="position: absolute; top: 0; right: 0; bottom: 0; width: 580px; display: flex; align-items: center; padding: 0 56px 0 24px">
    <form class="framed stack" style="gap: 14px; width: 100%">
      <div class="logo"><img src="{A['mark']}" width="48" height="48" alt=""><span><b style="font-size: 38px">Hof</b><small>Ваш личный двор</small></span></div>
      <div class="stack" style="gap: 4px"><h1 class="title t-2">Основание двора</h1><p class="muted small">Станьте хозяином двора: вы принимаете приближённых и присматриваете за Hof.</p></div>
      <div class="field"><label for="s-code">Ключ от ворот</label><input id="s-code" class="input" type="text" autocomplete="off" style="letter-spacing: 0.08em"><span class="hint">Одноразовый код из лога сервера: <code>docker compose logs hof</code></span></div>
      <div class="field"><label for="s-login">Логин</label><input id="s-login" class="input" type="text" autocomplete="username"><span class="hint">Латиница, цифры, точка, дефис и подчёркивание, до 32 символов.</span></div>
      <div class="field"><label for="s-pass">Пароль</label><input id="s-pass" class="input" type="password" autocomplete="new-password"><span class="hint">{PW}</span></div>
      <div class="field"><label for="s-pass2">Пароль ещё раз</label><input id="s-pass2" class="input" type="password" autocomplete="new-password"></div>
      <button type="button" class="btn btn-blue btn-wide{" press" if demo else ""}" data-go="{H('Home')}" data-spot="#gate" data-opens="#gate-open" data-unroll>Основать двор</button>
    </form>
  </div>
  {veil}
  {blots(('blot_m', 1370, 30, 52, 20, 0.65), ('ring', 1330, 820, 110, -15, 0.45))}
</div>'''


def home_page(demo=False, unroll=True):
    veil = '<div class="veil" style="--cycle: 12s; --delay: 4s"></div>' if demo else ''
    enter = ' fx-enter' if not PREVIEW and not demo and unroll else ''
    return f'''<div class="hof{enter}{" demo" if demo else ""}" style="width: 1440px; height: 900px">
  <div class="shell">
    {banner('home')}
    <main class="stack" style="min-width: 0">
      {map_block(demo)}
      <div style="display: grid; grid-template-columns: minmax(0, 1fr) 590px; column-gap: 40px; align-items: start; padding: 4px 40px 0">
        <div class="stack" style="gap: 8px; padding-top: 24px">
          <h2 class="title t-2">Ваш двор в порядке</h2>
          <img class="sprig" src="{A['sprig']}" alt="" style="width: 180px; margin: -2px 0 2px">
          <p class="muted">Вывески на карте ведут в службы и комнаты. Те же места всегда есть в знамени слева.</p>
        </div>
        <aside class="framed" style="display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 4px 18px; align-items: center">
          <h3 class="title t-3" style="grid-column: 1 / -1">Пока во дворе только вы</h3>
          <p class="small muted">Примите приближённых: у каждого будет свой ключ и свои мешки.</p>
          <a class="btn" href="{H('Users')}" data-fx="left" data-keep>Принять ко двору</a>
        </aside>
      </div>
    </main>
  </div>
  {veil}
  {blots(('blot_s', 420, 838, 42, 0, 0.75), ('spl_b', 690, 806, 76, 12, 0.5), ('ring', 1384, 846, 104, 20, 0.42), ('drip', 312, 640, 20, 0, 0.7))}
</div>'''


def key(img, login, status, link, target='User'):
    alt = 'ключ на крючке' if img == 'key' else 'пустой крючок'
    a = f'<a class="link-plain small" href="{H(target)}" data-fx="flip-fwd">{link}</a>' if link else ''
    return f'<div class="key"><img src="{A[img]}" alt="{alt}"><b>{login}</b><span class="small muted">{status}</span>{a}</div>'


users = f'''<div class="hof" style="width: 1440px; height: 900px">
  <div class="shell" style="grid-template-columns: 288px 420px minmax(0, 1fr)">
    {banner('users')}
    <div class="fade-lr">{img2('residents', 'Сторожка у ворот: ключница с ключами на крюках, один крюк пустой', style='object-position: 30% 50%')}</div>
    <main class="stack" style="gap: 18px; padding: 34px 40px 30px 0; min-width: 0; margin-left: -60px">
      <h1 class="ribbon md" style="align-self: flex-start"><span>Приближённые</span></h1>
      <p class="note">Ключ для anna готов. Передайте логин и начальный пароль лично.</p>
      <section class="keys" aria-label="Ключница">
        {key('key', 'admin', 'хозяин, это вы', '')}
        {key('key', 'anna', 'С ключом', 'Открыть ›')}
        {key('hook', 'pavel', 'Ключ взят', 'Открыть ›')}
      </section>
      <form class="framed stack" style="gap: 12px">
        <h2 class="title t-3">Принять ко двору</h2>
        <div style="display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) auto; gap: 12px; align-items: end">
          <div class="field"><label for="u-login">Логин</label><input id="u-login" class="input" type="text" autocomplete="off"></div>
          <div class="field"><label for="u-pass">Начальный пароль</label><input id="u-pass" class="input" type="text" autocomplete="off"></div>
          <button type="button" class="btn btn-blue">Принять</button>
        </div>
        <span class="hint">Пароль виден, чтобы его можно было передать. Человек сменит его в своих покоях.</span>
      </form>
    </main>
  </div>
  {blots(('spl_b', 1250, 250, 96, 8, 0.55), ('blot_s', 1372, 70, 44, 0, 0.7), ('ring', 1360, 838, 100, -20, 0.42))}
</div>'''

user = f'''<div class="hof" style="width: 1440px; height: 900px">
  <div class="shell">
    {banner('users')}
    <main class="stack" style="gap: 20px; padding: 34px 48px; min-width: 0">
      {back('Приближённые', 'Users')}
      <div style="display: grid; grid-template-columns: 200px minmax(0, 1fr) minmax(0, 1fr); gap: 28px; align-items: stretch; max-width: 1060px">
        <div class="stack" style="align-items: center; gap: 8px; padding-top: 10px">
          <img src="{A['key']}" alt="ключ anna на крючке" style="width: 128px; height: 262px">
          <h1 class="title t-1">anna</h1>
          <span class="badge">С ключом</span>
        </div>
        <form class="framed stack" style="gap: 14px">
          <h2 class="title t-3">Сбросить пароль</h2>
          <div class="field"><label for="p-new">Новый начальный пароль</label><input id="p-new" class="input" type="text" autocomplete="off"><span class="hint">anna выйдет со двора на всех устройствах. Передайте новый пароль лично.</span></div>
          <button type="button" class="btn btn-blue push" style="align-self: flex-start">Сбросить пароль</button>
        </form>
        <form class="framed stack" style="gap: 14px">
          <h2 class="title t-3">Ключ от двора</h2>
          <p>У anna есть ключ от двора. Если забрать ключ, вход закроется сразу, а мешки и записи останутся. Вернуть ключ можно в любой момент.</p>
          <button type="button" class="btn btn-danger push" style="align-self: flex-start">Забрать ключ</button>
        </form>
      </div>
    </main>
  </div>
  {blots(('blot_m', 1340, 690, 70, 25, 0.6), ('spl_a', 470, 780, 84, -10, 0.5), ('drip', 1400, 60, 22, 0, 0.7), ('blot_s', 900, 820, 40, 0, 0.7))}
</div>'''


def setting(key, title, hint, slider=None):
    row = f'<label class="check"><input type="checkbox" data-setting="{key}"><span><b>{title}</b><span class="small muted">{hint}</span></span></label>'
    if slider:
        vkey, value, label = slider
        row += (f'<div class="volume"><span class="small muted">громкость</span>'
                f'<input type="range" min="0" max="100" step="5" value="{value}" data-setting="{vkey}" aria-label="{label}"><output>{value} %</output></div>')
    return row


account = f'''<div class="hof" style="width: 1440px; height: 900px">
  <div class="shell" style="grid-template-columns: 288px minmax(0, 1fr) 600px">
    {banner('account')}
    <main class="stack" style="gap: 12px; padding: 24px 8px 20px 40px; min-width: 0">
      <div style="display: flex; align-items: center; gap: 10px"><h1 class="ribbon md" style="margin-left: -10px"><span>Мои покои</span></h1><span class="muted">admin · хозяин двора</span></div>
      <form class="framed stack" style="gap: 8px; padding: 22px 30px 20px">
        <h2 class="title t-3">Сменить пароль</h2>
        <div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px">
          <div class="field"><label for="a-cur">Текущий пароль</label><input id="a-cur" class="input" type="password" autocomplete="current-password"></div>
          <div class="field"><label for="a-new">Новый пароль</label><input id="a-new" class="input" type="password" autocomplete="new-password"></div>
          <div class="field"><label for="a-new2">Ещё раз</label><input id="a-new2" class="input" type="password" autocomplete="new-password"></div>
        </div>
        <span class="hint">{PW} На других устройствах вы выйдете со двора.</span>
        <button type="button" class="btn btn-blue" style="align-self: flex-start">Сменить пароль</button>
      </form>
      <form class="framed stack" style="gap: 6px; padding: 20px 30px 18px">
        <h2 class="title t-3">Звуки и движение</h2>
        {setting('anim', 'Анимации', 'знамя, фонтан, ветер в листве, двери, переходы')}
        {setting('sound', 'Звуки', 'двери, сундук, монеты, кот, вода и ветер во дворе', ('soundVol', 80, 'Громкость звуков'))}
        {setting('music', 'Музыка', 'лютня и старинные напевы, одна на всех экранах — играет дальше при переходах', ('musicVol', 50, 'Громкость музыки'))}
        <span class="hint">Сначала всё выключено. Настройка этого устройства.</span>
      </form>
      <div style="display: flex; align-items: center; gap: 16px; padding-left: 8px">
        <button type="button" class="btn" data-go="{H('Main')}" data-sound="door" data-fx="right">{door(26)}Покинуть двор</button>
        <span class="small muted">на этом устройстве; всё во дворе останется на месте</span>
      </div>
    </main>
    <div class="fade-l" style="position: relative">{img2('chambers', 'Покои: окно во двор, стол с пером и чернильницей, кот спит на стуле', style='object-position: 50% 50%')}{cat('left: 305px; top: 559px; width: 290px; height: 131px', pose=('chambers_cat', 'left: -28px; top: -29px; width: 302px; height: 183px'), attrs=' data-sound="purr"')}</div>
  </div>
  {blots(('blot_s', 760, 860, 40, 0, 0.7), ('spl_a', 330, 852, 70, 15, 0.5), ('drip', 806, 120, 20, 0, 0.7))}
</div>'''


def error_page(img, alt, title, text, buttons, blot_items, extra=''):
    return f'''<div class="hof" style="width: 1440px; height: 900px">
  {img2(img, alt, style='position: absolute; inset: 0; object-position: left center')}
  {extra}
  <main class="stack" style="position: absolute; top: 0; right: 0; bottom: 0; width: 500px; justify-content: center; gap: 14px; padding: 0 70px 0 10px">
    <a class="logo" href="{H('Home')}"><img src="{A['mark']}" width="40" height="40" alt=""><span><b style="font-size: 30px">Hof</b><small>Ваш личный двор</small></span></a>
    <h1 class="title t-1" style="margin-top: 18px">{title}</h1>
    <img class="sprig" src="{A['sprig']}" alt="">
    <p class="muted">{text}</p>
    <div style="display: flex; align-items: center; gap: 18px; margin-top: 8px">{buttons}</div>
  </main>
  {blots(*blot_items)}
</div>'''


TO_COURT = f'<a class="btn btn-blue" href="{H("Home")}" data-fx="right">Во двор</a>'
states = error_page('e404', 'Заросшая тропинка упирается в глухую стену, увитую плющом', 'Такой тропы во дворе нет',
                    'Возможно, ссылка устарела или в адресе опечатка.', TO_COURT,
                    [('blot_s', 1370, 70, 44, 0, 0.7), ('spl_b', 1300, 790, 88, 10, 0.5)])
error403 = error_page('e403', 'Тяжёлая дверь с висячим замком', 'Сюда только хозяину',
                      'Это место двора открыто только хозяину. Если нужно, попросите его.', TO_COURT,
                      [('drip', 1400, 60, 22, 0, 0.7), ('ring', 1290, 800, 100, -12, 0.42)])
error500 = error_page('e500', 'Опрокинутая бочка, по двору раскатились яблоки, кот разглядывает беспорядок', 'Во дворе что-то стряслось',
                      'Мы уже прибираемся. Попробуйте ещё раз через минуту — записанное раньше на месте.',
                      f'<a class="btn btn-blue" href="{H("Home")}">Попробовать ещё раз</a><a class="link" href="{H("Home")}">Во двор</a>',
                      [('blot_m', 1350, 60, 56, 20, 0.6), ('spl_a', 1240, 810, 70, -10, 0.5)], cat(sc(680, 736, 210, 160), pose=('pose_500', rel((606, 676, 336, 261), (680, 736, 210, 160)))))

users_empty = f'''<div class="hof" style="width: 1440px; height: 900px">
  <div class="shell" style="grid-template-columns: 288px 420px minmax(0, 1fr)">
    {banner('users')}
    <div class="fade-lr">{img2('residents', 'Сторожка у ворот: ключница с ключами на крюках', style='object-position: 30% 50%')}</div>
    <main class="stack" style="gap: 16px; padding: 34px 40px 30px 0; min-width: 0; margin-left: -60px">
      <h1 class="ribbon md" style="align-self: flex-start"><span>Приближённые</span></h1>
      <div style="display: grid; grid-template-columns: 330px minmax(0, 1fr); gap: 24px; align-items: center">
        <img class="vignette" src="{A['empty_res']}" alt="Ключница, на ней один ключ" style="width: 330px">
        <div class="stack" style="gap: 8px">
          <h2 class="title t-2">Пока у двора только хозяин</h2>
          <img class="sprig" src="{A['sprig']}" alt="" style="width: 170px">
          <p class="muted">На ключнице один ключ — ваш. Примите ко двору семью или друзей: у каждого будет свой ключ и свои мешки.</p>
        </div>
      </div>
      <form class="framed stack" style="gap: 12px">
        <h2 class="title t-3">Принять ко двору</h2>
        <div style="display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) auto; gap: 12px; align-items: end">
          <div class="field"><label for="ue-login">Логин</label><input id="ue-login" class="input" type="text" autocomplete="off"></div>
          <div class="field"><label for="ue-pass">Начальный пароль</label><input id="ue-pass" class="input" type="text" autocomplete="off"></div>
          <button type="button" class="btn btn-blue">Принять</button>
        </div>
        <span class="hint">Пароль виден, чтобы его можно было передать. Человек сменит его в своих покоях.</span>
      </form>
    </main>
  </div>
  {blots(('spl_a', 1270, 70, 80, 12, 0.5), ('ring', 1360, 838, 96, -20, 0.42))}
</div>'''

# ---------- Säckel, компьютер ----------


TABS = ['Мешки', 'Летопись']   # закладки службы по порядку: вправо — лист вперёд, влево — назад


def tab(name, current, target):
    if name == current:
        return f'<a class="tab" href="{H(target)}" aria-current="page">{name}</a>'
    fx = 'flip-fwd' if TABS.index(name) > TABS.index(current) else 'flip-back'
    return f'<a class="tab" href="{H(target)}" data-fx="{fx}">{name}</a>'


def sk_head(current):
    return f'''<header class="sk-head">
    {img2('treasury', 'Казначейская: стол с весами, монетами, книгой, мешками и сундуком')}
    <a class="sk-gate" href="{H('Home')}" data-fx="flip-back"><img src="{A['mark']}" width="22" height="22" alt="">Двор</a>
  </header>
  <nav class="sk-nav" aria-label="Säckel"><h1 class="ribbon md"><span>Säckel</span></h1>{tab('Мешки', current, 'Saeckel')}{tab('Летопись', current, 'SaeckelHistory')}<span class="caps" style="margin: 0 0 18px auto">Бюджет по мешкам</span></nav>'''


POUCHES = [('Продукты', 'последняя трата −1 240 ₽', '12 450,30 ₽'), ('Квартира', 'последняя трата −18 000 ₽', '25 000,00 ₽'),
           ('Транспорт', 'в долгу', '−760,00 ₽'), ('Отпуск', 'трат пока не было', '4 000,00 ₽')]
POUCH_ICON = {'Продукты': 'basket', 'Квартира': 'hearth', 'Транспорт': 'cart', 'Отпуск': 'bag'}


def pouch(name, sub, bal, active=False, neg=False, style='', target='Saeckel'):
    cur = ' active" aria-current="page' if active else ''
    n = ' neg' if neg else ''
    st = f' style="{style}"' if style else ''
    fx = ' data-fx="flip-fwd"' if target != 'Saeckel' else ''
    return (f'<a class="pouch{cur}" href="{H(target)}"{st}{fx}><img src="{ICONS[POUCH_ICON[name]][0]}" alt=""><span class="stack"><span class="name">{name}</span>'
            f'<span class="sub{n}">{sub}</span></span><span class="bal{n}">{bal}</span></a>')


def chest(w, h):
    return f'<span class="frames chest" style="width: {w}px; height: {h}px"><img src="{A["chest_c"]}" alt=""><img src="{A["chest"]}" alt=""></span>'


def sk_list(active=None, buttons=True):
    btns = (f'<div class="btns"><a class="btn btn-ochre" href="{H("SaeckelAssign")}" data-sound="coins">Разложить</a>'
            f'<a class="btn" href="{H("SaeckelForms")}">+ Доход</a></div>') if buttons else ''
    rows = '\n      '.join(pouch(n, s, b, n == active, b.startswith('−')) for n, s, b in POUCHES)
    return f'''<aside class="sk-list">
      <div class="framed treasury" data-sound="chest">
        {chest(62, 52)}
        <h2 class="title t-3">Казна</h2>
        <span class="money" style="font-size: 30px; line-height: 1.1">18 320 ₽</span>
        {btns}
      </div>
      {rows}
      <div style="display: flex; justify-content: space-between; padding: 12px 24px"><a class="link-plain" href="{H('SaeckelForms')}">+ Новый мешок</a><a class="link-plain small" href="#" style="color: var(--ink-2)">Кладовая (2)</a></div>
    </aside>'''


saeckel = f'''<div class="hof" style="width: 1440px; height: 900px">
  {sk_head('Мешки')}
  <div class="sk-body">
    {sk_list('Продукты')}
    <main class="sk-main">
      <div style="display: flex; align-items: center; gap: 14px">
        <img src="{ICONS['basket'][0]}" alt="" width="58" height="58" style="object-fit: contain">
        <h2 class="title t-1">Продукты</h2>
        <span style="margin-left: auto; display: flex; gap: 24px"><a class="link" href="{H('SaeckelForms')}">Переложить</a><a class="link" href="{H('SaeckelForms')}">Изменить</a></span>
      </div>
      <div class="balance"><span class="caps">Остаток</span><span class="money" style="font-size: 40px; line-height: 1.05">12 450,30 ₽</span></div>
      <form class="stack" style="gap: 8px">
        <h3 class="title t-3">Записать трату</h3>
        <div class="form-row">
          <div class="field"><label for="k-sum">Сумма, ₽</label><input id="k-sum" class="input" type="text" inputmode="decimal"></div>
          <div class="field"><label for="k-date">Дата</label><input id="k-date" class="input" type="text" value="05.10.2026"></div>
          <div class="field"><label for="k-note">Заметка</label><input id="k-note" class="input" type="text"></div>
          <button type="button" class="btn btn-ochre" data-sound="coins" data-fresh="#k-rows tr:first-child" data-squeeze=".pouch.active img">Записать трату</button>
        </div>
      </form>
      <table class="table"><tbody id="k-rows">
        <tr><td class="muted" style="width: 80px">05.10</td><td>Трата</td><td class="note-text">овощи на рынке</td><td class="num money">−1 240,00 ₽</td></tr>
        <tr><td class="muted">01.10</td><td>Из казны</td><td></td><td class="num money">+8 000,00 ₽</td></tr>
      </tbody></table>
    </main>
  </div>
  {blots(('blot_m', 1350, 840, 60, 30, 0.6), ('spl_a', 470, 852, 64, -12, 0.5), ('drip', 1408, 450, 20, 0, 0.7))}
</div>'''


def assign_row(name, now, val=''):
    v = f' value="{val}"' if val else ''
    neg = ' neg' if now.startswith('−') else ''
    return (f'<tr><td><span style="display: inline-flex; align-items: center; gap: 10px"><img src="{ICONS[POUCH_ICON[name]][0]}" alt="" width="30" height="30" style="object-fit: contain">{name}</span></td>'
            f'<td class="num money{neg}">{now}</td><td><input class="input slim" type="text" inputmode="decimal"{v} aria-label="Положить в мешок {name}"></td></tr>')


assign = f'''<div class="hof" style="width: 1440px; height: 900px">
  {sk_head('Мешки')}
  <div class="sk-body">
    {sk_list(buttons=False)}
    <main class="sk-main" style="gap: 12px">
      <p class="note">Доход 80 000 ₽ лёг в казну. Разложите его по мешкам или оставьте в казне на потом.</p>
      <div style="display: flex; align-items: baseline; gap: 20px"><h2 class="title t-2">Разложить по мешкам</h2><p class="muted">В казне: <span class="money" style="color: var(--ink)">18 320 ₽</span>. Пустые поля пропускаются.</p></div>
      <table class="table" style="max-width: 760px">
        <thead><tr><th>Мешок</th><th class="num">Сейчас в мешке</th><th style="width: 220px">Положить, ₽</th></tr></thead>
        <tbody>
          {assign_row('Продукты', '12 450,30 ₽', '8 000')}
          {assign_row('Квартира', '25 000,00 ₽')}
          {assign_row('Транспорт', '−760,00 ₽', '2 000')}
          {assign_row('Отпуск', '4 000,00 ₽')}
        </tbody>
      </table>
      <div style="display: flex; align-items: center; gap: 20px"><button type="button" class="btn btn-ochre" data-sound="coins">Разложить</button><a class="link" href="{H('Saeckel')}">Позже — вернуться к мешкам</a></div>
    </main>
  </div>
  {blots(('blot_s', 1360, 470, 44, 0, 0.7), ('ring', 1330, 810, 100, 15, 0.42))}
</div>'''


def hist(d, pouch_, op, note, s):
    return (f'<tr><td class="muted">{d}</td><td>{pouch_}</td><td>{op}</td><td class="note-text">{note}</td><td class="num money">{s}</td>'
            f'<td class="num"><a class="link-plain" href="{H("SaeckelForms")}" aria-label="Открыть запись">›</a></td></tr>')


history = f'''<div class="hof" style="width: 1440px; height: 900px">
  {sk_head('Летопись')}
  <main class="stack" style="gap: 10px; padding: 18px 48px; height: calc(100% - 414px)">
    <div style="display: flex; align-items: flex-end; justify-content: space-between; max-width: 1100px">
      <h2 class="title t-2">Летопись</h2>
      <div class="field" style="width: 260px"><label for="h-filter">Мешок</label>{select('h-filter', ['Все мешки', 'Продукты', 'Квартира', 'Транспорт', 'Отпуск'], 'input slim')}</div>
    </div>
    <table class="table" style="max-width: 1100px">
      <thead><tr><th style="width: 110px">Дата</th><th style="width: 240px">Мешок</th><th style="width: 180px">Запись</th><th>Заметка</th><th class="num">Сумма</th><th style="width: 40px"></th></tr></thead>
      <tbody>
        {hist('05.10.2026', 'Продукты', 'Трата', 'овощи на рынке', '−1 240,00 ₽')}
        {hist('04.10.2026', 'Отпуск → Транспорт', 'Из мешка в мешок', '', '760,00 ₽')}
        {hist('04.10.2026', 'Транспорт', 'Трата', 'бензин', '−1 300,00 ₽')}
        {hist('01.10.2026', 'Продукты', 'Из казны', '', '+8 000,00 ₽')}
        {hist('30.09.2026', 'Казна', 'Доход', 'зарплата', '+80 000,00 ₽')}
      </tbody>
    </table>
    <a class="btn" href="#" data-sound="page" style="align-self: flex-start">Показать ещё</a>
  </main>
  {blots(('blot_m', 1300, 470, 64, 25, 0.55), ('spl_b', 1250, 790, 90, 10, 0.5))}
</div>'''


def icon_picker(name, chosen):
    return '<div class="icons">' + ''.join(
        f'<label class="icon-pick"><input type="radio" name="{name}" value="{k}"{" checked" if k == chosen else ""}><img src="{src}" alt="">{label}</label>'
        for k, (src, label) in ICONS.items()) + '</div>'


forms = f'''<div class="hof" style="width: 1440px; height: 1120px; padding: 34px 40px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); grid-template-rows: auto auto; gap: 30px 40px; align-items: stretch; align-content: start">
  <form class="framed stack" style="gap: 14px">
    <h2 class="title t-2">Доход</h2>
    <div style="display: grid; grid-template-columns: 190px 160px minmax(0, 1fr); gap: 12px; align-items: end">
      <div class="field err"><label for="i-sum">Сумма, ₽</label><input id="i-sum" class="input big" type="text" inputmode="decimal" value="0" aria-invalid="true" aria-describedby="i-sum-err"></div>
      <div class="field"><label for="i-date">Дата</label><input id="i-date" class="input" type="text" value="30.09.2026"></div>
      <div class="field"><label for="i-note">Заметка</label><input id="i-note" class="input" type="text" value="зарплата"></div>
    </div>
    <p id="i-sum-err" class="err-text">Сумма должна быть больше нуля.</p>
    <p class="hint">Деньги лягут в казну. После записи откроется раскладка по мешкам — её можно отложить.</p>
    <button type="button" class="btn btn-ochre push" data-go="{H('SaeckelAssign')}" data-sound="coins" style="align-self: flex-start">Записать доход</button>
  </form>
  <form class="framed stack" style="gap: 14px">
    <h2 class="title t-2">Переложить из мешка в мешок</h2>
    <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px">
      <div class="field"><label for="t-from">Из мешка</label>{select('t-from', ['Отпуск — 4 000,00 ₽'])}</div>
      <div class="field"><label for="t-to">В мешок</label>{select('t-to', ['Транспорт — −760,00 ₽'])}</div>
    </div>
    <div style="display: grid; grid-template-columns: 190px 160px minmax(0, 1fr); gap: 12px; align-items: end">
      <div class="field"><label for="t-sum">Сумма, ₽</label><input id="t-sum" class="input big" type="text" inputmode="decimal" value="760"></div>
      <div class="field"><label for="t-date">Дата</label><input id="t-date" class="input" type="text" value="04.10.2026"></div>
      <div class="field"><label for="t-note">Заметка</label><input id="t-note" class="input" type="text"></div>
    </div>
    <button type="button" class="btn btn-ochre push" data-sound="coins" style="align-self: flex-start">Переложить</button>
  </form>
  <form class="framed stack" style="gap: 14px">
    <h2 class="title t-2">Мешок «Транспорт»</h2>
    <div class="field"><label for="e-name">Название</label><input id="e-name" class="input" type="text" value="Транспорт"></div>
    <fieldset class="field" style="border: 0; padding: 0; margin: 0"><legend style="padding: 0 0 6px">Знак мешка</legend>{icon_picker('e-icon', 'cart')}</fieldset>
    <button type="button" class="btn btn-ochre" style="align-self: flex-start">Сохранить</button>
    <div class="rule"></div>
    <h3 class="title t-3">В кладовую</h3>
    <p class="muted">Убрать в кладовую можно только пустой мешок. Сейчас в нём <span class="money neg">−760,00 ₽</span>.</p>
    <div style="display: flex; align-items: center; gap: 18px"><button type="button" class="btn" disabled>В кладовую</button><a class="link" href="#">Покрыть из другого мешка</a></div>
  </form>
  <form class="framed stack" style="gap: 14px">
    <h2 class="title t-2">Трата · 05.10.2026</h2>
    <div style="display: grid; grid-template-columns: minmax(0, 1fr) 190px; gap: 12px; align-items: end">
      <div class="field"><label for="o-pouch">Из мешка</label>{select('o-pouch', ['Продукты'])}</div>
      <div class="field"><label for="o-sum">Сумма, ₽</label><input id="o-sum" class="input big" type="text" inputmode="decimal" value="1 240"></div>
    </div>
    <div style="display: grid; grid-template-columns: 160px minmax(0, 1fr); gap: 12px">
      <div class="field"><label for="o-date">Дата</label><input id="o-date" class="input" type="text" value="05.10.2026"></div>
      <div class="field"><label for="o-note">Заметка</label><input id="o-note" class="input" type="text" value="овощи на рынке"></div>
    </div>
    <p class="hint">Вид записи не меняется. Удаление попросит подтверждения.</p>
    <div class="push" style="display: flex; align-items: center; gap: 12px"><button type="button" class="btn btn-ochre">Сохранить</button><button type="button" class="btn btn-danger">Удалить</button></div>
  </form>
  {blots(('blot_s', 700, 1076, 40, 0, 0.7), ('ring', 1320, 1020, 96, 20, 0.42), ('spl_a', 30, 1050, 64, -15, 0.5))}
</div>'''

empty = f'''<div class="hof" style="width: 1440px; height: 900px">
  {sk_head('Мешки')}
  <main style="display: grid; grid-template-columns: 440px minmax(0, 560px); gap: 48px; align-items: center; justify-content: center; height: calc(100% - 414px); padding: 10px 48px">
    {vstack('empty_sk', ['sniff_1', 'sniff_2'], 'Кот обнюхивает пустые мешочки', 440, SNIFF_CAT)}
    <form class="stack" style="gap: 12px">
      <h2 class="title t-1">Мешков пока нет</h2>
      <img class="sprig" src="{A['sprig']}" alt="">
      <p class="muted">Заведите первый мешок: «Продукты», «Квартира», «Транспорт». Траты берутся из мешка, а остаток переходит дальше сам.</p>
      <div style="display: flex; gap: 12px; align-items: flex-end"><div class="field" style="flex: 1"><label for="n-name">Название</label><input id="n-name" class="input" type="text" value="Продукты"></div><button type="button" class="btn btn-ochre">Завести мешок</button></div>
      <span class="hint">Знак мешка можно выбрать потом, в «Изменить».</span>
    </form>
  </main>
  <img class="corner" src="{A['corner']}" alt="" aria-hidden="true">
  {blots(('blot_m', 1330, 820, 60, 30, 0.6))}
</div>'''

history_empty = f'''<div class="hof" style="width: 1440px; height: 900px">
  {sk_head('Летопись')}
  <main style="display: grid; grid-template-columns: 420px minmax(0, 520px); gap: 48px; align-items: center; justify-content: center; height: calc(100% - 414px); padding: 10px 48px">
    {vstack('empty_hist', [], 'Закрытая книга, перо и чернильница', 420)}
    <div class="stack" style="gap: 12px">
      <h2 class="title t-1">Летопись пока пуста</h2>
      <img class="sprig" src="{A['sprig']}" alt="">
      <p class="muted">Сюда ляжет каждый доход, трата и перекладывание — по порядку, с датой и заметкой.</p>
      <div style="display: flex; align-items: center; gap: 18px; margin-top: 6px"><a class="btn btn-ochre" href="{H('SaeckelForms')}">Записать доход</a><a class="link" href="{H('Saeckel')}">К мешкам</a></div>
    </div>
  </main>
  <img class="corner" src="{A['corner']}" alt="" aria-hidden="true">
  {blots(('blot_s', 1360, 830, 42, 0, 0.7))}
</div>'''

# ---------- телефон ----------

login_m = f'''<div class="hof" style="width: 390px; height: 844px">
  <div class="zoom" style="position: absolute; left: 0; bottom: 0; width: 390px; height: 390px">
    <img src="{A['login_m']}" alt="Открытые ворота замка, кот смотрит во двор" style="display: block; width: 390px; height: 390px">
    <i class="spot" id="m-gate" style="left: 205px; top: 288px"></i>{cat('left: 230px; top: 311px; width: 47px; height: 47px', pose=('pose_login_m', rel((692, 961, 247, 238), (740, 1000, 150, 150))))}
  </div>
  <form class="stack" style="position: relative; gap: 18px; padding: 34px 28px 0">
    <div class="stack" style="align-items: center; gap: 4px"><img src="{A['mark']}" width="72" height="72" alt=""><span style="font-weight: 600; font-size: 52px; line-height: 1; letter-spacing: 0.06em">Hof</span><span class="caps" style="font-size: 11px; letter-spacing: 0.24em">Ваш личный двор</span></div>
    <div class="field"><label for="m-login">Логин</label><input id="m-login" class="input" type="text" autocomplete="username" autocapitalize="none"></div>
    <div class="field"><label for="m-pass">Пароль</label><input id="m-pass" class="input" type="password" autocomplete="current-password"></div>
    <button type="button" class="btn btn-blue btn-wide" data-go="{H('HomeMobile')}" data-spot="#m-gate">Войти во двор</button>
    <p class="small muted" style="text-align: center">Нет ключа или забыли пароль?<br>Обратитесь к хозяину двора.</p>
  </form>
  {blots(('blot_s', 330, 26, 34, 0, 0.7))}
</div>'''

def m_top(here='home'):
    """Шапка Hof на телефоне: знак ведёт во двор (назад), свеча — в Мои покои (вперёд)."""
    home = '' if here == 'home' else ' data-fx="right"'
    acc = ' aria-current="page"' if here == 'account' else ' data-fx="left"'
    return f'''<header class="m-top">
    <a class="logo" href="{H('HomeMobile')}"{home}><img src="{A['mark']}" width="32" height="32" alt=""><b style="font-size: 30px">Hof</b></a>
    <a href="{H('AccountMobile')}"{acc} aria-label="Мои покои" style="display: flex; align-items: center; justify-content: center; width: 44px; height: 44px"><img src="{A['candle']}" alt="" width="34" height="34"></a>
  </header>'''


m_top_hof = m_top()

home_m = f'''<div class="hof" style="width: 390px; height: 844px">
  {m_top_hof}
  <div class="map fade-b"><div class="map-inner zoom">{img2('map', MAP_ALT, cls='')}{MAP_FX}
    {place('Приближённые', 'UsersMobile', None, 'window_gate', (449, 476, 48, 63), pid='mp-users')}
    {place('Säckel', 'SaeckelMobile', None, 'door_treasury', (579, 429, 72, 145), pid='mp-saeckel')}
    {place('Мои покои', 'AccountMobile', None, 'door_tower', (1334, 459, 84, 227), pid='mp-account')}{MAP_CAT}</div></div>
  <div class="stack" style="align-items: center; gap: 6px; padding: 0 12px">
    <h1 class="ribbon md" style="position: relative; margin-top: -30px"><span>Добрый день!</span></h1>
    <nav class="stack" style="align-items: center; gap: 0" aria-label="Места двора">
      <a class="sign sm" href="{H('SaeckelMobile')}" data-go="{H('SaeckelMobile')}" data-spot="#mp-saeckel .lit" data-opens="#mp-saeckel" style="min-width: 240px"><span>Säckel</span></a>
      <a class="sign sm" href="{H('UsersMobile')}" data-go="{H('UsersMobile')}" data-spot="#mp-users .lit" data-opens="#mp-users" style="min-width: 240px"><span>Приближённые</span></a>
      <a class="sign sm" href="{H('AccountMobile')}" data-go="{H('AccountMobile')}" data-spot="#mp-account .lit" data-opens="#mp-account" style="min-width: 240px"><span>Мои покои</span></a>
    </nav>
    <aside class="framed stack" style="gap: 8px; width: 100%; margin-top: 8px; padding: 24px 24px 20px">
      <h2 class="title t-3">Пока во дворе только вы</h2>
      <p class="small muted">Примите приближённых: у каждого будет свой ключ и свои мешки.</p>
      <a class="btn btn-wide" href="{H('UsersMobile')}" data-fx="left">Принять ко двору</a>
    </aside>
  </div>
  {blots(('spl_a', 300, 790, 62, -12, 0.55), ('blot_s', 16, 560, 30, 0, 0.7))}
</div>'''


def m_band(back_label, target):
    return f'''<div class="m-band">
    {img2('treasury', 'Казначейская', style='object-position: 55% 72%')}
    <a class="sk-gate" href="{H(target)}" data-fx="flip-back" style="left: 12px; top: 12px; height: 40px">{back_label}</a>
  </div>'''


def m_sk_nav(current):
    return f'''<div class="stack" style="align-items: center; padding-top: 8px"><h1 class="ribbon md"><span>Säckel</span></h1></div>
  <nav style="display: flex; justify-content: center; gap: 6px; padding: 0 16px; background: url({U('pen/pen-rule-light.svg')}) left bottom / 100% 6px no-repeat" aria-label="Säckel">{tab('Мешки', current, 'SaeckelMobile')}{tab('Летопись', current, 'HistoryMobile')}</nav>'''


sk_m = f'''<div class="hof" style="width: 390px; height: 844px">
  {m_band('Двор', 'HomeMobile')}
  {m_sk_nav('Мешки')}
  <div>
  <div class="framed treasury" data-sound="chest" style="margin: 8px 10px 4px; padding: 18px 18px 14px; grid-template-columns: 54px minmax(0, 1fr)">
    {chest(54, 46)}
    <h2 class="title t-3">Казна</h2>
    <span class="money" style="font-size: 28px; line-height: 1.1">18 320 ₽</span>
    <div class="btns" style="display: grid; grid-template-columns: minmax(0, 1fr) auto"><a class="btn btn-ochre" href="{H('AssignMobile')}" data-fx="flip-fwd">Разложить</a><a class="btn" href="{H('IncomeMobile')}" data-fx="flip-fwd">+ Доход</a></div>
  </div>
  {''.join(pouch(n, s, b, False, b.startswith('−'), 'margin: 0 6px; padding: 6px 10px 8px', 'PouchMobile') for n, s, b in POUCHES)}
  <div style="display: flex; justify-content: space-between; padding: 12px 16px"><a class="link-plain" href="{H('SaeckelEmptyMobile')}">+ Новый мешок</a><a class="link-plain small" href="#" style="color: var(--ink-2)">Кладовая (2)</a></div>
  </div>
  {blots(('blot_s', 340, 800, 32, 0, 0.7))}
</div>'''

pouch_m = f'''<div class="hof" style="width: 390px; height: 844px">
  {m_band('Мешки', 'SaeckelMobile')}
  <div class="stack" style="gap: 12px; padding: 14px 16px 16px">
    <div style="display: flex; align-items: center; gap: 10px"><img id="pm-icon" src="{ICONS['basket'][0]}" alt="" width="48" height="48" style="object-fit: contain"><h1 class="title t-1">Продукты</h1><a class="link small" href="{H('PouchEditMobile')}" data-fx="flip-fwd" style="margin-left: auto">Изменить</a></div>
    <div class="balance"><span class="caps">Остаток</span><span class="money" style="font-size: 34px; line-height: 1.05">12 450,30 ₽</span></div>
    <form class="framed stack" style="gap: 10px; padding: 22px 20px 18px">
      <div class="field"><label for="pm-sum">Сумма траты, ₽</label><input id="pm-sum" class="input big" type="text" inputmode="decimal"></div>
      <div style="display: grid; grid-template-columns: 116px minmax(0, 1fr); gap: 10px">
        <div class="field"><label for="pm-date">Дата</label><input id="pm-date" class="input" type="text" value="05.10.2026"></div>
        <div class="field"><label for="pm-note">Заметка</label><input id="pm-note" class="input" type="text"></div>
      </div>
      <button type="button" class="btn btn-ochre btn-wide" data-sound="coins" data-fresh="#pm-rows tr:first-child" data-squeeze="#pm-icon">Записать трату</button>
    </form>
    <table class="table"><tbody id="pm-rows">
      <tr><td class="small muted" style="width: 50px">05.10</td><td class="note-text">овощи на рынке</td><td class="num money">−1 240,00 ₽</td></tr>
      <tr><td class="small muted">01.10</td><td>из казны</td><td class="num money">+8 000,00 ₽</td></tr>
    </tbody></table>
  </div>
  {blots(('spl_b', 300, 796, 66, 10, 0.5))}
</div>'''

def m_pic(key, alt, w, left, top, h, extra='', cls=''):
    """Кадр сцены на телефоне: картинка шириной w px сдвинута на left/top внутри полосы высотой h."""
    return (f'<div class="m-pic {cls}" style="position: relative; height: {h}px; overflow: hidden">'
            f'<img src="{A[key]}" srcset="{A[key]} 1x, {A[key + "2"]} 2x" alt="{alt}" style="position: absolute; left: {left}px; top: {top}px; width: {w}px; max-width: none">{extra}</div>')


def at(x, y, w=None, h=None, k=1.0, ox=0, oy=0):
    """Точка/прямоугольник сцены (px исходника) в кадре телефона: масштаб k, сдвиг ox, oy."""
    s = f'left: {x * k + ox:.0f}px; top: {y * k + oy:.0f}px'
    return s + (f'; width: {w * k:.0f}px; height: {h * k:.0f}px' if w else '')


SK = 760 / 1536                       # основание: сцена 1536 → 760 px, видны арка ворот и кот
setup_m = f'''<div class="hof" style="width: 390px; height: 844px">
  <form class="stack" style="position: relative; z-index: 1; gap: 10px; padding: 20px 24px 0">
    <div class="logo"><img src="{A['mark']}" width="36" height="36" alt=""><span><b style="font-size: 30px">Hof</b><small>Ваш личный двор</small></span></div>
    <div class="stack" style="gap: 2px"><h1 class="title t-2">Основание двора</h1><p class="muted small">Станьте хозяином: вы принимаете приближённых и присматриваете за Hof.</p></div>
    <div class="field"><label for="sm-code">Ключ от ворот</label><input id="sm-code" class="input" type="text" autocomplete="off"><span class="hint">Код из лога сервера</span></div>
    <div class="field"><label for="sm-login">Логин</label><input id="sm-login" class="input" type="text" autocomplete="username" autocapitalize="none"></div>
    <div class="field"><label for="sm-pass">Пароль</label><input id="sm-pass" class="input" type="password" autocomplete="new-password"></div>
    <div class="field"><label for="sm-pass2">Пароль ещё раз</label><input id="sm-pass2" class="input" type="password" autocomplete="new-password"></div>
    <button type="button" class="btn btn-blue btn-wide" data-go="{H('HomeMobile')}" data-spot="#sm-gate" data-opens="#sm-gate-open">Основать двор</button>
  </form>
  <div class="zoom fade-t" style="position: absolute; left: 0; bottom: 0; width: 390px; height: 274px; overflow: hidden">
    <img src="{A['setup']}" srcset="{A['setup']} 1x, {A['setup2']} 2x" alt="Ворота замка закрыты, в замке ключ, кот ждёт у ворот" style="position: absolute; left: -85px; top: -160px; width: 760px; max-width: none">
    <img class="gate-open" id="sm-gate-open" src="{A['gate_open']}" alt="" style="{at(424, 440, 264, 350, SK, -85, -160)}">
    <i class="spot" id="sm-gate" style="{at(556, 600, k=SK, ox=-85, oy=-160)}"></i>
    {cat(at(574, 740, 100, 124, SK, -85, -160), pose=('pose_setup', rel((514, 680, 225, 215), (574, 740, 100, 124))))}
  </div>
</div>'''

users_m = f'''<div class="hof" style="width: 390px; height: 844px">
  {m_top('users')}
  {m_pic('residents', 'Сторожка у ворот: ключница с ключами на крюках', 390, 0, -150, 170)}
  <div class="stack" style="align-items: center; margin-top: -28px; position: relative"><h1 class="ribbon md"><span>Приближённые</span></h1></div>
  <div class="stack" style="gap: 14px; padding: 4px 16px 16px">
    <section class="keys m-keys" aria-label="Ключница">
      {key('key', 'admin', 'хозяин, это вы', '')}
      {key('key', 'anna', 'С ключом', 'Открыть ›', 'UserMobile')}
      {key('hook', 'pavel', 'Ключ взят', 'Открыть ›', 'UserMobile')}
    </section>
    <form class="framed stack" style="gap: 10px; padding: 20px 20px 18px">
      <h2 class="title t-3">Принять ко двору</h2>
      <div class="field"><label for="um-login">Логин</label><input id="um-login" class="input" type="text" autocomplete="off" autocapitalize="none"></div>
      <div class="field"><label for="um-pass">Начальный пароль</label><input id="um-pass" class="input" type="text" autocomplete="off"><span class="hint">Пароль виден, чтобы его можно было передать.</span></div>
      <button type="button" class="btn btn-blue btn-wide">Принять</button>
    </form>
  </div>
</div>'''

user_m = f'''<div class="hof" style="width: 390px; height: 844px">
  {m_top('users')}
  <div class="stack" style="gap: 14px; padding: 14px 16px 16px">
    {back('Приближённые', 'UsersMobile')}
    <div style="display: flex; align-items: center; gap: 18px; padding-left: 10px">
      <img src="{A['key']}" alt="ключ anna на крючке" style="width: 64px; height: 131px">
      <div class="stack" style="gap: 6px; align-items: flex-start"><h1 class="title t-1">anna</h1><span class="badge">С ключом</span></div>
    </div>
    <form class="framed stack" style="gap: 10px; padding: 20px 20px 18px">
      <h2 class="title t-3">Сбросить пароль</h2>
      <div class="field"><label for="pm-new">Новый начальный пароль</label><input id="pm-new" class="input" type="text" autocomplete="off"><span class="hint">anna выйдет со двора на всех устройствах.</span></div>
      <button type="button" class="btn btn-blue btn-wide">Сбросить пароль</button>
    </form>
    <form class="framed stack" style="gap: 10px; padding: 20px 20px 18px">
      <h2 class="title t-3">Ключ от двора</h2>
      <p class="small">Если забрать ключ, вход закроется сразу, а мешки и записи останутся. Вернуть можно в любой момент.</p>
      <button type="button" class="btn btn-danger btn-wide">Забрать ключ</button>
    </form>
  </div>
</div>'''

KC = 390 / 683                        # покои: панель 683 → 390 px, видны стол и кот
account_m = f'''<div class="hof" style="width: 390px; height: 1180px">
  {m_top('account')}
  {m_pic('chambers', 'Покои: стол с пером и чернильницей, кот спит на стуле', 390, 0, -300, 170,
         cat(at(315, 603, 344, 208, KC, 0, -300), pose=('chambers_cat', 'left: 0; top: 0; width: 100%; height: 100%'), attrs=' data-sound="purr"'))}
  <div class="stack" style="align-items: center; gap: 2px; margin-top: -28px; position: relative"><h1 class="ribbon md"><span>Мои покои</span></h1><span class="small muted">admin · хозяин двора</span></div>
  <div class="stack" style="gap: 14px; padding: 10px 16px 16px">
    <form class="framed stack" style="gap: 10px; padding: 20px 20px 18px">
      <h2 class="title t-3">Сменить пароль</h2>
      <div class="field"><label for="am-cur">Текущий пароль</label><input id="am-cur" class="input" type="password" autocomplete="current-password"></div>
      <div class="field"><label for="am-new">Новый пароль</label><input id="am-new" class="input" type="password" autocomplete="new-password"></div>
      <div class="field"><label for="am-new2">Ещё раз</label><input id="am-new2" class="input" type="password" autocomplete="new-password"><span class="hint">{PW} На других устройствах вы выйдете со двора.</span></div>
      <button type="button" class="btn btn-blue btn-wide">Сменить пароль</button>
    </form>
    <form class="framed stack m-settings" style="gap: 6px; padding: 20px 20px 18px">
      <h2 class="title t-3">Звуки и движение</h2>
      {setting('anim', 'Анимации', 'знамя, фонтан, ветер, двери, переходы')}
      {setting('sound', 'Звуки', 'двери, сундук, монеты, кот, вода и ветер', ('soundVol', 80, 'Громкость звуков'))}
      {setting('music', 'Музыка', 'лютня и старинные напевы', ('musicVol', 50, 'Громкость музыки'))}
      <span class="hint">Сначала всё выключено. Настройка этого устройства.</span>
    </form>
    <button type="button" class="btn btn-wide" data-go="{H('LoginMobile')}" data-sound="door" data-fx="right">{door(26)}Покинуть двор</button>
  </div>
</div>'''

history_m = f'''<div class="hof" style="width: 390px; height: 844px">
  {m_band('Двор', 'HomeMobile')}
  {m_sk_nav('Летопись')}
  <div class="stack" style="gap: 8px; padding: 12px 16px">
    <div class="field"><label for="hm-filter">Мешок</label>{select('hm-filter', ['Все мешки', 'Продукты', 'Квартира', 'Транспорт', 'Отпуск'], 'input slim')}</div>
    <div class="m-list">
      {''.join(f'<a class="m-row" href="{H("IncomeMobile")}"><span class="small muted">{d}</span><span class="money{" neg" if v.startswith("−") else ""}">{v}</span><span>{p_} · {op}</span><span class="note-text small">{n}</span></a>'
               for d, p_, op, n, v in [('05.10', 'Продукты', 'Трата', 'овощи на рынке', '−1 240,00 ₽'), ('04.10', 'Отпуск → Транспорт', 'Переложено', '', '760,00 ₽'),
                                         ('04.10', 'Транспорт', 'Трата', 'бензин', '−1 300,00 ₽'), ('01.10', 'Продукты', 'Из казны', '', '+8 000,00 ₽'),
                                         ('30.09', 'Казна', 'Доход', 'зарплата', '+80 000,00 ₽')])}
    </div>
    <a class="btn btn-wide" href="#" data-sound="page">Показать ещё</a>
  </div>
</div>'''

assign_m = f'''<div class="hof" style="width: 390px; height: 844px">
  {m_band('Мешки', 'SaeckelMobile')}
  <div class="stack" style="gap: 10px; padding: 14px 16px 16px">
    <p class="note" style="margin-left: 22px">Доход 80 000 ₽ лёг в казну.</p>
    <h1 class="title t-2">Разложить по мешкам</h1>
    <p class="small muted">В казне: <span class="money" style="color: var(--ink)">18 320 ₽</span>. Пустые поля пропускаются.</p>
    <div class="m-list">
      {''.join(f'<div class="m-assign"><img src="{ICONS[POUCH_ICON[n]][0]}" alt=""><span class="stack"><b>{n}</b><span class="small money{" neg" if now.startswith("−") else ""}">{now}</span></span>'
               f'<input class="input slim" type="text" inputmode="decimal"{f" value={chr(34)}{v}{chr(34)}" if v else ""} aria-label="Положить в мешок {n}"></div>'
               for n, now, v in [('Продукты', '12 450,30 ₽', '8 000'), ('Квартира', '25 000,00 ₽', ''), ('Транспорт', '−760,00 ₽', '2 000'), ('Отпуск', '4 000,00 ₽', '')])}
    </div>
    <button type="button" class="btn btn-ochre btn-wide" data-sound="coins">Разложить</button>
    <a class="link" href="{H('SaeckelMobile')}" style="align-self: center">Позже — вернуться к мешкам</a>
  </div>
</div>'''

income_m = f'''<div class="hof" style="width: 390px; height: 844px">
  {m_band('Мешки', 'SaeckelMobile')}
  <div class="stack" style="gap: 12px; padding: 14px 16px 16px">
    <form class="framed stack" style="gap: 10px; padding: 20px 20px 18px">
      <h1 class="title t-2">Доход</h1>
      <div class="field err"><label for="im-sum">Сумма, ₽</label><input id="im-sum" class="input big" type="text" inputmode="decimal" value="0" aria-invalid="true" aria-describedby="im-sum-err"><span id="im-sum-err" class="err-text">Сумма должна быть больше нуля.</span></div>
      <div class="field"><label for="im-date">Дата</label><input id="im-date" class="input" type="text" value="30.09.2026"></div>
      <div class="field"><label for="im-note">Заметка</label><input id="im-note" class="input" type="text" value="зарплата"></div>
      <p class="hint">Деньги лягут в казну. После записи откроется раскладка по мешкам — её можно отложить.</p>
      <button type="button" class="btn btn-ochre btn-wide" data-go="{H('AssignMobile')}" data-sound="coins">Записать доход</button>
    </form>
    <p class="small muted" style="padding: 0 6px">Так же устроены «Переложить», «Новый мешок» и правка записи: одна колонка, поля друг под другом.</p>
  </div>
</div>'''

pouch_edit_m = f'''<div class="hof" style="width: 390px; height: 1180px">
  {m_band('Мешки', 'SaeckelMobile')}
  <div class="stack" style="gap: 12px; padding: 14px 16px 16px">
    <form class="framed stack" style="gap: 10px; padding: 20px 18px 18px">
      <h1 class="title t-2">Мешок «Транспорт»</h1>
      <div class="field"><label for="pe-name">Название</label><input id="pe-name" class="input" type="text" value="Транспорт"></div>
      <fieldset class="field" style="border: 0; padding: 0; margin: 0"><legend style="padding: 0 0 6px">Знак мешка</legend>{icon_picker('pe-icon', 'cart')}</fieldset>
      <button type="button" class="btn btn-ochre btn-wide">Сохранить</button>
    </form>
    <section class="framed stack" style="gap: 10px; padding: 20px 18px 18px">
      <h2 class="title t-3">В кладовую</h2>
      <p class="small muted">Убрать в кладовую можно только пустой мешок. Сейчас в нём <span class="money neg">−760,00 ₽</span>.</p>
      <button type="button" class="btn btn-wide" disabled>В кладовую</button>
      <a class="link" href="#" style="align-self: center">Покрыть из другого мешка</a>
    </section>
  </div>
</div>'''

empty_m = f'''<div class="hof" style="width: 390px; height: 844px">
  {m_band('Двор', 'HomeMobile')}
  {m_sk_nav('Мешки')}
  <div class="stack" style="gap: 10px; padding: 8px 20px 16px; align-items: center">
    {vstack('empty_sk', ['sniff_1', 'sniff_2'], 'Кот обнюхивает пустые мешочки', 280, SNIFF_CAT)}
    <h2 class="title t-2" style="align-self: stretch">Мешков пока нет</h2>
    <p class="small muted">Заведите первый мешок: «Продукты», «Квартира», «Транспорт». Траты берутся из мешка, а остаток переходит дальше сам.</p>
    <div class="field" style="align-self: stretch"><label for="em-name">Название</label><input id="em-name" class="input" type="text" value="Продукты"></div>
    <button type="button" class="btn btn-ochre btn-wide">Завести мешок</button>
  </div>
</div>'''

E4 = 640 / 1536                       # 404: сцена 1536 → 640 px, видны тропа и стена
error_m = f'''<div class="hof" style="width: 390px; height: 844px">
  {m_pic('e404', 'Заросшая тропинка упирается в глухую стену, увитую плющом', 640, -40, -20, 390, cls='fade-b')}
  <main class="stack" style="gap: 10px; padding: 0 24px 20px">
    <a class="logo" href="{H('HomeMobile')}" data-fx="right"><img src="{A['mark']}" width="32" height="32" alt=""><span><b style="font-size: 26px">Hof</b><small>Ваш личный двор</small></span></a>
    <h1 class="title t-2">Такой тропы во дворе нет</h1>
    <img class="sprig" src="{A['sprig']}" alt="" style="width: 170px">
    <p class="muted">Возможно, ссылка устарела или в адресе опечатка.</p>
    <a class="btn btn-blue btn-wide" href="{H('HomeMobile')}" data-fx="right">Во двор</a>
    <p class="small muted">«Сюда только хозяину» и «Во дворе что-то стряслось» устроены так же — своя картинка сверху.</p>
  </main>
</div>'''

# ---------- витрина анимаций (только холст: там не выполняются скрипты) ----------

small_demo = f'''<div class="hof demo" style="width: 1440px; height: 900px; padding: 40px; display: grid; grid-template-columns: 300px repeat(3, minmax(0, 1fr)); gap: 30px 40px; align-content: start">
  <div class="unroll-demo" style="grid-row: span 3; position: relative; height: 810px; overflow: hidden">
    <nav class="banner loop" aria-label="Пример" style="height: 810px">
      <span class="logo"><img src="{A['mark_w']}" width="44" height="44" alt=""><span><b>Hof</b><small>Ваш личный двор</small></span></span>
      <span class="nav"><img src="{A['fountain']}" alt="">Двор</span><span class="nav"><img src="{A['pouch']}" alt="">Säckel</span>
    </nav>
  </div>
  <div class="framed stack" style="align-items: center; gap: 8px"><span class="caps">Казна: сундук</span>{chest(110, 92)}<span class="small muted">нажатие: открывается со скрипом</span></div>
  <div class="framed stack" style="align-items: center; gap: 8px"><span class="caps">Покинуть двор</span>{door(92)}<span class="small muted">нажатие: дверь открывается со звуком</span></div>
  <div class="framed stack" style="align-items: center; gap: 8px"><span class="caps">Забрать ключ</span><span class="key-loop" style="position: relative; flex: none; width: 60px; height: 123px"><img src="{A['key']}" alt="" style="position: absolute; inset: 0; width: 60px; height: 123px"><img src="{A['hook']}" alt="" style="position: absolute; inset: 0; width: 60px; height: 123px; opacity: 0"></span><span class="small muted">ключ снимается с крючка</span></div>
  <div class="stack" style="gap: 10px; justify-content: center"><span class="caps">Сообщение: печать ставится</span><p class="note">Доход 80 000 ₽ лёг в казну.</p><p class="note note-error">Пароли не совпадают.</p></div>
  <div class="stack" style="align-items: center; gap: 8px; justify-content: center"><span class="caps">Кот: нажатие — звук и другая поза</span><span style="position: relative; display: block; width: 300px; height: 220px; overflow: hidden"><img src="{A['map']}" alt="" style="position: absolute; left: -680px; top: -560px; width: 1536px; max-width: none">{cat('left: 146px; top: 120px; width: 54px; height: 72px', pose=('map_cat', 'left: -62.96%; top: -79.17%; width: 287.04%; height: 211.11%'))}</span></div>
  <div class="stack" style="gap: 18px; justify-content: center; align-items: flex-start"><span class="caps">Вывеска и «назад»</span><span class="sign loop" style="min-width: 220px"><span>Säckel</span></span>{back('Приближённые', 'Users', ' loop')}</div>
  <div class="stack" style="gap: 10px; justify-content: center"><span class="caps">Новая запись дописывается пером</span>
    <table class="table" style="white-space: nowrap"><tbody><tr class="fresh"><td class="muted">05.10</td><td class="note-text">овощи на рынке</td><td class="num money">−1 240,00 ₽</td></tr>
    <tr><td class="muted">01.10</td><td>из казны</td><td class="num money">+8 000,00 ₽</td></tr></tbody></table></div>
  <div class="stack" style="align-items: center; gap: 8px; justify-content: center"><span class="caps">Мешок после траты</span><img class="squeeze" src="{ICONS['basket'][0]}" alt="" width="90" height="90" style="object-fit: contain"><span class="small muted">сжимается, звенят монеты</span></div>
  <div class="stack" style="gap: 10px; justify-content: center"><span class="caps">Лист книги: вперёд — влево, назад — вправо</span>
    <div class="framed turn-loop stack" style="gap: 4px"><h3 class="title t-3">Летопись</h3><span class="small muted">05.10 · Продукты · −1 240,00 ₽</span><span class="small muted">04.10 · Транспорт · −1 300,00 ₽</span></div></div>
</div>'''

empty_demo = f'''<div class="hof demo" style="width: 1440px; height: 560px; padding: 44px 60px; display: grid; justify-items: center; align-content: start">
  <div class="stack" style="gap: 12px; align-items: center"><span class="caps">Мешков пока нет — нажатие на кота: нюхает мешки (3 с, звук нюханья)</span>{vstack('empty_sk', ['sniff_1', 'sniff_2'], 'Кот обнюхивает пустые мешочки', 520, extra=' loop-sniff')}</div>
</div>'''

slide_demo = f'''<div class="hof slide-demo" style="width: 1440px; height: 900px">
  <div class="slide-a">{home_page(unroll=False)}</div>
  <div class="slide-b">{users}</div>
  <div class="veil"></div>
</div>'''

BOARDS = [  # файл, заголовок на холсте, x, y, w, h, разметка, заголовок страницы, витрина
    ('Main.dc.html', 'Вход', 0, 0, 1440, 900, login_page(), 'Hof — вход', False),
    ('Setup.dc.html', 'Основание двора', 1520, 0, 1440, 900, setup_page(), 'Hof — основание двора', False),
    ('Home.dc.html', 'Двор — наведение: вывеска качается; нажатие на вывеску или дверь: дверь открывается и вход', 3040, 0, 1440, 900, home_page(), 'Hof — двор', False),
    ('Users.dc.html', 'Приближённые — ключница', 4560, 0, 1440, 900, users, 'Hof — приближённые', False),
    ('User.dc.html', 'Приближённый — карточка', 0, 1020, 1440, 900, user, 'Hof — anna', False),
    ('Account.dc.html', 'Мои покои — анимации, звуки и музыка с громкостью', 1520, 1020, 1440, 900, account, 'Hof — мои покои', False),
    ('UsersEmpty.dc.html', 'Приближённые — пока только хозяин', 3040, 1020, 1440, 900, users_empty, 'Hof — приближённые', False),
    ('Saeckel.dc.html', 'Säckel — мешки и открытый мешок', 0, 2340, 1440, 900, saeckel, 'Säckel — мешки', False),
    ('SaeckelAssign.dc.html', 'Säckel — разложить по мешкам', 1520, 2340, 1440, 900, assign, 'Säckel — разложить', False),
    ('SaeckelHistory.dc.html', 'Säckel — летопись', 3040, 2340, 1440, 900, history, 'Säckel — летопись', False),
    ('SaeckelEmpty.dc.html', 'Säckel — мешков пока нет', 4560, 2340, 1440, 900, empty, 'Säckel — пусто', False),
    ('SaeckelForms.dc.html', 'Säckel — формы: доход с ошибкой ввода, переложить, мешок со знаком, запись', 0, 3360, 1440, 1120, forms, 'Säckel — формы', False),
    ('SaeckelHistoryEmpty.dc.html', 'Säckel — летопись пуста', 1520, 3360, 1440, 900, history_empty, 'Säckel — летопись пуста', False),
    ('LoginMobile.dc.html', 'Вход', 0, 4880, 390, 844, login_m, 'Hof — вход, телефон', False),
    ('SetupMobile.dc.html', 'Основание двора', 470, 4880, 390, 844, setup_m, 'Hof — основание, телефон', False),
    ('HomeMobile.dc.html', 'Двор', 940, 4880, 390, 844, home_m, 'Hof — двор, телефон', False),
    ('UsersMobile.dc.html', 'Приближённые', 1410, 4880, 390, 844, users_m, 'Hof — приближённые, телефон', False),
    ('UserMobile.dc.html', 'Приближённый', 1880, 4880, 390, 844, user_m, 'Hof — anna, телефон', False),
    ('AccountMobile.dc.html', 'Мои покои (вся страница)', 2350, 4880, 390, 1180, account_m, 'Hof — мои покои, телефон', False),
    ('ErrorMobile.dc.html', 'Ошибка 404', 2820, 4880, 390, 844, error_m, 'Hof — тропы нет, телефон', False),
    ('SaeckelMobile.dc.html', 'Säckel — мешки', 0, 6180, 390, 844, sk_m, 'Säckel — мешки, телефон', False),
    ('PouchMobile.dc.html', 'Säckel — мешок', 470, 6180, 390, 844, pouch_m, 'Säckel — мешок, телефон', False),
    ('HistoryMobile.dc.html', 'Säckel — летопись', 940, 6180, 390, 844, history_m, 'Säckel — летопись, телефон', False),
    ('AssignMobile.dc.html', 'Säckel — разложить', 1410, 6180, 390, 844, assign_m, 'Säckel — разложить, телефон', False),
    ('IncomeMobile.dc.html', 'Säckel — доход с ошибкой', 1880, 6180, 390, 844, income_m, 'Säckel — доход, телефон', False),
    ('PouchEditMobile.dc.html', 'Säckel — мешок со знаком (вся страница)', 2350, 6180, 390, 1180, pouch_edit_m, 'Säckel — мешок, телефон', False),
    ('SaeckelEmptyMobile.dc.html', 'Säckel — мешков пока нет', 2820, 6180, 390, 844, empty_m, 'Säckel — пусто, телефон', False),
    ('States.dc.html', 'Ошибка 404 — тропы нет', 0, 7780, 1440, 900, states, 'Hof — тропы нет', False),
    ('Error403.dc.html', 'Ошибка 403 — сюда только хозяину', 1520, 7780, 1440, 900, error403, 'Hof — только хозяину', False),
    ('Error500.dc.html', 'Ошибка 500 — что-то стряслось', 3040, 7780, 1440, 900, error500, 'Hof — что-то стряслось', False),
    ('DemoHome.dc.html', 'Витрина: двор — окно, дверь казначейской и вход в неё, дверь башни; знамёна, дым, птицы, кот', 0, 9100, 1440, 900, home_page(True), 'Витрина — двор', True),
    ('DemoSetup.dc.html', 'Витрина: «Основать двор» — ворота распахиваются, наезд, сцена темнеет', 1520, 9100, 1440, 900, setup_page(True), 'Витрина — основание', True),
    ('DemoLogin.dc.html', 'Витрина: «Войти во двор» — наезд в ворота, сцена темнеет', 3040, 9100, 1440, 900, login_page(True), 'Витрина — вход', True),
    ('DemoSlide.dc.html', 'Витрина: сдвиг по меню — двор уезжает влево и темнеет, Приближённые выезжают справа; назад — наоборот', 4560, 9100, 1440, 900, slide_demo, 'Витрина — сдвиг', True),
    ('DemoEmpty.dc.html', 'Витрина: пустая страница мешков — кот нюхает мешки', 1520, 10120, 1440, 560, empty_demo, 'Витрина — пустая страница мешков', True),
    ('DemoSmall.dc.html', 'Витрина: знамя разворачивается, сундук, дверь, ключ, печать, кот, вывеска, «назад», запись, мешок, лист', 0, 10120, 1440, 900, small_demo, 'Витрина — мелочи', True),
]


def stale():
    """Файлы, которые экраны и стили используют, но на холст не загружены или изменились."""
    for c in ('screens.css', 'demo.css'):
        css_for_canvas(c)                       # отметить картинки из стилей в USED
    out = [p for p in sorted(USED) if p not in TABLE or TABLE[p]['sha'] != sha(p)]
    for c in ('screens.css', 'demo.css'):
        h = hashlib.sha256(css_for_canvas(c).encode()).hexdigest()[:16]
        if c not in TABLE or TABLE[c]['sha'] != h:
            out.append(c)
    return out


if MODE == 'check':
    todo = stale()
    print('\n'.join(todo) if todo else 'всё загружено')
elif MODE == 'record':
    path, blob = sys.argv[2], sys.argv[3]
    TABLE[path] = {'id': blob, 'sha': hashlib.sha256(css_for_canvas(path).encode()).hexdigest()[:16] if path.endswith('.css') else sha(path)}
    json.dump(TABLE, open(TABLE_PATH, 'w', encoding='utf-8'), indent=1, sort_keys=True)
    print('записано', path)
elif MODE == 'css':
    open(sys.argv[3], 'w', encoding='utf-8').write(css_for_canvas(sys.argv[2]))
    todo = [p for p in stale() if not p.endswith('.css')]
    print('не загружены:', todo) if todo else print('ok')
elif MODE == 'boards':
    todo = stale()
    if todo:
        sys.exit('сначала загрузить: ' + ', '.join(todo))
    P = sys.argv[2]
    for name, _, _, _, w, h, body, title, demo in BOARDS:
        open(f'{P}/{name}', 'w', encoding='utf-8').write(page(title, w, h, body, demo))
    c = json.load(open(f'{P}/canvas.json', encoding='utf-8'))
    removed = [k for k in c['boards'] if k not in {b[0] for b in BOARDS}]
    c['boards'] = {name: {'x': x, 'y': y, 'w': w, 'h': h, 'title': t, 'is_interactive': True, **({'radius': 24} if w == 390 else {})}
                   for name, t, x, y, w, h, *_ in BOARDS}
    c['order'] = [b[0] for b in BOARDS]
    c['notes'] = {
        't1': {'kind': 'title1', 'maxW': 6000, 'text': 'Hof — компьютер', 'x': 0, 'y': -300},
        't2': {'kind': 'title1', 'maxW': 6000, 'text': 'Säckel — компьютер', 'x': 0, 'y': 2040},
        't3': {'kind': 'title1', 'maxW': 3300, 'text': 'Телефон — Hof и Säckel', 'x': 0, 'y': 4580},
        't4': {'kind': 'title1', 'maxW': 4480, 'text': 'Ошибки', 'x': 0, 'y': 7480},
        't5': {'kind': 'title1', 'maxW': 6000, 'text': 'Анимации — витрина (крутятся сами)', 'x': 0, 'y': 8800},
    }
    json.dump(c, open(f'{P}/canvas.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print('boards', len(BOARDS), 'removed', removed)
elif MODE == 'preview':
    D = os.path.join(HERE, 'preview')
    os.makedirs(D, exist_ok=True)
    GROUPS = [('Hof — компьютер', (0, 1020)), ('Säckel — компьютер', (2340, 3360)), ('Телефон', (4880, 6180)), ('Ошибки', (7780,)),
              ('Витрина анимаций — крутятся сами, как на холсте', (9100, 10120))]
    for name, t, _, _, w, h, body, title, demo in BOARDS:
        open(os.path.join(D, name.replace('.dc.html', '.html')), 'w', encoding='utf-8').write(page(title, w, h, body, demo))
    sections = []
    for gname, ys in GROUPS:
        cards = []
        for name, t, _, y, w, h, *_ in BOARDS:
            if y not in ys:
                continue
            fn = name.replace('.dc.html', '.html')
            tw = 300 if w > 400 else 150
            cards.append(f'<a class="card" href="{fn}"><span class="thumb" style="width: {tw}px; aspect-ratio: {w} / {h}">'
                         f'<iframe src="{fn}" loading="lazy" tabindex="-1" title=""></iframe></span><span>{t}</span></a>')
        sections.append(f'<h2>{gname}</h2><div class="cards">{"".join(cards)}</div>')
    open(os.path.join(D, 'index.html'), 'w', encoding='utf-8').write(f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Hof — прототип</title>
<link href="{FONTS}" rel="stylesheet">
<style>
  body {{ margin: 0; background: #F7EFE0 url(../generated/paper-tile.webp); color: #14243D; font: 19px/1.45 'EB Garamond', Georgia, serif; }}
  main {{ max-width: 1360px; margin: 0 auto; padding: 36px 32px 60px; }}
  h1, h2 {{ font-style: italic; font-weight: 500; margin: 0; }} h1 {{ font-size: 46px; }} h2 {{ font-size: 30px; margin: 40px 0 14px; }}
  .how {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 10px 36px; max-width: 1100px; margin-top: 10px; }}
  .how p {{ margin: 0; }} a {{ color: #1F4E9E; }}
  .cards {{ display: flex; flex-wrap: wrap; gap: 26px 22px; align-items: flex-start; }}
  .card {{ display: flex; flex-direction: column; gap: 6px; width: min-content; color: inherit; text-decoration: none; font-size: 16px; line-height: 1.3; }}
  .card:hover > span:last-child {{ color: #1F4E9E; text-decoration: underline; }}
  .thumb {{ display: block; box-sizing: content-box; padding: 7px; overflow: hidden; border: 2px solid transparent; border-image: url(../pen/pen-panel.svg) 16 fill / 16px stretch; background: #2E2A24; }}
  .thumb iframe {{ display: block; width: 100%; height: 100%; border: 0; pointer-events: none; }}
  .card:hover .thumb {{ border-image-source: url(../pen/pen-pick.svg); }}
  .fx-set {{ display: flex; flex-wrap: wrap; gap: 6px 22px; font-weight: 600; }} .fx-set input {{ width: 18px; height: 18px; vertical-align: -3px; accent-color: #1F4E9E; }}
  .warn {{ grid-column: 1 / -1; padding: 12px 18px; border: 2px solid transparent; border-image: url(../pen/pen-note-error.svg) 16 fill / 16px stretch; color: #A83224; }}
</style></head>
<body><main>
<h1>Hof — живой прототип</h1>
<div class="how">
  <p class="warn" id="file-warn" hidden>Прототип открыт прямо с диска — так браузер не переносит настройки между экранами, и звука не будет.
    Закройте эту вкладку и откройте прототип двойным щелчком по файлу «Открыть прототип.command» в папке design/preview.</p>
  <p>Начните со <a href="Main.html">входа</a> или <a href="Setup.html">основания двора</a> и дальше ходите по ссылкам, как на сайте. Экран вписывается в окно целиком.</p>
  <p>Анимации, звуки и музыка включаются в <a href="Account.html">«Моих покоях»</a> — у нового человека всё выключено. Для прототипа их можно включить и здесь:</p>
  <p class="fx-set"><label><input type="checkbox" data-setting="anim"> анимации</label><label><input type="checkbox" data-setting="sound"> звуки</label><label><input type="checkbox" data-setting="music"> музыка</label></p>
  <p>Формы ничего не сохраняют. «Записать трату» в Säckel показывает, как новая строка дописывается и мешок сжимается.</p>
  <p>Все звуки и музыку по отдельности можно послушать на <a href="../sounds/listen.html">странице звуков</a>. Миниатюры ниже — без движения и звука.</p>
</div>
{"".join(sections)}
</main>
<script>if (location.protocol === 'file:') document.getElementById('file-warn').hidden = false;</script>
<script src="../fx.js" data-base="../"></script>
</body></html>
''')
    print('preview', len(BOARDS), D)

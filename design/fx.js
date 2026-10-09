// Hof — эффекты: анимации, звуки, музыка. Прототип будущего /static/fx.js.
// Без этого файла всё работает: ссылки и формы обычные. Настройки — в localStorage этого браузера,
// у нового пользователя всё выключено. Системное «уменьшить движение» выключает анимации.
(() => {
  'use strict';
  const root = document.documentElement;
  const BASE = document.currentScript?.dataset.base ?? '/static/';
  const FRAMED = window !== window.top;    // миниатюра в обзоре прототипа: без движения и звука
  const DEFAULTS = { anim: false, sound: false, soundVol: 80, music: false, musicVol: 50 };
  const MUSIC = 20;                       // общий список: music-1 … music-20
  const POOLS = { door: 6, chest: 3, coins: 2, banner: 4, page: 2, wind: 6, meow: 9, purr: 1, sniff: 3 };
  const ACTS = {                           // сценки по нажатию: класс с кадрами на виньетке и звуки по времени (мс)
    sniff: { cls: 'sniffing', sounds: [[0, 'sniff'], [1850, 'sniff']] },   // кот нюхает пустые мешки, 3 с
  };
  const FOUNTAINS = 3;
  const DUCK = 0.63;                       // −4 дБ музыки на время звука

  const store = {
    get(area, key, fallback) { try { return JSON.parse(area.getItem(key)) ?? fallback; } catch { return fallback; } },
    set(area, key, value) { try { area.setItem(key, JSON.stringify(value)); } catch { /* приватный режим */ } },
  };
  const cfg = { ...DEFAULTS, ...(FRAMED ? {} : store.get(localStorage, 'hof.fx', {})) };
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const anim = () => cfg.anim && !reduced;
  const vol = (v) => Math.max(0, Math.min(1, v / 100));
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const replay = (el, cls) => { el.classList.remove(cls); void el.offsetWidth; el.classList.add(cls); };
  const all = (sel) => (sel ? document.querySelectorAll(sel) : []);
  root.classList.toggle('fx-off', !anim());

  // ---------- звуки: случайный вариант из набора, без повтора подряд; вернёт запись (или null) ----------
  const last = {};
  function play(name) {
    const n = POOLS[name];
    if (!cfg.sound || !n) return null;
    let i;
    do { i = 1 + Math.floor(Math.random() * n); } while (n > 1 && i === last[name]);
    last[name] = i;
    const a = new Audio(`${BASE}sounds/${name}-${i}.m4a`);
    a.volume = vol(cfg.soundVol);
    a.play().catch(() => {});
    duck();
    return a;
  }

  // ---------- музыка: один список на все экраны; при переходе продолжается с того же места ----------
  let track = null;
  let duckTimer = 0;
  const musicLevel = () => vol(cfg.musicVol) * (duckTimer ? DUCK : 1);
  function duck() {
    if (!track) return;
    clearTimeout(duckTimer);
    duckTimer = setTimeout(() => { duckTimer = 0; fade(track, musicLevel(), 600); }, 900);
    fade(track, musicLevel(), 120);
  }
  const fading = new WeakMap();            // у каждой записи — только последнее затухание
  function fade(a, to, ms) {
    const from = a.volume, t0 = performance.now(), id = {};
    fading.set(a, id);
    const step = (t) => {
      if (fading.get(a) !== id) return;
      const k = Math.min(1, (t - t0) / ms);
      a.volume = Math.max(0, Math.min(1, from + (to - from) * k));
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }
  // браузер не даёт звуку начаться без действия человека — тогда запись начнётся с первого нажатия
  function begin(a, then, alive) {                        // alive() — запись всё ещё нужна (её не выключили)
    a.play().then(then).catch(() => {
      const go = () => { removeEventListener('pointerdown', go); removeEventListener('keydown', go); if (alive()) a.play().then(then).catch(() => {}); };
      addEventListener('pointerdown', go); addEventListener('keydown', go);
    });
  }
  function startMusic() {
    if (!cfg.music || FRAMED || track) return;
    const saved = store.get(sessionStorage, 'hof.music', null);           // где остановились на прошлой странице
    let i = saved ? saved.i % MUSIC : Math.floor(Math.random() * MUSIC);   // новый визит — со случайной пьесы
    const open = (at, fadeMs) => {
      track = new Audio(`${BASE}sounds/music/music-${i + 1}.m4a`);
      track.volume = 0;
      track.currentTime = at;
      track.dataset.i = i;
      track.addEventListener('ended', () => { i = (i + 1) % MUSIC; track = null; open(0, 1500); });
      const t = track;
      begin(t, () => fade(t, musicLevel(), fadeMs), () => track === t);
    };
    open(saved?.t ?? 0, saved ? 400 : 1500);                             // продолжение — почти без паузы
  }
  function stopMusic() { if (track) { const t = track; track = null; fade(t, 0, 400); setTimeout(() => t.pause(), 450); } }
  addEventListener('pagehide', () => {
    if (track) store.set(sessionStorage, 'hof.music', { i: Number(track.dataset.i), t: track.currentTime });
  });

  // ---------- фонтан: тихая петля на дворе; при каждом заходе — следующая запись ----------
  let water = null;
  function startFountain() {
    if (!cfg.sound || water || !document.querySelector('.fx-fountain')) return;
    const visit = store.get(localStorage, 'hof.fountain', 0);
    store.set(localStorage, 'hof.fountain', visit + 1);
    water = new Audio(`${BASE}sounds/fountain-${(visit % FOUNTAINS) + 1}.m4a`);
    water.loop = true;
    water.volume = 0;
    const w = water;
    begin(w, () => fade(w, vol(cfg.soundVol), 2000), () => water === w);
  }
  function stopFountain() { if (water) { const w = water; water = null; fade(w, 0, 400); setTimeout(() => w.pause(), 450); } }

  // ---------- редкие события: порыв ветра в одном дереве, стайка птиц над двором ----------
  function sometimes(fn, min, max) {
    const next = () => setTimeout(() => { if (anim() && !document.hidden) fn(); next(); }, min + Math.random() * (max - min));
    next();
  }
  const leaves = [...document.querySelectorAll('.fx-leaves')];
  if (leaves.length) {
    sometimes(() => { replay(leaves[Math.floor(Math.random() * leaves.length)], 'gust'); play('wind'); }, 14000, 40000);
  }
  const flock = document.querySelector('.fx-birds');
  if (flock) {
    flock.addEventListener('animationend', (e) => { if (e.target === flock) flock.classList.remove('fly'); });
    sometimes(() => flock.classList.add('fly'), 20000, 70000);
    setTimeout(() => { if (anim()) flock.classList.add('fly'); }, 4000 + Math.random() * 6000);
  }

  // ---------- переходы между сценами ----------
  // «в дверь»: дверь открывается → наезд к проёму → темнота → новая страница проявляется из темноты;
  // «сдвиг»: сцена уезжает влево (вперёд) или вправо (назад) и темнеет, новая выезжает навстречу;
  // «лист»: страница переворачивается, как в книге (вперёд — уходит влево, назад — прошлая ложится обратно).
  // Как появиться новой странице, решает fx-head.js по флагу hof.arrive — до первой отрисовки.
  // Лист рисует сам браузер (View Transitions между страницами): видны сразу обе страницы.
  // Где браузер этого не умеет, вместо листа — сдвиг в ту же сторону.
  const FLIP = 'onpagereveal' in window;
  document.body.append(Object.assign(document.createElement('div'), { className: 'veil' }));
  function aim(spot) {
    const s = spot.getBoundingClientRect();
    const x = s.left + s.width / 2, y = s.top + s.height / 2;
    for (const z of document.querySelectorAll('.zoom')) {     // в процентах: верно и при масштабе страницы
      const r = z.getBoundingClientRect();
      z.style.transformOrigin = `${((x - r.left) / r.width) * 100}% ${((y - r.top) / r.height) * 100}%`;
    }
  }
  async function enter(href, spot, opener) {
    play('door');
    if (!anim()) { await sleep(cfg.sound ? 250 : 0); location.href = href; return; }
    aim(spot);
    opener?.classList.add('open');
    await sleep(550);                                     // дверь открывается 0,7 с, наезд начинается чуть раньше
    root.classList.add('enter');
    store.set(sessionStorage, 'hof.arrive', { fx: 'door' });
    await sleep(1150);
    location.href = href;
  }
  async function move(href, dir, keepBanner, el) {
    const flip = dir.startsWith('flip');
    if (flip && FLIP && anim()) {                         // звук листа — на новой странице, вместе с переворотом
      root.classList.add(dir); store.set(sessionStorage, 'hof.arrive', { fx: dir }); location.href = href; return;
    }
    play(flip ? 'page' : el.dataset.sound);
    if (!anim()) { await sleep(cfg.sound && (flip || el.dataset.sound) ? 250 : 0); location.href = href; return; }
    if (flip) dir = dir === 'flip-back' ? 'right' : 'left';
    const door = el.querySelector('.frames');
    if (door) { door.classList.add('open'); await sleep(600); }            // дверь открывается 0,75 с
    store.set(sessionStorage, 'hof.arrive', { fx: dir, banner: keepBanner });
    root.classList.add(dir === 'left' ? 'go-left' : 'go-right');
    if (keepBanner) root.classList.add('keep-banner');
    await sleep(500);
    location.href = href;
  }
  if (store.get(sessionStorage, 'hof.unroll', false)) {
    sessionStorage.removeItem('hof.unroll');
    if (anim() && document.querySelector('.banner')) {
      document.querySelector('.hof')?.classList.add('fx-enter');
      play('banner');
      setTimeout(() => play('banner'), 600);              // разворот 1,2 с — два шороха ткани подряд
    }
  }
  // лист переворачивается сейчас (0,75 с): звук листа; потом класс снять — он не должен влиять на следующий переход
  if (root.matches('.flip-fwd, .flip-back')) { play('page'); setTimeout(() => root.classList.remove('flip-fwd', 'flip-back'), 1000); }
  // «Назад» в браузере возвращает страницу из памяти как была — уже затемнённой; вернуть как было
  addEventListener('pageshow', (e) => {
    if (!e.persisted) return;
    root.classList.remove('enter', 'arrive', 'go-left', 'go-right', 'keep-banner', 'flip-fwd', 'flip-back');
    for (const el of document.querySelectorAll('.open')) el.classList.remove('open');
  });

  // ---------- клики ----------
  document.addEventListener('click', (e) => {
    if (e.metaKey || e.ctrlKey || e.shiftKey) return;     // в новой вкладке — без эффектов
    const scene = e.target.closest('[data-act]');
    if (scene) {
      const act = ACTS[scene.dataset.act];
      for (const [ms, name] of act.sounds) setTimeout(() => play(name), ms);
      if (anim()) replay(scene.closest('.vstack'), act.cls);
      return;
    }
    const cat = e.target.closest('.cat');
    if (cat) {                                            // поза держится, пока звучит звук
      const a = play(cat.dataset.sound || 'meow');
      const show = (sec) => { cat.style.setProperty('--pose', `${Math.max(0.9, sec + 0.3).toFixed(2)}s`); replay(cat, 'meow'); };
      if (a) { a.addEventListener('loadedmetadata', () => show(a.duration), { once: true }); a.addEventListener('error', () => show(1.2), { once: true }); } else show(1.2);
      return;
    }
    const place = e.target.closest('.place');
    if (place) { e.preventDefault(); enter(place.href, place.querySelector('.lit') ?? place, place); return; }
    const moving = e.target.closest('[data-fx]');
    if (moving) {          // data-fx = left | right (сдвиг) | flip-fwd | flip-back (лист); data-keep — знамя на месте
      e.preventDefault();
      if (!moving.matches('[aria-current]')) move(moving.href ?? moving.dataset.go, moving.dataset.fx, moving.dataset.keep !== undefined, moving);
      return;
    }
    const go = e.target.closest('[data-go]');
    if (go) {
      e.preventDefault();
      if (go.dataset.unroll !== undefined) store.set(sessionStorage, 'hof.unroll', true);
      const spot = document.querySelector(go.dataset.spot || '');
      if (spot) enter(go.dataset.go, spot, document.querySelector(go.dataset.opens || '') ?? null);
      else { play(go.dataset.sound); setTimeout(() => { location.href = go.dataset.go; }, cfg.sound && go.dataset.sound ? 250 : 0); }
      return;
    }
    const act = e.target.closest('[data-sound], [data-fresh], [data-squeeze]');
    if (act) {
      play(act.dataset.sound);
      const lid = act.querySelector(':scope > .frames');    // сундук Казны: нажатие открывает, следующее закрывает
      if (lid && anim()) lid.classList.toggle('open');
      // в прототипе показывает то, что на сайте сервер отметит после записи: новую строку и сжатый мешок
      if (anim()) { for (const el of all(act.dataset.fresh)) replay(el, 'fresh'); for (const el of all(act.dataset.squeeze)) replay(el, 'squeeze'); }
    }
  });

  // ---------- настройки в «Моих покоях» ----------
  for (const input of document.querySelectorAll('[data-setting]')) {
    const key = input.dataset.setting;
    const out = input.parentElement.querySelector('output');
    if (input.type === 'checkbox') input.checked = cfg[key]; else input.value = cfg[key];
    if (out) out.value = `${cfg[key]} %`;
    input.addEventListener('input', () => {
      cfg[key] = input.type === 'checkbox' ? input.checked : Number(input.value);
      if (out) out.value = `${cfg[key]} %`;
      store.set(localStorage, 'hof.fx', cfg);
      root.classList.toggle('fx-off', !anim());
      if (key === 'music') (cfg.music ? startMusic() : stopMusic());
      if (key === 'musicVol' && track) track.volume = musicLevel();
      if (key === 'sound') (cfg.sound ? startFountain() : stopFountain());
      if (key === 'soundVol') { if (water) water.volume = vol(cfg.soundVol); play('coins'); }
    });
  }

  startMusic();
  startFountain();
})();

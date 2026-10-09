// Hof — до первой отрисовки страницы: какой переход ждёт её после прошлой (флаг оставляет fx.js).
// Подключается в <head> обычным скриптом: класс на <html> должен появиться раньше, чем браузер
// нарисует страницу, — иначе мелькнёт сцена без анимации. Без файла страница просто появляется.
(() => {
  try {
    const arrive = JSON.parse(sessionStorage.getItem('hof.arrive'));
    sessionStorage.removeItem('hof.arrive');
    const fx = JSON.parse(localStorage.getItem('hof.fx')) ?? {};
    if (!arrive || !fx.anim || window !== window.top || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    // дверь — проявиться из темноты; сдвиг — выехать навстречу; лист — переворот страницы
    const cls = { door: 'arrive', left: 'from-right', right: 'from-left', 'flip-fwd': 'flip-fwd', 'flip-back': 'flip-back' }[arrive.fx];
    if (cls) document.documentElement.classList.add(cls);
    if (arrive.banner) document.documentElement.classList.add('keep-banner');
  } catch { /* приватный режим: просто без перехода */ }
})();

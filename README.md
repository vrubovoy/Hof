# Hof

Небольшой набор веб-приложений для себя, семьи или небольшой группы людей на своём сервере.
Что это и зачем — [PRODUCT.md](PRODUCT.md), как устроено — [ARCHITECTURE.md](ARCHITECTURE.md).

## Разработка

Нужен Node.js 24.12 или новее и npm. Сборки нет: Node запускает `.ts` напрямую, удаляя типы.

```sh
npm ci          # зависимости строго по package-lock.json
npm run dev     # сервер на http://localhost:3000, перезапуск при изменении файлов
npm run check   # prettier --check, eslint, tsc --noEmit, node --test
npm run format  # отформатировать всё через prettier
```

`npm run check` должен проходить перед каждым коммитом.

Код сервера — в `src/`, тесты лежат рядом с кодом (`*.test.ts`). В TypeScript допустим только
синтаксис, который Node может просто стереть: без `enum`, `namespace` с кодом, parameter
properties и декораторов (ARCHITECTURE.md §7) — `tsc` такие конструкции отклоняет.

`design/` — утверждённый визуальный эталон и исходники картинок и звуков, а не код сервера.

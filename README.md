# Hof

Небольшой набор веб-приложений для себя, семьи или небольшой группы людей на своём сервере.
Что это и зачем — [PRODUCT.md](PRODUCT.md), как устроено — [ARCHITECTURE.md](ARCHITECTURE.md).

## Разработка

Нужны Node.js 24.12 или новее с npm и Docker с Compose (на macOS — например, colima).
Сборки нет: Node запускает `.ts` напрямую, удаляя типы.

Один раз — конфигурация и база для разработки:

```sh
cp .env.example .env && chmod 600 .env   # заполнить пароли: openssl rand -hex 24
docker compose -f compose.dev.yaml up -d # PostgreSQL 18 на 127.0.0.1:5433
```

Контейнер создаёт базы `hof` (для `npm run dev`) и `hof_test` (для тестов), роли `hof_core` и
`hof_saeckel` и их схемы — скриптом `deploy/postgres-init.sh`. Скрипт выполняется только на
пустом томе; после его изменения том пересоздают:

```sh
docker compose -f compose.dev.yaml down -v && docker compose -f compose.dev.yaml up -d
```

Порт 5433 выбран, чтобы не мешать локально установленному PostgreSQL на 5432. Сервер и тесты
находят его через стандартную переменную `PGPORT` из `.env`.

```sh
npm ci          # зависимости строго по package-lock.json
npm run dev     # сервер на http://localhost:3000, перезапуск при изменении файлов
npm run check   # prettier --check, eslint, tsc --noEmit, node --test
npm run format  # отформатировать всё через prettier
```

`npm run check` должен проходить перед каждым коммитом; тестам нужна запущенная база.

При старте сервер применяет новые миграции (`src/<модуль>/migrations/NNN_*.sql`) к базе `hof` и
только потом открывает порт. Тесты работают с `hof_test` и выполняются последовательно.

Код сервера — в `src/`, тесты лежат рядом с кодом (`*.test.ts`). В TypeScript допустим только
синтаксис, который Node может просто стереть: без `enum`, `namespace` с кодом, parameter
properties и декораторов (ARCHITECTURE.md §7) — `tsc` такие конструкции отклоняет.

`design/` — утверждённый визуальный эталон и исходники картинок и звуков, а не код сервера.

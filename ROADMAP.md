# Hof Platform — Roadmap

Local planning note, survives across sessions on disk (not part of any
service's own git history). Full history was compressed out of this file
on 2026-08-04 — git log / closed issues+PRs/milestones in each repo are
the source of truth for what happened and why.

## Services (all public under `zudaR107`, AGPL-3.0)

- `schlussel` — auth/SSO (Hono API, RS256 JWT/JWKS, PKCE, invites+admin panel)
- `schloss` — home page / launcher
- `kuvert` — envelope budgeting
- `tafel` — tasks/projects (kanban, calendar, recurrence)
- `zettel` — markdown notes (wiki-links + backlinks done; tags and a
  Ctrl+K quick switcher still pending)
- `tor` — Caddy reverse-proxy gateway, single entry point, no host ports
  published by any other service
- `schloss-ui` — shared React component library
- `schloss-server-kit` — shared backend auth/CORS kit

**Status**: platform foundation (auth, CI/Docker/GHCR, gateway, shared
design system, SSO) and all 5 app repos' core feature sets are done and
merged. The "small visual signature" pass (mascot illustration + sidebar
badge + one micro-animation per service) is also done for
schlussel/kuvert/tafel. Every backend now lives in `backend/` and every
frontend in `frontend/` (renamed from `api`/`web` platform-wide on
2026-08-04, including the `/backend/*` URL path itself — schlussel is the
one exception, no `backend/` dir of its own, backend at repo root).
Nothing in progress — every repo's only open PRs are Dependabot.

## Standing workflow (every stage)

- Milestone = umbrella of issues, not one-per-issue. One branch per
  milestone, one PR per repo from it into `main`.
- Labels: this repo's own `type:feat/fix/chore/test/docs` — check
  `gh label list` first, never assume.
- Project board `PVT_kwHOBhrZh84BctmC`, Status field
  `PVTSSF_lAHOBhrZh84BctmCzhXUW3s` (Todo `f75ad846` / In Progress
  `47fc9ee4` / Done `98236657`) — every issue/PR added, kept current.
- A fresh subagent with no implementation access writes tests from a
  behavioral spec; a separate docs agent updates README/OpenAPI when the
  API surface changes.
- Local git identity per repo must be `zudaR107 <zudin_daniil@mail.ru>`
  (check `.git/config`, not just global) — otherwise GitHub injects a
  Co-Authored-By trailer on squash-merge.
- PR: Conventional Commits title, `Closes #N`, same label/assignee/board
  status as its issue(s); merge via `gh pr merge` once CI is green;
  verify the merge commit has no Co-Authored-By line.
- After merge: delete the branch, set board items to Done, close the
  milestone.

## Future roadmap (recorded 2026-08-04, all open questions resolved interactively with the user the same day)

Raw list of 10 items from the user, structured into dependency order.
Nothing below is started — this is intent, not status.

1. **Zettel quick wins**: browser-tab favicon; a minimal-text `/help`
   page now, screenshots deferred to the hardening phase.
2. **Zettel feature expansion**: virtual folders on top of tags (saved
   filters) — independent of the future file-storage service, doesn't
   need to wait on phase 4, moved earlier than originally sketched for
   that reason. Optional ideas on top, pick freely: graph view of the
   wiki-link network, note templates, trash/restore, attachments, md/PDF
   export, daily notes, pinned notes, better search ranking. Tags +
   Ctrl+K quick switcher already pending from M3 regardless of this list.
3. **Remaining architecture + cross-cutting foundation services**: i18n
   via `react-i18next`, set up once in schloss-ui, rolled out everywhere
   later (phase 5); notification service - in-app center + browser push
   + a Telegram bot as the mobile channel (a native/PWA mobile app is a
   separate, later, unscheduled idea), built as an event bus every other
   service emits through; profile settings folded into schlussel's
   existing `/account` rather than a new service (avatar, language,
   timezone, theme, date format, week-start, notification prefs,
   privacy, connected accounts, data export). Before phase 4 so new
   services can hook into notifications/settings from day one.
4. **New content services**: file storage (Drive-like - real nested
   folders, not tags; preview limited to images + PDF via browser-native
   rendering, no office-doc/video preview; no sharing/permissions in v1 -
   single-user platform, add only if actually needed later) and a mail
   client (a webmail UI for existing external IMAP/SMTP accounts, not a
   self-hosted mail server/MTA).
5. **Platform ops/infrastructure**: a new standalone, minimal, near-
   dependency-free **bootstrap installer** service - the very first thing
   deployed on a bare server, before schlussel even exists, since nothing
   else can host a web UI yet at that point. Presents a full web UI
   (chosen deliberately over a CLI/TUI wizard) to configure then provision
   the platform: pick which services to enable, fill in their config,
   write one `services.yml`, then run one idempotent Ansible playbook
   that reconciles the server to match it. Once the platform is up,
   ongoing service management (add/remove/reconfigure later) moves into a
   "Services" tab in schlussel's `/admin` panel, reusing the exact same
   `services.yml` + Ansible playbook as the bootstrap installer - one
   source of truth, two front doors (a temporary bootstrap-only one, and
   the permanent in-platform one). Also: localization string-extraction
   across every service (last, once the service list/UI is stable) +
   the shared language-switcher component in schloss-ui, next to
   ThemeToggle; tag-push deploy automation for the real server - simple
   pull+restart of the one changed container, deliberately not
   rolling/zero-downtime (not worth the complexity for a single-user
   personal platform).
6. **Mobile testing**: a dedicated pass once the feature/UI surface is
   stable across all services.
7. **Per-service hardening -> v1.0.0**: explicitly last, explicitly
   user-led — manual testing, help screenshots, code cleanup, dev docs,
   one service at a time.
8. **Real server deployment**: after hardening.

## Repo locations

`/home/zudar/Sandbox/Hof/{schlussel,schloss,kuvert,tafel,zettel,tor,schloss-ui,schloss-server-kit}/`
— same names at `https://github.com/zudaR107/<name>`. This directory
itself is the `Hof` meta-repo (docs + submodule pins only, no CI, no
branch protection).

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
- `zettel` — markdown notes (wiki-links/backlinks, tags, virtual tag
  folders, quick switching, pinning, archive/restore, and scoped export)
- `glocke` — durable in-app notification center and transactional delivery
  foundation (API `3004`, frontend development server `5177`)
- `tor` — Caddy reverse-proxy gateway, single entry point, no host ports
  published by any other service
- `schloss-ui` — shared React component library
- `schloss-server-kit` — shared backend auth/CORS kit

**Status as of 2026-08-17**: platform foundation (auth, CI/Docker/GHCR,
gateway, shared design system, SSO) and the five established app repos' core
feature sets are merged; Glocke's notification foundation is the sixth app
repo. The small visual-signature pass (service-specific
illustration, badge, and motion details where applicable) is complete
across all five apps: schloss, schlussel, kuvert, tafel, and zettel.

Full-stack consumer apps use `backend/` and `frontend/`. There are two
repository-layout exceptions: schloss is frontend-only and keeps its
frontend at the repo root; schlussel keeps its backend at the repo root and
its frontend in `frontend/`. The `/backend/*` URL rename is separate from
those source-directory layouts.

The platform stabilization milestone is merged across every repository. It
includes profile-aware date controls and formatting, modal/focus/theme
fixes, regional JWT claims and validation, PATCH-capable CORS, end-to-end
regional-preference propagation through kuvert/tafel/zettel, scoped service
exports, archive/restore corrections, API/OpenAPI and auth/config fixes,
transaction/task integrity fixes, and gateway routing/TLS corrections. The
Hof submodule pins record the tested compatible set. This milestone is not
the later screenshot or v1 hardening pass.

The platform-wide data-export milestone is merged. It retains each service's
direct JSON export and adds standardized `/exports/me` snapshots plus
Schlüssel's asynchronous, delegated all-services ZIP jobs with partial-success
manifests, retries, expiring private artifacts, and storage/user quotas.

The notification producer rollout is complete for the seven registered events:
`schlussel.security.password_changed.v1`, `kuvert.goal.completed.v1`,
`kuvert.debt.paid_off.v1`, `kuvert.envelope.overdrawn.v1`,
`tafel.task.due.v1`, `tafel.project.completed.v1`, and
`zettel.note.backlink_added.v1`. The debt/envelope/project events (2026-08-19)
follow the same "milestone transition, computed fresh from current state, no
stored notified-flag" shape as the original goal/task events - envelope
overdrawn is the trickiest of the three (period-scoped "available" crossing
zero, deliberately excluding bulk CSV import as a non-real-time path).
Producers use transactional retained outboxes with bounded retries; Glocke
provides idempotent duplicate intake, central registry validation/rendering,
current-preference-at-processing-time suppression, and trusted Kuvert/Tafel
action origins. Tafel
keeps a separate due-occurrence ledger across outbox retention, and the four
producer directions plus Glocke's Schlüssel lookup use five distinct secrets.

The shared header bell and unread-state rollout is also complete. All
authenticated application headers use the shared controlled bell, exact unread
state, auth-safe refresh, active-page polling, focus/connectivity recovery, and
same-origin/cross-tab invalidation. Glocke applies private cache headers and an
exact platform CORS allowlist at its outer HTTP boundary; Tor supplies one
validated browser-facing Glocke origin to every frontend build.

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

## Roadmap in dependency order

Originally recorded 2026-08-04; status reconciled with the checked-out
implementations on 2026-08-18.

1. **Zettel quick wins and expansion — done**: favicon, minimal text help,
   tags, Ctrl+K/Cmd+K quick switching, minimal virtual folders as tag
   shortcuts, pinning, archive/restore, and Zettel-scoped JSON export are
   implemented. Help screenshots remain deferred. Unscheduled optional
   ideas remain graph view, templates, attachments, md/PDF export, daily
   notes, and better search ranking.
2. **Cross-cutting foundation — partly done**: schloss-ui's shared
   `react-i18next` foundation is merged; app string rollout and a shared
   language switcher are pending. Schlussel `/account` now provides
   profile/avatar, session timeout, regional preferences, notification
   preference storage, connected-account status, and service-scoped JSON
   export. Platform-wide asynchronous ZIP export is implemented and merged
   across all data-bearing services. Timezone/date-format/week-start
    propagation to consumers is implemented end to end. Glocke now provides the
    durable in-app notification and transactional-delivery foundation, and all
    four current producer services are connected to it.
3. **Notification rollout — in-app and Browser Push done**: Glocke's
   foundation, the four-producer event rollout, the shared authenticated
   header bell with unread state, and Browser Push (Glocke-owned VAPID keys,
   subscriptions, retry worker, and service worker; Schlüssel owns only the
   global on/off switch) are all complete and merged. Disabled by default -
   an operator sets `GLOCKE_BROWSER_PUSH_ENABLED` and a generated VAPID
   keypair to turn it on. The Telegram bot and account-linking flow remain
   the one still-unscheduled future phase, as does iOS/PWA installation
   (this rollout supports desktop and Android).
4. **New content services — not started**: Drive-like file storage with
   real nested folders and browser-native image/PDF preview; and a webmail
   client for external IMAP/SMTP accounts, not a mail server/MTA. Sharing,
   permissions, office/video preview, and other expansion stay outside v1
   unless a concrete need appears.
5. **Platform operations — not started**: a standalone bootstrap installer
   web UI, the shared `services.yml`, its idempotent Ansible reconciliation
   playbook, the later Schlussel `/admin` Services front door, and tag-push
   deployment automation. The installer remains the first bare-server
   component; installer and admin UI must use the same file and playbook.
   Deployment remains simple pull-and-restart, not rolling or zero-downtime.
6. **Localization rollout — pending**: extract and translate app strings
   after the service/UI surface is stable, then expose the shared language
   switcher. The library foundation alone does not make any app bilingual.
7. **Mobile testing — not started**: dedicated cross-service pass after the
   feature and localization surface stabilizes. A native/PWA app remains a
   separate unscheduled idea.
8. **Per-service hardening and v1.0.0 — not started**: explicitly last and
   user-led, one service at a time: manual testing, help screenshots, code
   cleanup, developer docs, and release hardening. Current stabilization
   must not be counted as this phase.
9. **Real-server deployment — not started**: follows v1 hardening.

## Repo locations

`/home/zudar/Sandbox/Hof/{schlussel,schloss,kuvert,tafel,zettel,glocke,tor,schloss-ui,schloss-server-kit}/`
— same names at `https://github.com/zudaR107/<name>`. This directory
itself is the `Hof` meta-repo (docs + submodule pins only, no CI, no
branch protection).

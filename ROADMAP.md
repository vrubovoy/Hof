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
- `schrank` — file storage with nested folders (API `3005`, frontend
  development server `5178`) - **complete** (2026-08-20): folders,
  upload/download/rename/move/delete, quota, its own wardrobe mascot, a
  gallery-grid file browser with bounded viewport-lazy thumbnails, and
  full in-app preview (image/PDF/markdown/text) - PDF renders via
  client-side pdf.js into a real page thumbnail plus a bespoke
  near-fullscreen viewer dialog, markdown through the same
  react-markdown/remark-gfm pipeline Zettel uses. The shared Glocke
  bell is wired up like every service's header - Schrank just doesn't
  emit any notification events of its own yet (same as Zettel).
  Sharing/permissions are deliberately deferred, same standing as the
  Telegram bot/account-linking flow - not blocking, revisit later
- `herold` — webmail client for external IMAP/SMTP accounts (API `3006`,
  frontend development server `5179`) - **complete** (2026-08-21):
  account management, read-only IMAP sync, compose/send, message
  actions/search, a metadata-only export, and its own mascot (a paper
  airplane, after two earlier concepts didn't read clearly), bootstrapped
  through all six staged-rollout stages and a live-testing polish round
  the same day
- `wachter` — server resource monitoring (API `3007`, no frontend of its
  own) - **complete** (2026-08-25): auxiliary/infrastructure service, not
  a content app - backend-only, no `DIENSTE` launcher card, no accent
  color. Reports host CPU/memory/disk/uptime and per-container Docker
  status/CPU/memory through a separately hardened host agent. The web API
  has no Docker socket or host-root mount; the agent exposes only fixed,
  authenticated operations and label-gated restart. Sampled every 5s
  (down from an initial 30s, after
  live-testing feedback that the widget felt static); three in-memory
  history tiers per metric (raw 5s/1h, 1min-rollup/24h, 1hr-rollup/7d,
  no database) back an hour/day/week range selector on the detailed
  stats pages. Surfaced as an admin-only widget on Schloss's home page
  (stat tiles, sparklines, a live "N of M containers active" line),
  reached same-origin via Schloss's own Caddyfile at `/wachter/*` - not
  a `tor` subdomain. Every clickable area on the widget leads deeper,
  all hosted inside Schloss's own frontend since Wächter has none:
  `/server-stats` (full graphs + the container list), `/server-stats/
  :name` (one container's own graphs plus a restart action - admin-only,
  confirmation-gated, cooldown-protected, and limited to explicitly
  restartable non-critical containers),
  and `/server-stats/docs` (its Swagger UI). First new repo created
  after the GitHub account rename (`zudaR107` → `vrubovoy`); its own
  URLs use `vrubovoy` throughout since it has no legacy alias to
  redirect from.
- `tor` — Caddy reverse-proxy gateway, single entry point, no host ports
  published by any other service
- `schloss-ui` — shared React component library
- `schloss-server-kit` — shared backend auth/CORS kit

**Status as of 2026-08-25**: platform foundation (auth, CI/Docker/GHCR,
gateway, shared design system, SSO) and the five established app repos' core
feature sets are merged; Glocke's notification foundation is the sixth app
repo, Schrank (file storage) is the seventh - bootstrapped 2026-08-19
and declared **complete** the next day, after a full in-app preview pass
(image/PDF/markdown/text, gallery-grid thumbnails, breadcrumb trail
navigation that keeps the visited path visible instead of truncating it,
and illustrated loading/error states) on top of its initial folders/
files/quota/mascot v1 - and Herold (webmail client) is the eighth,
bootstrapped 2026-08-21 and declared **complete** the same day, after
all six stages of its staged rollout (mail account management,
read-only IMAP folder/message sync, compose/send, message
actions/search/exports, and a cross-service docs pass) plus a
live-testing polish round: localized connection/send error messages
(was leaking raw English library text), an SMTP-security default that
now follows the IMAP side's own choice, a sender-email field that
auto-follows the IMAP login (most providers reject a mismatch), the
account list rebuilt as clickable cards, a real `.inline-error` style
(was referenced but never defined, so error banners rendered
unstyled), an SMTP socket timeout (nodemailer's own default is
effectively unbounded - a stalled send could hang for minutes), and a
`Modal` body-scroll-lock fix upstreamed into schloss-ui itself (a tall
dialog showed two adjacent scrollbars). A connected account's mail is
browsable, a new message/reply/reply-all/forward can be sent through
it, and read/unread, flag/star, delete, and search are all in place.
Wächter (server resource monitoring) is the ninth repo and the
platform's first auxiliary/infrastructure service rather than a
content app - bootstrapped and declared **complete** 2026-08-25:
backend-only (no frontend, no launcher card, no accent color), it
reports host CPU/memory/disk/uptime and per-container Docker status
through an admin-only widget embedded directly into Schloss's home
page, with no database of its own. The small visual-signature pass (service-specific illustration, badge,
and motion details where applicable) is complete across all seven apps
that have one: schloss, schlussel, kuvert, tafel, zettel, Schrank, and
now Herold - whose own mascot took three attempts (a scroll+wax-seal
and a herald's horn both read as an unrelated object once actually
rendered; a paper airplane finally landed) - not yet extended to
Glocke, which has none.

Browser Push is now complete (central Glocke-owned service worker, VAPID
config, exact current-device registration, session-bound cleanup on logout,
leased delivery retention, and a header-bell pop-up toast on new arrivals).
The Telegram bot and account-linking flow
are explicitly **deferred** (user decision 2026-08-19) - revisit after
the phases below, not blocking any of them. The notification event
catalog also grew this pass (Kuvert's `debt.paid_off`/`envelope.overdrawn`,
Tafel's `project.completed`), and the shared header bell/sidebar got a
round of polish: hover-preview dropdown with mark-read/clear-all/delete-all,
avatar rendering, relative-actionUrl resolution, and a `Sidebar` component
shared by kuvert/tafel/zettel/glocke (was independently hand-copied by the
first three; Glocke now has full parity instead of a visibly different rail).

The 2026-08-25 platform hardening release closed the cross-service audit.
Herold now enforces outbound public-address policy with explicit operator
exceptions, mandatory STARTTLS semantics, bounded mail ingestion, mirror
reconciliation, sent-message deduplication, and UI pagination. Schrank now
uses atomic quota reservations, a durable filesystem operation queue, and
bounded thumbnail fetching. Schlüssel's archive includes metadata snapshots
from all seven data owners, while retained older jobs keep their historical
five-service manifest. Account deletion is a durable, audience-bound saga
across every data service. Wächter isolates host authority in its narrow
agent, and GHCR publication is gated on successful tests under the current
`vrubovoy` namespace.

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
implementations on 2026-08-17 and 2026-08-18, then again on 2026-08-19
(Browser Push landed, Telegram explicitly deferred, Schrank bootstrapped),
2026-08-20 (Schrank declared complete), and 2026-08-21 (Herold
bootstrapped, taken through all six stages of its staged rollout, and
declared complete after a live-testing polish round - the same day).

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
3. **Notification rollout — done except Telegram (deferred)**: Glocke's
   foundation, the producer event rollout (now 7 registered events across
   Schlüssel/Kuvert/Tafel), the shared authenticated header bell with
   unread state, and Browser Push (Glocke-owned VAPID keys, subscriptions,
   retry worker, and service worker; Schlüssel owns only the global on/off
   switch; per-device registration; pop-up toast on new arrivals) are all
   complete and merged. Push is disabled by default - an operator sets
   `GLOCKE_BROWSER_PUSH_ENABLED` and a generated VAPID keypair to turn it
   on; it supports desktop and Android, not iOS/PWA installation. The
   Telegram bot and account-linking flow are **explicitly deferred** (user
   decision 2026-08-19) - not scheduled next; revisit after phase 4 or
   later, whenever it's picked back up.
4. **New content services — both complete**:
   `schrank` (new repo, 2026-08-19) is a Drive-like file storage service,
   declared **complete** 2026-08-20: real nested folders (create/rename/
   move with cycle-detection/recursive delete), file upload/download/
   rename/move/delete, a per-file and per-account storage quota with a
   usage bar in Settings, a metadata-only export, a gallery-grid file
   browser with eager per-file-type thumbnails, and full in-app preview
   for image/PDF/markdown/text - PDF via client-side pdf.js (a real
   page-content thumbnail plus a bespoke near-fullscreen viewer dialog,
   since the shared Modal's caps are deliberately sized for forms, not
   documents), markdown through the same react-markdown/remark-gfm
   pipeline Zettel uses. Breadcrumb navigation keeps the full visited
   trail on screen when stepping back instead of truncating it. The
   shared Glocke bell is wired up like every service's header - Schrank
   just doesn't emit any notification events yet (same as Zettel).
   Sharing, permissions, office/video preview, and other expansion stay
   outside Schrank's v1 unless a concrete need appears later.

   `herold` (new repo, 2026-08-21) is a webmail client for external
   IMAP/SMTP accounts (explicitly not a mail server/MTA), declared
   **complete** the same day it was bootstrapped: platform wiring,
   mail account management, read-only IMAP sync, compose/send,
   message actions/search/exports, and the cross-service docs pass
   (all six stages of its staged plan) shipped first, followed by a
   live-testing polish round against a real Yandex account that fixed
   raw-English error leakage, an SMTP-security default mismatched from
   IMAP's own choice, an undefined `.inline-error` style, an
   effectively-unbounded SMTP send timeout, a sender-email field that
   didn't follow the IMAP login (most providers reject a mismatch), an
   edit-only-via-small-pencil-icon account list (rebuilt as clickable
   cards), a favicon that was a shrunk mascot copy instead of the real
   service glyph, and the mascot itself (two earlier concepts didn't
   read clearly once rendered; a paper airplane did). herold now
   appears in the platform-services list of every sibling repo's own
   README (schloss, schlussel, kuvert, tafel, zettel, schrank, tor,
   schloss-ui, schloss-server-kit - glocke already had it), and a
   pre-existing gap from its original bootstrap was found and fixed
   along the way - `tor`'s own `.env.example`/`.env.production.example`
   and CI workflow were missing `HEROLD_CREDENTIAL_ENCRYPTION_KEY`
   entirely (the real `tor/.env` already had it set, so the running
   deployment was unaffected; only the example files and CI validation
   were out of sync). Account management:
   connect/edit/disconnect an external account (`/accounts` CRUD), a
   "test connection" round-trip against the real IMAP server before
   saving (`imapflow`, mocked in tests - never a real network call in
   CI), passwords encrypted at rest (AES-256-GCM,
   `HEROLD_CREDENTIAL_ENCRYPTION_KEY`). Sync: a background worker
   (`sync/worker.ts`, `HEROLD_SYNC_INTERVAL_MS`, default 3 minutes)
   mirrors every account's IMAP folders and messages into the local
   database - first-time sync, incremental new-UID fetch, a flags-only
   refresh pass for already-mirrored messages, UIDVALIDITY-reset
   re-sync, and per-account failure isolation. The `/mail` page (now
   what `/` redirects to) reads that mirror: account switcher, folder
   sidebar, message list, message detail. Attachments are never
   mirrored - `GET /messages/:id/attachments/:attachmentId` streams
   them live from IMAP on request, a fresh connection per download.
   Compose/send: `POST /accounts/:accountId/messages/send` sends via
   nodemailer using the account's own SMTP settings, with a compose
   modal (new/reply/reply-all/forward, prefilled recipient/subject/
   quoted body/In-Reply-To) and a best-effort mirror of the sent
   message into the local database and the real Sent folder (IMAP
   APPEND) once one has been discovered by sync - never required for
   the send itself to succeed. Actions/search/exports: `PATCH
   /messages/:id` (read/unread, flag/star - writes through to IMAP
   before updating the local mirror) and `DELETE /messages/:id`
   (IMAP `MOVE` to Trash, imapflow's own RFC 6851 fallback to
   COPY+EXPUNGE included, or a permanent delete in place when no Trash
   folder is known locally yet); a `q` search param on the folder
   message list (SQL LIKE across subject/sender/body); a metadata-only
   `GET /exports/me` (account labels/hosts, folder names, message
   counts - never credentials or message content) behind Schlüssel's
   export-delegation auth. Design decisions already
   settled: multiple external accounts per user; username/password (or
   app-password) auth only for v1, no OAuth; mirrors message headers
   and plain-text body locally, never raw HTML bodies (sidesteps
   stored-XSS/sanitization entirely for v1 - HTML-only emails show
   mailparser's stripped-text fallback).
5. **Platform operations — in progress (item 9 of 18 done, item 10 next, PRs #48-58 - applied-mode reconciliation, ADR 0005: item 8's own plan-v2/durable-lock/journal/event/signed-EE/action-whitelist foundation (PRs #24-47, six closure calls, five premature - see below) extended to cover an already-applied installation for real, not just a fresh bootstrap - config/topology/drift reconciliation, retain-only removal of a persistent service (`dataRetention: retain`, its volume/schema carried forward for a later re-enable, never deleted, never backed up - backup/restore stays item 10's own scope), a genuine applied no-op that takes no lock and creates no journal, `installationId` permanent forever, generation strictly `N -> N+1` on a real change; release/schema/image upgrades on an existing unit stay explicitly out of scope (items 10-11). PRs #48-52 the executor/planner/Ansible-role work itself; #53-54 a new signed Execution Environment (`ee-v0.1.4`) and signed platform release (`v0.2.0`), both independently re-verified the same way every prior EE/release has been; #55 a real CI-only disposable-target acceptance run - bootstrap, enable an optional persistent service, write a real marker into its own real volume, an applied no-op, disable-with-retain, another no-op, re-enable - genuinely green end to end, the retained volume and its marker surviving the whole round trip byte for byte, every immutable per-generation snapshot confirmed present and schema-valid. Independent review (five rounds against PRs #48-55, PR #57) then went through the Required Gate this item's own Definition of Done actually demands - merge, a new signed EE, a new signed platform release, real `test:apply-ssh` acceptance required fully green against it - which itself caught three further genuine bugs no static review had: a Compose network-lifecycle race (external `hof`/`wachter-internal` networks, Ansible as sole owner), an operation-ordering deadlock (dependency-aware topological sort of `service.start`/`readiness.wait`), and a real Docker-socket-gid `EACCES` behind Wächter's own persistent `/ready` 503 (the target's own real gid discovered and passed as `DOCKER_GID`, not guessed at). Each forced its own new signed EE/release (`ee-v0.1.5`/`v0.2.1` → `ee-v0.1.6`/`v0.2.2` → `ee-v0.1.7`/`v0.2.3`) on PR #58; final real acceptance against `v0.2.3` genuinely green (11/11 SSH transport, 4/4 apply-acceptance scenarios), PR #58 merged with no waiver. Given item 8's own five-premature-closures history, treat this as the currently-best-verified state, not a guarantee; item 10 (backup/restore) next. Item 8's own full six-call history: PRs #24-30's initial close missed nine bootstrap/apply blockers, fixed by #31-37 with a genuinely full, live, disposable-VM `hofctl apply` run; that close missed eight more invariants including two real crash windows, fixed by #38-41 with a new signed EE `ee-v0.1.2` and platform release `v0.1.3`; that close missed seven more gaps including two more Critical ones, fixed by #42-45 with a new signed EE `ee-v0.1.3` and platform release `v0.1.4`; that close missed six more gaps - real lock/journal creation atomicity, a genuine releaseLock() compare-and-delete race, event/plan-order validation, a discarded lock-release check on the normal commit path, the succeeded fast path still skipping live validation, and a deployment-file TOCTOU - fixed by #46; THAT close missed two more real gaps - atomicExclusiveCreateStep()'s own fixed temp filename was itself a corruption path (a crashed prior invocation's orphaned hard link let a later one silently overwrite an already-live lock via a shared inode) and cross-step event-order validation still only checked for gaps, not the raw stream's own actual order - fixed by #47 (again JS-only, no new EE/release, the atomicity fix specifically re-verified against a real executing shell script); see `PLATFORM-OPS-PLAN.md`'s "Item 8, fifth review" log entry for the full story)**: a
   standalone bootstrap installer web UI, the shared
   `services.yml`, its idempotent Ansible reconciliation playbook, the later
   Schlussel `/admin` Services front door, and tag-push deployment
   automation. The installer remains the first bare-server component;
   installer and admin UI must use the same file and playbook. Deployment
   remains simple pull-and-restart, not rolling or zero-downtime.
   User-authored recommended plan for this phase (new `hof-ops` repo,
   release-lock/signed-image supply chain, `hofctl`, Ansible reconciliation,
   restic backup/restore, upgrade/rollback, claim-token admin bootstrap,
   installer UI, later `hof-opsd` + `/admin/services`) recorded 2026-08-25
   in [`PLATFORM-OPS-PLAN.md`](PLATFORM-OPS-PLAN.md). Scope review is
   resolved; the `hof-ops` contract foundation (published, branch-protected)
   and portable runtime frontend images (all eight frontends + Tor
   validation) are merged. Backend `*_FILE` secrets and explicit migrations
   are also merged, in every database-backed backend plus wachter's agent
   token. Platform registries are now topology-aware too: Glocke no longer
   requires Kuvert/Tafel's origins at startup, Schlüssel's export/deletion
   sagas skip disabled services instead of failing against them, and every
   frontend (Schloss's launcher grid and all eight frontends' shared
   notification bell) hides UI for a service with no configured URL. Every
   image-publishing repo (all except Tor, which ships no custom image) now
   signs published digests with keyless Cosign, attests an SPDX SBOM and
   SLSA build provenance, and publishes an immutable `vX.Y.Z` release tag
   that refuses to be overwritten - fixed two latent CI bugs along the way
   (kuvert/glocke/zettel/tafel were publishing ungated and to the
   pre-rename `zudaR107` GHCR namespace). `hof-ops` resolves and signs a
   real release lock too - `hof-ops render` (new: services.yml + catalog +
   lock → Compose/Caddyfile/env/backup inventory, the piece that lets
   `services.yml` actually drive a deployment) and a real integration
   matrix (renders topology fixtures against the pinned lock and runs
   `docker compose up --wait` against the result) landed alongside it.
   A review of items 3-6 found several real gaps behind those checkmarks
   twice over - once in the code, once again in the release pipeline
   itself once it was actually run for real rather than only unit-tested -
   and every one was fixed and re-verified, not just noted: a secret
   still bypassing `resolveSecret` in Schrank; production migrations
   invoking a devDependency CLI absent from the built image; startup
   defaulting to auto-migrate instead of schema-check-only; missing
   readiness/build-info endpoints, plus readiness never checking the
   mandatory Schlüssel JWKS dependency (only its own database) anywhere,
   with two recurring test-fidelity bugs found while landing that fix
   (reconstructed `/ready` stubs and mock databases that never populated
   `__drizzle_migrations`); shipped Compose files re-enabling every
   "disabled" service via default URLs, including a genuinely missing
   `GLOCKE_BASE_URL` in Tor that broke Glocke delivery outright;
   Schlüssel still requiring Glocke's secrets unconditionally; CI
   accepting non-semver release tags; the release lock resolving
   `:latest` and never actually running `cosign verify`; Wächter's
   generated topology being broken (undefined port, wrong agent command,
   missing hardening/labels); and six more bugs the hardened integration
   matrix caught only once it started real containers for the first
   time (a cosign/GitHub-attestation incompatibility, release-pinned
   topology fixtures, a missing rendered Caddyfile, a too-short shared
   placeholder secret, Glocke needing real P-256 VAPID key material, and
   a wrong Docker-socket GID for Wächter's agent). The result is a
   genuine signed release built from real platform state end to end:
   [`v0.1.1`](https://github.com/vrubovoy/hof-ops/releases/tag/v0.1.1)
   (the earlier `v0.1.0`, built under the pre-hardening pipeline, stays
   published as a historical artifact). Delivery item 7 (`hofctl
   validate/preflight/plan`) is now fully landed: `hofctl validate`
   checks a real deployment's services.yml/catalog/release-lock at
   arbitrary paths (not just the repo's own examples) against schema
   and cross-contract rules, plus four checks the final hardening
   review named explicitly - `catalogDigest`/`composeTemplateDigest`
   freshness, `minimumHofctlVersion` compatibility, and the release
   lock's own Cosign signature (now a real gate in the release pipeline
   itself, exercised against a live signature on every release run, not
   just unit-tested). `hofctl preflight` runs the Ansible role's own
   disk/RAM/CPU/clock → DNS → ports → Docker checks standalone,
   fails closed on anything it can't verify (e.g. a privileged port
   without root) rather than assuming pass. `hofctl plan`'s state/diff
   design is decided and its pure core is landed: a hybrid model (an
   authoritative last-applied state file drives the desired diff, live
   Docker observation drives an independent drift diff), a synthetic
   empty baseline on a truly clean host, and fail-closed refusal - not
   automatic adoption - when state is missing but Docker already holds
   managed resources. `buildPlan()` computes typed, ordered operations
   (twelve action types, never a shell string) across bootstrap/no-op/
   topology-change/drift/upgrade, with migrations now keyed to the
   release lock's own per-component schema version instead of the
   `MIGRATE_ON_STARTUP` env flag apps used to self-trigger on every
   boot. A second review pass hardened that core further: config-only
   changes (domain/CORS/browserPush/TLS/backup-schedule) now register
   even with no image change, Wächter's API and its agent are tracked as
   two distinct units instead of collapsing into one, manual drift
   blocks a plan by default instead of only warning, migration
   operations carry their own argv/volume, upgrade migrations verify the
   baseline's schema and back up before running, and "the inspector
   couldn't reach the host" is now a distinct, explicit state instead of
   defaulting to "nothing is running". A `TargetInspector` is landed too:
   a single fixed, read-only, versioned probe script plus a hardened SSH
   transport (exactly one of a known_hosts file or a verified host-key
   fingerprint required, real OpenSSH SHA256 fingerprinting, `--target-
   mode local` only ever explicit) - real transport tested against a
   genuinely ephemeral, pinned Debian 12 sshd container in CI, not just
   mocked. `hofctl preflight` now checks `target.host`/`target.user` for
   real (the bug above is fixed) as pure evaluation over that inspector's
   snapshot. A follow-up security review before wiring `hofctl plan` in
   found (and closed) a critical OpenSSH option-injection gap plus ten
   further real gaps - Docker/state inspection failures no longer look
   like "nothing's there", port/managed-resource ownership checks the
   actual installation ID, the protocol is now fully fail-closed, and a
   real plan-contract bug (a routine generation bump alone would have
   made every unit look changed) is fixed. Orphan Hof-managed volume/
   network detection was deferred there, then landed for real in a
   follow-up pass together with ten more concrete gaps: every Compose
   volume/network is now labeled and probed the same fail-closed,
   one-bad-inspect-taints-the-batch way containers already were;
   `buildPlan` drift matching is scoped by installation ID, not a bare
   label match, so a second Hof installation sharing a host can't mask
   or be mistaken for this one's own resources; disabling a service now
   backs up its volume exactly once per service (was once per removed
   unit) and actually removes the container, not just stops it;
   generated-file checksums (collected but unused since the previous
   pass) now drive real repair/blocker drift, including a Caddyfile
   regeneration correctly forcing the gateway to restart; a missing
   persistent volume is a hard blocker, never silently recreated empty,
   while a missing network safely self-heals. **Item 7 closes with the
   real `hofctl plan` CLI itself**: its own subcommand (a new
   `scripts/plan-command.mjs`) wires every already-landed piece together
   end to end - validates the deployment exactly like `hofctl validate`
   does (never skippable, unlike `validate`), inspects the target
   exactly once, explicitly refuses to plan against an incomplete
   observation on both a bootstrap and an already-applied host (closing
   a real gap `buildPlan`/`resolveBaseline` alone didn't cover for an
   applied host), resolves the baseline, renders the desired topology in
   memory with the correct installation/generation semantics (a fixed,
   deterministic placeholder installationId on bootstrap - never a fresh
   random one, so two back-to-back plans against the same untouched host
   stay identical), and prints exactly one `plan-v1` JSON document to
   stdout, diagnostics only on stderr, exit code 0/1/2 for executable/
   blocked/usage-error. Verified through a real (fake) `cosign` binary
   on `PATH` so the release-lock signature gate genuinely runs, and one
   genuine end-to-end bootstrap plan through the real CLI binary itself
   (real `sh` + `target-probe.sh` + a fake docker/sudo pair + fake
   cosign, real schema validation, a real `buildPlan()` call). Operation
   journal, lock, stale-plan recheck, and `apply` remain the next
   delivery items, explicitly out of scope for item 7. A small gate-7
   errata pass then closed four concrete post-review issues without
   reopening the design: Cosign now verifies the exact release-lock
   bytes already read into memory (pinned into a temp file) rather than
   a fresh, possibly-mutated re-read of the same path; a generated file
   that exists but couldn't be hashed even with sudo is now a distinct
   "unreadable" status, never folded into "missing" (which would have
   let the planner silently regenerate a file that wasn't actually
   gone); a missing network plans as its own typed `network.ensure`
   action instead of a reused `volume.ensure`; and `hofctl validate`'s
   `--release-selection`/`--stable-channel` flags, previously silently
   dropped by a key-naming mismatch, are now actually wired through.

   **Item 8 (Ansible fresh install) is now underway.** Its first PR
   lands the apply execution contracts, per a new ADR: exact target
   binding (a plan is bound to the real accepted SSH host-key
   fingerprint from the same connection it was computed against, not
   just the caller's trust anchor - a key change invalidates it),
   explicit `--approve-plan-id` approval, bootstrap-only apply for this
   item (applied-mode reconciliation is item 9), a signed Ansible
   Execution Environment, a durable host lock that survives the
   invoking process dying, a durable operation journal that never
   records a secret, a stale-plan recheck under the lock, and safe
   bounded resume (an operation whose outcome can't be determined blocks
   resume rather than guessing). A new `plan-v2` contract wraps the
   unchanged `plan-v1` diff engine with that target binding, planning
   policy, per-image trust policy pulled from the release lock, and the
   bootstrap-only recovery age recipient / supplied-TLS fingerprint -
   deliberately not wired into the real CLI yet, since `hofctl apply`
   doesn't exist to consume it. `inspectTarget()` now returns the real
   accepted host-key fingerprint in both trust modes (parsed from a real
   `ssh -v` transcript, cross-checked against an independent
   `ssh-keygen` computation in the real SSH acceptance suite). Docker
   genuinely not being installed is now its own distinct "absent" state,
   never confused with "unavailable" - a fresh host with no Docker yet
   is a legitimate bootstrap candidate, and `hofctl preflight` now says
   so instead of falsely reporting Docker unreachable. Three new schemas
   for the operation journal/event/lock and a pure bootstrap-action
   whitelist round out the contract.

   **Item 8 closed.** Secret-safe Compose rendering landed first - every
   real platform secret (inter-service HMAC secrets, Glocke's VAPID
   key, Herold's/Wächter's own secrets) now flows through Compose's
   native `secrets:` mechanism via a `<VAR>_FILE` convention every
   consuming app already implements, sourced from a SOPS-encrypted
   workstation store (`hofctl secrets ensure`) with a mandatory external
   `age` recovery recipient. A pinned, digest-locked Ansible Execution
   Environment followed - its own ten roles (one per plan operation
   phase) started as a skeleton enforcing each operation's real variable
   contract, then got their real implementation: `host` bootstraps
   python3 and installs Docker only when genuinely absent; `secret`
   delivers decrypted values over the real SSH/SFTP connection, never
   through extra-vars or the journal; `volume`/`network` create
   Hof-labeled Docker resources matching the renderer's own labels;
   `image` runs a real keyless `cosign verify` (delegated to the control
   node, never the target) for signed components and trusts third-party
   images by digest pin alone; `config` delivers the rendered Compose/
   Caddy/env files; `database` runs each service's own migration via
   `docker compose run`, reusing its already-rendered definition;
   `service` starts one Compose unit, scoped with `--no-deps`;
   `readiness` polls the real container state by its own Compose
   ownership labels; `state` atomically commits `current.json`/
   `topology.json` (topology first, matching the corruption check the
   baseline resolver already enforces). `hofctl apply` itself ties all
   of this together: it recomputes the plan itself (never trusts one
   handed to it), requires an exact `--approve-plan-id` match, verifies
   the Execution Environment's own signature, acquires a durable target
   lock, re-verifies the target under that lock before running anything,
   dispatches only the bootstrap action whitelist into the Execution
   Environment (never local Ansible, never a generic command), and
   supports safe bounded resume - a step whose outcome can't be
   determined from the journal blocks resume rather than guessing. A
   real installation-id bug surfaced and got fixed along the way: every
   real resource was being labeled with the same fixed placeholder
   `hofctl plan` also uses for its own approval-matching computation,
   which would have made two separate bootstraps indistinguishable to
   later drift detection - real dispatch now renders a second time,
   after the lock is held, with a real, unique id. The whole pipeline is
   exercised for real in CI against a genuinely ephemeral, systemd-
   enabled target container (real Docker install, real secret delivery,
   real volume creation, then a real, expected failure at the first
   illustrative image reference) - a real incident during that work
   (a privileged, host-namespace-sharing test container briefly
   disrupted a real desktop session during local development) narrowed
   local iteration to read-only checks from then on, with CI itself
   - a genuinely disposable VM - doing the real verification instead.
   `ee-v0.1.0` has been cut for real and independently re-verified
   (signature, SBOM and provenance attestations all genuinely present).

   **Item 8 reopened (2026-08-28).** That closure call was premature. A
   review against the exact merged pins found nine concrete blockers in
   item 8's own bootstrap/apply scope - two Critical ones independently
   re-verified against the code: `hofctl plan` still prints `plan-v1`
   while `hofctl apply` independently requires approval of a different,
   richer `plan-v2` document, so a real `plan` run's ID can never satisfy
   `--approve-plan-id`; and `apply --resume` runs the ordinary bootstrap-
   baseline check before ever reading the lock/journal, so it necessarily
   refuses to resume after the exact case it exists for - a real mutation
   (a created volume/network/container) that happened before
   `state.commit`. Seven more High-severity gaps (stale-EE detection on
   resume, supplied-TLS material never actually reaching the target, a
   possible permanently-wedged host after a successful commit whose own
   cleanup then fails, Docker-without-Compose not being fixed, no
   platform/architecture re-check right before mutation, the EE's own
   `ee-vX.Y.Z` tag not wired into the release-lock builder so no real
   signed platform lock carries it yet, and the CI acceptance test
   stopping at the first expected image-pull failure rather than
   reaching config/migrate/start/readiness/commit) round it out. See
   `PLATFORM-OPS-PLAN.md`'s "Item 8 reopened" log entry for the full
   list and the three-PR stabilization plan (#31 approved-plan-and-resume,
   #32 complete-bootstrap-modes, #33 real-release-and-full-acceptance)
   that closes it for real. Applied-mode reconciliation (update/remove),
   backup/restore, upgrade/rollback, first-admin bootstrap, and the
   installer UI remain item 9 and later, unaffected by this reopening.

   **Item 8 closed for real (2026-08-28), PRs #31-37.** All nine
   findings fixed and independently re-verified: `hofctl plan` against a
   bootstrap target now prints the real `plan-v2` document `apply`
   itself checks byte for byte (recomputed twice, full document diff);
   resume reads the lock/journal first, always, never re-deriving a live
   baseline; supplied TLS is genuinely parsed/key-matched/validity- and
   SAN-checked and actually delivered to the target; the `host` role
   fixes Compose-without-Engine; `apply` re-verifies the exact supported
   platform on every live recompute; journal/lock reads are schema-
   validated; SSH `ProxyCommand`/`ProxyJump` are disabled outright;
   `build-release-lock.mjs` resolves the Execution Environment's real
   `ee-vX.Y.Z` tag correctly. A real `ee-v0.1.1` was cut baking in the
   PR #31/#32 fixes, then a real platform release `v0.1.2` - the first
   to carry a real Execution Environment - surfaced and fixed two more
   genuine bugs along the way (a fixture secret-file permission bug
   breaking Wächter's own non-root agent process; a real Docker-in-
   Docker overlay2-on-overlay2 kernel limitation in the test fixture
   itself). The result: a genuinely full, live, disposable-VM `hofctl
   apply` run - real signed release, real signed Execution Environment,
   real application images, real `database.migrate`/`service.start`/
   `readiness.wait`, a real generation-1 `state.commit` - confirmed
   afterward by a real second `hofctl plan` seeing an `"applied"`
   baseline, not `"bootstrap"`. See PLATFORM-OPS-PLAN.md's own "Item 8
   closed for real" log entry for the full account.

   **Item 8, second review (2026-08-28/31), PRs #38-41.** That closure
   call was also premature: a further line-cited review found eight more
   invariants still open, two of them genuine crash windows the "resume
   reads lock/journal first" fix hadn't actually covered (an event-append
   crash after a successful `state.commit`; a lock-release crash after
   a succeeded journal, which the resumability check then refused to
   ever recover from). Also found: resume trusted its own journal's
   embedded plan and events with no schema/planId/whitelist validation;
   `--plan` approval only checked a file's own `planId` field, never
   recomputed it from content; supplied TLS was re-read at delivery time
   with no comparison against the approved plan (a resume-only TOCTOU);
   the platform-support check never ran on resume; SSH proxy hardening
   was missing from the Ansible inventory specifically; and the
   real-target secret file mode (`root:root 0400`) was invisible to any
   non-root consuming container, a real case for Wächter's own `USER
   node` agent. All eight fixed and independently re-verified. The
   secret-mode fix required a new Execution Environment (`ansible/` is
   baked in at image-build time) - `ee-v0.1.2` was cut and independently
   re-verified, then a new signed platform release `v0.1.3` (reusing
   `v0.1.2`'s own app-component selections unchanged), then the full
   disposable-VM `hofctl apply` acceptance run repeated end to end
   against both, genuinely green in CI, with the secret-file mode
   assertion now checking `444` for real rather than the old `400`. See
   PLATFORM-OPS-PLAN.md's own "Item 8, second review" log entry for the
   full account.

   **Item 8, third review (2026-08-31), PRs #42-45.** That closure call
   was also premature: a further line-cited review found seven more
   gaps, two of them Critical. Fresh apply created the lock and the
   journal as two separate SSH round trips - a crash of the LOCAL apply
   process itself between them left a durable lock with no journal at
   all, which resume then had nothing to do but refuse forever; fixed
   via a single combined remote create (`acquireLockAndJournal()`), plus
   auto-recovery of that exact state on resume. The already-succeeded
   fast path silently discarded a real `releaseLock()` failure (a bare
   `.catch(() => {})`) and never even looked at a clean `{ released:
   false }` response either - reporting `blocked: false` regardless;
   fixed with a real release-confirmation check. Also found: resume's
   cross-binding validation was partial and, worse, entirely skipped by
   the succeeded fast path; the event-resumability check trusted any
   history containing a "succeeded" phase in any shape (a standalone one
   with no preceding "started" resolved identically to a genuine pair);
   post-commit recovery compared only two fields against the target's
   own `current.json`, not the full expected document; the journal
   schema's own documented status/committedGeneration invariant was
   prose-only; `computePlanId()` wasn't actually canonical despite its
   own name; the acceptance test's own journal/event assertions were
   still spot-checks, not real schema validation; and the ansible host
   role's own Docker-service-enable task silently skipped an
   already-installed-but-disabled service. All seven fixed and
   independently re-verified, same methodology as the two rounds before.
   The Docker-service fix again needed a new Execution Environment
   (`ee-v0.1.3`, independently re-verified) and a new signed platform
   release (`v0.1.4`, reusing `v0.1.3`'s own app-component selections
   unchanged), with the full disposable-VM acceptance run repeated end to
   end against both, genuinely green in CI. See PLATFORM-OPS-PLAN.md's
   own "Item 8, third review" log entry for the full account.

   **Item 8, fourth review (2026-08-31), PR #46.** That closure call was
   also premature: a further line-cited review found six more gaps,
   entirely JS/schema-side this time - no ansible role touched, no new
   Execution Environment or platform release needed. `acquireLockAndJournal()`
   wasn't actually atomic (a plain `>` redirection still exposed a
   truncated file during a mid-transfer crash) - fixed with a
   temp-file-then-`ln` pattern, reordered to create the journal first,
   then the lock. `releaseLock()`'s own grep-then-rm was a genuine
   compare-and-delete race - fixed with a shared target-side `flock`
   guard. The event-order check only counted phases per attempt, never
   physical append order, and nothing checked the plan's own dispatch
   order across steps - both fixed. The normal (non-resume) commit path
   discarded a real lock-release failure the same way the resume-side
   fast path used to, before the third review closed it there - fixed
   with the same check. The succeeded fast path still ran before
   platform/digest/host-key/event validation and never confirmed
   against the target's own real current.json/topology.json - fixed.
   And a real TOCTOU between parsing the deployment files and
   independently re-reading them a second time for digests - fixed by
   returning and reusing the bytes from the one read.

   All six fixed and, for the first time this round, independently
   re-verified against REAL running shell scripts, not just code
   reading or mocked unit tests: the actual generated lock/journal
   scripts were run against a scratch directory and killed mid-write in
   three different ways (final path never existed in any of them), and
   a genuine ~1.7s block was measured on a concurrent acquire attempt
   while a delayed release held the flock. 425/425 tests locally; one
   pre-existing, unrelated test flake fixed alongside it (a shared-OS-
   tmpdir snapshot race this round's own added test volume made far
   more likely to trip). See PLATFORM-OPS-PLAN.md's own "Item 8, fourth
   review" log entry for the full account.

   **Item 8, fifth review (2026-08-31), PR #47.** That closure call was
   also premature, though this round confirmed most prior findings
   genuinely fixed and found only two real gaps left, both entirely
   JS-side. `atomicExclusiveCreateStep()` reused a FIXED temp filename
   on every call - a prior invocation whose own `ln` succeeded but whose
   own `rm` never ran (a crash in exactly that gap) left the fixed tmp
   name and the real lock/journal as two hard links to the same inode;
   a LATER invocation's own write to that fixed name would then
   silently corrupt the already-live lock, even though its own `ln`
   would correctly refuse afterward - the damage was already done by
   then. The fourth round's own flock doesn't protect against this: the
   crashed process already released it. Reproduced for real both before
   fixing (an orphaned hard link manually left behind, a second attempt
   confirmed to corrupt the live lock) and after (the same scenario, now
   surviving untouched). Fixed with a genuinely unique `mktemp` name
   every call plus opportunistic cleanup of orphaned priors. Also found:
   cross-step event-order validation still only checked for gaps, not
   the raw stream's own actual order - a later step's events appearing
   entirely before an earlier step's, or two steps' events genuinely
   interleaved, both survived every prior check. Fixed by walking the
   raw stream once, requiring the previous step to already resolve to a
   genuine success before the next one may open.

   Both fixed and, for the atomicity fix, re-verified against a real
   executing shell script and a real scratch filesystem - reproducing
   the exact crash scenario, not just reading the code. 429/429 tests
   locally. See PLATFORM-OPS-PLAN.md's own "Item 8, fifth review" log
   entry for the full account.

   Given **five** closure calls on this one item, four of them
   premature, this is reported as the currently-best-verified state,
   not a guarantee - an even more careful, skeptical read is warranted
   before trusting it further, and before building item 9's own
   applied-mode reconciliation on this same journal/event/lock
   foundation.
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

`/home/zudar/Sandbox/Hof/{schlussel,schloss,kuvert,tafel,zettel,glocke,schrank,herold,wachter,tor,schloss-ui,schloss-server-kit}/`
— same names at `https://github.com/zudaR107/<name>`, except `wachter`
at `https://github.com/vrubovoy/wachter` (created after the account
rename, no legacy `zudaR107` alias). This directory itself is the `Hof`
meta-repo (docs + submodule pins and exact-pin integration CI).

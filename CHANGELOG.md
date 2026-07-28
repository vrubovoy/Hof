# Changelog

Brief log of notable changes to this meta-repo — submodule bumps and
cross-cutting docs updates, not the services' own changes (see each
submodule's own `CHANGELOG.md` for that).

## Setup
- Initial repo: submodules for schlussel, schloss, kuvert, tor; README,
  LICENSE, and the existing ROADMAP.md/docs/stages carried over from the
  pre-git planning directory.

## Submodule bumps
- Bumped all four submodules to their open-source presentation polish
  commits (license/CI badges, per-repo GitHub descriptions and topics,
  gateway repo URL fixes after its rename to lowercase, and
  `.env.production.example` in tor).
- Bumped all four submodules again: the gateway's project name is now
  written lowercase ("tor") everywhere in prose, not just in URLs/slugs.
- Bumped schlussel/schloss/kuvert to their Authorization Code + PKCE
  commits - the login handoff no longer puts the access token in a URL.
  Verified live end-to-end against the real running stack.
- Bumped all four submodules to their community-health-files commits
  (CODE_OF_CONDUCT.md, SECURITY.md, issue/PR templates); added the same
  two files here, and removed `docs/stages/` now that all 13 original
  stages are done - the ROADMAP.md table plus each linked issue/PR already
  carries what was worth keeping.
- Bumped schlussel/schloss/kuvert again: their docker-compose.yml default
  origins (`ALLOWED_ORIGINS`, `VITE_ALLOWED_RETURN_ORIGINS`,
  `VITE_SCHLUSSEL_URL`, `VITE_KUVERT_URL`, `VITE_DEFAULT_APP_URL`) still
  assumed `http://`, but tor's gateway auto-upgrades everything to HTTPS -
  broke the return_to allowlist and CORS for anyone actually running the
  real stack. Found live by the user testing through the gateway.
- Bumped schlussel/kuvert/tor once more: `ALLOWED_ORIGINS` was the same
  outer variable name in both schlussel's and kuvert's docker-compose.yml,
  so tor's one shared `.env` fed the same value into both, silently
  overriding kuvert-api's own CORS allowlist. Split into
  `SCHLUSSEL_ALLOWED_ORIGINS`/`KUVERT_ALLOWED_ORIGINS`.
- Bumped schlussel/schloss/kuvert for the user-feedback batch: shared
  session across services (`COOKIE_DOMAIN`, schlussel), unified
  Header/Footer + a redrawn hero illustration/favicon (schloss), a
  header/footer on the login/register pages (schlussel/web), and a
  resizable sidebar + visible user identity + onboarding copy (kuvert).
- Bumped schlussel again: `COOKIE_DOMAIN` didn't actually work
  (`localhost` has no dot, so browsers won't share a Domain-scoped
  cookie across its subdomains) - reverted it and replaced with silent
  re-authentication through schlussel's own same-origin session.
  Verified live end-to-end against the real running stack.
- Bumped schlussel/schloss/kuvert once more: reduced the visible flicker
  during the first-time SSO redirect chain by restoring the stored theme
  before first paint on every page load, instead of flashing the
  default theme first.
- Bumped kuvert once more: switching between its own tabs also
  flickered - each page fetched its own data only after mounting.
  Fixed with TanStack Router loaders prefetching each route's data
  before the transition completes.
- Bumped kuvert again: replaced the sidebar's toggle button with
  click-anywhere-empty-to-toggle, and fixed the Footer being clipped
  and unreachable on tall pages (a missing `min-height: 0` on a flex
  item) - found live, in a fresh private window, ruling out caching.
- Bumped kuvert and tor once more: fixed the sidebar reverting a
  just-completed drag-resize (a synthetic click bubbling to the
  click-to-toggle handler); added a header with a link back to
  schloss's home page and settings/logout access (tor's new
  `SCHLOSS_URL` env var feeds it); and fixed a build-breaking unused
  import that `pnpm test` didn't catch but `docker compose build` did.
- Bumped kuvert/schlussel/schloss once more: shortened the Budget and
  Accounts empty-state copy to match every other tab's one-sentence
  hint; also pinned `pnpm/action-setup`'s version exactly in CI across
  all three - an unrelated pnpm 11.12.0 release broke every workflow
  run regardless of what changed.
- Added a fifth submodule, `schloss-ui` - a new repo for the shared
  design-token/component package the other three will consume. Design
  decided and seven issues filed (milestone "Shared UI system") before
  any implementation - see ROADMAP.md for the full design rationale.
- Reworked the schloss-ui plan after a deeper, iterative design pass
  (an HTML draft, refined across three rounds) - deleted the original
  seven issues outright and replaced them with 13 concrete ones
  covering Header, cards/empty states, buttons, badges, filters,
  forms, modals, icons, number coloring, and a new toast pattern.
- Bumped schloss-ui to `v0.1.0`: all 8 of its own issues from that plan
  shipped (tokens, publish pipeline, Header/Footer/EmptyState, Button/
  Badge/SegmentedControl, Field/Modal, StatTile/Amount/Sparkline,
  Toast, icon docs), plus one hover-feedback fix found along the way.
  Tagged and published to GitHub Packages - the three consumer
  adoption issues (schloss, schlussel, kuvert) are next.
- Bumped schloss to its schloss-ui adoption commit: local Header/Footer/
  ThemeToggle button and hand-copied tokens replaced with the shared
  package, schloss's own purple accent layered on top. Also fixed a
  Docker build bug the rollout surfaced - `pnpm-workspace.yaml` (holding
  pnpm's own `minimumReleaseAgeExclude` entry for the freshly-published
  package) wasn't copied into the build context, so the container-side
  install fell back to the default supply-chain policy and rejected the
  recently-published dependency. schlussel and kuvert are next, and may
  hit the same Docker fix if their Dockerfiles have the same gap.
- Bumped schloss-ui to `v0.2.0`: added a `suffix` slot to `Field`
  (symmetric to `prefix` but interactive), needed for schlussel's
  password show/hide toggle - a real capability gap found during
  consumer adoption, fixed in the package rather than worked around
  locally.
- Bumped schlussel to its schloss-ui adoption commit: Header/Footer,
  Login/RegisterPage's form fields, and the submit buttons now use the
  shared package. Hit a second, repo-specific Docker build bug: this
  repo is a pnpm workspace, and `pnpm install --frozen-lockfile`
  fetches every package in the lockfile to verify it regardless of
  `--filter`, so even the API image's Dockerfile (which never uses
  schloss-ui) needed the same GitHub Packages auth wired in. kuvert is
  next.
- Bumped kuvert to its schloss-ui adoption commit (all three of its
  issues): Header/Footer/EmptyState/accent, buttons/badges/filters/
  numbers, and form fields/modals/toasts. The local `Modal` component
  is now deleted, replaced everywhere by the shared one; a new
  `useToast` hook wires up the shared `Toast` for the first real usage
  anywhere on the platform. Neither of the two Docker-auth bugs found
  in schloss/schlussel recurred here - kuvert's Dockerfiles already
  copied `pnpm-workspace.yaml` into their build context from the
  start. **This closes out the entire schloss-ui rollout** - schloss,
  schlussel, and kuvert now share one design system.
- Bumped schloss, schlussel, and kuvert once more: their
  `docker-compose.yml` files never declared the `npm_token` BuildKit
  secret their own Dockerfiles mount for GitHub Packages auth (only
  CI's `docker/build-push-action` step had it) - a plain `docker
  compose build`/`up --build` failed with `ERR_PNPM_FETCH_401`. Found
  while preparing local/docker-compose test instructions.
- Bumped all three once more: every Dockerfile installed pnpm
  unpinned, which pulled 11.13.0 at build time and aborted with
  `ERR_PNPM_ABORTED_REMOVE_MODULES_DIR_NO_TTY` (a stricter pre-script
  node_modules check that needs a TTY, which Docker builds never
  have) - the same class of issue CI pinned around weeks earlier, just
  never applied to the Dockerfiles themselves. Pinned all five
  Dockerfiles to the same known-good `11.7.0`. Found on the user's
  first real local `docker compose up --build`.
- Bumped all three once more: the pnpm pin above wasn't the actual
  fix - the same error reproduced on 11.7.0 too. The real cause: pnpm
  runs a deps-status check before any run/exec script and needs a TTY
  to confirm a node_modules purge on a mismatch, which a Docker build
  never has, regardless of pnpm version. GitHub Actions sets `CI=true`
  automatically for every workflow (pnpm's own suggested remedy),
  which is why CI never hit this. Set `ENV CI=true` explicitly in each
  Dockerfile's builder stage.
- Bumped schloss-ui to `v0.3.0`: fixed `Field`'s too-small left
  padding (a shorthand/longhand style-mixing bug jsdom couldn't
  catch), added an optional `version` prop to `Footer`. Bumped all
  three consumers to match: fixed the Header's home-link logo showing
  the current service's own icon instead of schloss's (schlussel,
  kuvert); fixed two kuvert empty-state icons with no background,
  rendered flush left instead of centered (Tailwind's
  `svg { display: block }` preflight breaking a `text-align: center`
  assumption); added error handling + a toast to kuvert's header
  logout button as a hardening measure for a reported "doesn't work"
  that couldn't be conclusively reproduced via code review alone; and
  wired each app's own package.json version into the footer. Found via
  the user's first real hands-on walkthrough of the platform behind
  the tor gateway.
- Bumped all four once more: found the real cause of "logout doesn't
  work" - the session cookie is host-only to schlussel's own origin,
  so schloss/kuvert's `/auth/logout` calls (proxied through their own
  origin) never actually carried it, and the redirect to login then
  silently re-authenticated via the still-valid session. Added a new
  `/logout` page to schlussel (real browser navigation, same-origin
  with the cookie there) and pointed both consumers at it instead of
  the broken cross-origin fetch - a pre-existing bug since the SSO
  silent-reauth architecture was adopted, not a schloss-ui regression.
  Also bumped schloss-ui to `v0.4.0`: `Footer` gained an optional
  `description` prop, wired into all three consumers with a one-line
  summary of what each service does.
- Bumped kuvert once more: Debts/Budget/Transactions each briefly showed
  a loading skeleton on every tab/period/filter switch, since their
  `useQuery` calls re-key on that local state - added `placeholderData:
  keepPreviousData` to all three so the previous list stays on screen
  until the new one arrives. First stage run under the newly formalized
  process rules (milestone as umbrella task, one branch per milestone,
  `type(module): head` PR titles, Project board status tracking) - see
  ROADMAP.md for the full checklist.
- Bumped all four once more: the real root cause of "logout doesn't
  work" - every consumer app's own proxied /auth/token and
  /auth/refresh calls mint their OWN, separately-scoped session cookie
  (no Domain attribute, by design), which schlussel's own /logout page
  can never see. schlussel now only sets that cookie when the request
  carries a trusted header only its own frontend's proxy injects;
  kuvert and schloss's logout() also clears their own already-existing
  cookie immediately, instead of waiting for it to expire. Also bumped
  schloss-ui to v0.4.1 (Footer's description line got a small accent
  marker) and capitalized each consumer's description string.
- Bumped schlussel and kuvert once more: `docker compose build` failed
  intermittently with `gyp ERR! find Python` - better-sqlite3 falls
  back to compiling from source (needs Python + a C/C++ toolchain,
  absent from `node:22-alpine`) whenever its prebuilt-binary download
  hits a transient network timeout, and the fallback then hard-failed
  instead of just being slower. Installed `python3 make g++` in every
  builder/runner stage that touches it (including each repo's web
  image, which pulls it in too via the shared workspace lockfile).
  Found on the user's real `docker compose up -d --build`.
- Bumped schloss once more: logout on the home page still didn't work
  even after the cross-origin cookie fix - a separate bug where the
  page's own "redirect to login when logged out" effect raced logout's
  navigation to schlussel's logout page and could win, silently
  re-authenticating the user. Fixed with a ref that tells the effect a
  deliberate logout is in flight.
- Bumped schloss-ui to `v0.5.0`: `Modal` now submits its primary
  action when Enter is pressed in a field - its Save/Cancel buttons
  live outside the `<form>` by design, so native implicit-submission
  never had anything to trigger. Bumped kuvert to match, alongside two
  more UX fixes: an account's starting balance is now recorded as a
  real opening transaction (so it counts toward "Осталось
  распределить" instead of just sitting invisible in `initialBalance`),
  and the budget period name field's placeholder is now computed live
  from the start date and used as the actual name when left blank.
- Bumped all four once more: stopped publishing schloss-ui to GitHub
  Packages, which required an authenticated token to install even
  though the package is public - it's now a git submodule in each
  consumer, linked via pnpm's `workspace:*` protocol. Removed the
  `npm_token` BuildKit secret from every Dockerfile, `docker-compose.
  yml`'s `secrets:` blocks, CI's registry auth, every `.npmrc`, and
  `minimumReleaseAgeExclude`. Verified for real: a plain `docker
  compose build` now works with no token set at all, previously
  impossible.
- Bumped kuvert once more: the placeholder-fallback-on-blank pattern
  was only ever applied to the budget period name field, not every
  form as originally asked - Accounts/Debts/Goals still blocked
  submission with the browser's native "Please fill out this field".
  Applied the same fix to all three.
- Bumped kuvert once more: a delete-period button for the Budget page
  (the backend route existed, nothing in the UI ever called it) and a
  new Envelopes page - the actual namesake of envelope budgeting had a
  full CRUD API but zero frontend, so creating one was only possible
  via a raw API call. A real gap in the original MVP scope, not a
  deliberately deferred feature.
- Bumped kuvert once more: the period-delete button's `window.confirm()`
  was inconsistent with every other destructive action in the app
  (Accounts/Envelopes archive, Debts/Goals delete never confirm) -
  removed it.
- Bumped kuvert once more: three real bugs from the opening-balance
  change - creating an account never invalidated the Transactions/
  Budget cache (stale until a hard reload), editing an account's
  "Начальный баланс" was a silent no-op once transactions existed (now
  removed from the edit form entirely), and every account created
  before that change showed balance 0 (backfilled with a one-time
  migration). Also fixed the test harness itself, which only ever ran
  the first migration file - any migration after it, including this
  one, was silently unexercised by the whole suite.
- Bumped kuvert once more: the Budget page's envelope-allocation button
  (click the "Выделено" amount to edit it) worked correctly but had no
  visual affordance at all - styled identically to the read-only cells
  next to it, so a user who had created an account, a period, income,
  and an envelope had no way to discover how to allocate money to it.
  Added a dashed-underline/hover affordance plus a tooltip.
- Bumped kuvert once more: archiving a счёт/конверт was a one-way
  trip - `archived` was only ever set to true, never back to false,
  and the list endpoints always filtered it out, so archived items
  weren't even listable. Added `?archived=true` listing, a restore
  endpoint, and an "Активные/Архивные" tab on both pages.
- Bumped schloss-ui and kuvert together: added `DateField`/
  `DateRangeField` (a custom click-to-pick calendar replacing every
  native `type="date"` input app-wide), `NumberField`/`AmountField`
  (thousand-space formatting while typing, an existing "0" gets
  replaced instead of prepended-to, and the amount prefix now
  follows the currency actually selected instead of a hardcoded ₽),
  and `handleArrowFieldNavigation` (Up/Down move between form fields
  instead of driving a number input's native spinner). Found and
  fixed a caret-position bug in schloss-ui along the way: typing a
  decimal point mis-anchored the cursor, so "10.50" posted as "1050".
- Bumped schloss-ui and kuvert once more, from user feedback with a
  screenshot: a "Период" field's calendar could open far above the
  trigger, disconnected from the field, instead of right next to
  it - the popover's "does it fit below" guess used a hardcoded
  height estimate that didn't match reality. Now measures the real
  rendered height and only nudges up the minimum amount needed to
  stay on-screen. Also restyled the Budget page's inline "Выделено"
  editor (plain/flat before - always-on accent border, no focus
  ring, no currency context) to match the rest of the app's fields.
- Bumped kuvert once more: that "Выделено" polish still wasn't
  enough - it only touched the editing-mode input, and the
  display-mode control (a dashed underline) was still barely
  visible. Redesigned as a colored pill button with a pencil icon,
  filling solid accent on hover.
- Bumped kuvert once more: the pill was wider than the editing
  input in some rows and narrower in others, so switching a row into
  edit mode reflowed the whole table's later columns to the right
  (the table used the browser's default "auto" layout, which
  recomputes column widths from whatever's rendered in every row).
  Locked column widths with `table-layout: fixed`.
- Bumped kuvert once more: asked to rework the display/edit
  transition itself, not just fix its side-effects - swapping a
  `<button>` for an `<input>` (a full mount/unmount) meant nothing
  could actually animate between them. Replaced with one persistent
  container that morphs shape via CSS transition (pill radius ->
  box radius, background, focus ring) and crossfades two
  always-mounted content layers via opacity, each made
  keyboard/pointer-unreachable while inactive.
- Bumped kuvert once more: the morph container was hardcoded to a
  fixed (editing-sized) width in both states, so a short idle value
  like "0 ₽" rendered as a stretched, mostly-empty pill. The fixed
  width now only applies once actually editing; while idle the
  display button sizes the pill to its own content again.
- Bumped schlussel, kuvert, and schloss together: added a single
  unified account settings page (password change, delete account) at
  schlussel's `/account`, and repointed every service's header
  settings button at it instead of a local settings page - kuvert's
  used to (wrongly) open its own currency preferences, and schloss
  never wired up a settings button at all. Per-service settings stay
  reachable from each service's own navigation; the header's gear
  icon is now reserved platform-wide for this one page.
- Bumped schloss-ui, schlussel, kuvert, and schloss together: the
  header's settings gear icon is gone - the avatar itself opens
  account settings now (kuvert's sidebar identity block does too, a
  second entry point). Moved the already-triplicated `theme.ts` into
  schloss-ui along with a new shared `ThemeToggle` dropdown (kuvert's
  sidebar swapped its blind cycle-button for it; schlussel's header
  gained a theme control for the first time). Account settings grew
  an editable display name, an active-sessions list with per-session
  revoke, and a "Выйти на всех устройствах" button - and fixed a bug
  an independent test agent caught along the way, where a failed
  session-list fetch left the loading indicator stuck on forever.
- Bumped schlussel and kuvert: self-registration now requires an
  admin-issued invite code (except the platform's first user); a new
  admin panel (schlussel `/admin`) manages users and invites; both
  services publish an admin-only OpenAPI spec + Swagger UI viewer at
  `/docs`. Bumped schloss and schloss-ui too, for a documentation-only
  follow-up shared across all four service repos (README refreshes,
  an "Updated docs" line added to every PR checklist template). See
  this file's own `ROADMAP.md` for the full writeup.
- Bumped kuvert (Transactions page filter-select height fix) and tor
  (documented the one-time step of trusting Caddy's local HTTPS CA in the
  browser for local dev, discovered while testing the invite/admin batch
  above against a freshly wiped local database).
- Bumped schlussel and kuvert again: `/admin` and `/docs` weren't linked
  from anywhere in the normal UI, discovered during the same testing pass
  - added an admin-only shortcut card on schlussel's `/account`, a small
  back-link loop between `/account`/`/admin`/`/docs`, and an admin-only
  "Документация API" nav item in kuvert's sidebar.
- Bumped schloss-ui (StatTile row-misalignment and Badge/text baseline
  fixes, both hit on the new admin panel), and schlussel/kuvert again to
  pick up the new schloss-ui pin. Bumped tor for a TLS-handshake fix on
  unrecognized subdomains (a typo'd hostname previously failed the
  handshake outright instead of getting any HTTP response) - all three
  found during the same manual testing pass.
- Bumped schlussel, kuvert, schloss, and tor for a full security-audit
  pass (three independent agents, one per service) run at the user's
  request: schlussel gained a last-admin guard on self-service account
  deletion, closed a login-endpoint gap that could plant a session cookie
  on a consumer app's own origin, made the last-admin guard atomic against
  a concurrent-request race, and added a per-IP login rate limiter; kuvert
  gained ownership checks on cross-referenced ids in transactions/goals/
  envelopes (previously only checked existence, not that they belonged to
  the caller) and a request body size limit; kuvert and schloss's `/auth/*`
  proxies now strip a trust header that's only supposed to come from
  schlussel-web itself; tor gained baseline security response headers.
  See each repo's own `CHANGELOG.md` for the full writeup.
- Bumped schloss-ui, schlussel, and kuvert for a platform-wide precise
  field-level validation push (per the user's request): every form now
  highlights the specific invalid field in red instead of a generic
  banner. schlussel additionally moved invite links from a query param to
  a URL fragment, so the code never touches Caddy's access logs. `/login`
  deliberately keeps its wrong-email-vs-wrong-password error merged, to
  avoid reopening the user-enumeration gap the security audit above
  closed. See schloss-ui/schlussel/kuvert's own `CHANGELOG.md` for the
  full writeup.
- Cleared the Dependabot backlog across every repo (per the user's
  request), merging GitHub Actions and npm bumps in schlussel, kuvert,
  and schloss and deleting each PR's branch both locally and remotely.
  Several npm PRs needed a manual lockfile regeneration and force-push,
  since Dependabot's own automated update couldn't fully resolve pnpm's
  lockfile for a few of the larger version jumps (typescript 6→7, jsdom
  26→30, vitest 3→4, and others). Docker-build verification of the
  result (not just each repo's own test suite) caught one real
  regression: kuvert's TypeScript 6→7 bump left a test file using the
  now-untyped Node-specific `global.fetch`, breaking kuvert-web's
  production build - fixed by switching to `globalThis.fetch` (see
  kuvert's own `CHANGELOG.md`). A handful of PRs in kuvert (1) and
  schloss (4) remain open, all blocked by the pnpm supply-chain policy's
  `minimumReleaseAge` check (the resolved package versions were
  published too recently to pass) - left alone rather than bypassed,
  expected to clear and become mergeable naturally within hours to
  about a day.

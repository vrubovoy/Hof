# Hof

Hof ("yard"/"courtyard" in German) is the meta-repo for the **Hof
platform** — a small suite of self-hosted personal services. It doesn't
contain any application code itself; it's docs plus git submodules pinning
the service repos to the commits that make up the current release.

## The platform

- [`schloss`](https://github.com/zudaR107/schloss) — home page / launcher
- [`schlussel`](https://github.com/zudaR107/schlussel) — auth: accounts, login, tokens
- [`kuvert`](https://github.com/zudaR107/kuvert) — envelope budgeting
- [`tafel`](https://github.com/zudaR107/tafel) — task/project tracking
- [`zettel`](https://github.com/zudaR107/zettel) — markdown note-taking
- [`glocke`](https://github.com/zudaR107/glocke) — in-app notification center and delivery foundation
- [`tor`](https://github.com/zudaR107/tor) — reverse-proxy gateway all of the above sit behind
- [`schloss-ui`](https://github.com/zudaR107/schloss-ui) — shared frontend
  components, consumed by every service's web app
- [`schloss-server-kit`](https://github.com/zudaR107/schloss-server-kit) —
  shared backend auth/CORS kit, consumed by every service's API

Each is independently developed, tested, and deployed (its own CI, its own
Docker images, its own issue tracker). This repo exists to answer "what
versions of each service go together" and to hold cross-cutting planning
docs that don't belong in any single service's history.

## Notifications

The in-app notification producer rollout is complete. Glocke centrally
registers, validates, and renders the current event catalog; producers send
domain data, not presentation text:

- `schlussel.security.password_changed.v1`
- `kuvert.goal.completed.v1`
- `kuvert.debt.paid_off.v1`
- `kuvert.envelope.overdrawn.v1`
- `tafel.task.due.v1`
- `tafel.project.completed.v1`
- `zettel.note.backlink_added.v1`

Mutation-originated producers write events transactionally with their domain
change. Tafel's clock-driven scanner atomically records the due occurrence and
its outbox row. Every producer uses a leased, retained outbox with bounded
retries; Glocke's durable inbox and notification uniqueness constraints make
duplicate delivery idempotent.
At processing time Glocke reads the recipient's current preference from
Schlüssel and durably suppresses disabled or missing recipients. Glocke alone
owns rendering, including trusted deployment-configured Kuvert and Tafel action
origins; producer payloads cannot supply action URLs.

Every authenticated application header now includes the same accessible Glocke
bell. It fetches the exact unread count with the existing in-memory bearer token,
shows `99+` visually without losing the exact accessible count, polls while the
page is active, and refreshes after focus, connectivity recovery, or a Glocke
read/delete mutation. Requests use one validated browser-facing Glocke origin;
tokens never enter links, and Glocke's notification responses are private and
no-store with an exact platform-origin CORS allowlist.

Tafel's due scanner records persistent occurrence identities separately from
the outbox, so pruning retained terminal delivery rows cannot re-emit an old
due or overdue occurrence. The deployment uses five distinct directional HMAC
secrets: one from each of Schlüssel, Kuvert, Tafel, and Zettel to Glocke, plus
a separate Glocke-to-Schlüssel secret for recipient and preference lookup.

Browser Push is implemented and disabled by default. Schlüssel owns only a
global `notifyBrowserPush` switch on the account profile; Glocke owns
everything else - VAPID keys, per-browser subscriptions, a leased retry
worker around `web-push`, and a push-only service worker
(`glocke/frontend/public/sw.js`). Materialization gates the in-app row and
each active subscription's delivery row independently inside the same
fenced inbox write, so either channel can be on without the other. A push
notification carries only generic text and a trusted destination URL -
never the event's rendered title/body - and a click focuses an existing
Glocke tab before opening a new one. The retry worker re-checks the global
preference at send time, deletes a subscription and settles its deliveries
on 404/410, and reconciles orphaned subscriptions for deleted accounts on a
schedule. Telegram bot/account-linking remains the one still-unimplemented
notification channel.

## Data exports

The platform keeps direct service exports and the platform archive separate.
Kuvert, Tafel, Zettel, and Glocke expose synchronous `GET /exports/me` JSON
snapshots; their Settings pages download those responses directly. Schlüssel
retains its synchronous `GET /auth/export` JSON. Only Schlüssel's authenticated
`POST /auth/export-jobs` API creates the asynchronous ZIP containing snapshots
from Schlüssel and all four consumer services.

For collection, Schlüssel mints a short-lived RS256 delegation for one exact
service audience. Services verify it through Schlüssel's JWKS and exact issuer
and require `token_use: export`, `data:export` scope, and nonempty subject, job,
and token IDs plus a non-expired numeric expiry. Delegations work only on that
service's `/exports/me`; ordinary routes and retained legacy exports reject
them. The verified subject defines
ownership, and clients cannot supply service URLs.

Every service reads a locally consistent snapshot when its own request runs.
There is no distributed transaction, so the files are not one platform-wide
point-in-time view; retrying failures keeps successful files and captures the
retried services later. A job with at least one success can publish a partial
ZIP. Its `manifest.json` records per-service status, attempts, paths, byte
counts, SHA-256 checksums, timestamps, and sanitized errors; failed response
bodies are not included.

Artifacts are private, owner-only, and short-lived (24 hours by default).
Status and download responses use no-store/no-cache and nosniff headers.
Creation is bounded by a per-user cooldown, retained-job and retained-byte
caps, per-service and aggregate response limits, a global storage quota, and a
filesystem free-space reserve. Exports contain sensitive profile, financial,
task, note, and notification data; protect and delete downloaded files as
appropriate. They exclude passwords/hashes, token and signing/HMAC material,
runtime configuration, logs, worker leases, notification inbox payloads and
hashes, internal audit state, other users, and services outside the fixed
Schlüssel/Kuvert/Tafel/Zettel/Glocke registry.

Kuvert, Tafel, Zettel, and Glocke keep application code in `backend/` and
`frontend/`. Schloss is frontend-only and keeps that frontend at its repo
root; Schlussel keeps its backend at its repo root and its frontend in
`frontend/`.

## Services, ports, and API docs

Only `tor` publishes a host port - everything else is reached through it by
subdomain. Where a service has its own REST API, its OpenAPI spec and a
Swagger UI viewer live at `/docs` in that service's own web app, visible to
admins only.

| Service | Purpose | Internal ports | Public path | API docs |
|---|---|---|---|---|
| `schloss` | Home page / launcher | `80` (web) | `https://<domain>/` | — (no API of its own) |
| `schlussel` | Auth: accounts, login, tokens, invites, admin | `4000` (api), `80` (web) | `https://auth.<domain>/` | `/docs` (admin only) |
| `kuvert` | Envelope budgeting | `3001` (api), `80` (web) | `https://kuvert.<domain>/` | `/docs` (admin only) |
| `tafel` | Task/project tracking | `3002` (api), `80` (web) | `https://tafel.<domain>/` | `/docs` (admin only) |
| `zettel` | Markdown note-taking | `3003` (api), `80` (web) | `https://zettel.<domain>/` | `/docs` (admin only) |
| `glocke` | In-app notification center and delivery foundation | `3004` (api), `80` (web) | `https://glocke.<domain>/` | `/docs` (admin only) |
| `tor` | Reverse-proxy gateway | `80`/`443` | entry point for all of the above | — |

Glocke's direct frontend development server uses port `5177`; production
traffic reaches its web container through Tor on port `80` like the other
full-stack apps.

## What's in here

- `ROADMAP.md` — development history and status across all repos.
- Nine git submodules (`schlussel/`, `schloss/`, `kuvert/`, `tafel/`,
  `zettel/`, `glocke/`, `tor/`, `schloss-ui/`, `schloss-server-kit/`), each
  pinned to a specific commit.

## Getting the code

```sh
git clone --recurse-submodules git@github.com:zudaR107/Hof.git
# or, if you already cloned without --recurse-submodules:
git submodule update --init --recursive
```

## Running the platform

See [`tor/README.md`](https://github.com/zudaR107/tor#readme) — one
`docker compose up` from `tor/` starts everything (`schloss`, `schlussel`,
`kuvert`, `tafel`, `zettel`, `glocke`, and the gateway itself) behind a single
address, no ports to remember.

## Updating this repo

This repo is committed to rarely, by design — only when bumping a submodule
pointer to a service's new release, or updating cross-cutting docs. Regular
development happens in the submodule repos themselves, each with its own
issue/PR workflow. There's no branch protection here for that reason.

## License

AGPL-3.0 — see [LICENSE](LICENSE). Each submodule carries its own copy of
the same license.

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

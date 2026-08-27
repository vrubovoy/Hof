# Platform Operations — recommended plan

Authored by the user 2026-08-25, as the recommended plan for
[`ROADMAP.md`](ROADMAP.md)'s phase 5 ("Platform operations"). Saved
here (Russian, as written) as the reference spec for that phase's
implementation.

**Scope review resolved (2026-08-26):** `hof-ops` is a distributable
single-host product; portable runtime images remain required; `hof-opsd`
starts read-only and mutation controls retain a separate security gate.

**Implementation progress:**
- [x] Foundation (delivery item 1): public `vrubovoy/hof-ops` repository
  (standard docs, branch protection on `main`), accepted ADRs, versioned
  desired-state/catalog/release-lock schemas, release-owned service catalog,
  examples, cross-contract validation, and CI definition. Published and
  pinned as a `Hof` submodule 2026-08-26.
- [x] Portable runtime frontend configuration (delivery item 2): all eight
  frontend images (glocke, herold, kuvert, schloss, schlussel, schrank,
  tafel, zettel) now consume a versioned, JSON-safe `window.__HOF_CONFIG__`
  generated at container startup; deployment URLs are no longer Vite build
  arguments; `/config.js` is non-cacheable; Tor's `validate-runtime-config`
  builds and starts every image and proves reconfiguration without rebuild.
  Landed and merged in all nine repos (incl. Tor) 2026-08-26.
- [x] Backend `*_FILE` secrets and explicit migrations (delivery item 3):
  done in every backend. kuvert, tafel, schlussel, glocke, herold, and
  zettel got `resolveSecret` (mutual-exclusion/size/UTF-8 validation) plus
  `db/migrate.ts` + `MIGRATE_ON_STARTUP`-gated `prepareDatabase`; schrank
  has no secret of its own, so migration-gating only; wachter's agent token
  uses the same `*_FILE` pattern (no database). Landed and merged in all
  seven database-backed backends plus wachter 2026-08-26.
- [x] Dynamic platform topology (delivery item 4): a service is "enabled"
  iff its URL/origin env var is set in the deployment (no new
  manifest-reading mechanism yet — that's a later, not-yet-built delivery
  stage). Glocke no longer requires `KUVERT_ORIGIN`/`TAFEL_ORIGIN` at
  startup; Schlüssel's export/deletion registries drop their
  internal-hostname fallback and skip disabled services entirely instead
  of dispatching to them and failing (a deletion job with zero enabled
  targets now completes immediately instead of hanging at `pending`);
  Schloss's launcher hides a card when its service has no configured URL.
  Every frontend's runtime config gained an explicit `services.glocke`
  flag (URL-truthiness alone can't signal "disabled" once a dev-fallback
  default exists) gating the shared notification bell and its polling in
  all eight frontends. Health aggregation and readiness checks needed no
  change — neither assumed a fixed service list. Tor's routing is
  deliberately deferred to hof-ops's own manifest-driven Compose
  generation (a later delivery stage), per ADR 0001. Landed and merged in
  all eight frontends plus schlussel's backend 2026-08-26.
- [x] Image supply chain (delivery item 5): every image-publishing repo
  (kuvert, tafel, zettel, glocke, schrank, herold, schlussel, schloss,
  wachter — Tor publishes no custom image, it runs stock `caddy:2-alpine`)
  now signs every pushed digest with keyless Cosign (GitHub OIDC, no
  stored key), generates and attests an SPDX SBOM, and attests SLSA build
  provenance, all via `actions/attest-sbom`/`actions/attest-build-provenance`
  pushed to the registry alongside the image and independently verifiable
  with `gh attestation verify`. A `vX.Y.Z` git tag push additionally
  publishes that exact semver tag and a preflight check refuses to
  overwrite one that already exists (validated live: deleting and
  re-pushing a test tag correctly fails the job). Builds are pinned to
  `linux/amd64`. Fixed two latent bugs along the way: kuvert, glocke,
  zettel, and tafel published via a separate ungated `publish.yml` with no
  dependency on tests passing, and to the pre-rename `ghcr.io/zudar107`
  namespace instead of `ghcr.io/vrubovoy` — both fixed. Landed and merged
  in all nine image-publishing repos 2026-08-26. The "Hof release
  workflow" (get exact component commits → verify CI → resolve digest →
  verify signatures/provenance → assemble and sign a release lock →
  integration matrix → publish) that consumes this per-repo signing to
  produce an actual platform release is delivery item 6 ("signed release
  lock"), owned by `hof-ops` per ADR 0001 — not part of this item.
- [x] Signed release lock (delivery item 6): fixed three catalog/GHCR
  artifact-name mismatches the earlier fake example had been hiding (Tor
  publishes no image of its own; Schlüssel and Schloss don't use a
  `-backend`/`-frontend` suffix; Wächter's API and agent share one image),
  and extended the release-lock schema with a `thirdParty` branch for
  artifacts Hof doesn't build or sign itself (Tor's pinned upstream Caddy
  base). `hof-ops/scripts/build-release-lock.mjs` resolves every catalog
  artifact against its real, currently published GHCR digest and
  independently re-verifies its Cosign signature and SBOM/provenance
  attestations (a component can't resolve without a valid one, so this
  step doubles as "verify component CI"/"verify signatures and
  provenance"); `.github/workflows/release.yml` signs the assembled file
  with its own keyless Cosign signature and publishes it as a GitHub
  Release. Run for real against live platform state 2026-08-26:
  [`v0.1.0`](https://github.com/vrubovoy/hof-ops/releases/tag/v0.1.0) - a
  genuine signed release lock, not a fixture, kept published rather than
  deleted as a test artifact. No integration matrix yet (delivery items
  7–9's reconciler doesn't exist to bring the platform up against pinned
  digests); `ansibleEnvironment` stays schema-optional until item 8 ships
  a real image.
- [x] **Hardening round (2026-08-26):** a review of items 3–6 found real
  gaps behind the "done" checkmarks above; each was fixed and re-verified,
  not just noted:
  - **Item 3:** Schrank's Zettel-sync secrets (`sync/{inbox,outbox}.ts`)
    read `process.env` directly, bypassing `resolveSecret` — fixed.
    Production `db:migrate` ran `drizzle-kit migrate`, a devDependency
    absent from the built image, in kuvert/tafel/zettel/schlussel — fixed
    to run the compiled `dist/migrate.js`. Normal startup defaulted to
    auto-migrating; `MIGRATE_ON_STARTUP` now defaults to schema-check-only
    across every backend, matching "explicit migrations" more literally.
    `/ready` now asserts schema currency and `/health` carries
    version/build metadata everywhere (both were unimplemented gaps from
    Stage 1's own bullet list).
  - **Item 4:** Glocke's own `KUVERT_ORIGIN`/`TAFEL_ORIGIN` fix from the
    first pass never mattered in practice — every shipped `docker-compose.yml`
    still defaulted every optional service's URL to its always-on
    hostname, silently re-enabling everything the topology code was
    supposed to let an operator disable. Fixed across kuvert, tafel,
    zettel, glocke, schrank, herold, schloss, and Tor's own `.env.example`/
    `.env.production.example` (which was also just missing `GLOCKE_BASE_URL`
    outright — a real, separate delivery break, not a topology gap).
    Schlüssel's notification dispatcher still required Glocke's HMAC
    secrets unconditionally; `loadNotificationConfig` now returns `null`
    when `GLOCKE_ENABLED !== 'true'`, and both callers handle that. Tor's
    own dev/integration Compose gained a profile per optional service
    (`--profile kuvert`, …) so a developer can start a subset locally;
    two of Tor's own validation scripts had stopped seeing profiled
    services entirely once profiles landed and needed the same profile
    flags added to their own `docker compose config` calls.
  - **Item 5:** the `v*` tag trigger accepted any ref matching that glob,
    not just semver, and the immutability check shared a job with the
    build instead of gating it. Every one of the nine image-publishing
    repos now validates the tag against a strict `vX.Y.Z` regex and
    checks for an existing image in a dedicated `publish-preflight` job
    (with a `concurrency` group) before `publish` runs at all.
  - **Item 6:** `build-release-lock.mjs` resolved every component from
    the mutable `:latest` tag and only ran `gh attestation verify` — never
    a real `cosign verify`/`cosign verify-attestation` against the image
    signature. A new `release-selection.yml` contract now pins an
    explicit version/commit tag, workflow identity, and OIDC issuer per
    component; resolution verifies the plain Cosign signature and both
    attestations, cross-checks the attesting workflow's own source
    repository and revision, and directly queries GitHub's check-runs/
    status API for each required check rather than inferring "tests
    passed" from an attestation merely existing. The release lock now
    carries `composeTemplateDigest` and real `database.{from,to,
    rollbackCompatible}` per persistent component (previously always
    omitted), resolved from `render-topology.mjs` (new — the actual
    services.yml → Compose/Caddyfile/env/backup-inventory generator,
    closing item 4's other open half: `services.yml` now genuinely
    drives what gets deployed) and `integration-matrix.mjs` (new — renders
    multiple topology fixtures against the pinned lock and runs
    `docker compose config`/optionally `create`+`down` against the
    result, closing the "no integration matrix" gap). The release
    workflow rebuilds the lock a second time and diffs it against the
    first to catch non-determinism, and now also signs and publishes
    `stable-channel.json` alongside the lock. Every fix independently
    re-verified (test suites, `docker compose config`, a live Tor
    Browser-Push/gateway validation run) rather than trusted on read.
- [x] **Second hardening round (2026-08-27):** a follow-up review issued a
  no-go on 6/18 pending four blockers. All four addressed:
  - **Generated Wächter topology was broken**: `APP_PORTS` had no `wachter`
    entry (`PORT` rendered as the literal string `"undefined"`; the
    healthcheck URL was `http://localhost:undefined/ready`), the agent
    container had no `command` override so it silently ran the API's
    default CMD instead of `backend/dist/agent.js`, and neither container
    carried the reference `docker-compose.yml`'s `read_only`/`cap_drop`/
    `no-new-privileges` hardening. A related gap the review didn't
    explicitly name: **no service anywhere got a
    `hof.wachter.critical`/`restartable` label**, so Wächter's own
    restart-control feature would have had nothing to act on in a real
    deployment. All fixed in `render-topology.mjs`, covered by two new
    regression tests (one of which caught a second bug in the fix itself —
    Schloss briefly ended up labeled restartable, which the platform's
    own convention reserves for frontends only).
  - **Readiness checked only the database, never a mandatory dependency**:
    every consuming backend now calls `checkJwksReachable` (new,
    `schloss-server-kit`) against Schlüssel's JWKS alongside its existing
    schema check. Schlüssel itself was reviewed and correctly *not*
    given one — it's the JWKS issuer, not a consumer, so there's no
    analogous dependency to probe; its own gap was `/ready` having zero
    HTTP-level test coverage, fixed instead. Landing this surfaced two
    recurring test-fidelity bugs across the backends: several test
    harnesses reconstructed their own `/ready` route as a static
    always-ready stub (or didn't mount it at all) independent of the real
    handler, so the new dependency check would have gone completely
    untested; and several mock test databases applied migrations by
    hand-running raw SQL instead of calling the real `migrateDatabase()`,
    leaving `__drizzle_migrations` empty so `assertSchemaCurrent` would
    always throw once actually exercised. Both fixed everywhere they
    occurred.
  - **The new release pipeline had never actually produced a release**:
    the only published lock was still the old `:latest`-based `v0.1.0`.
    Cut a real one: persistent `v0.1.1` tags pushed to all nine
    image-publishing repos, a concrete `releases/0.1.1.yml` selection
    resolved and independently re-verified against every one of them, and
    a genuine signed release published -
    [`v0.1.1`](https://github.com/vrubovoy/hof-ops/releases/tag/v0.1.1) -
    superseding the old `v0.1.0` (kept published as a historical
    artifact, not deleted).
  - **The integration matrix's `--runtime` mode never started anything**:
    `create` alone starts no process, so a wrong port, wrong command, or
    a migration that never runs all passed silently. Now `docker compose
    up --wait`, which fails loudly if any service doesn't report healthy
    within its timeout - this single change is what actually surfaced
    six further real, previously-invisible bugs once it ran against real
    image digests for the first time: the Wächter port/command/hardening
    bugs above; `cosign verify-attestation` being incompatible with how
    `actions/attest-sbom`/`attest-build-provenance` publish (dropped -
    `gh attestation verify`, called right after, already does full
    cryptographic verification; `cosign verify` stays for the one gap
    that call alone doesn't close, the plain image signature); topology
    fixtures hardcoding `release: 1.0.0`; the gateway's own invented
    healthcheck failing against a real (necessarily-rejected) ACME
    domain, mirrored to remove it entirely, matching Tor's actual
    `docker-compose.yml`, which never had one; the rendered Caddyfile
    never being written next to the rendered Compose file; every
    `:?required` placeholder secret sharing one identical, too-short
    value even though Schlüssel demands its directional HMAC secrets be
    both distinct and ≥32 bytes; Glocke's VAPID keys needing real P-256
    key material, not an arbitrary string; and `wachter-agent` getting a
    real `EACCES` on the Docker socket because the rendered
    `DOCKER_GID:-998` fallback doesn't match this runner's actual group.
    Every one of those was invisible to `pnpm test`/`docker compose
    config` alone and would have stayed invisible without actually
    running the pipeline for real, repeatedly, against its own failures.
  - **Go verdict (2026-08-27):** a follow-up review confirmed 6/18 for
    real - clean worktrees on published commits/tags, the Wächter fixes
    verified by test, readiness/test-harness fidelity confirmed, a
    successful live `--runtime` run
    ([33049559813](https://github.com/vrubovoy/hof-ops/actions/runs/33049559813)),
    and `v0.1.1`'s six assets independently checked (`catalogDigest`/
    `composeTemplateDigest` match the current files, the stable-channel
    digest matches the published lock). Three **non-blocking** notes to
    carry into items 7-8, not yet acted on:
    - Wächter's own `/ready` checks its agent/sampler but not Schlüssel's
      JWKS the way every other backend now does - acceptable for now
      (Schlüssel isn't Wächter's primary runtime dependency the way it is
      for the others), but item 7's shared health model should make that
      an explicit, deliberate choice rather than an unremarked asymmetry.
    - `render-topology.mjs`'s `MIGRATE_ON_STARTUP: "true"` is the interim
      default noted when it was added (delivery item 6 entry above) -
      item 7's `hofctl plan` should already surface migrations as a
      distinct, visible operation even before item 8 replaces this with
      dedicated pre-start migration jobs.
    - `catalogDigest`/`composeTemplateDigest`/`minimumHofctlVersion`/the
      lock's own signature are currently only checked ad hoc (by
      `integration-matrix.mjs`, or by hand as above) - `hofctl validate`
      should make all of that a first-class, always-run check.
  - **Item 7 progress (2026-08-27):** `hofctl validate`
    ([#14](https://github.com/vrubovoy/hof-ops/pull/14)) and `hofctl
    preflight` ([#15](https://github.com/vrubovoy/hof-ops/pull/15)) are
    landed and tested; `validate` closes the third non-blocking note above
    (catalogDigest/composeTemplateDigest/minimumHofctlVersion/signature are
    now always-run checks, and `release.yml` runs `hofctl validate` against
    a live cosign signature on every real release). `hofctl plan` design,
    decided this session:
    - **State model - hybrid, not file-only or Docker-only:** an
      authoritative last-applied state file drives the *desired* diff
      (what `apply` should do); live Docker/host inspection drives a
      separate *drift* diff (what changed outside `apply`'s control). A
      file alone can't see manual changes or broken containers; Docker
      alone doesn't know the previous release, schema versions,
      checksums, or backup policy - `plan` needs both diffs, kept
      distinct, so an operator can tell "services.yml changed" apart
      from "someone touched Docker by hand" apart from both at once.
    - **Bootstrap on a truly clean host is not an error:** read
      `/var/lib/hof/state/current.json`; if absent, check for any
      `hof.managed=true`-labeled Docker resource. Neither present ->
      synthetic empty baseline (`{mode: "bootstrap", generation: 0,
      release: null, services: {}, volumes: []}`) and `plan` shows
      creating the whole selected topology. `plan` itself never writes
      state - only a fully successful `apply` does (out of scope for
      item 7, but the contract is decided now so `plan`'s shape doesn't
      need to change under it later). If state is absent but Hof-labeled
      resources already exist, **fail closed** ("managed resources exist
      but the authoritative state is missing") rather than silently
      adopting them - a future typed `hofctl adopt`, not automatic
      adoption, is the only sanctioned recovery path.
    - **State layout:** `/var/lib/hof/state/{current.json, topology.json,
      generations/NNNNNN/{state.json, topology.json, release-lock.json}}`.
      `current.json` (schema `hof.dev/state/v1`) carries
      `installationId`, `generation`, `lastSuccessfulOperationId`,
      `appliedAt`, `release`, and digests for the manifest/release-lock/
      catalog/compose-template/topology/each generated artifact -
      never secrets or plaintext environment values.
    - **Observed state via a fixed label set, not raw `docker inspect`:**
      every generated resource gets `hof.managed`, `hof.installation-id`,
      `hof.service`, `hof.artifact`, `hof.generation` labels (added in
      the renderer). The Docker inspector reads only a whitelist -
      labels, image digest, container state/health, network/volume
      names, published ports - explicitly never `Config.Env` or a full
      `docker inspect`, since secrets can appear there.
    - **Plan contract** (schema `hof.dev/plan/v1`): `planId` (a digest of
      inputs+baseline, deterministic - no timestamp in it, since a future
      `apply` needs to reject a stale plan whose inputs changed
      underneath it), `mode`, `executable`, `baseline`, `desired`,
      `drift[]`, a `summary` (create/update/remove/migrate counts), and
      `operations[]` that are typed and ordered - never shell strings.
      Action types: `host.prepare`, `secret.ensure`, `volume.ensure`,
      `image.verify`, `image.pull`, `config.write`, `backup.create`,
      `service.stop`, `database.migrate`, `service.start`,
      `readiness.wait`, `state.commit` (always last, only after a
      success gate).
    - **Migrations become typed operations, not an env flag:**
      `MIGRATE_ON_STARTUP` moves from `true` (item 6's interim default)
      to `false` in the renderer. `plan` surfaces `database.migrate`
      explicitly - always on bootstrap, on upgrade whenever a DB
      component/release/schema changed, never on a no-op re-apply. The
      catalog gains typed per-service `database: {component, command,
      volume}` metadata (item 8's Ansible role and the integration
      matrix both run migration jobs explicitly, before `up --wait`,
      instead of hardcoding a command by repo name).
    - **Real bug found while designing this: `hofctl preflight` checks
      the operator's own workstation, not `target.host`/`target.user`**
      (`os.totalmem()`, local `statfsSync`, binding `0.0.0.0` locally,
      local `docker version` - `scripts/preflight.mjs`, landed in PR #15).
      This contradicts the architecture (`hofctl`/the installer run on
      the operator's machine, `target.*` names the host being
      provisioned). Before `plan` is implemented, `preflight` needs a
      `TargetInspector` abstraction (`collectHostFacts`,
      `collectPortOwners`, `collectDockerState`, `readManagedState`,
      `checksumGeneratedArtifacts`) with a real SSH-backed implementation
      for production and a `LocalTargetInspector` reachable only via an
      explicit `--target-mode local` for tests/dev. A repeat `apply`
      must also not treat 80/443 as failed-occupied when the occupant is
      Hof's own gateway - needs the same managed-state/label read
      `preflight` is gaining.
    - **Implementation order agreed:** state-v1/plan-v1 schemas -> pure
      `buildPlan(desired, lastApplied, observed)` -> synthetic empty
      baseline -> `TargetInspector` interface + preflight's local/remote
      fix -> ownership labels in the renderer -> desired diff + drift
      diff -> migrations as typed operations -> bootstrap/no-op/topology-
      change/drift/missing-state-with-resources/upgrade fixtures ->
      deterministic `planId`. `apply` accepting and rejecting a stale
      `planId` is explicitly future work, not item 7.
  - **Item 7 progress, continued (2026-08-27):** foundational pieces
    landed in [#16](https://github.com/vrubovoy/hof-ops/pull/16)
    (typed per-service `database` catalog metadata; `MIGRATE_ON_STARTUP`
    moved from the interim `"true"` default to `"false"`; Hof ownership
    labels on every generated Compose service; the real integration
    matrix now runs each service's migration job before `up --wait` -
    verified against v0.1.1's actual published, signed release lock, not
    just unit-tested) and [#17](https://github.com/vrubovoy/hof-ops/pull/17)
    (`hofctl plan`'s pure core - `state-v1`/`plan-v1` schemas,
    `resolveBaseline`'s bootstrap/fail-closed rules, `buildPlan`'s
    desired+drift diffing and typed operation emission, all 75 tests
    passing including every named fixture category). Still open: a real
    `TargetInspector` (SSH-backed for production, local only via an
    explicit dev/test flag) to actually collect the Docker/host
    observation `buildPlan` takes as an input, wiring `hofctl plan` to
    it, and fixing `hofctl preflight`'s real bug (checks the operator's
    own workstation, not `target.host`/`target.user`) as part of the
    same change. Paused here before that piece - it's a real
    architecture change to already-shipped `preflight` code, and the one
    part of this whole delivery item that can't be verified against a
    genuine remote host inside this working environment (only against a
    mocked exec or, at best, SSH-to-localhost).
  - **Item 7 progress, second review round (2026-08-27):** a follow-up
    review of the pure core (before touching `TargetInspector`) found
    six real gaps, all closed in
    [#18](https://github.com/vrubovoy/hof-ops/pull/18): config-only
    changes (domain/CORS/browserPush/TLS/backup-schedule) produced a
    false no-op - fixed with a per-unit `configFingerprint` (the full
    rendered Compose definition, not just the image) plus a
    `topologyDigest` covering everything with no per-unit footprint at
    all; Wächter's API and its agent shared one catalog artifact and
    collapsed into a single state/diff entry - fixed with a new
    `hof.unit` label, state/diff now keyed by unit everywhere; manual
    drift produced a warning but never blocked or offered a repair path -
    now `executable: false` by default, with an explicit (not yet
    CLI-wired) `repairDrift` option that still never auto-adopts an
    unmanaged resource; `database.migrate` operations didn't carry their
    own `argv`/`volume`, so an approved plan wasn't self-sufficient -
    fixed; upgrade migrations neither verified the baseline's schema
    version against what the release lock expects to start from (now a
    blocker) nor backed up before an in-place migration (now automatic,
    stop → backup → migrate, skipped only on a fresh bootstrap);
    `observedResources` defaulted to `[]`, conflating "couldn't reach the
    host" with "confirmed clean" - `buildPlan`/`resolveBaseline` now both
    require an explicit `observation: {status, resources}`, and
    `"unavailable"` hard-blocks an applied host. Also corrected two wrong
    comments in the catalog (Kuvert/Tafel do already gate their startup
    migration on `MIGRATE_ON_STARTUP`, direct code inspection confirmed -
    the earlier PR #16 comment claiming otherwise was simply a misread).
    90/90 tests passing; two more real bugs were caught by the new
    `configFingerprint`/`topologyDigest` fixtures themselves before this
    ever shipped (a backup-only change producing zero operations; a
    CORS-only cascade onto an unrelated database-backed service
    spuriously triggering that service's own migration) - see the PR for
    both. Same pause point as before: `TargetInspector` next.

---

## Recommended Plan

Следующая стадия должна называться Platform Operations и выполняться отдельным репозиторием hof-ops. Правильный порядок: сначала release/deployment contracts, затем headless reconciliation, backup/restore и только потом installer UI и /admin/services.

## Fixed Decisions

- Новый repository: hof-ops.
- Installer работает на компьютере оператора и слушает только 127.0.0.1.
- Target: один rootful Docker host.
- Первая host matrix: Debian 12 и Ubuntu 24.04, только amd64.
- Production использует signed, digest-pinned GHCR images.
- Secrets: SOPS + age.
- Backup: restic с local и S3-compatible destinations.
- Upgrade: только после ручного подтверждения.
- Optional services можно выбирать независимо, но mandatory core и dependency validation сохраняются.
- Первый admin создаётся через expiring one-time claim token.
- Air-gapped deployment не входит в v1.

Для TLS рекомендую:
- ACME HTTP-01 как основной автоматический режим.
- Предоставленный оператором certificate/key как второй режим.
- DNS-01 отложить до следующей версии.

Это покрывает обычный публичный сервер и installations за CDN/NAT без необходимости сразу безопасно поддерживать credentials разных DNS providers.

## Architecture

### hof-ops

Репозиторий должен владеть:
- installer UI;
- hofctl;
- hof-opsd;
- JSON Schema для services.yml;
- service catalog;
- Ansible playbooks и roles;
- Ansible Execution Environment image;
- Compose generation;
- backup/restore tooling;
- deployment audit model;
- documentation для install, upgrade, recovery и uninstall.

Tor остаётся development/integration Compose и gateway implementation. Не следует превращать Tor в privileged deployment controller.

### Components

| Component | Responsibility |
|---|---|
| hofctl | Validate, preflight, plan, apply, backup, restore, upgrade |
| Installer UI | Local browser workflow поверх фиксированных операций hofctl |
| Ansible roles | Идемпотентное приведение target host к desired state |
| hof-opsd | Ограниченный on-host operations API для будущего admin UI |
| services.yml | User-owned desired state без секретов и image digests |
| Service catalog | Release-owned dependencies, ports, volumes, health checks |
| Release lock | Immutable source commits, image digests и migration metadata |
| Generated Compose | Производный artifact, который пользователь не редактирует |

## Configuration Contracts

### services.yml

Manifest хранит только пользовательские намерения:

```yaml
apiVersion: hof.dev/v1alpha1
release: "1.0.0"

target:
  host: hof.example.net
  user: deploy

domains:
  base: example.net

tls:
  mode: acme-http01
  email: admin@example.net

services:
  kuvert:
    enabled: true
  tafel:
    enabled: true
  zettel:
    enabled: true
  schrank:
    enabled: false
  herold:
    enabled: true
  glocke:
    enabled: true
  wachter:
    enabled: true

backup:
  schedule: "03:00"
  destinations:
    - local
    - s3
```

В services.yml не должны попадать:
- passwords;
- tokens;
- VAPID private keys;
- S3 credentials;
- image tags или digests;
- generated ports;
- internal container topology.

### Mandatory Core

Нельзя отключить:
- Tor gateway;
- Schlüssel;
- Schloss;
- platform database/state requirements.

Остальные сервисы можно выбирать свободно. Reconciler должен либо автоматически отключать недоступную integration, либо отклонять несовместимую конфигурацию.

Примеры:
- Zettel без Schrank работает без attachment synchronization.
- Schrank без Zettel работает как самостоятельное storage service.
- Сервисы без Glocke работают без notifications.
- Wächter без Docker agent недопустим.
- Browser Push требует Glocke и корректную VAPID configuration.

### Release Lock

Каждый platform release получает immutable release-lock.json:

```json
{
  "release": "1.0.0",
  "schemaVersion": 1,
  "components": {
    "schlussel": {
      "commit": "...",
      "image": "ghcr.io/vrubovoy/schlussel@sha256:...",
      "configSchema": 1,
      "databaseSchema": 4
    }
  },
  "ansibleEnvironment": "ghcr.io/vrubovoy/hof-ansible-ee@sha256:..."
}
```

Lock должен включать:
- exact source commit;
- OCI image digest;
- signature identity;
- SBOM/provenance references;
- configuration schema;
- database schema before/after;
- rollback compatibility;
- minimum hofctl version;
- digest service catalog и Compose templates.

latest не должен использоваться при deployment.

## Implementation Stages

### 1. Portable Runtime Images

Сначала нужно устранить зависимость production images от build-time environment.

Работы во всех frontend repositories:
- Добавить runtime config.js.
- Монтировать generated config read-only.
- Убрать deployment URLs из VITE_* build arguments.
- Сохранить same-origin API paths там, где это возможно.
- Скрывать UI integrations для отключённых сервисов.
- Валидировать config schema при frontend startup.
- Добавить image revision/version в diagnostic endpoint или static metadata.

Рекомендуемый contract:

```html
<script src="/config.js"></script>
```
```js
window.__HOF_CONFIG__ = {
  services: {
    schrank: { enabled: false },
    glocke: { enabled: true }
  }
};
```

Работы во всех backend repositories:
- Поддержать secrets через *_FILE.
- Разделить migrate и normal application startup.
- Добавить readiness, которая проверяет database schema и обязательные dependencies.
- Не выполнять неявную destructive migration при обычном container restart.
- Добавить version/build metadata endpoint.

### 2. Dynamic Platform Topology

Произвольный выбор optional services сейчас блокируется статическими registries.

Нужно сделать manifest-driven:
- Schlüssel archive/deletion service registry;
- Schloss launcher/navigation;
- Tor routes;
- Glocke producers и notification links;
- frontend service links;
- CORS allowlists;
- health aggregation;
- backup volume inventory;
- readiness dependency checks.

Отсутствующий disabled service не должен считаться degraded или вызывать deletion/archive failure.

### 3. Image Supply Chain

Каждый component repository должен:
- публиковать в ghcr.io/vrubovoy;
- собирать linux/amd64;
- запускать tests до publish;
- публиковать immutable semver tag;
- подписывать image через keyless Cosign/OIDC;
- прикреплять SBOM;
- публиковать provenance;
- не перезаписывать release tag.

Hof release workflow должен:
1. Получить exact component commits.
2. Проверить component CI.
3. Разрешить tag в digest.
4. Проверить signatures и provenance.
5. Собрать release lock.
6. Прогнать integration matrix.
7. Подписать release lock.
8. Опубликовать GitHub Release и stable channel metadata.

### 4. Headless Reconciler

До UI реализовать команды:

```
hofctl validate
hofctl preflight
hofctl plan
hofctl apply
hofctl status
hofctl backup
hofctl restore
hofctl upgrade
hofctl uninstall
```

Обязательные свойства:
- один operation lock на host;
- machine-readable JSON events;
- resumable operation journal;
- no-op при повторном apply;
- explicit diff перед изменениями;
- никакого generic shell endpoint;
- secrets никогда не попадают в output;
- interrupted operation можно безопасно продолжить;
- все generated artifacts имеют checksum и ownership.

Target layout:

```
/etc/hof/
  services.yml
  release-lock.json
  generated/
  secrets.sops.yaml

/var/lib/hof/
  operations/
  backups/
  state/

/run/hof/
  secrets/
  opsd.sock
```

### 5. Ansible Reconciliation

Roles выполняются в таком порядке:

1. Host facts и supported-platform validation.
2. SSH host-key verification.
3. sudo capability.
4. Disk, RAM, CPU и clock preflight.
5. DNS A/AAAA verification.
6. Ports 22, 80 и 443 validation.
7. Docker Engine и Compose plugin.
8. Dedicated system user/groups.
9. /etc/hof, /var/lib/hof, /run/hof.
10. Firewall rules.
11. age identity и SOPS material.
12. Volume preparation.
13. Signed image verification.
14. Digest-pinned image pull.
15. Config/Compose generation.
16. Database migration jobs.
17. Coordinated service startup.
18. Readiness verification.
19. Backup timer installation.
20. Operation result and audit record.

Ansible acceptance rule: второй run на неизменённом manifest возвращает changed=0.

### 6. Secrets and Recovery Kit

Installer должен:
- сгенерировать host age identity на target;
- сохранить identity как root-owned 0600;
- хранить encrypted secrets в /etc/hof/secrets.sops.yaml;
- расшифровывать runtime files в /run/hof/secrets;
- монтировать secret files read-only;
- запрещать secrets в Compose environment dump;
- подготовить encrypted recovery kit.

Recovery kit должен содержать:
- age recovery material;
- restic repository configuration;
- release lock;
- sanitized services.yml;
- host fingerprint;
- disaster recovery instructions.

Он не должен автоматически сохраняться в Git.

### 7. Backup and Restore

Для SQLite нужен coordinated offline backup:

1. Запретить новые operations.
2. Перевести platform в maintenance mode.
3. Остановить writers.
4. Корректно остановить containers.
5. Архивировать все declared volumes.
6. Сохранить /etc/hof без plaintext runtime secrets.
7. Записать release lock и backup manifest.
8. Передать snapshot в один или несколько restic repositories.
9. Проверить snapshot metadata.
10. Запустить platform и проверить readiness.

Defaults:
- daily backup в 03:00;
- configurable schedule;
- local и S3 destinations могут использоваться вместе или отдельно;
- encryption всегда включено;
- retention configurable;
- перед каждым upgrade выполняется обязательный backup.

Restore поддерживает только whole-platform consistency set. Частичный raw restore отдельных SQLite volumes в v1 не поддерживается.

Обязательна автоматизированная restore drill на disposable VM.

### 8. Migration and Rollback

Upgrade pipeline:

1. Проверить подписанный target release.
2. Рассчитать release diff.
3. Проверить disk space и migration compatibility.
4. Создать verified backup.
5. Остановить affected services.
6. Выполнить explicit migration jobs.
7. Запустить новый release.
8. Выполнить health и browser smoke tests.
9. Зафиксировать upgrade только после success gate.

Rollback разрешён автоматически только если release lock объявляет schema rollback-compatible.

После incompatible migration rollback означает:
- остановить platform;
- восстановить полный pre-upgrade backup;
- вернуть старый release lock;
- повторно запустить readiness checks.

### 9. First-Admin Bootstrap

Нужно удалить race модели "первый зарегистрировавшийся становится admin".

Новый flow:

1. Installer генерирует high-entropy claim token.
2. В Schlüssel сохраняется hash, expiration и unused state.
3. Installer показывает одноразовую bootstrap URL.
4. Token передаётся через URL fragment, а не query string.
5. Schlüssel атомарно создаёт первого admin и помечает claim consumed.
6. Повторное использование возвращает отказ.
7. До bootstrap public registration закрыта.
8. Claim автоматически истекает, например через 30 минут.

Raw token не должен попадать в logs, operation history или backup.

### 10. Local Installer UI

Installer распространяется как signed OCI image с pinned Ansible Execution Environment.

Запуск должен быть приблизительно таким:

```sh
docker run --rm \
  --network host \
  -p 127.0.0.1:8787:8787 \
  ghcr.io/vrubovoy/hof-installer@sha256:...
```

UI stages:

1. Select signed platform release.
2. SSH target и host fingerprint.
3. Automated host preflight.
4. Domain и DNS verification.
5. TLS mode.
6. Optional service selection.
7. Backup destination.
8. Secrets generation/import.
9. Review generated plan.
10. Explicit apply confirmation.
11. Streaming structured progress.
12. Readiness and smoke checks.
13. First-admin claim.
14. Recovery kit export.

Installer backend должен принимать только typed operations. Поле "run command" или generic terminal запрещено.

Для ACME HTTP-01 preflight должен отдельно проверять:
- A record;
- AAAA record и реальную IPv6 reachability;
- доступность port 80;
- отсутствие conflicting reverse proxy;
- корректный public hostname.

### 11. On-Host Operations API

После стабильного headless installer можно устанавливать hof-opsd.

Допустимые verbs:
- read status;
- read current/available release;
- generate plan;
- start approved backup;
- start upgrade до подписанного release;
- restart declared service;
- fetch operation progress.

Недопустимые возможности:
- arbitrary image;
- arbitrary Compose override;
- shell command;
- arbitrary Ansible tags;
- filesystem browser;
- Docker socket passthrough.

hof-opsd должен использовать Unix socket или localhost-only transport, exact-action authorization, operation lock и durable audit.

### 12. /admin/services

Внедрять в три этапа:

1. Добавить /admin/services в manual Schlüssel routing.
2. Сделать front door к существующим Schloss /server-stats*.
3. Добавить read-only platform release, backup и service status.
4. Добавить mutation controls только после production hardening hof-opsd.

Все mutations требуют:
- admin role;
- recent step-up authentication;
- CSRF protection;
- exact operation confirmation;
- short-lived action token;
- operation audit;
- отсутствие secrets в UI.

Schlüssel остаётся authorization authority, но не получает Docker socket, SSH key или shell.

## Verification Matrix

Обязательные scenarios:
- Fresh Debian 12 install.
- Fresh Ubuntu 24.04 install.
- Minimal core-only profile.
- Full platform profile.
- Pairwise optional-service combinations.
- Повторный apply без changes.
- Добавление optional service.
- Удаление optional service с explicit data-retention choice.
- Invalid DNS и broken AAAA.
- Expired ACME challenge.
- Supplied certificate mismatch.
- Interrupted image pull.
- Interrupted migration.
- Expired и reused admin claim.
- Tampered image signature.
- Tampered release lock.
- Local restic backup/restore.
- S3 restic backup/restore.
- Upgrade с compatible migration.
- Upgrade с incompatible migration.
- Full rollback через pre-upgrade restore.
- Host reboot после successful installation.
- Installer workstation disconnect во время apply.

## Delivery Order

Рекомендуемый merge order:

1. [x] Создать hof-ops, ADRs и schemas. Completed 2026-08-26; details
   collapsed into the implementation-progress entry above.
2. [x] Добавить runtime frontend configuration. Completed 2026-08-26;
   details collapsed into the implementation-progress entry above.
3. [x] Добавить backend *_FILE secrets и explicit migrations. Completed
   2026-08-26 in all seven database-backed backends plus wachter; details
   collapsed into the implementation-progress entry above.
4. [x] Сделать platform registries topology-aware. Completed 2026-08-26;
   details collapsed into the implementation-progress entry above.
5. [x] Унифицировать GHCR publishing, signing, SBOM и provenance.
   Completed 2026-08-26; details collapsed into the implementation-progress
   entry above.
6. [x] Реализовать signed release lock. Completed 2026-08-26; details
   collapsed into the implementation-progress entry above.
7. Реализовать hofctl validate/preflight/plan.
8. Реализовать Ansible fresh install.
9. Реализовать idempotent update/remove reconciliation.
10. Реализовать backup и tested restore.
11. Реализовать upgrade/rollback.
12. Реализовать one-time admin bootstrap.
13. Реализовать local installer UI.
14. Провести Debian/Ubuntu clean-VM acceptance.
15. Реализовать read-only hof-opsd.
16. Добавить /admin/services.
17. Добавить privileged admin operations последним этапом.
18. Обновить Hof roadmap, release documentation и operational runbooks.

## Explicitly Out of Scope

Не включать в первую версию:
- Kubernetes;
- multi-host topology;
- rolling deployment;
- zero-downtime upgrades;
- rootless Docker;
- arm64;
- automatic unattended upgrades;
- DNS-01 provider plugins;
- air-gapped installation;
- arbitrary third-party services;
- per-service partial database restore.

## Definition of Done

Platform Operations v1 готова, когда с чистого Debian 12 или Ubuntu 24.04 host можно:
- запустить local installer;
- выбрать optional services;
- установить platform без source checkout;
- получить signed digest-pinned deployment;
- повторить apply без изменений;
- выполнить backup и восстановить его на чистом host;
- вручную подтвердить и выполнить upgrade;
- безопасно создать первого admin;
- пережить reboot;
- увидеть состояние через /admin/services;
- выполнить всё это без Docker socket, SSH keys или shell authority в Schlüssel.

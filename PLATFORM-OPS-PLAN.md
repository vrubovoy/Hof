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
  - **Item 7 progress, TargetInspector (2026-08-27):** landed in
    [#19](https://github.com/vrubovoy/hof-ops/pull/19), closing the real
    architectural bug the previous rounds surfaced but hadn't yet fixed -
    `hofctl preflight` was checking the operator's own workstation, not
    `target.host`. `scripts/target-probe.sh` is a single fixed, read-only,
    versioned protocol script; `scripts/target-inspector.mjs`'s
    `inspectTarget()` is the only export (no generic "run this on the
    target" escape hatch) - a hardened SSH transport by default
    (requires exactly one of `--known-hosts` or `--host-key-sha256`,
    real OpenSSH SHA256 fingerprinting, a temp known_hosts holding only
    the matched key, always cleaned up) and `--target-mode local` only
    ever explicit, never inferred from the hostname. `preflight.mjs` is
    now pure evaluation over one atomic snapshot - added OS/architecture
    checks (Debian 12/Ubuntu 24.04, x86_64 only), a port policy where a
    repeat apply no longer treats its own gateway as a conflict, and a
    managed-state check that reuses `resolveBaseline()`'s own corruption/
    fail-closed rules. `resolveBaseline()` itself is now pure too - takes
    `managedState` from the snapshot instead of reading files itself.
    110/110 tests passing (unit tests with an injected process runner,
    since a real SSH transport needed real verification, not mocks
    alone) plus a genuinely new real-transport layer: an ephemeral,
    pinned Debian 12 sshd container (`pnpm test:ssh`, now its own CI
    step) exercising a real OpenSSH handshake in both trust modes, a
    real rejected stale known_hosts entry, and a real rejected wrong
    identity - run for real in this session (not just asserted to work)
    before landing, and confirmed running for real in CI too. Two real
    bugs surfaced building the fixture itself (a duplicate `Subsystem
    sftp` directive that kept sshd from starting; a stale host-key
    `.pub` file that didn't match the mounted private key). Remaining
    for item 7: wire an actual `hofctl plan` CLI subcommand around the
    already-landed `buildPlan`/`resolveBaseline`/`inspectTarget` pieces,
    and the deferred `--repair-drift` CLI flag.
  - **Item 7 progress, inspection contract hardening (2026-08-27):** a
    security-focused review of the inspector/preflight before wiring
    `hofctl plan` to it found a critical OpenSSH option-injection gap
    (an unvalidated `manifest.target.host`/`user` reaching a real SSH
    argv - closed with schema validation before use, a second
    independent validation inside the inspector itself, and a `--`
    option-terminator as a third layer) plus ten further real gaps, all
    closed in [#20](https://github.com/vrubovoy/hof-ops/pull/20) - the
    probe protocol bumped to `HOF-PROBE-V2`. Highlights: Docker/state-
    file inspection failures no longer look identical to "genuinely
    nothing there" (new `docker-resources-status`/state-file
    present|absent|unreadable statuses, sudo used as the fixed-path
    fallback it was always checked for but never used); port ownership
    and managed-resource matching now check `installationId` and
    `state=running`, not just a bare label; `current.json` is schema-
    validated against `state-v1` before a snapshot is ever returned; the
    protocol parser is now fully fail-closed (every singleton mandatory,
    strict base64, field-count/range/enum checks, no duplicate ports);
    invalid numeric CLI flags are a usage error instead of silently
    comparing against NaN; and a real, separate plan-contract bug -
    `configFingerprint` included the generation/installation-id labels,
    so a routine generation bump alone would have made every unit look
    "changed" and defeated the no-op guarantee - is fixed and covered by
    a test proven to fail without the fix. 136/136 tests passing plus
    9/9 real containerized SSH acceptance tests (up from 5, now also
    covering Docker-genuinely-absent and real state-file present/
    absent/unreadable scenarios over a real transport). **Explicitly
    deferred, not silently dropped:** orphan Hof-managed volumes/
    networks (no container currently running) aren't yet covered by the
    bootstrap fail-closed check - needs new ownership labels on Compose
    volumes/networks (none exist today) plus new probe records; a real
    scope of its own for a future pass, not folded into this PR. Same
    remaining item-7 work as before: the `hofctl plan` CLI itself.
  - **Item 7 progress, resource completeness (2026-08-27):** the
    previously-deferred orphan volume/network scope, plus ten more
    concrete gaps a follow-up review found before `hofctl plan` could
    actually be wired to a CLI, all closed in
    [#21](https://github.com/vrubovoy/hof-ops/pull/21) - the probe
    protocol bumped to `HOF-PROBE-V3`. Every Compose volume/network is
    now labeled (`hof.managed`/`installation-id`/`generation`/`kind`/
    `resource`) and probed the same buffer-then-commit way containers
    already were - one failed `docker inspect` among several now taints
    the *whole* resource kind as `unavailable` with zero partial
    records (previously a partial batch still reported `available`,
    silently dropping the failed container); the bootstrap fail-closed
    check now requires containers/volumes/networks all independently
    available and unmanaged, closing the orphan gap for real. `buildPlan`
    drift matching is now scoped by `installationId`, not a bare
    service/unit label match - a different Hof installation sharing the
    host can no longer mask a real "missing" or be silently treated as
    "ours". `docker_run()`'s plain-then-sudo fallback (already used for
    state-file reads) now covers every Docker CLI call too. Disabling a
    service now backs up its volume exactly once per *service* (was
    once per removed unit - a real double-backup bug) and actually
    issues `service.remove` after `service.stop` (units were previously
    only ever stopped, never removed, leaving orphans). Generated-file
    checksums (collected since PR #20 but never used) now feed real
    drift: a missing generated file is always auto-repaired via
    `config.write`; a hand-modified one is a blocker unless
    `--repair-drift`; a regenerated Caddyfile specifically forces the
    gateway through a real stop/start/readiness cycle. A missing
    baseline-expected persistent volume is a hard blocker (never
    silently recreated empty - data may be gone); a missing network is
    stateless and safely auto-repaired. Protocol status fields are now
    strictly enum-validated with payload/status consistency checks (a
    typo like `"presnt"` can no longer fall through silently);
    `readiness.wait` operations carry an explicit `condition: "running"
    | "healthy"` (the gateway has no Compose healthcheck by design);
    `state-v1`'s `generation` minimum tightens to 1 (generation 0 is
    exclusively the in-memory synthetic bootstrap baseline, never a
    real `current.json`); the CLI's own `--connect-timeout-seconds`
    parser now rejects `0`/fractional values at the boundary instead of
    failing deeper inside a real SSH attempt; `preflight` now schema-
    validates the full catalog, not just the manifest, before deriving
    public hostnames from it. 168/168 tests passing (every test file
    rewritten for the V3 shapes) plus a new `target-probe.test.mjs` that
    runs the real, unmodified `target-probe.sh` under a real `sh` with a
    fake `docker`/`sudo` pair on `PATH` - genuinely exercising "Docker
    reachable only via sudo" and "one failed inspect taints the whole
    batch" without a real Docker daemon or sudoers grant - plus 9/9 real
    containerized SSH acceptance tests (one of which needed fixing: the
    new positive-confirmation-only absence policy means a target with
    no sudo access at all can never report a state file "absent", only
    "unreadable" - correct, not a regression). Gate 7 closes once the
    `hofctl plan` CLI itself lands; operation journal, lock, stale-plan
    recheck, and `apply` remain explicitly out of scope for both this PR
    and the CLI PR after it.
  - **Item 7 closed, `hofctl plan` CLI (2026-08-27):** landed in
    [#22](https://github.com/vrubovoy/hof-ops/pull/22), wiring every
    already-landed pure piece (`buildPlan`/`resolveBaseline`/
    `inspectTarget`) into a real subcommand, in its own
    `scripts/plan-command.mjs` rather than growing `hofctl.mjs` itself.
    Sequence: validate the deployment exactly like `hofctl validate`
    does (schema, cross-contract, digest freshness, the release lock's
    real Cosign signature - never skippable here, `--skip-signature` is
    rejected outright) before any network access; inspect the target
    exactly once; explicitly check state/artifact/Docker completeness
    for BOTH a bootstrap and an already-applied host (closing a real gap
    - `buildPlan`'s own blocker only re-checks `containersStatus`, and
    `resolveBaseline` only re-derives this for the bootstrap branch, so
    an applied host with an unreadable volumes/networks/generated-
    artifacts listing could otherwise have silently planned with a
    blind spot); resolve the baseline; render the desired topology in
    memory with the correct installation/generation semantics (an
    applied host's next plan is its own real installationId one
    generation ahead of disk; a bootstrap gets a fixed, deterministic
    placeholder, never a fresh random id, so `planId` stays reproducible
    between two back-to-back plans against the same untouched host);
    call `buildPlan()`; schema-validate its own output against
    `plan-v1` before ever printing it. CLI contract: its own flag parser
    (distinct from every other subcommand's) rejects a duplicate flag,
    an unknown flag, and `--skip-signature` specifically; stdout carries
    exactly one raw `hof.dev/plan/v1` JSON document (or nothing), every
    diagnostic on stderr; exit 0 executable, 1 blocked/runtime-failure,
    2 usage error; writes nothing, anywhere, ever. 187/187 in the fast
    suite (was 168) - a new `plan-command.test.mjs` covers every blocked
    branch plus a genuine schema-valid bootstrap and applied no-op,
    against a real (fake) `cosign` binary on `PATH` so the signature
    gate genuinely runs rather than being mocked away; a new
    `plan-cli-acceptance.test.mjs` spawns the real `hofctl.mjs plan`
    binary as a subprocess for one genuine end-to-end bootstrap plan
    (real `sh` + `target-probe.sh` + the fake docker/sudo pair from
    #21 + the fake cosign, real schema/cross-contract validation, a
    real `buildPlan()` call) verifying stdout is exactly one line.
    **Gate 7 closes here.** Operation journal, lock, stale-plan recheck,
    and `apply` remain explicitly out of scope, as agreed before this
    PR started - the next delivery items.
  - **Gate 7 errata (2026-08-27):** a small, tightly-scoped follow-up
    review of the closed gate found four concrete issues, all fixed in
    [#23](https://github.com/vrubovoy/hof-ops/pull/23), deliberately
    without reopening any of item 7's own design: Cosign was verifying a
    mutable pathname instead of the exact bytes already read into
    memory and used to build the plan - a real TOCTOU, closed by pinning
    the already-read bytes into a fresh temp file before ever invoking
    cosign; a generated file that existed but couldn't be hashed even
    with sudo was indistinguishable from one confirmed absent, so the
    planner could have auto-regenerated a file that wasn't actually
    missing at all - closed with a new per-file present/absent/
    unreadable status (protocol bumped to `HOF-PROBE-V4`) and a new
    `generated-unreadable` drift kind that always blocks, never repaired
    even with `--repair-drift`; a missing network was planned as
    `volume.ensure` instead of its own typed `network.ensure` action;
    and `hofctl validate`'s `--release-selection`/`--stable-channel`
    flags were silently never wired through to `validateDeployment` at
    all (a key-naming mismatch between the flag parser's own output and
    what the code building its options object looked for), so a
    supplied file was never actually read regardless of its content.
    200/200 tests passing (was 187), including a deterministic real-
    (fake-)cosign test proving the pinned bytes survive a mid-
    verification mutation of the original file, two new real-transport
    ssh-acceptance tests for the new per-file generated-artifact status,
    and a real `hofctl validate` subprocess test proven to fail against
    the pre-fix code before being confirmed passing against the fix.
  - **Item 8 progress, apply contracts and fresh-host planning
    (2026-08-27):** the first item-8 PR - contracts only, per ADR 0004,
    no real executor and no target mutation anywhere in it - landed in
    [#24](https://github.com/vrubovoy/hof-ops/pull/24). ADR 0004 fixes
    the shape of everything `hofctl apply` will need: exact target
    binding (a plan is bound to the real accepted SSH host-key
    fingerprint, not just the caller's trust anchor - a key change
    invalidates it), explicit `--approve-plan-id <exact-plan-id>`
    approval, bootstrap-only apply for item 8 (applied-mode
    reconciliation stays item 9), a signed Ansible Execution Environment
    (never the operator's own local Ansible), a durable host lock that
    survives the invoking process dying, a durable operation journal
    with no secrets ever, a stale-plan recheck under the lock, and safe
    bounded resume where an unknown operation outcome blocks rather than
    guesses. A new `plan-v2` schema and pure builder
    (`scripts/plan-v2.mjs`) wrap the unchanged `buildPlan()` v1 core with
    that target binding, planning policy, per-`image.verify` trust
    policy pulled straight from the release lock (first-party components
    get a real Cosign identity, third-party ones are digest-only), and
    the bootstrap-only recovery age recipient / supplied-TLS certificate
    fingerprint - `planId` now covers the target binding too, so a
    host-key change alone changes it. `plan-v1` is untouched and stays
    the historical contract; `plan-v2` is deliberately not wired into
    the real CLI yet - that's `hofctl apply`'s own PR. `inspectTarget()`
    now returns the real accepted host-key fingerprint in both trust
    modes (parsed from a real `ssh -v` transcript - asking the client
    that already connected, rather than reimplementing key selection).
    Docker not being installed at all is now a real, distinct "absent"
    state (protocol bumped to `HOF-PROBE-V5`), never confused with
    "unavailable" (installed but unsafe to inspect) - a fresh host with
    no Docker yet is a legitimate bootstrap candidate, and `hofctl
    preflight` now says so instead of falsely reporting Docker
    unreachable. Three new schemas (`operation-journal-v1`,
    `operation-event-v1`, `operation-lock-v1`) and a pure bootstrap
    action whitelist (`scripts/bootstrap-actions.mjs`, rejecting
    `backup.create`/`service.stop`/`service.remove` and a non-bootstrap
    plan mode by name) round out the contract. 253/253 tests passing
    (was 213) plus 11/11 real containerized SSH acceptance tests,
    including Docker-genuinely-absent and the host-key fingerprint
    independently cross-checked against `ssh-keygen`'s own computation.
    Remaining for item 8: durable lock/journal implementations, the
    pinned/signed Execution Environment itself, and `hofctl apply` -
    see the Delivery Order below for the full remaining PR sequence.
  - **Item 8 closed (2026-08-28), PRs #25-30:** secret-safe Compose
    rendering landed first
    ([#25](https://github.com/vrubovoy/hof-ops/pull/25)) - every real
    platform secret now flows through Compose's native `secrets:`
    mechanism via the `<VAR>_FILE` convention every consuming app
    already implements, sourced from a SOPS-encrypted workstation store
    (`hofctl secrets ensure`) with a mandatory external `age` recovery
    recipient; local "supplied" TLS reads the operator's own certificate
    file and hashes it for the plan, never the key. A pinned,
    digest-locked Ansible Execution Environment followed
    ([#26](https://github.com/vrubovoy/hof-ops/pull/26)) with its ten
    roles (one per plan operation phase) as a skeleton enforcing each
    operation's real variable contract only. `hofctl apply` itself
    landed next ([#27](https://github.com/vrubovoy/hof-ops/pull/27)):
    it recomputes the plan itself (never trusts one handed to it on
    disk), requires an exact `--approve-plan-id` match, verifies the
    Execution Environment's own Cosign signature, acquires a durable
    target lock (or reclaims it on `--resume`), re-verifies the target
    under that lock before running anything, dispatches only the
    bootstrap action whitelist, journals every operation before and
    after it runs, and supports safe bounded resume - a step whose
    outcome can't be determined from the journal blocks resume rather
    than guessing. Two PRs then gave all ten roles their real
    implementation: `host`/`secret`/`volume`/`network`/`image`/`config`
    ([#28](https://github.com/vrubovoy/hof-ops/pull/28)) and
    `database`/`service`/`readiness`/`state`
    ([#29](https://github.com/vrubovoy/hof-ops/pull/29)). `host`
    bootstraps python3 and installs Docker only when genuinely absent;
    `secret` delivers decrypted values over the real SSH/SFTP
    connection, never through extra-vars or the journal; `volume`/
    `network` create Hof-labeled Docker resources matching the
    renderer's own labels; `image` runs a real keyless `cosign verify`
    (delegated to the control node, never the target) for signed
    components and trusts third-party images by digest pin alone;
    `config` delivers the rendered Compose/Caddy/env files; `database`
    runs each service's own migration via `docker compose run`, reusing
    its already-rendered definition; `service` starts one Compose unit
    scoped with `--no-deps`; `readiness` polls the real container state
    by its own Compose ownership labels; `state` atomically commits
    `current.json`/`topology.json` (topology first, matching the
    corruption check the baseline resolver already enforces). A real
    installation-id bug surfaced and got fixed while wiring `state`:
    every real resource was being labeled with the same fixed
    placeholder `hofctl plan` also uses for its own approval-matching
    computation, which would have made two separate bootstraps
    indistinguishable to later drift detection - real dispatch now
    renders a second time, after the lock is held, with a real, unique
    id (the operation's own id, reused deterministically - resume needs
    no new durable state to recover it). The whole pipeline is exercised
    for real in CI (`pnpm test:apply-ssh`) against a genuinely
    ephemeral, systemd-enabled target container: real Docker install,
    real secret delivery, real volume creation, then a real, expected
    failure at the first illustrative image reference (the example
    release lock's own images are placeholders, not real published
    digests) - exercising the real failure path (journal marked failed,
    lock released) against a genuine failure for the first time. A real
    incident happened during this work: a `docker run --privileged
    --cgroupns=host` test container, run locally against what turned
    out to be a real desktop rather than an isolated sandbox, reached
    real host tty/cgroup resources and disrupted a real login session
    (recovered via reboot, no lasting damage) - local iteration moved to
    read-only checks from then on, with CI itself (a genuinely
    disposable VM) doing the real verification instead; several more
    real, CI-discovered gaps got fixed the same way (a missing SSH
    client in the Execution Environment image, the Execution
    Environment container never joining the target's own Docker
    network, the target missing the Docker Python SDK community.docker
    modules need). Finally
    ([#30](https://github.com/vrubovoy/hof-ops/pull/30)): `ee-v0.1.0`
    was cut for real (a real git tag, a real keyless-signed build, real
    SBOM/provenance attestations) and independently re-verified
    afterward with a real `cosign verify` - both attestations genuinely
    present. Interruption/resume was already covered by PR #27's own
    tests; nothing further was needed there.
  - **Item 8 reopened (2026-08-28):** the "closed" call above was
    premature. A review of PRs #25-30, against the exact merged pins
    (`Hof` `bd0f83a`, `hof-ops` `419520d`), running no tests/containers,
    found nine concrete blockers in item 8's own bootstrap/apply scope
    (explicitly not item 9/reconciliation, backup, upgrade, or item 14's
    clean-VM acceptance - those stay later items, unaffected). Two
    Critical, re-verified directly against the code before accepting the
    review:
    1. **The approve workflow doesn't actually work.** `hofctl plan`
       (`plan-command.mjs`) still prints a `plan-v1` document via
       `buildPlan()`; `hofctl apply` (`apply.mjs`) independently builds
       its own `plan-v2` via `buildPlanV2()`, which adds the target
       binding, recovery recipient, and supplied-TLS fingerprint - fields
       `plan-v1` never had. The two are structurally different documents
       with different `planId`s, so the ID a real `hofctl plan` run
       prints is never the ID `--approve-plan-id` actually needs - an
       operator can never see and approve the exact bytes `apply` is
       about to run. `test/apply-acceptance.mjs` papers over exactly this
       by first submitting a wrong ID on purpose and regex-extracting the
       real one out of the resulting error message; the same trick, not
       a real approval, is what every apply test in the suite does.
    2. **Resume cannot work after the first real mutation.**
       `apply --resume` runs the ordinary bootstrap-baseline
       `resolveBaseline()` check before ever reading the lock/journal
       (`apply.mjs`, current code path). Once any managed resource
       (`volume.ensure`, `network.ensure`, a started container) has
       actually been created but `state.commit` hasn't run yet - the
       exact case resume exists to recover from - that baseline check
       necessarily rejects the host as "not a clean bootstrap target"
       before the lock/journal are ever consulted. The resume tests only
       exercise a still-clean target, never a genuinely partial one.
    Seven more High/Critical findings, not independently re-verified line
    by line but consistent with the codebase and not disputed: the
    journal records input/EE digests but resume only compares
    `approvedPlanId`, so an EE or input change outside the plan
    projection can silently continue under a stale execution environment;
    supplied-TLS certificate/key material is fingerprinted into the plan
    but never actually delivered to the target (the renderer leaves
    workstation-local paths in the generated Compose file, and the
    `config` role only ever copies the six generated files); a successful
    `state.commit` whose post-commit journal/lock cleanup then fails can
    wedge a host permanently, since the next run sees "already applied"
    before resume logic is reached; the `host` role skips Docker
    installation whenever `docker --version` succeeds, even if the
    Compose plugin specifically is missing; `apply` doesn't itself
    enforce the exact supported-platform check `preflight` already has
    (Debian 12/Ubuntu 24.04/x86_64) before its first real mutation; the
    Execution Environment's own `ee-vX.Y.Z` tag isn't wired into
    `build-release-lock.mjs`'s revision resolution (which looks up plain
    `vX.Y.Z`) and no real signed platform release-lock actually carries
    the published EE digest yet - `examples/release-lock.json` stays
    illustrative; and the CI acceptance test that "closed" item 8
    deliberately stops at the first expected image-pull failure with EE
    signature verification disabled and a local image override, so it
    never actually exercises config delivery, migrations, service start,
    readiness, or a real generation-1 `state.commit` end to end - real,
    but partial, evidence, not what the closure claim asserted.
    **Not blocking item 8** (explicitly out of this review's scope):
    applied-mode update/remove (item 9), backup/restore, upgrade/
    rollback, the Ubuntu clean-VM acceptance pass (item 14), a stricter
    operation schema, and network-reconciliation edge cases outside a
    bootstrap plan. **Recovery plan, three stabilization PRs, no further
    architecture growth needed:**
    - **PR #31 (Approved Plan And Resume):** wire `hofctl plan` to the
      real `plan-v2` (including the recovery-recipient/supplied-TLS plan
      options it's currently missing); add `hofctl apply --plan <file>`
      so `--approve-plan-id` is checked against that exact file's own ID;
      `apply` recomputes the plan under the lock and diffs the full
      canonical document, not just the ID; resume starts from lock/
      journal, never the bootstrap baseline check; the journal gains the
      real installation ID and immutable input/EE digests, all checked on
      resume; partial resources found under lock are treated as this
      operation's own checkpoint, not foreign state; a state already
      committed by this exact operation lets resume finish journal/lock
      cleanup instead of re-running; new crash fixtures after
      volume-creation, after image-pull, after migration, and after
      `current.json` but before the succeeded event.
    - **PR #32 (Complete Bootstrap Modes):** real supplied-TLS delivery
      (read/validate cert+key locally, key-match/SAN/validity checks,
      safe fingerprints in the plan, deliver to fixed target paths, the
      renderer stops embedding workstation paths); exact
      Debian-12/Ubuntu-24.04/x86_64 enforcement before any mutation; the
      `host` role checks/installs the Compose plugin independently of the
      Engine check; journal/state documents schema-validated on read; SSH
      `ProxyCommand`/`ProxyJump` either explicitly rejected or properly
      bound into target identity.
    - **PR #33 (Real Release And Full Acceptance):** teach the
      release-lock builder to resolve `ee-vX.Y.Z` (and update the
      release-lock schema/tag contract accordingly); cut a new EE after
      PR #31/#32's fixes; publish a real signed platform release-lock
      carrying that EE's real digest; rerun the disposable-VM acceptance
      test with EE signature verification on, no local-image override,
      real application images, real supplied-TLS material, and the full
      path through migrations/startup/readiness/`state.commit`; assert a
      schema-valid `current.json`, a full topology snapshot, a succeeded
      journal, a released lock, and a second bootstrap `apply` against
      the same host correctly refused as "already applied"; fix
      `ansible/README.md`, which currently asserts both "apply is
      implemented" and "hofctl apply (not yet implemented)" at once.
    Item 8 stays open until all three land; item 9 does not start first.
  - **Item 8 closed for real (2026-08-28), PRs #31-37:** all nine
    findings from the reopened review fixed, each independently
    verified, not just asserted:
    - **#31 (blockers #1-2, both Critical):** `hofctl plan` against a
      bootstrap target now prints the real `plan-v2` document `apply`
      itself requires `--plan`/`--approve-plan-id` to match byte for
      byte (recomputed once before the lock, once again under it, both
      times as a full canonical-document diff, not just an ID
      comparison). `apply --resume` now reads the lock/journal first,
      always - the journal embeds the full approved plan (schema
      bumped) and resume never re-derives a live baseline, closing the
      "can't resume after the first real mutation" bug and, as a direct
      consequence, the separate "a successful but uncommitted-journal
      state.commit could wedge a host" finding too (the existing
      per-step skip logic now gets the chance to finish the journal/lock
      cleanup on its own). 372/372 tests, new coverage: a pre-lock
      stale-plan refusal, a genuinely partial-bootstrap resume, a
      resume refused on a changed input digest.
    - **#32 (blockers #4/#6/#7, plus schema-validated reads and SSH
      hardening):** supplied TLS is now genuinely parsed, key-matched
      (`X509Certificate.checkPrivateKey`), validity- and SAN-checked
      (exact + RFC 6125 wildcard) against every real public hostname,
      and delivered to the target through the same `secret.ensure`
      mechanism every other secret uses - the rendered Compose file
      previously bind-mounted a workstation path directly into a
      target-side volume definition, meaningless on the actual target.
      The `host` role now checks/installs the Compose plugin
      independently of Engine's own presence. `apply` re-verifies the
      exact supported platform (Debian 12/Ubuntu 24.04/x86_64) on every
      live plan recompute, not just once in `preflight`. Journal/lock
      documents read off the target are now schema-validated before
      apply ever acts on a field from either. `ProxyCommand`/`ProxyJump`
      are explicitly disabled on every SSH connection this platform
      makes (verified against a real transport, `pnpm test:ssh`, 11/11).
      382/382 tests, including `supplied-tls.test.mjs` rewritten against
      real `openssl`-generated certificates.
    - **#33 (blocker #8):** `build-release-lock.mjs` resolves the
      Execution Environment's own `ee-vX.Y.Z` git tag correctly now
      (`resolveRevision()`/`resolveBuiltArtifact()` take an explicit
      `tagPrefix`) - previously it always looked up plain `vX.Y.Z`,
      which for a version number coinciding with an already-published
      platform tag in this same repository would have silently resolved
      the *wrong commit*. `schemas/release-lock-v1.schema.json` gained a
      dedicated `ansibleEnvironmentArtifact` definition enforcing the
      `ee-v` prefix. 387/387 tests.
    - **A real `ee-v0.1.1`** was then cut and independently re-verified
      (real `cosign verify`, both attestations present), baking PR
      #31/#32's own Ansible role fixes into a real pinned image for the
      first time.
    - **#34-36 (blocker #9, "no full live evidence"):** a real platform
      release, `v0.1.2` (`releases/0.1.2.yml`), was cut - the first to
      carry a real `ansibleEnvironment`, reusing `v0.1.1`'s own
      unchanged app-component selections. Cutting it for real surfaced
      two more genuine, previously-unknown bugs, both fixed before it
      would pass: `integration-matrix.mjs`'s own fixture secret files
      were mode `0600`, invisible to any non-root container process
      (`wachter-agent` specifically, found via two real, deterministic
      CI failures - PR #35, fixed at `0644` for these synthetic
      fixture-only values; the real target-side secret role stays
      `root:root 0400`, untouched). `test/apply-acceptance.mjs` was then
      rewritten (PR #36) to download the real, published, signed
      `v0.1.2` lock and run the entire real `hofctl apply` pipeline
      against it with nothing bypassed: the real, published `ee-v0.1.1`
      image (no local build, no override), its real Cosign signature
      genuinely verified, the release lock's own real blob signature
      genuinely verified (`.github/workflows/test.yml`'s `contracts` job
      gained a `cosign-installer` step), real application images
      (`schlussel`/`schlussel-frontend`/`schloss` - the platform's own
      mandatory core, every optional service disabled, matching
      `test/fixtures/topologies/core.yml`; `requiredSecrets()` at this
      scope is empty, so no secrets store is needed either). A real,
      previously-unknown Docker-in-Docker limitation surfaced along the
      way and got fixed too: the target fixture's own nested Docker
      daemon defaulted to the `overlay2` storage driver, which the
      kernel genuinely refuses when already running inside another
      overlayfs-backed container - pinned to `vfs` for this fixture
      only (never touching a real target's own, always-overlay2,
      defaults). The result: every real role ran for real for the first
      time in one single CI run - `host.prepare`, `secret.ensure`
      (including the real TLS material), every `volume.ensure`, every
      real `image.verify`/`image.pull`, `config.write`,
      `database.migrate`, every `service.start`/`readiness.wait`, and a
      genuine generation-1 `state.commit` - confirmed afterward by a
      real second `hofctl plan` against the same host correctly seeing
      an `"applied"` baseline (not `"bootstrap"`), at the real committed
      generation and installation id.
    - **#37:** `ansible/README.md` updated to say all ten roles are now
      verified live, not six of ten.
    Nothing about items 9-18 changed by any of this - applied-mode
    reconciliation, backup/restore, upgrade/rollback, and the clean-VM
    acceptance pass (item 14) remain their own, later, unstarted work.

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
7. [x] Реализовать hofctl validate/preflight/plan. Completed 2026-08-27;
   details collapsed into the implementation-progress entries above.
8. [x] Реализовать Ansible fresh install. PRs
   [#24](https://github.com/vrubovoy/hof-ops/pull/24)-[#30](https://github.com/vrubovoy/hof-ops/pull/30)
   landed a real, CI-exercised pipeline, but a 2026-08-28 review found
   the "closes item 8" claim premature: nine concrete blockers in the
   bootstrap/apply scope itself. All nine fixed for real across PRs
   [#31](https://github.com/vrubovoy/hof-ops/pull/31)-[#37](https://github.com/vrubovoy/hof-ops/pull/37),
   closing with a genuinely full, live, disposable-VM `hofctl apply` run
   (real signed release, real signed Execution Environment, real
   application images, real migration/start/readiness, a real
   generation-1 commit, confirmed by a real follow-up `hofctl plan`
   seeing an `"applied"` baseline) - see the "Item 8 closed for real"
   log entry below. Completed 2026-08-28 (second call, this one backed
   by real CI evidence, not a partial run).
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

# Platform Operations — recommended plan

Authored by the user 2026-08-25, as the recommended plan for
[`ROADMAP.md`](ROADMAP.md)'s phase 5 ("Platform operations"). Saved
verbatim here (Russian, as written) as the reference spec for that
phase's implementation — not yet started, not yet revised after the
scope-review discussion below.

**Open review notes (2026-08-25, not yet resolved with the user):**
- Whether `hof-ops` targets *personal* redeployability (this operator,
  this one install) or a *distributable* product other people install
  their own copy of — the plan's rigor (keyless Cosign/OIDC signing,
  SBOM, provenance, a two-distro host matrix, a 20+ scenario
  verification matrix, a disposable-VM restore drill) fits the second
  framing much more than the first, and that distinction should decide
  how much of this v1 actually gets built.
- Stage 11–12 (`hof-opsd` as a network-reachable on-host agent, plus
  `/admin/services` mutation controls) adds real attack surface for a
  single-operator platform where "SSH in and run `hofctl`" is already a
  complete answer - candidate for cutting entirely, or admin/services
  staying read-only-only.
- Stage 1 ("Portable Runtime Images") is the most invasive stage,
  touching all nine existing services' frontends and backends. It's only
  a hard prerequisite if the installer must toggle services on/off
  without rebuilding images - if rebuilding per-install with the right
  build args is an acceptable v1 shortcut, this stage (and its
  destabilization risk to already-working services) goes away.

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

1. Создать hof-ops, ADRs и schemas.
2. Добавить runtime frontend configuration.
3. Добавить backend *_FILE secrets и explicit migrations.
4. Сделать platform registries topology-aware.
5. Унифицировать GHCR publishing, signing, SBOM и provenance.
6. Реализовать signed release lock.
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

<h1 align="center">Lerd Service Store</h1>

<p align="center">
  The community-driven store of service presets that powers <a href="https://lerd.sh">Lerd</a>.<br>
  Add a database, cache, search engine, or admin dashboard by editing YAML, no binary release required.
</p>

<p align="center">
  <a href="https://lerd.sh"><img src="https://img.shields.io/badge/part%20of-lerd-ff2d20" alt="Part of Lerd"></a>
  <a href="https://lerd.sh/usage/service-presets"><img src="https://img.shields.io/badge/docs-lerd.sh-blue" alt="Docs"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
</p>

<p align="center">
  <img src=".github/logos/adminer.svg" width="38" height="38" alt="adminer" title="adminer">
  <img src=".github/logos/clickhouse.svg" width="38" height="38" alt="clickhouse" title="clickhouse">
  <img src=".github/logos/elasticsearch.svg" width="38" height="38" alt="elasticsearch" title="elasticsearch">
  <img src=".github/logos/floci.svg" width="38" height="38" alt="floci" title="floci">
  <img src=".github/logos/kafka.svg" width="38" height="38" alt="kafka" title="kafka">
  <img src=".github/logos/localstack.svg" width="38" height="38" alt="localstack" title="localstack">
  <img src=".github/logos/mailpit.svg" width="38" height="38" alt="mailpit" title="mailpit">
  <img src=".github/logos/mariadb.svg" width="38" height="38" alt="mariadb" title="mariadb">
  <img src=".github/logos/meilisearch.svg" width="38" height="38" alt="meilisearch" title="meilisearch">
  <img src=".github/logos/mercure.svg" width="38" height="38" alt="mercure" title="mercure">
  <img src=".github/logos/mongo.svg" width="38" height="38" alt="mongo" title="mongo">
  <img src=".github/logos/mysql.svg" width="38" height="38" alt="mysql" title="mysql">
  <img src=".github/logos/opensearch.svg" width="38" height="38" alt="opensearch" title="opensearch">
  <img src=".github/logos/phpmyadmin.svg" width="38" height="38" alt="phpmyadmin" title="phpmyadmin">
  <img src=".github/logos/postgres.svg" width="38" height="38" alt="postgres" title="postgres, postgres-pgvector, postgres-timescaledb">
  <img src=".github/logos/rabbitmq.svg" width="38" height="38" alt="rabbitmq" title="rabbitmq">
  <img src=".github/logos/redis.svg" width="38" height="38" alt="redis" title="redis">
  <img src=".github/logos/selenium.svg" width="38" height="38" alt="selenium" title="selenium">
  <img src=".github/logos/solr.svg" width="38" height="38" alt="solr" title="solr">
  <img src=".github/logos/stripe-mock.svg" width="38" height="38" alt="stripe-mock" title="stripe-mock">
  <img src=".github/logos/valkey.svg" width="38" height="38" alt="valkey" title="valkey">
</p>

Run `lerd service search`, pick something, `lerd service preset <name>` — and Lerd pulls the matching preset from this store, then knows exactly how to run it: which image and ports, how to wire your project's `.env`, which admin dashboard to embed, what it depends on, and which config files to mount for auto-login. Everything is a single YAML file. Add a service here and every Lerd install can use it within 24 hours, with no new Lerd release and no Go code.

That's the whole point: **Lerd ships only the default stack — MySQL, PostgreSQL, Redis, Meilisearch, RustFS, Mailpit — and every other service lives here.** MongoDB, MariaDB, phpMyAdmin, pgAdmin, Elasticsearch, RabbitMQ, and whatever you add next are all defined in this repo, not hardcoded in the binary.

## What a preset powers

A single `<name>.yaml` teaches Lerd to:

- 📦 **Run the container** — image, ports, volumes, and environment, wired into a rootless Podman quadlet
- 🌱 **Wire your `.env`** — inject the host, port, and credentials your framework expects, with auto-detection
- 🖥️ **Embed a dashboard** — phpMyAdmin, pgAdmin, RedisInsight and friends open inside the Lerd UI, already logged in
- 👪 **Group into families** — alternates and admin UIs discover every installed family member automatically
- 🔢 **Offer versions** — ship multiple selectable image tags; every member shares the family's canonical host port and Lerd shifts collisions for you
- 🔗 **Declare dependencies** — pull in the services a preset needs, started in order
- 📄 **Mount config files** — static files inline, or dynamic ones (like pgAdmin's discovered server list) via a built-in generator

All of it is data. None of it ships in the binary.

## Available services

**Databases**

| | Service | What it is |
|:-:|---|---|
| <img src=".github/logos/clickhouse.svg" width="28" height="28" alt=""> | `clickhouse` | ClickHouse column-oriented analytics database, with its own SQL console |
| <img src=".github/logos/mariadb.svg" width="28" height="28" alt=""> | `mariadb` | MariaDB, the MySQL-compatible server (multi-version) |
| <img src=".github/logos/mongo.svg" width="28" height="28" alt=""> | `mongo` | MongoDB document database |
| <img src=".github/logos/mysql.svg" width="28" height="28" alt=""> | `mysql` | MySQL database server · **built into Lerd** |
| <img src=".github/logos/postgres.svg" width="28" height="28" alt=""> | `postgres` | PostgreSQL with PostGIS · **built into Lerd** |
| <img src=".github/logos/postgres-pgvector.svg" width="28" height="28" alt=""> | `postgres-pgvector` | PostgreSQL + pgvector for vector search (16, 17, 18 Trixie) |
| <img src=".github/logos/postgres-timescaledb.svg" width="28" height="28" alt=""> | `postgres-timescaledb` | PostgreSQL + TimescaleDB for time-series (multi-version) |

**Admin dashboards** — open inside the Lerd UI, auto-logged-in

| | Service | For |
|:-:|---|---|
| <img src=".github/logos/adminer.svg" width="28" height="28" alt=""> | `adminer` | every installed MySQL / MariaDB / PostgreSQL / ClickHouse service |
| <img src=".github/logos/elasticvue.svg" width="28" height="28" alt=""> | `elasticvue` | Elasticsearch |
| <img src=".github/logos/kafka-ui.svg" width="28" height="28" alt=""> | `kafka-ui` | Kafka |
| <img src=".github/logos/mongo-express.svg" width="28" height="28" alt=""> | `mongo-express` | MongoDB |
| <img src=".github/logos/opensearch-dashboards.svg" width="28" height="28" alt=""> | `opensearch-dashboards` | OpenSearch |
| <img src=".github/logos/pgadmin.svg" width="28" height="28" alt=""> | `pgadmin` | every installed PostgreSQL service |
| <img src=".github/logos/phpmyadmin.svg" width="28" height="28" alt=""> | `phpmyadmin` | every installed MySQL / MariaDB service |
| <img src=".github/logos/redisinsight.svg" width="28" height="28" alt=""> | `redisinsight` | Redis |
| <img src=".github/logos/typesense-dashboard.svg" width="28" height="28" alt=""> | `typesense-dashboard` | Typesense |

**Search & analytics**

| | Service | What it is |
|:-:|---|---|
| <img src=".github/logos/elasticsearch.svg" width="28" height="28" alt=""> | `elasticsearch` | Elasticsearch single-node engine |
| <img src=".github/logos/meilisearch.svg" width="28" height="28" alt=""> | `meilisearch` | Meilisearch search engine · **built into Lerd** |
| <img src=".github/logos/opensearch.svg" width="28" height="28" alt=""> | `opensearch` | OpenSearch single-node engine |
| <img src=".github/logos/solr.svg" width="28" height="28" alt=""> | `solr` | Apache Solr, the search backend Drupal and TYPO3 expect |
| <img src=".github/logos/typesense.svg" width="28" height="28" alt=""> | `typesense` | Typesense typo-tolerant search |

**Cache, queues & messaging**

| | Service | What it is |
|:-:|---|---|
| <img src=".github/logos/beanstalkd.svg" width="28" height="28" alt=""> | `beanstalkd` | Beanstalkd work queue |
| <img src=".github/logos/kafka.svg" width="28" height="28" alt=""> | `kafka` | Apache Kafka event streaming broker |
| <img src=".github/logos/memcached.svg" width="28" height="28" alt=""> | `memcached` | Memcached in-memory cache |
| <img src=".github/logos/mercure.svg" width="28" height="28" alt=""> | `mercure` | Mercure hub for server-sent events, the Symfony realtime transport |
| <img src=".github/logos/rabbitmq.svg" width="28" height="28" alt=""> | `rabbitmq` | RabbitMQ broker with management UI |
| <img src=".github/logos/redis.svg" width="28" height="28" alt=""> | `redis` | Redis in-memory store · **built into Lerd** |
| <img src=".github/logos/soketi.svg" width="28" height="28" alt=""> | `soketi` | Pusher-compatible WebSocket server |
| <img src=".github/logos/valkey.svg" width="28" height="28" alt=""> | `valkey` | Valkey, the Redis-compatible cache (coexists with Redis) |

**AI & models**

| Service | What it is |
|---------|------------|
| `ollama` | Ollama local LLM server with automatic model bootstrap |
| `open-webui` | Persistent chat interface connected to the Lerd Ollama service |

Ollama currently bootstraps `qwen3-embedding:8b`, an embeddings model; that
bootstrap alone does not provide a chat model. Pull a chat-capable model into
Ollama before using Open WebUI for chat. Open WebUI keeps its application data
under `/app/backend/data` and reaches Ollama at `http://lerd-ollama:11434` from
the shared Lerd service network.

**Content management**

| Service | What it is |
|---------|------------|
| `grav` | Harvester Grav CMS runtime, built from the reviewed project Dockerfile (requires the local `blogger-grav` image) |

**Content management**

| Service | What it is |
|---------|------------|
| `grav` | Harvester Grav CMS runtime, built from the reviewed project Dockerfile (requires the local `blogger-grav` image) |

**Testing & tooling**

| | Service | What it is |
|:-:|---|---|
| <img src=".github/logos/floci.svg" width="28" height="28" alt=""> | `floci` | Floci, the open-source AWS emulator, no auth token and coexists with LocalStack |
| <img src=".github/logos/gotenberg.svg" width="28" height="28" alt=""> | `gotenberg` | Gotenberg API for PDF and document conversion |
| <img src=".github/logos/localstack.svg" width="28" height="28" alt=""> | `localstack` | LocalStack, the AWS APIs run locally (SQS, SES, DynamoDB, Secrets Manager) |
| <img src=".github/logos/mailpit.svg" width="28" height="28" alt=""> | `mailpit` | Mailpit SMTP catcher with a web inbox · **built into Lerd** |
| <img src=".github/logos/rustfs.svg" width="28" height="28" alt=""> | `rustfs` | RustFS S3-compatible object storage · **built into Lerd** |
| <img src=".github/logos/selenium.svg" width="28" height="28" alt=""> | `selenium` | Headless Chromium with a noVNC viewer for browser tests |
| <img src=".github/logos/spamassassin.svg" width="28" height="28" alt=""> | `spamassassin` | SpamAssassin scoring backend for the Mailpit catcher |
| <img src=".github/logos/stripe-mock.svg" width="28" height="28" alt=""> | `stripe-mock` | Stripe API mock server |
| `github-actions-runner` | Persistent self-hosted GitHub Actions runner; use the linked Lerd skill for per-project configuration and its private Docker worker |

Don't see what you need? [Add it](#contributing) — that's what this repo is for.

### GitHub Actions runner

`github-actions-runner` is the runner image base. It deliberately has no ports and
contains no repository credentials. Use the
[`lerd-add-actions-runner` skill](https://github.com/miguelenes/lerd-actions-runner/tree/main/skill)
to create a site-named Lerd custom service with that image, register it with a
short-lived token, and add the host worker that supervises its private Docker
sidecar. This workflow supports Linux x64, rootless Podman, and systemd user
services for trusted private GitHub repositories. Do not run untrusted pull
requests, forks, or `pull_request_target` jobs on this persistent runner. The
released image is pinned by manifest digest in the service index. The skill owns
the per-project runner URL, labels, and lifecycle.

To check that the published image is available and refuses tokenless startup, dispatch the opt-in hosted smoke workflow after it is present on the target repository:

```bash
gh-axi workflow run runner-image-smoke.yml --ref main --repo lerd-env/services
gh-axi run list --workflow "Runner image smoke" --limit 5 --repo lerd-env/services
gh-axi run view <run-id> --repo lerd-env/services
```

The workflow runs on a temporary `ubuntu-latest` GitHub-hosted runner. It does not register a runner or prove full runner operation.

## Usage

You rarely touch the store directly: everything routes through the usual service commands.

```bash
lerd service search                  # list everything available
lerd service search search-engine    # search by name, description, or family
lerd service preset phpmyadmin        # install a preset (fetched on demand)
lerd service preset mariadb --version 11.8   # pick a version on multi-version presets
```

Installed presets are cached locally and auto-refresh every 24 hours, so improvements landed here reach existing installs without an update.

## Contributing

New services and version bumps are welcome — this store is only as good as the community around it.

1. Fork this repo
2. Add or update `services/<name>.yaml`
3. Optionally add the service's own mark as `services/<name>.svg` (see below), then run `python3 .github/scripts/readme_logos.py` to draw its tile for this README
4. Add or update the matching entry in `services/index.json` (name, description, and optionally family, dashboard, depends_on)
5. Open a pull request

Keep images pinned to a specific tag or a `track_latest` family; avoid `:latest` for anything that stores data.

### Preset schema

Definitions live under `services/`: an `index.json` catalogue plus one `<name>.yaml` per preset. A minimal preset:

```yaml
name: my-service
image: docker.io/example/my-service:1
description: What it is
ports:
  - "8099:80"
```

Common fields build on that:

```yaml
family: my-family          # group alternates + dashboards for auto-discovery
versions:                  # multi-version family (all share the canonical port)
  - tag: "2"
    image: docker.io/example/my-service:2
    canonical: true
env_vars:                  # keys injected into the project .env
  - MY_HOST=lerd-{{name}}
dynamic_env:               # computed at install time (e.g. family discovery)
  MY_HOSTS: discover_family:my-family
depends_on:                # started first
  - mysql
dashboard: http://localhost:8099
files:                     # config-file mounts (static content, or a generator)
  - target: /etc/my-service/config
    content: |
      key = value
introspect:                # database engines only: power the web UI Databases tab
  list_databases: >        # print one "name<TAB>size_bytes" row per user database
    psql -U postgres -tAc
    "SELECT datname || chr(9) || GREATEST(pg_database_size(datname)
    - (SELECT pg_database_size('template1')), 0) FROM pg_database
    WHERE datistemplate = false AND datname <> 'postgres' ORDER BY datname"
extensions:                # postgres engines only: what the image can create
  - name: vector           # created wherever Lerd creates a database
    always: true
    types: [vector]        # a dump naming one of these brings the extension with it
```

### How a preset appears in the dashboard

Three fields decide that, and all three live here rather than in lerd, so a new
service looks right the day it lands:

```yaml
category: databases    # discovery section: databases, cache, messaging, search,
                       # mail, admin, storage, testing, other
icon: database         # one of lerd's built-in glyphs
color: "#003545"       # the brand colour its mark is tinted with
```

`color` must be a plain hex literal, `#003545` or `#abc`. Anything else, a colour
function or a CSS variable, is dropped and the service falls back to its
category's tint. A colour too dark to read on lerd's dark card, or too light for
the light one, is nudged toward the card until it separates, so a near-black
brand still shows up.

### Shipping a service's own mark

`icon` can only borrow a glyph lerd already ships. To give a service its actual
logo, add `services/<name>.svg` next to its YAML. lerd fetches it with the
definition and caches it, so it reaches existing installs on the same 24 hour
refresh with no lerd release, and the dashboard serves it from that cache rather
than from here, which keeps it drawing offline.

The mark is **monochrome**: one silhouette of filled paths with no colours of its
own, tinted at render time by `color`. It renders at 20 px beside lerd's built-in
glyphs and has to work on a light and a dark card, so a full-colour brand mark is
not what this is for, and neither is a wordmark, which turns into a smear at that
size. Take the logo, not the lockup.

That markup is inlined into the dashboard, so lerd cuts it down on the way in.
Only `svg`, `g`, `path`, `circle`, `ellipse`, `rect`, `line`, `polyline` and
`polygon` survive, keeping their geometry alone: script, `foreignObject`, event
handlers, external references, and any `fill`, `stroke`, `style`, `class` or `id`
are stripped, as is anything over 32 KB. Keep the file to a bare
`<svg viewBox="…">` around its paths and nothing is lost:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="…"/></svg>
```

A file lerd refuses is simply not cached, and the service falls back to the glyph
its `icon` names. The marks currently in this repo come from
[Simple Icons](https://simpleicons.org), which is CC0.

Ship a mark only when it is the service's own. An admin UI has no business
borrowing the engine's: Mongo Express drawing the Mongo leaf in Mongo green makes
the two tiles indistinguishable, where falling back leaves it on the `admin` tint
and readable as the separate thing it is. phpMyAdmin ships a mark because it has
one of its own.

A family is the other way round. Every member of one is that engine, so they all
carry its mark and its colour: pgvector and TimescaleDB are Postgres, and both
draw the Postgres elephant in Postgres blue rather than a mark of their own.

The coloured tiles in this README are not the marks themselves. `.github/scripts/readme_logos.py` paints each mark in its declared colour on a white tile, so GitHub shows it in either theme, and a service without one gets the lerd glyph its `icon` names in its category's tint, from copies kept in `.github/glyphs/`. The six services built into lerd are listed too, from the marks and colours mirrored in `.github/builtin/`. It writes the result to `.github/logos/`; run it again whenever a service, its mark or its colour changes.

See the [service presets documentation](https://lerd.sh/usage/service-presets) for the full schema reference and every available field.

### Service bundle catalog (schema v1)

The existing catalog root remains `LERD_SERVICES_BASE_URL`. Single-service
clients continue to read `services/index.json` exactly as before. Bundle-aware
clients discover groups at `<LERD_SERVICES_BASE_URL>/bundles/index.json`; its
`schema_version` is `1`, and each entry points to a YAML descriptor by a safe
filename relative to the `bundles/` directory, for example
`bundles/firecrawl.yaml`.

Each descriptor declares its schema version, name, catalog version, description,
and components. A component has a unique name, immutable OCI image reference
(`@sha256:<64 lowercase hex digits>`), verified OS/architecture pairs, declared
ports, and readiness check. Optional fields describe component dependencies,
environment, generated or operator-supplied secret references, persistent state
mount paths, and positive CPU/memory caps. Component dependencies must resolve
inside the bundle and form an acyclic graph. Host-published ports are explicit;
the descriptor must keep host exposure on loopback. The schema rejects unknown
fields rather than passing arbitrary container or host commands through.

Bundle descriptors are catalog data, not Compose files. They do not support
builds, host mounts, privileged containers, device passthrough, or free-form
hooks. Resource caps are optional controls only; they are not minimum hardware
recommendations, and a static catalog check does not establish that a runtime
can enforce them. Do not put reusable credentials in catalog files. Use only
`secret://<name>` references for secret-valued bundle environment settings.

For a fresh checkout, install the pinned development dependencies and run the
network-free static preflight:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --requirement requirements-dev.lock
python3 tools/catalog_preflight.py
```

The same preflight and its invalid-catalog fixtures run in GitHub Actions on
pushes and pull requests with read-only repository permissions. It checks
schemas, index parity, descriptor paths, dependency graphs, image/platform
metadata, resource values, and secret literals. It does not pull images, start
containers, or claim that a compatible Lerd runtime can install or operate a
bundle. Runtime support is a prerequisite and must be verified separately in
the companion Lerd project.

### Local AI and Firecrawl

The Ollama preset bootstraps `qwen3-embedding:8b`, an embedding model; that
setting alone does not provide chat completions. Open WebUI is a separate
preset with its own persistent data at `/app/backend/data` and depends on the
`ollama` family. Both presets require a compatible Lerd runtime for dependency
and environment wiring. From a host process Ollama uses
`http://127.0.0.1:11434`; a Lerd container uses `http://lerd-ollama:11434`.

`services/bundles/firecrawl.yaml` describes a trusted-local stack: the
Firecrawl API, Playwright browser service, Redis cache/queue support, RabbitMQ
broker, and NuQ PostgreSQL database. PostgreSQL data persists at
`/var/lib/postgresql/data`; Redis and RabbitMQ are runtime state, not declared
durable stores. The API and database share a generated PostgreSQL password.
RabbitMQ credentials are operator-supplied and must match between its password
and the API's AMQP URL settings. Ollama integration is unset.

The catalog pins every component by immutable digest. The API is the
`2.11.162` release (`sha256:1b223ef1…e63`), whose image reports source commit
`7666c1f9ae8720a6bba271e0f60b6a217f8a5210`. At review time on 2026-10-14,
Playwright (`sha256:717699bf…fcc6`) and NuQ Postgres
(`sha256:9b638af7…e8fc`) were official GHCR `latest` manifests, pinned by their
observed digests; their source commit relationship to the API release was not
established. The API, browser and database manifests list Linux amd64 and
arm64. Known per-architecture compressed OCI sizes are API 571/559 MB,
Playwright 555/587 MB, and NuQ Postgres 162/160 MB (amd64/arm64). Redis
(`sha256:858f009f…3499`) and RabbitMQ (`sha256:e582c0bc…1f69`) are also
digest-pinned; their manifest architecture set includes Linux amd64 and arm64.
Digest pins make these observations reproducible, but do not prove the full
stack was run or that all component versions work together.

The API uses Firecrawl's self-host default `USE_DB_AUTHENTICATION=false`.
Its host port defaults to loopback, `http://127.0.0.1:3002`; projects in a
compatible Lerd container should use the API component's internal bundle
hostname and port 3002 (for example, `http://lerd-firecrawl-api:3002` only
when that runtime provides this alias). Loopback host publication does not
isolate the unauthenticated API from other containers on Lerd's shared network.
Treat every container that can reach that network as trusted. Do not expose this
API to untrusted callers or the LAN.

The reviewed Playwright source blocks direct requests to loopback/private
addresses, and an isolated build of the v2.11.162 source returned 403 for
loopback, RFC1918, link-local/metadata, and Docker bridge target addresses.
A controlled redirect-to-private end-to-end test did not complete, so that
behavior remains unverified. Source review found both browser request
interception and a local SSRF proxy that rechecks destination DNS; this is not
runtime proof for redirects. CVE-2026-32857 (GHSA-9j9r-wghq-j565) describes a
redirect-based SSRF bypass in Firecrawl 2.8.0 and earlier; it does not establish
a vulnerability in 2.11.162. The descriptor is documented only for
trusted-local development, not as safe for untrusted URL submissions. A
compatible Lerd runtime and a successful lifecycle/scrape check are still
required before installation can be claimed.

## License

MIT

# Design

## Context

See [proposal.md](proposal.md) for motivation and user-visible behavior. The store currently serves a flat `services/` directory rooted at `LERD_SERVICES_BASE_URL`; `services/index.json` and preset YAML files are fetched relative to that URL. The local store server points at this checkout’s `services/` directory. There is no schema or validator in the checkout, and the current Lerd service lifecycle owns one service preset at a time.

Firecrawl’s documented self-host stack is multi-container. Its quickstart disables API authentication and describes a trusted-network boundary. Lerd containers share a service network, so an internal service hostname is reachable from other Lerd containers even when the host-published port is loopback-only.

## Goals / Non-Goals

**Goals:**

- Define an additive bundle contract that fits the current service-catalog URL and does not change `services/index.json` for older Lerd versions.
- Describe container images, dependency order, readiness, internal endpoints, host publication, secrets, durable state, platforms, and optional enforced resource caps without embedding arbitrary Compose or shell behavior.
- Keep invalid or unsupported bundles from causing image pulls or partial provisioning.
- Pair the store artifacts with a versioned Lerd runtime contract and honest integration evidence.

**Non-Goals:**

- Accept arbitrary Compose files, builds from source, host mounts, privileged containers, device passthrough, or free-form hooks.
- Promise GPU access, production availability, a universal resource floor, or isolation from other containers on Lerd’s shared network.
- Package Context.dev credentials or enable a general-purpose self-modifying agent harness.

## Decisions

### Keep the registry under the existing service-catalog root

Store the bundle registry at `services/bundles/index.json` and descriptors at `services/bundles/<slug>.yaml`. From the existing base URL, Lerd fetches `bundles/index.json` and descriptor paths relative to that catalog root. This keeps the current local server and published service URL usable. Keep `services/index.json` byte-for-byte compatible with older Lerd clients.

The bundle index is a JSON object with `schema_version: 1` and a `bundles` array. Each entry has a unique `name`, `description`, and relative `descriptor` path. The bundle descriptor repeats `schema_version: 1`, carries its own `name` and release `version`, and contains a non-empty `components` array. A Lerd runtime that does not support schema version 1 does not fetch or install the bundle registry.

**Alternative considered:** Put `bundles/` at the repository root. That would not be reachable from the currently configured local catalog base URL, which serves the `services/` directory, without another server root or a second URL setting.

### Use strict, typed descriptors and schemas

Use JSON Schema Draft 2020-12 for `schema/service-preset-v1.schema.json`, `schema/bundle-index-v1.schema.json`, and `schema/service-bundle-v1.schema.json`. YAML descriptors are parsed to JSON-compatible values before validation. A Python 3 preflight command (`python3 tools/catalog_preflight.py`) uses pinned PyYAML and `jsonschema` development dependencies from a lock file. It has no network access and does not start containers.

Bundle schemas reject unknown fields. Structural rules include:

| Field | Type and validation |
|---|---|
| `schema_version` | Integer; bundle format requires exactly `1`. |
| `name` | Lowercase DNS-style slug, unique in its index; maximum 32 characters for bundle names and 24 for component names. |
| `components` | Non-empty array with unique component names. |
| `image` | OCI reference with a `@sha256:` digest followed by exactly 64 hexadecimal characters. |
| `depends_on` | Array of component slugs; no duplicates, unknown names, self-dependencies, or cycles. |
| `supported_hosts` | Non-empty array of unique `{os, architecture}` pairs; `os` is `linux` or `macos`, `architecture` is `amd64` or `arm64`. Runtime maps host architecture to the matching Linux OCI architecture under Podman. |
| `ports` | Container and optional requested host ports are integers from 1 through 65535; only declared bundle entrypoints can request host publication. |
| `readiness` | Structured `tcp` or `http` check; TCP names a component port, HTTP also requires an absolute path. No shell command is accepted. |
| `state` | Array of uniquely named volumes with absolute, non-root container mount paths; parent traversal and overlapping paths are rejected. |
| `environment` | Map from valid environment-variable names to non-secret literal strings or declared internal endpoint references. |
| `secrets` | Array of `{name, target_env, source}` entries where `source` is `generated` or `operator`; there is no secret-literal field. |
| `resources` | Optional `cpu_millis` and `memory_bytes` positive integers, interpreted as enforced upper limits. They are rejected on host/runtime profiles that cannot enforce them. |

The validator checks cross-field rules JSON Schema cannot express reliably: catalog-to-file parity, duplicate names and endpoints, descriptor path traversal, dependency cycles, unique mount paths, and supported-host/image-manifest compatibility metadata. Secret checks scan all committed descriptors for known secret assignments and credential-like literals, while allowing documented placeholders and test fixtures.

### Make bundle provisioning preview-first and retryable

Before fetching any component image, Lerd validates the full bundle, checks every image reference and host platform, and obtains image sizes where the registry provides them. It displays all images with their individual sizes and the known aggregate; unknown sizes are labelled unknown. No image is fetched until the operator confirms, following current Lerd service-install behavior. A failed preflight fetches no image and creates no units or volumes.

Model weights are separate from OCI images. Before the existing Ollama preset’s `OLLAMA_PULL_MODELS` bootstrap runs, Lerd shows the configured model names, reports an authoritative size when available (otherwise `unknown`), and asks for confirmation. This avoids hiding a potentially large model download behind the Open WebUI dependency.

Serialize lifecycle operations per bundle. Repeated install/start/stop operations reconcile the declared state without duplicating units or volumes. If another lifecycle operation is active, return a conflict naming the bundle and operation without mutating state. Persist the bundle descriptor locally so status, stop, and remove work when the catalog is unavailable; install/update that need missing images fail before mutation when offline.

Represent every runtime operation by bundle and component, with phase (`resolve`, `pull`, `create`, `start`, `health`, `update`, or `remove`), state, and a redacted error message. A partial failure stops dependants that cannot function, keeps declared data, and leaves enough state to retry or inspect. Update is not advertised as transactional: it reports which images/components changed and preserves data for retry or rollback. Removing a bundle retains data by default; explicit data removal follows Lerd’s existing recoverability policy.

**Alternative considered:** Treat the bundle as one opaque container or pass through Docker Compose. Both options lose per-component failure detail and bypass Lerd’s normal service ownership, confirmation, and recovery behavior.

### Keep networks and published endpoints explicit

Connect bundle members to Lerd’s shared service network. Give each component the stable hostname `lerd-<bundle>-<component>`; the slug limits keep this under the 63-character DNS label limit. Internal service ports are never host-published by default. A declared bundle entrypoint may request a host port, which binds to `127.0.0.1`; if the requested port is busy, use Lerd’s existing next-free-port behavior and return the assigned port.

Project containers use internal service hostnames and container ports. Host processes use loopback URLs and assigned host ports. A separate private network would require a routing proxy to support Lerd project containers; it is deferred. Because the current service network is shared, every Lerd container must be treated as able to reach a bundle’s internal API.

### Keep credentials out of catalog and output

Generate bundle-internal credentials during installation or request them from the operator. Persist them in Lerd’s user-only local state with mode `0600`; pass them only to the components that need them. Do not write them into `services/bundles/`, the project’s `.env`, a committed `.lerd.yaml`, endpoint URLs, logs, status output, diagnostics, or failure messages. The catalog preflight rejects literal secrets before CI succeeds.

Firecrawl’s documented local baseline does not enable API authentication. Keep its host-published API on loopback and label the bundle trusted-local development software. Explicitly disclose that any container on Lerd’s shared network can call its internal API. Never present loopback binding as project-level isolation or production security.

Before selecting a Firecrawl release, review its current security advisories and test both a direct private-address target and a public URL that redirects to a private address. Record exactly what the upstream release blocks. If redirect and private-address behavior cannot be verified, do not advertise the bundle as safe for untrusted callers; keep the documented use boundary to projects and agents the operator trusts.

### Verify image support before publishing the Firecrawl descriptor

Pin every required image by digest and list the supported host OS/architecture pairs for the complete component set. Compare API and Playwright image versions to one Firecrawl release’s Compose configuration, and verify that the API, Playwright, Redis, RabbitMQ, and `nuq-postgres` images are published and support the declared pairs. Do not build images from source during service installation. If a required image is missing for a host profile, omit that profile until a compatible reviewed image exists.

Firecrawl’s `OLLAMA_BASE_URL` stays unset unless the operator selects the Lerd Ollama endpoint. Keep the initial bundle’s CPU/memory limits absent unless a particular profile has verified runtime enforcement; no universal Firecrawl sizing value is claimed.

### Separate static preflight from runtime acceptance

The local preflight validates all service YAML and indexes, bundle YAML and index, supported schema versions, image syntax, index parity, dependencies, platform/resource metadata, and secret hygiene. CI runs the same command on pull requests and pushes, with read-only repository permission; the workflow performs no image pulls and requires no secrets. The existing `runner-image-smoke.yml` remains independent and `workflow_dispatch`-only.

Before publishing Firecrawl, run a supported rootless-Podman integration check that installs the bundle, confirms readiness per component, scrapes a controlled public URL, and verifies an intentionally stopped required component produces a named not-ready result. Lerd’s companion code change also passes the existing `lerd-preflight` and a live CLI, UI, and MCP smoke check.

## Risks / Trade-offs

- **Risk:** One image or platform is unavailable after earlier members have started. → **Mitigation:** Resolve every image and platform before the first pull; report partial runtime failures by component and retain data.
- **Risk:** The bundle can download a large amount of image and model data. → **Mitigation:** Show image totals before confirmation and surface Ollama model names and known/unknown sizes before bootstrap.
- **Risk:** Firecrawl’s unauthenticated API can be reached by any container on Lerd’s shared network and can fetch external URLs. → **Mitigation:** Keep host exposure loopback-only, state the trusted-container boundary, review redirect/private-target behavior, and do not claim production or untrusted-caller safety.
- **Risk:** Registry outage prevents discovery or update. → **Mitigation:** Cache installed descriptors and keep status/stop/remove available from local state; do not partially install from an unavailable registry.
- **Risk:** Store and Lerd runtime support ship at different times. → **Mitigation:** Keep the bundle registry separate and require runtime schema-version support before discovery or installation.

## Migration Plan

1. Add the schemas, catalog preflight, CI workflow, and contributor documentation without changing `services/index.json` or existing preset behavior.
2. Land the companion Lerd runtime change and validate a small fixture bundle through version gating, preview, lifecycle, recovery, and endpoint wiring.
3. Add Open WebUI and document the current Ollama model bootstrap before enabling the dependent path.
4. Select and security-review a Firecrawl release, then add its bundle descriptor only for verified images and host profiles.
5. Run static preflight, the controlled scrape integration, and Lerd’s live preflight before describing the bundle as ready.

Rollback disables bundle-registry discovery in Lerd while leaving existing single-service presets intact. Bundle removal keeps declared data unless the operator explicitly requests its removal; no rollback step deletes persistent state implicitly.

## Open Questions

None remain that change the registry path or first-version contract. The selected Firecrawl release and its exact images/platforms are implementation-time evidence gates; an unverified image or host profile is excluded rather than guessed.

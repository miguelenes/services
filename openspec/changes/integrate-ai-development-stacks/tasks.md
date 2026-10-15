# Tasks

## 1. Define and validate the service-store contracts

- [x] 1.1 Add Draft 2020-12 schemas for existing service presets, the bundle index, and bundle descriptors; verify every current preset and index entry validates and negative fixtures fail with file and field details.
- [x] 1.2 Add the Python catalog preflight command with pinned YAML/schema dependencies; verify full-catalog mode checks index parity, duplicate names, safe paths, dependency cycles, image/platform metadata, resource-limit shape, and secret literals without network access or container operations.
- [x] 1.3 Add a read-only CI workflow for push and pull-request events that runs the exact documented preflight command; verify invalid schema, index, dependency, platform, resource, and secret fixtures fail without pulling images.
- [x] 1.4 Document bundle/index paths relative to the existing `LERD_SERVICES_BASE_URL`, descriptor fields, safety limits, the local preflight command, and CI behavior in the contribution guide; verify the documented command works from a fresh checkout.

## 2. Prepare the catalog entries and documentation

- [x] 2.1 Add a digest-pinned Open WebUI preset with persistent app data, dependency on the `ollama` family, and internal `OLLAMA_BASE_URL`; verify schema validation and static dependency resolution against the existing Ollama preset.
- [x] 2.2 Review Firecrawl API 2.11.162 and the pinned supporting image snapshot for digests, architectures, configuration, authentication defaults, advisories, and direct/redirect-to-private-address behavior.

  Evidence recorded in services/bundles/firecrawl.yaml and the service documentation: API 2.11.162 digest sha256:1b223ef18d410f67615f32ccaa3dcedfc26af4286f096247bddca3b624545e63 reports source commit 7666c1f9ae8720a6bba271e0f60b6a217f8a5210. Official GHCR Playwright and NuQ Postgres latest manifest digests are sha256:717699bf8a61d94451926c810d19ca1d36278192907e307bf5229a558b08fcc6 and sha256:9b638af78d99873bc0ba2b57c9cbcd01df6ce96efeaa72d36cfbe0f76521e8fc; their source-commit relationship to that API release is unknown. Redis 7 Alpine and RabbitMQ 3-management are pinned to sha256:858f009f9709ce576febc734aa78b8f6d624b82571f9ddb6bda4377c833b3499 and sha256:e582c0bc7766f3342496d8485efb5a1df782b5ce3886ad017e2eaae442311f69. All five manifests list Linux amd64 and arm64. Upstream Compose uses Redis, RabbitMQ, Playwright and NuQ Postgres as internal dependencies; API auth defaults off (USE_DB_AUTHENTICATION=false), so the descriptor is restricted to trusted-local development. An isolated Playwright source build returned 403 for direct loopback, RFC1918, link-local/metadata and Docker bridge targets. Redirect-to-private end-to-end behavior was not observed; source inspection found request interception plus destination DNS checks in the SSRF proxy, but this is not treated as runtime proof. GHSA-9j9r-wghq-j565 / CVE-2026-32857 affects Firecrawl 2.8.0 and earlier. The unverified release provenance and redirect behavior are explicitly disclosed; no unverified OS/architecture pair or untrusted-caller compatibility is claimed.
- [x] 2.3 Add the Firecrawl bundle descriptor with isolated dependencies, durable state, generated/operator-supplied secret references, internal readiness, loopback API publication, supported hosts, and Ollama unset by default; verify static preflight rejects unsupported descriptor settings and that catalog files contain no reusable secrets.
- [x] 2.4 Update catalog documentation with Ollama/Open WebUI model semantics, bundle components, data expectations, host and in-network URL examples, image metadata, Firecrawl’s unauthenticated shared-network boundary, and an explicit compatible-runtime prerequisite; verify each statement against the descriptors and recorded source evidence.
- [x] 2.5 Run the catalog preflight over all presets and bundles and review index-to-descriptor parity; verify `services/index.json` and existing single-service preset behavior remain unchanged.

## Deferred companion scope — Lerd runtime

The following work is retained as a separate companion change and is not counted as completion of this service-store change:

- Implement version-gated bundle discovery, descriptor caching, preflight-before-pull, platform checks, download preview/confirmation, grouped lifecycle, readiness, recovery, offline management, secret handling, and supported resource limits; verify through Lerd CLI, UI, and MCP.
- Implement Ollama model-bootstrap disclosure and confirmation, including model names and known/unknown sizes; verify direct and dependency-triggered startup without redownloading persistent models.
- Update Lerd’s `lerd-dev` and `lerd-preflight` workflows; verify supported-host bundle lifecycle and a real Firecrawl scrape, recording runtime version and host profile.
- Gate any claim that Firecrawl is installable or runtime-ready on the companion’s successful lifecycle, trust-boundary, and scrape evidence.

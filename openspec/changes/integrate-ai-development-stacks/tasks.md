# Tasks

## 1. Define and validate the store contracts

- [ ] 1.1 Add Draft 2020-12 schemas for existing service presets, the bundle index, and bundle descriptors; verify every current preset/index entry validates and negative fixtures fail with file and field details.
- [ ] 1.2 Add the Python catalog preflight command with pinned YAML/schema dependencies; verify full-catalog mode checks index parity, duplicate names, paths, dependency cycles, image/platform metadata, resource limits, and secret literals without network access.
- [ ] 1.3 Add a read-only CI workflow for push and pull-request events that runs the exact documented preflight command; verify invalid schema, index, dependency, platform, resource, and secret fixtures fail the job without pulling images.
- [ ] 1.4 Document bundle/index paths relative to the existing `LERD_SERVICES_BASE_URL`, descriptor fields, safety limits, local preflight command, and CI behavior in the contribution guide; verify the example command works from a fresh checkout.

## 2. Add the Lerd runtime companion

- [ ] 2.1 Implement bundle registry fetch and schema-version gating relative to the service-catalog base URL; verify a runtime supporting version 1 discovers a fixture at `bundles/index.json` and an older runtime continues using `services/index.json` only.
- [ ] 2.2 Implement complete bundle preflight for descriptor, host/image platform, ports, readiness, secret references, and dependency cycles; verify every invalid case fails before any image pull or unit/volume creation.
- [ ] 2.3 Implement aggregate image-size preview, explicit confirmation, offline descriptor caching, and component-level lifecycle serialization; verify no image is fetched before confirmation, status/stop/remove work offline, and duplicate or concurrent operations do not create duplicate state.
- [ ] 2.4 Implement grouped install/start/inspect/update/stop/remove, dependency readiness, persistent-state retention, retryable partial-failure reporting, secret redaction, and supported optional CPU/memory limits; verify each lifecycle and failure path through CLI, UI, and MCP, including unsupported-limit rejection before pull.
- [ ] 2.5 Update `lerd-dev` and `lerd-preflight` for bundle setup, host/container URLs, the trusted-network boundary, and the live bundle smoke; verify the companion runtime passes the full local preflight and a fixture-bundle lifecycle smoke.

## 3. Publish the Ollama and Open WebUI path

- [ ] 3.1 Add a digest-pinned Open WebUI preset with persistent app data, dependency on the `ollama` family, and internal `OLLAMA_BASE_URL`; verify preset schema validation and dependency resolution against the existing Ollama preset.
- [ ] 3.2 Add Ollama model-bootstrap disclosure before download, including configured model names, known/unknown size, and explicit confirmation; verify it prompts only for models absent from persistent model data and works whether Ollama starts directly or through Open WebUI.
- [ ] 3.3 Verify Open WebUI lists models on a supported CPU-only rootless-Podman profile and model data survives container recreation; document the exact host and in-container URLs and observed model/bootstrap behavior in the AI section of README.

## 4. Add the Firecrawl bundle

- [ ] 4.1 Select one Firecrawl release and verify API, Playwright, Redis, RabbitMQ, and `nuq-postgres` image digests, host architectures, config, authentication defaults, current advisories, and direct/redirect-to-private-address behavior; record evidence and exclude any unverified host profile or release.
- [ ] 4.2 Add the Firecrawl descriptor under `services/bundles/` with isolated dependencies, durable state, generated/operator secrets, internal readiness, loopback API publication, supported hosts, and Ollama unset by default; include resource caps only on profiles where they are enforceable and verify preflight rejects unsupported settings before pulls.
- [ ] 4.3 Run the bundle on a supported rootless-Podman host and issue a controlled `POST /v2/scrape`; verify Markdown extraction, component readiness, named failure when a required member is stopped, and the recorded private/redirect target policy.
- [ ] 4.4 Document Firecrawl’s components, data retention, image sizes, host/in-network URLs, unauthenticated API reachability from Lerd containers, trusted-local use, and verified target-safety behavior; verify each documented claim against the selected release and integration result.

## 5. Complete cross-catalog integration

- [ ] 5.1 Run the catalog preflight over all current presets and bundles and review index-to-descriptor metadata parity; verify legacy service entries and searches are unchanged.
- [ ] 5.2 Run the compatible runtime against the local service-store URL and verify it fetches the descriptor from `bundles/index.json`, previews all required images, and completes the supported fixture and Firecrawl smoke paths; record runtime version and host profile.
- [ ] 5.3 Validate both OpenSpec changes with strict validation and review task/status evidence; verify no deferred capability or unsupported platform is represented as installable.

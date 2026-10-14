# Proposal

## Why

Lerd’s service catalog currently describes one container per preset, while a useful local AI and web-research setup combines independently stateful services. Firecrawl’s self-hosted topology needs several coordinated containers; treating it as a normal preset would hide its lifecycle, download cost, readiness, network trust boundary, and recovery behavior.

This change defines an additive bundle contract for the service store and pairs it with a Lerd runtime change so developers can use Ollama, Open WebUI, and Firecrawl through the project setup they already use.

## What Changes

- Define a versioned bundle registry and descriptor format under `services/bundles/`, rooted at the existing service-catalog URL so local and hosted Lerd installations can fetch it without changing their base URL. Preserve `services/index.json` for existing clients.
- Add schemas and a local preflight validator for current presets, bundle descriptors, indexes, dependencies, image/platform declarations, resource limits, and secret hygiene. Run the network-free static preflight in repository CI.
- Add a companion Lerd runtime change for version-gated bundle discovery, grouped lifecycle and per-component health, persistent state, recovery, local-only host publishing, confirmation before image pulls, and readable component-level failures.
- Build on the existing Ollama preset, add an Ollama-dependent Open WebUI preset, and disclose Ollama’s configured model bootstrap before it downloads model data.
- Add a Firecrawl bundle only after one upstream release’s images, platform support, persistence, authentication baseline, and redirect/private-address protections have been reviewed. Ollama remains an explicit optional provider.
- Document host-loopback and Lerd-network URLs, model and image downloads, and Firecrawl’s trusted-local access boundary. Update the Lerd development guidance and run the Lerd preflight against the companion runtime surface.

## User Stories and Acceptance Criteria

### A contributor validates the catalog before review

- **Given** a catalog checkout with preset and bundle schemas, **when** the contributor runs the documented preflight, **then** every indexed descriptor validates and index, dependency, platform, resource, or secret errors identify the invalid file and field.
- **Given** a pull request changes catalog data, **when** CI runs, **then** the same static preflight runs without pulling images or requiring credentials.

### A Lerd developer discovers a local AI service

- **Given** a Lerd runtime that supports the bundle schema, **when** the developer searches the catalog, **then** Ollama, its dependent Open WebUI preset, and the compatible Firecrawl bundle show their requirements and endpoints.
- **Given** an older Lerd runtime, **when** it reads the existing service catalog, **then** its `services/index.json` behavior remains unchanged and it ignores the separate bundle registry.
- **Given** starting Ollama will bootstrap configured models, **when** Lerd prepares that start, **then** it names the models, reports a size when it can verify one (otherwise says it is unknown), and requests confirmation before the model download.

### A project connects to a local service

- **Given** a project runs inside a Lerd PHP or custom container, **when** it connects to a bundle service, **then** Lerd supplies the service’s internal hostname and container port.
- **Given** a developer calls a service from a host process, **when** they follow the setup guide, **then** it uses the loopback URL and never gives the host a container-only hostname.

### A developer operates Firecrawl safely

- **Given** the selected Firecrawl release passes the image, platform, and network-safety review, **when** the developer installs it, **then** Lerd presents the component image downloads before pulling, starts dependencies in readiness order, preserves declared data, and binds its host API to loopback by default.
- **Given** Firecrawl’s local API has no authentication and is reachable on Lerd’s shared container network, **when** the bundle is presented, **then** Lerd identifies it as trusted-local development software and states that other containers on that network can reach it.
- **Given** every container is healthy, **when** the integration smoke submits a controlled public URL and follows the result, **then** readiness is reported only after Firecrawl returns the expected extraction; a failed component or scrape names the failing component or stage.
- **Given** an update or start fails partway through, **when** the developer retries or inspects the bundle, **then** component states and retained data are available and the retry does not create duplicate units or volumes.

## Non-Functional Requirements

- Validate the entire descriptor and host compatibility before the first image pull. Show known aggregate image sizes, identify unknown sizes, and require confirmation before fetching images, following Lerd’s current service-install behavior.
- Keep generated or operator-supplied credentials in local user-only Lerd state; do not include secret values in catalog data, project endpoint values, logs, status output, or error details.
- Serialize concurrent lifecycle operations per bundle and make repeated install/start/stop operations idempotent.
- Bind host-published endpoints to `127.0.0.1` by default. Do not claim that this isolates an endpoint from containers on Lerd’s shared network.
- Use immutable image references for bundle components. Declare supported host OS/architecture combinations and reject unsupported combinations before pulling.
- Treat resource limits as optional enforced caps only on profiles where the Lerd runtime supports them. Do not claim universal minimum resource requirements.
- Preserve existing single-service catalog behavior and state-retention defaults.

## Capabilities

### New Capabilities

- `service-bundles`: versioned, validated, lifecycle-managed groups of container services with bounded networking, state, secrets, downloads, and recovery.
- `local-ai-development`: discoverable Ollama, Open WebUI, and Firecrawl paths with accurate endpoint, model-download, readiness, and trust-boundary behavior.

### Modified Capabilities

None. This checkout has no published OpenSpec capability specs.

## Impact

This repository will add `services/bundles/`, schemas under `schema/`, a preflight tool and CI workflow, and contributor and service documentation. A companion change in the Lerd runtime must consume `bundles/index.json` relative to the existing service-catalog base URL and provide bundle lifecycle, network, secret, download-preview, and readiness behavior before the Firecrawl descriptor is published. The Lerd development guidance and `lerd-preflight` workflow also need companion updates. No service-store or Lerd runtime code is implemented by this proposal.

## Deferred Ideas

- A broad AI lab catalog (LiteLLM, Langfuse, vector stores, workflow builders, and more crawlers) until one bundle is maintained through upgrades and recovery.
- GPU passthrough, hardware-specific model profiles, and performance promises; support varies by host and rootless container runtime.
- Context.dev as a container preset; it is a hosted API integration and should remain an optional client-side provider with operator-managed credentials.
- Self-modifying agent harnesses and their evaluation loops; those need a separate evaluator, sandbox, and acceptance controls.
- Fine-grained per-project network isolation or private-target allowlists until the selected Firecrawl release and Lerd networking model can support and verify them end to end.

## Assumptions

- The bundle registry will be served relative to the current `services/` catalog root. The local Lerd store server currently serves this checkout’s `services/` directory, so `services/bundles/index.json` is reachable as `<LERD_SERVICES_BASE_URL>/bundles/index.json`.
- The Lerd runtime team will accept a separate companion change. This store alone cannot run a multi-container bundle.
- The Firecrawl self-host quickstart is a trusted-network development setup with API authentication disabled; the first bundle is not a production deployment. Every container on Lerd’s shared network must be treated as trusted to call its internal API.
- The chosen Firecrawl release will pass a review of current advisories and a redirect-to-private-address test. If that behavior cannot be verified, the bundle will not be advertised as ready for use by untrusted callers.
- The first Ollama path is CPU-capable and local. GPU access is not implied by an Ollama image.
- Any per-component CPU and memory limits are optional operator controls only where the current runtime can enforce them; they are not a sizing recommendation or a guarantee that Firecrawl has enough resources.
- Presets and bundles never embed hosted API credentials. Required Firecrawl secrets are generated or supplied through Lerd’s local secret handling.

## Evidence

- The service-store README and current local Lerd setup use `services/index.json` and a base URL rooted at the `services/` directory. The Ollama preset at `services/ollama.yaml` declares the `ollama` family, an internal URL, persistent model data, and `OLLAMA_PULL_MODELS=qwen3-embedding:8b`.
- Firecrawl’s [self-hosting guide](https://docs.firecrawl.dev/contributing/self-host) documents API authentication disabled for its trusted-network quickstart, warns against exposing that baseline to untrusted networks, and says a heartbeat does not verify dependencies or a scrape. Its [v2.11.162 Compose file](https://raw.githubusercontent.com/firecrawl/firecrawl/v2.11.162/docker-compose.yaml) includes the API, Playwright, Redis, RabbitMQ, and a Firecrawl-specific Postgres image; API and Playwright are built from source by default in that file, so matching published images and platforms need verification.
- The [CVE-2026-32857 advisory](https://github.com/advisories/GHSA-9j9r-wghq-j565) documents a redirect-based SSRF protection bypass in Firecrawl versions 2.8.0 and earlier. This does not establish a vulnerability in the proposed later release; it makes redirect and destination checks a release-selection gate.
- Ollama’s [Docker guide](https://docs.ollama.com/docker) documents persistent model storage and CPU/GPU differences. Open WebUI documents `OLLAMA_BASE_URL` in its [environment reference](https://docs.openwebui.com/reference/env-configuration/).
- Lerd’s [service preset guide](https://lerd.sh/usage/service-presets) documents preset dependencies and environment wiring. The existing Lerd workflow discloses image size before fetching an image. This checkout currently has no `schema/` directory or catalog validator, despite `AGENTS.md` requiring preset validation against a schema.

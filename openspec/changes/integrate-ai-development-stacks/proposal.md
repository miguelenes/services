# Proposal

## Why

Lerd’s service catalog currently describes one container per preset, while a useful local AI and web-research setup can combine independently stateful services. Firecrawl’s self-hosted topology needs several coordinated containers; representing it as a normal preset would hide its lifecycle, downloads, readiness, network trust boundary, and recovery behavior.

This change defines and validates the service-store side of a versioned bundle contract and catalogs a reviewed local AI path. Lerd runtime behavior is a separate companion change and is deferred; this change does not implement it or claim the bundles can already be installed.

## What Changes

- Define a versioned bundle registry and descriptor format under `services/bundles/`, rooted at the existing service-catalog URL so local and hosted Lerd installations can fetch it without changing their base URL. Preserve `services/index.json` for existing clients.
- Add schemas and a local preflight validator for current presets, bundle descriptors, indexes, dependencies, image/platform declarations, resource limits, and secret hygiene. Run the network-free static preflight in repository CI.
- Extend the catalog with an Ollama-dependent Open WebUI preset and a Firecrawl bundle only after the selected images, supported platforms, persistence, authentication baseline, and redirect/private-address behavior have been reviewed.
- Document the catalog contract, endpoint values, model/image download expectations, and Firecrawl’s trusted-local access boundary. Keep runtime setup guidance conditional on the companion Lerd support.
- Record the Lerd runtime behavior needed to consume these descriptors as a companion contract, including version gating, grouped lifecycle, readiness, local-only host publishing, download confirmation, and component-level failures. Implementation and runtime-only acceptance are deferred to that companion change.

## Capabilities

### New Capabilities

- `service-bundles`: versioned, validated catalog descriptors for groups of container services, defining dependencies, state, networking, secrets, downloads, platforms, and expected lifecycle behavior for a compatible Lerd runtime.
- `local-ai-development`: catalog definitions and accurate setup information for Ollama, Open WebUI, and a reviewed Firecrawl bundle, including endpoint, model-download, readiness, and trust-boundary expectations.

### Modified Capabilities

None. This checkout has no published OpenSpec capability specs.

## Impact

This repository will add `services/bundles/`, schemas under `schema/`, a preflight tool and CI workflow, and contributor and service documentation. A separate companion change in the Lerd repository must consume `bundles/index.json` relative to the existing service-catalog base URL and implement the runtime contract before any bundle is described as installable. Updating Lerd development guidance and its `lerd-preflight` workflow also belongs to that companion. This change owns no Lerd runtime implementation or runtime acceptance run.

## Deferred Ideas

- Implementing bundle discovery, grouped lifecycle, networking, readiness, secrets, download confirmation, and model-bootstrap confirmation in Lerd.
- Running a live bundle lifecycle or Firecrawl scrape, and changing Lerd’s `lerd-dev` or `lerd-preflight` workflows.
- A broad AI lab catalog (LiteLLM, Langfuse, vector stores, workflow builders, and more crawlers) until one bundle is maintained through upgrades and recovery.
- GPU passthrough, hardware-specific model profiles, and performance promises; support varies by host and rootless container runtime.
- Context.dev as a container preset; it is a hosted API integration and should remain an optional client-side provider with operator-managed credentials.
- Self-modifying agent harnesses and their evaluation loops; those need a separate evaluator, sandbox, and acceptance controls.
- Fine-grained per-project network isolation or private-target allowlists until the selected Firecrawl release and Lerd networking model can support and verify them end to end.

## Assumptions

- The bundle registry will be served relative to the current `services/` catalog root. The local Lerd store server currently serves this checkout’s `services/` directory, so `services/bundles/index.json` is reachable as `<LERD_SERVICES_BASE_URL>/bundles/index.json`.
- The Lerd runtime team will accept a separate companion change. This store alone cannot run a multi-container bundle.
- The Firecrawl self-host quickstart is a trusted-network development setup with API authentication disabled; the first bundle is not a production deployment. Every container on Lerd’s shared network must be treated as trusted to call its internal API.
- The chosen Firecrawl release will pass a review of current advisories and a redirect-to-private-address test. If that behavior cannot be verified, the bundle will not be advertised for use by untrusted callers.
- The first Ollama path is CPU-capable and local. GPU access is not implied by an Ollama image.
- Any per-component CPU and memory limits are optional operator controls only where the companion runtime can enforce them; they are not a sizing recommendation or a guarantee that Firecrawl has enough resources.
- Presets and bundles never embed hosted API credentials. Required Firecrawl secrets are generated or supplied through Lerd’s local secret handling.

## Evidence

- The service-store README and current local Lerd setup use `services/index.json` and a base URL rooted at the `services/` directory. The Ollama preset at `services/ollama.yaml` declares the `ollama` family, an internal URL, persistent model data, and `OLLAMA_PULL_MODELS=qwen3-embedding:8b`.
- Firecrawl’s [self-hosting guide](https://docs.firecrawl.dev/contributing/self-host) describes a trusted-network local setup with API authentication disabled and says a heartbeat does not verify dependencies or an actual scrape. Its [v2.11.162 Compose file](https://raw.githubusercontent.com/firecrawl/firecrawl/v2.11.162/docker-compose.yaml) includes the API, Playwright, Redis, RabbitMQ, and a Firecrawl-specific Postgres image; API and Playwright are built from source by default there, so matching published images and platforms need review.
- The [CVE-2026-32857 advisory](https://github.com/advisories/GHSA-9j9r-wghq-j565) documents a redirect-based SSRF protection bypass in Firecrawl versions 2.8.0 and earlier. It makes redirect and destination checks a release-selection gate; it does not establish a vulnerability in the proposed later release.
- Ollama’s [Docker guide](https://docs.ollama.com/docker) documents persistent model storage and CPU/GPU differences. Open WebUI documents `OLLAMA_BASE_URL` in its [environment reference](https://docs.openwebui.com/reference/env-configuration/).
- Lerd’s [service preset guide](https://lerd.sh/usage/service-presets) documents preset dependencies and environment wiring. This checkout currently has no `schema/` directory or catalog validator, despite `AGENTS.md` requiring preset validation against a schema.

# Discovery notes: AI development services in Lerd

## Opportunity

Make local inference and web research usable in Lerd projects through maintained service definitions, a coherent setup path, and verification that checks real readiness. The store already contains Ollama, so the opportunity is to build a dependable workflow around it and to add multi-container support for services whose upstream deployment is a stack.

## Round 1: breadth by perspective

### Product manager

1. Package a project-ready local AI path with explicit Lerd URLs and environment wiring.
2. Support both a small first-run path and an expandable service set so users can start without selecting many tools.
3. Offer Firecrawl as a maintained local option where data locality or repeatable scraping matters.
4. Make bundle install, update, and removal predictable as one user-visible service.
5. Define a minimum supported matrix of host platform, runtime, and images before promising compatibility.

### Product designer

1. Show a bundle as one discoverable catalog choice with its component services visible before install.
2. Preview image and model downloads, disk needs, and host-port use before the user starts the stack.
3. Show readiness per component and a useful reason when a dependent service is not ready.
4. Provide copyable host and in-container endpoint examples for project setup.
5. Make retry, stop, and cleanup actions understandable when one component fails during startup.

### Software engineer

1. Add a versioned bundle manifest with schema validation and a dependency-cycle check.
2. Give each bundle an isolated network and durable, named data for stateful members.
3. Model health checks, readiness ordering, startup failure, and retry as first-class lifecycle data.
4. Generate or request secrets without committing secret values to the catalog.
5. Smoke-test a real Firecrawl scrape through the published API, not only container liveness.

## Round 2: challenge and evidence

- **Adopt bundle manifests and grouped lifecycle.** Firecrawl’s pinned Compose example has five required service roles (API, Playwright, Redis, RabbitMQ, and a dedicated Postgres image). The current catalog describes individual image presets; `depends_on` alone does not capture per-bundle isolation, data ownership, or readiness. This requires a companion Lerd runtime change.
- **Adopt actual readiness and an end-to-end scrape check.** Firecrawl’s own guide says its heartbeat does not test Redis, PostgreSQL, RabbitMQ, Playwright, workers, or outbound access. A passing container check would be weak evidence.
- **Adopt local-only exposure and secret hygiene.** Firecrawl’s baseline has API authentication off and uses a database password that must be changed. A local preset must keep host access local and must never ship reusable credentials.
- **Adopt Open WebUI as a separate, dependent service.** Its documented `OLLAMA_BASE_URL` setting gives the existing Ollama preset a user-facing local interface while preserving the catalog’s reusable single-service model.
- **Adopt store schema and preflight validation.** The checkout contains neither `schema/` nor validation tooling although `AGENTS.md` requires schema validation before a change. The new contract needs a validator before catalog entries are merged.
- **Defer hardware-specific GPU setup.** Ollama’s GPU instructions require host-specific toolkit/runtime work; the current evidence does not establish a portable rootless Podman setup across Lerd’s Linux and macOS targets.
- **Defer a full self-improving agent platform.** That would require an independent evaluator, sandbox, and acceptance gate. A service catalog can provide tools but does not own those controls.
- **Keep Context.dev outside the container catalog.** It is a hosted API provider and needs user-controlled credentials; no self-hosted image is part of the evidence.

## Round 3: synthesis and priority

| Priority | Idea | Why it leads | Assumption to test |
| --- | --- | --- | --- |
| 1 | Versioned bundle contract consumed by Lerd | Unlocks real multi-container tools while keeping one installable lifecycle | Lerd can safely represent bundle networks, state, secrets, ports, and partial failures |
| 2 | Firecrawl bundle with dedicated dependencies | Directly supports the requested web-research use case and validates the bundle contract | The chosen upstream release has usable, pinned images and works under rootless Podman |
| 3 | Open WebUI dependent on existing Ollama | Adds an approachable interface without rebuilding or replacing the current Ollama preset | The service dependency can target the catalog’s Ollama family and persist WebUI state |
| 4 | Project endpoint wiring and setup guidance | Connects installed services to real PHP projects and the `lerd-dev` workflow | Lerd can inject optional service variables without overwriting operator choices |
| 5 | Store validation plus runtime smoke preflight | Prevents invalid descriptors and catches deployment failures before publishing | CI can run static catalog checks, and a supported rootless-Podman integration host can run a representative bundle within practical resource limits |

### Deferred

LiteLLM, Langfuse, Qdrant, workflow builders, more crawlers, GPU-specific variants, Context.dev credentials/integration, and self-modifying harness behavior are excluded from the first change. Add them after the bundle contract and its failure, security, and update behavior are proven.

## Enhancement audit

### Pass 1: applied and deferred

- **APPLY — host-catalog path.** The local store server serves the existing `services/` directory, so the bundle registry belongs under `services/bundles/` and can be fetched relative to the current `LERD_SERVICES_BASE_URL` without a second setting.
- **APPLY — image and model download disclosure.** Lerd already gates missing service-image pulls on confirmation. Bundle previews should aggregate those images; Ollama model weights are a separate, potentially large download and need their own model-name and known/unknown-size disclosure.
- **APPLY — describe the actual Ollama model.** The current preset bootstraps `qwen3-embedding:8b`, which is an embedding model. Open WebUI can list it, but the plan must not promise chat generation until a user-selected chat model is present.
- **APPLY — trust boundary for Firecrawl.** Firecrawl’s documented local configuration has no API authentication. Loopback host binding does not prevent containers on Lerd’s shared network from reaching its internal hostname, so the setup guide must state the trusted-container boundary.
- **APPLY — redirect/private-target review.** The GitHub advisory for CVE-2026-32857 reports that Firecrawl 2.8.0 and earlier did not revalidate redirect destinations in the Playwright service. Image selection and integration validation must cover redirect-to-private-address behavior.
- **APPLY — CI boundaries.** Static catalog validation belongs on pull requests and pushes without credentials or image pulls. The existing runner image workflow remains a separate opt-in `workflow_dispatch` check.
- **DEFER — per-project bundle networks and private-host allowlists.** These would broaden the runtime topology and may conflict with scraping local development sites. The initial contract states the shared-network trust boundary and does not imply fine-grained isolation.
- **DEFER — GPU access and model performance profiles.** Current evidence does not establish portable rootless Podman GPU support or universal resource sizing.
- **DEFER — further AI catalog breadth and self-improving agent loops.** They add separate image-maintenance, evaluator, sandbox, and acceptance responsibilities.

### Pass 2: coherence and risk challenge

- The existing Ollama bootstrap uses a model name but does not show a size or ask before downloading. The proposal adds a distinct model-weight confirmation; image pull confirmation alone would not cover it.
- Firecrawl’s API is unauthenticated in its local quickstart, while Lerd’s service network is shared. The plan now makes the reachable-container boundary explicit and refuses wider host publication without an authentication policy.
- Firecrawl’s scraper accepts URLs and has a documented historical redirect SSRF issue. A digest pin by itself does not prove safe redirect handling, so the selected release must pass direct and redirected private-target checks before it is advertised for use by trusted local callers.
- Both active changes mention README and CI, but their contracts do not conflict: the AI proposal owns the service catalog/preflight section and push/PR checks; `add-hosted-runner-smoke` owns the GitHub Actions runner section and manual workflow. Keep edits to those sections scoped.
- The registry path stays relative to the configured `services/` root, preserving the local store configuration and older clients that never fetch the new bundle index.

### Pass 3: synthesis

The proposal now makes the catalog URL, schema version, install confirmation, runtime companion, service-network trust boundary, and runtime evidence gates explicit. Ollama, Open WebUI, and Firecrawl remain the initial user-facing path. Private network isolation, private-target allowlisting, GPU profiles, additional AI products, and agent self-modification remain deferred until their compatibility and security models are independently proven.

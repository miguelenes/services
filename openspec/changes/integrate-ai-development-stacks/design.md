# Design

## Context

See [proposal.md](proposal.md) for motivation and scope. The store serves a flat `services/` directory rooted at `LERD_SERVICES_BASE_URL`; `services/index.json` and preset YAML files are fetched relative to that URL. The local store server points at this checkout’s `services/` directory. There is no schema or validator in the checkout.

Firecrawl’s documented self-host stack is multi-container. Its quickstart disables API authentication and describes a trusted-network boundary. Lerd containers share a service network, so an internal hostname is reachable from other Lerd containers even when a host-published port is loopback-only.

The service store owns registry data, schemas, static checks, catalog documentation, and review of candidate image metadata. Lerd runtime behavior and runtime acceptance belong to a separate companion change. Requirements in the delta specs describe the consumer contract; this change’s tracked tasks do not implement or claim that behavior.

## Goals / Non-Goals

**Goals:**

- Define an additive bundle contract that fits the current service-catalog URL and preserves `services/index.json` for existing clients.
- Validate service presets, bundle indexes, and descriptors locally and in CI without network access or container operations.
- Prepare reviewed catalog entries and documentation that accurately state their compatibility prerequisites and trust boundaries.
- Preserve the runtime requirements as a clear contract for the deferred Lerd companion work.

**Non-Goals:**

- Implement or run Lerd bundle discovery, lifecycle, networking, readiness, secret storage, image/model download confirmation, or runtime preflight.
- Claim that a bundle is installable until a compatible Lerd runtime exists and passes its companion acceptance checks.
- Accept arbitrary Compose files, builds from source, host mounts, privileged containers, device passthrough, or free-form hooks.
- Promise GPU access, production availability, a universal resource floor, or isolation from other containers on Lerd’s shared network.
- Package Context.dev credentials or enable a general-purpose self-modifying agent harness.

## Decisions

### Keep the registry under the existing service-catalog root

Store the bundle registry at `services/bundles/index.json` and descriptors at `services/bundles/<slug>.yaml`. From the existing base URL, a future compatible runtime can fetch `bundles/index.json` and descriptor paths relative to that catalog root. This keeps the current local server and published service URL usable. Keep `services/index.json` compatible with older Lerd clients.

The bundle index is a JSON object with `schema_version: 1` and a `bundles` array. Each entry has a unique `name`, `description`, and relative `descriptor` path. The descriptor repeats `schema_version: 1`, carries its own `name` and release `version`, and contains a non-empty `components` array. Runtime version gating is a companion requirement, not code delivered here.

**Alternative considered:** Put `bundles/` at the repository root. That would not be reachable from the configured local catalog base URL, which serves the `services/` directory, without changing the server root or adding another URL setting.

### Use strict, typed descriptors and schemas

Use JSON Schema Draft 2020-12 for `schema/service-preset-v1.schema.json`, `schema/bundle-index-v1.schema.json`, and `schema/service-bundle-v1.schema.json`. Parse YAML descriptors to JSON-compatible values before validation. A Python 3 preflight command (`python3 tools/catalog_preflight.py`) uses pinned PyYAML and `jsonschema` development dependencies from a lock file. It has no network access and does not start containers.

Bundle schemas reject unknown fields. Structural rules cover schema version, unique DNS-style names, digest-pinned OCI images, dependency references and cycles, supported host OS/architecture pairs, declared ports, structured readiness checks, persistent state paths, environment mappings, secret sources, and optional CPU/memory caps. The preflight validates catalog-owned structure and cross-references; it does not assert that an image runs or that a runtime can enforce a declaration.

**Alternative considered:** Use Compose as the descriptor. That imports arbitrary host/runtime behavior and does not give the store a stable, bounded contract to validate.

### Treat lifecycle behavior as a companion consumer contract

The descriptor expresses the information a compatible Lerd runtime needs: component identity, dependencies, readiness, internal ports, explicit host entrypoints, state, secrets, supported platforms, and optional limits. The specs retain the expected behavior for bundle discovery, preflight-before-pull, preview and confirmation, grouped lifecycle, failure reporting, offline management, and data retention. A separate Lerd change owns implementation and runtime evidence for those requirements.

The store may publish descriptor examples and image metadata, but documentation must label installability as dependent on the compatible runtime. Firecrawl must not be advertised as ready for use until the companion runtime’s end-to-end scrape and trust-boundary checks pass.

**Alternative considered:** Count a valid descriptor as a runnable bundle. Static validation cannot establish image availability, runtime compatibility, dependency health, or scrape success.

### Keep catalog validation separate from runtime acceptance

The store’s preflight checks schemas, index-to-file parity, duplicate names, safe relative paths, dependency cycles, platform declarations, resource-limit shape, and committed secret literals. CI runs the exact documented static command on pushes and pull requests without credentials or image pulls.

Runtime acceptance remains in the deferred companion plan: compatible-host lifecycle, actual readiness, downloads, and a Firecrawl scrape through the selected release. Neither this store preflight nor CI claims to substitute for those checks.

**Alternative considered:** Run the full bundle in ordinary catalog CI. That would require privileged container infrastructure, large downloads, credentials or external network access, and could not replace the runtime project’s host-specific acceptance.

### Keep the first catalog path narrow

Keep the existing Ollama preset; add Open WebUI as a dependent single-service preset and define Firecrawl as a bundle only after the selected image set and supported platforms are reviewed. Catalog documentation distinguishes the existing embedding model from a chat model, host loopback URLs from in-container service names, and the shared-network reachability of Firecrawl’s unauthenticated API.

Do not claim model-download confirmation, grouped install, or runtime readiness until the companion implements and verifies those behaviors. Image/model download sizes and confirmation remain Lerd runtime responsibilities.

**Alternative considered:** Expand into a broad AI catalog now. That would add more image-maintenance and security work before the bundle contract has a maintained example.

## Risks / Trade-offs

- **Risk:** Users may mistake a valid catalog descriptor for an installable feature. → **Mitigation:** State that compatible Lerd runtime support is a prerequisite and gate installability claims on companion evidence.
- **Risk:** Upstream images or environment contracts drift. → **Mitigation:** Pin reviewed image digests and platform metadata; require review before changing them.
- **Risk:** Firecrawl’s local API is unauthenticated and reachable from Lerd containers. → **Mitigation:** Document trusted-container access and loopback-only host publication in the descriptor contract.
- **Risk:** Static validation passes while runtime behavior fails. → **Mitigation:** Keep separate companion lifecycle and scrape acceptance criteria; do not represent static CI as runtime proof.

## Migration Plan

1. Add schemas and static preflight without changing `services/index.json` or existing preset behavior.
2. Add the bundle registry format, reviewed catalog entries, and contribution/service documentation. Clearly mark runtime compatibility as a prerequisite.
3. In a separate Lerd companion change, implement the consumer contract and run the Lerd preflight plus supported-host lifecycle and Firecrawl scrape acceptance.
4. Only after that companion evidence exists, describe Firecrawl as installable for the verified runtime and host profile.

The store change can be rolled back by removing the new registry and catalog entries; existing single-service presets remain usable.

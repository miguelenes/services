# Spec Delta

## Purpose

Service bundles let Lerd users install and operate a group of cooperating containers as one catalog choice, with explicit ownership of dependencies, state, configuration, networking, downloads, and failures.

## ADDED Requirements

### Requirement: Bundle registry is versioned and backward compatible
The service store SHALL expose bundle discovery under `bundles/index.json` relative to the configured service-catalog base URL. Existing `services/index.json` content and behavior SHALL remain valid for Lerd runtimes that do not support bundle schema version 1.

#### Scenario: Compatible runtime discovers a bundle
- **GIVEN** the Lerd runtime supports bundle schema version 1
- **WHEN** it reads the service catalog
- **THEN** it reads `bundles/index.json`, validates the registry version, and presents valid entries with their component summaries

#### Scenario: Older runtime reads the catalog
- **GIVEN** the Lerd runtime does not support bundle schema version 1
- **WHEN** it reads the service catalog
- **THEN** it continues to use `services/index.json` and does not try to install or partially interpret a bundle

### Requirement: Bundle descriptors are validated before installation
The catalog SHALL accept a bundle only when its supported schema version, component names, immutable image references, supported host profiles, declared ports and state, dependency graph, readiness checks, and required configuration are valid.

#### Scenario: Valid bundle is discoverable
- **GIVEN** a catalog bundle passes schema and cross-field validation
- **WHEN** a compatible user searches the catalog
- **THEN** Lerd presents it as one installable choice and lists its components, dependencies, and host endpoints

#### Scenario: Invalid descriptor is rejected before fetch
- **GIVEN** a bundle has a missing component reference, duplicate component name, unsupported schema version, digest-less image, unsafe descriptor path, or dependency cycle
- **WHEN** Lerd validates it for installation
- **THEN** Lerd identifies the bundle and invalid field or relationship and pulls no images or creates no units or volumes

### Requirement: Bundle downloads require a preview and confirmation
Before the first image pull, Lerd SHALL validate all component references and host compatibility, display every required image and its known size (or explicitly show `unknown`), and require operator confirmation when any required image is not already local.

#### Scenario: Bundle images are not present locally
- **GIVEN** at least one required bundle image must be fetched
- **WHEN** the operator requests installation
- **THEN** Lerd displays the image list and known aggregate size, fetches no image before confirmation, and identifies unknown image sizes

#### Scenario: Host profile is unsupported
- **GIVEN** a required component does not support the current host OS and architecture
- **WHEN** the operator requests installation
- **THEN** Lerd rejects the bundle before image pulls and identifies the incompatible component and available profiles

### Requirement: A bundle has one user-visible lifecycle
Lerd SHALL install, start, inspect, update, stop, and remove every component through the owning bundle while reporting component-level state and failures.

#### Scenario: Bundle starts in dependency order
- **GIVEN** an installed bundle is stopped
- **WHEN** a user starts it
- **THEN** Lerd starts dependencies before dependants and reports the state of each component under the bundle

#### Scenario: A component fails during startup
- **GIVEN** a required component fails to start or become ready
- **WHEN** the user starts the bundle
- **THEN** Lerd names the failing component and phase, stops dependants that cannot operate, redacts secrets from the error, and leaves the bundle recoverable through its lifecycle commands

#### Scenario: A lifecycle operation is repeated
- **GIVEN** a bundle is already installed, started, or stopped in the requested state
- **WHEN** the same lifecycle action is repeated
- **THEN** Lerd reconciles the existing state without creating duplicate units or volumes

#### Scenario: Lifecycle operations overlap
- **GIVEN** an install, update, or removal is active for a bundle
- **WHEN** another lifecycle operation for that bundle begins
- **THEN** Lerd returns a conflict naming the active operation and makes no concurrent mutation

### Requirement: Installed bundles remain manageable when the catalog is offline
Lerd SHALL retain each installed bundle descriptor locally. Catalog unavailability SHALL NOT prevent status, stop, or removal of an installed bundle; install or update SHALL fail before mutation when required descriptors or images are unavailable.

#### Scenario: Catalog is unavailable for an installed bundle
- **GIVEN** a bundle was installed and its descriptor is cached locally
- **WHEN** the catalog cannot be reached
- **THEN** Lerd can inspect, stop, and remove the bundle using local state

#### Scenario: Install needs an unavailable image
- **GIVEN** the catalog or a required image is unavailable and not cached
- **WHEN** a user requests a new install or update
- **THEN** Lerd reports the unavailable dependency before changing the installed bundle

### Requirement: Bundle state, network access, and secrets are bounded
Each bundle SHALL define component state, internal connectivity, host-published endpoints, and secret inputs explicitly. Catalog defaults MUST bind host-published endpoints to loopback and MUST NOT contain reusable secret literals.

#### Scenario: State survives a container replacement
- **GIVEN** a component declares persistent state
- **WHEN** Lerd updates its image or recreates its container
- **THEN** the declared state remains attached to that component

#### Scenario: Secret input is supplied safely
- **GIVEN** a bundle needs an internal credential
- **WHEN** Lerd installs it
- **THEN** Lerd generates the credential or obtains it from the operator, stores it in user-only local state, and excludes its value from catalog data, project endpoint values, logs, status output, diagnostics, and error messages

#### Scenario: Local endpoint is published
- **GIVEN** a bundle declares an unauthenticated host-facing endpoint
- **WHEN** no wider exposure is explicitly requested
- **THEN** Lerd binds it to `127.0.0.1`, reports the assigned host port, and reports the internal address separately

### Requirement: Optional resource limits are enforceable
Bundle descriptors MAY set positive integer `cpu_millis` and `memory_bytes` limits for a component only when the current host/runtime profile can enforce them. Unset limits SHALL use runtime defaults. A limit SHALL NOT be presented as a minimum resource recommendation.

#### Scenario: A supported component limit is configured
- **GIVEN** a bundle declares a valid CPU or memory limit on a profile that supports enforcement
- **WHEN** Lerd creates the component
- **THEN** Lerd applies the limit and reports the configured value

#### Scenario: A limit cannot be enforced on the current host
- **GIVEN** a bundle declares a resource limit the current profile cannot enforce
- **WHEN** Lerd validates the bundle
- **THEN** Lerd rejects it before image pulls and identifies the unsupported component and setting

### Requirement: Bundle updates and removal preserve recoverability
Lerd SHALL update and remove bundle components as a group while following Lerd’s data-retention policy and reporting incomplete operations.

#### Scenario: Update fails partway through
- **GIVEN** an update changes some component images before another component fails
- **WHEN** the user inspects the bundle or retries the update
- **THEN** Lerd reports which components changed and which did not, leaves declared data available, and makes the bundle state clear enough to retry or roll back

#### Scenario: Bundle is removed without a data-removal request
- **GIVEN** a user removes an installed bundle without explicitly requesting data removal
- **WHEN** Lerd removes the bundle
- **THEN** Lerd removes its containers, retains declared persistent data, and reports where that data remains

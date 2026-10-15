# Spec Delta

## Purpose

Service bundles define a versioned catalog contract for describing groups of cooperating services. A compatible Lerd runtime consumer is required to install and operate them; runtime requirements here are deferred companion scope.

## ADDED Requirements

### Requirement: Bundle registry is versioned and backward compatible
The service store SHALL define bundle discovery under `bundles/index.json` relative to the configured service-catalog base URL while preserving `services/index.json` for existing clients.

#### Scenario: Bundle registry is present
- **GIVEN** a contributor adds bundle discovery metadata
- **WHEN** catalog preflight validates the registry
- **THEN** it checks the declared schema version, unique entries, and safe descriptor paths without changing the existing service index

#### Scenario: Older runtime reads the catalog
- **GIVEN** a Lerd runtime does not support bundle schema version 1
- **WHEN** it reads the service catalog
- **THEN** it can continue using `services/index.json` unchanged; bundle discovery behavior is implemented and verified only by the companion runtime change

### Requirement: Bundle descriptors are statically validated
The catalog preflight SHALL reject bundle descriptors with unsupported schema versions, invalid component names, mutable or invalid image references, unsupported platform declarations, invalid ports or state paths, missing dependencies, dependency cycles, or invalid configuration.

#### Scenario: Valid bundle descriptor
- **GIVEN** a descriptor passes schema and cross-field validation
- **WHEN** the documented preflight runs
- **THEN** it reports catalog validity and does not claim runtime installability

#### Scenario: Invalid dependency graph is rejected
- **GIVEN** a bundle has a missing component, duplicate name, unsupported schema, invalid image, unsafe path, or dependency cycle
- **WHEN** catalog preflight validates it
- **THEN** it identifies the bundle and invalid field or relationship before any network or container operation

### Requirement: Bundle runtime contract is explicit
Bundle descriptors SHALL provide the information required for a compatible runtime to manage component dependencies, readiness, internal connectivity, host endpoints, secrets, state, supported platforms, and optional enforceable resource limits.

#### Scenario: Descriptor declares bundle behavior
- **GIVEN** a contributor prepares a bundle descriptor
- **WHEN** catalog preflight validates it
- **THEN** it checks the declared fields and relationships without claiming that a runtime applied them

#### Scenario: Runtime cannot enforce a declared option
- **GIVEN** a descriptor declares a platform-specific resource limit or capability
- **WHEN** the catalog contribution is reviewed
- **THEN** it documents supported profiles accurately and leaves enforcement or rejection before image pulls to the companion runtime contract

### Requirement: Bundle image metadata is reviewable before publication
Catalog entries SHALL use immutable image references, declare supported host OS and architecture pairs, and identify known image sizes where the catalog can verify them.

#### Scenario: Image metadata is reviewed
- **GIVEN** a contributor proposes bundle component images
- **WHEN** the catalog contribution is reviewed
- **THEN** it records immutable references, verified platform pairs, and known or unknown image sizes without claiming that an image was fetched or executed

#### Scenario: Image compatibility is unknown
- **GIVEN** a component’s image platform support cannot be verified
- **WHEN** the descriptor is prepared
- **THEN** the unverified host profile is excluded or explicitly marked unsupported

### Requirement: Bundle state, network access, and secrets are bounded
Bundle descriptors SHALL declare component state, internal connectivity, host-published endpoints, and secret inputs explicitly. Catalog defaults MUST bind host endpoints to loopback and MUST NOT contain reusable secret literals.

#### Scenario: Secret input is represented safely
- **GIVEN** a bundle needs an internal credential
- **WHEN** catalog preflight checks the descriptor
- **THEN** it accepts only a generated or operator-supplied secret reference and rejects reusable secret values

#### Scenario: Local endpoint is declared
- **GIVEN** a bundle declares a host-facing endpoint
- **WHEN** catalog preflight checks its exposure settings
- **THEN** it confirms the default is loopback and keeps the internal address separately represented

### Requirement: Runtime lifecycle and recovery are companion requirements
A compatible Lerd runtime SHALL install, start, inspect, update, stop, and remove bundle components through the owning bundle while reporting component-level state and preserving declared data according to Lerd’s retention policy.

#### Scenario: Bundle starts in dependency order
- **GIVEN** an installed bundle is stopped
- **WHEN** the companion runtime starts it
- **THEN** it starts dependencies before dependants and reports each component’s state

#### Scenario: A component fails during startup
- **GIVEN** a required component fails to start or become ready
- **WHEN** the companion runtime starts the bundle
- **THEN** it identifies the failing component and phase, stops dependants that cannot operate, and leaves declared state available for recovery

#### Scenario: Update fails partway through
- **GIVEN** an update changes some component images before another component fails
- **WHEN** the companion runtime reports the operation
- **THEN** it identifies changed and unchanged components and preserves declared data for retry or rollback

#### Scenario: Bundle removal retains data by default
- **GIVEN** a user removes a bundle without requesting data deletion
- **WHEN** the companion runtime removes it
- **THEN** it removes containers and retains declared persistent data

### Requirement: Bundle download confirmation is a companion requirement
Before the first image pull, a compatible Lerd runtime SHALL validate all component references and host compatibility, display required images and known sizes, and obtain confirmation when an image is not already local.

#### Scenario: Bundle images are not present locally
- **GIVEN** at least one required image must be fetched
- **WHEN** the companion runtime prepares installation
- **THEN** it previews image references and known or unknown size and fetches nothing before confirmation

#### Scenario: Host profile is unsupported
- **GIVEN** a required component does not support the current host profile
- **WHEN** the companion runtime validates installation
- **THEN** it rejects the bundle before image pulls and identifies the incompatible component

### Requirement: Bundle resource limits are conditional on runtime support
Bundle descriptors MAY specify CPU or memory limits only for profiles where the consumer runtime can enforce them. Unset limits SHALL use runtime defaults, and catalog documentation SHALL NOT present limits as a minimum resource recommendation.

#### Scenario: Supported limit is declared
- **GIVEN** a bundle declares a resource cap for a profile whose support is documented
- **WHEN** catalog preflight validates the descriptor
- **THEN** it confirms the cap is well formed without claiming runtime enforcement

#### Scenario: Limit support is unavailable
- **GIVEN** a profile cannot enforce a declared resource cap
- **WHEN** the descriptor is reviewed
- **THEN** that profile is excluded or marked unsupported, and runtime rejection before image pulls remains a companion acceptance requirement

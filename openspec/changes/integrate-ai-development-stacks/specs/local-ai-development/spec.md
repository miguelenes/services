# Spec Delta

## Purpose

The local AI development catalog describes service choices and connection information for local inference and web research. Runtime-dependent behavior remains a consumer contract for a separate Lerd companion change.

## ADDED Requirements

### Requirement: AI development services are catalogued accurately
The service catalog SHALL describe local inference and web-research services with their purpose, dependencies, endpoints, persistence, and runtime compatibility prerequisites.

#### Scenario: User discovers the local AI path
- **GIVEN** the catalog contains Ollama, Open WebUI, and a Firecrawl bundle descriptor
- **WHEN** a user searches the service catalog for local inference or web research
- **THEN** the catalog identifies each service, its component requirements, and whether compatible Lerd runtime support is a prerequisite for installation

#### Scenario: Ollama service remains independently described
- **GIVEN** a user reads the Ollama catalog entry without Open WebUI or Firecrawl
- **WHEN** the entry is presented
- **THEN** it identifies its local API endpoint, persistent model data, and configured model bootstrap without claiming chat capability from an embedding model

### Requirement: Project connection settings match the caller network
Catalog documentation SHALL distinguish service DNS names used from a Lerd container from loopback host ports used by a host process.

#### Scenario: Project runs in Lerd containers
- **GIVEN** a Lerd-managed PHP or custom-container project connects to Ollama or Firecrawl
- **WHEN** catalog documentation describes the service URL
- **THEN** it uses the component’s internal Lerd hostname and container port and marks runtime wiring as dependent on compatible Lerd support

#### Scenario: Developer uses a host process
- **GIVEN** a developer calls a host-published service from a host process
- **WHEN** they follow catalog documentation
- **THEN** it uses the loopback host URL and does not direct the host process to a container-only DNS name

### Requirement: Open WebUI catalog entry depends on Ollama
The Open WebUI preset SHALL declare its dependency on the `ollama` family, its internal Ollama endpoint, and independent persistent application data.

#### Scenario: Open WebUI dependency is represented
- **GIVEN** a contributor validates the Open WebUI preset
- **WHEN** catalog preflight checks its dependencies and environment
- **THEN** it confirms the Ollama family reference and internal URL are represented by the descriptor

#### Scenario: Ollama is not installed
- **GIVEN** a user reviews the Open WebUI catalog entry without a compatible Ollama service
- **WHEN** they read its dependency information
- **THEN** the catalog identifies the Ollama preset needed to satisfy it and makes no claim that this store change implements runtime dependency resolution

### Requirement: Firecrawl catalog entry defines a trusted-local bundle
The Firecrawl descriptor SHALL declare digest-pinned API and browser components, required queue, cache, dedicated database, state, supported platforms, and local-only host API defaults.

#### Scenario: Firecrawl descriptor is reviewed
- **GIVEN** the selected upstream release passes image, platform, and security review
- **WHEN** a contributor adds its descriptor
- **THEN** it records the release evidence and identifies compatible Lerd runtime support as a prerequisite to installation

#### Scenario: Unauthenticated API is reachable from Lerd containers
- **GIVEN** the selected upstream local configuration has API authentication disabled
- **WHEN** catalog documentation describes its connection settings
- **THEN** it states that Firecrawl is trusted-local development software and other containers on Lerd’s shared service network can reach its internal endpoint

#### Scenario: Wider host exposure is requested
- **GIVEN** the catalog’s Firecrawl configuration has no supported authentication policy
- **WHEN** a user reviews its declared host endpoint
- **THEN** the catalog defaults to loopback and does not document LAN or public exposure as supported

### Requirement: Firecrawl release safety evidence is recorded
Before a Firecrawl release is marked compatible in the catalog, the contribution SHALL record relevant advisories and observed direct and redirected requests to private, loopback, link-local, and metadata-service addresses.

#### Scenario: Redirect target is private
- **GIVEN** a controlled public test URL redirects to a protected address
- **WHEN** maintainers record compatibility evidence for the selected release
- **THEN** they record observed behavior and do not advertise the release for untrusted callers if the redirect reaches that destination

#### Scenario: Security behavior cannot be verified
- **GIVEN** the selected release’s destination policy cannot be verified
- **WHEN** maintainers prepare the bundle entry
- **THEN** they record the limitation and keep the entry scoped to trusted-local development use

### Requirement: Runtime readiness claims require companion evidence
Catalog documentation SHALL distinguish static descriptor validation from runtime readiness and successful scraping.

#### Scenario: Descriptor passes static preflight
- **GIVEN** a Firecrawl descriptor passes the service-store preflight
- **WHEN** the catalog reports its validation status
- **THEN** it claims only catalog/schema validity and does not claim the runtime is ready or a scrape succeeded

#### Scenario: Compatible runtime completes a scrape
- **GIVEN** a separate Lerd companion verifies the bundle lifecycle and a controlled scrape on a named host profile
- **WHEN** the catalog documentation is updated after that evidence
- **THEN** any installability statement names the compatible runtime and verified host profile

### Requirement: Ollama integration with Firecrawl is opt-in
The Firecrawl descriptor SHALL leave optional model-provider settings unset unless a user explicitly selects an Ollama endpoint.

#### Scenario: No model endpoint is selected
- **GIVEN** a user reviews Firecrawl without selecting Ollama
- **WHEN** the descriptor is validated
- **THEN** optional Ollama settings remain absent and the documented baseline makes no model-provider call through Ollama

#### Scenario: User selects local Ollama
- **GIVEN** an Ollama endpoint is selected for Firecrawl
- **WHEN** the descriptor’s optional setting is documented
- **THEN** it uses the internal Ollama URL without requiring a hosted API credential

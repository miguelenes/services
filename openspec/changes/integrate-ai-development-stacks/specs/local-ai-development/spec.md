# Spec Delta

## Purpose

Local AI development services give Lerd projects discoverable, reproducible endpoints for local inference and web research, with setup guidance that distinguishes host access from container-network access and discloses expensive downloads and trust boundaries.

## ADDED Requirements

### Requirement: AI development services are catalogued for Lerd projects
The service catalog SHALL expose local inference and web-research services as discoverable Lerd presets or bundles with their purpose, dependencies, endpoints, supported host profiles, and persistence needs.

#### Scenario: User discovers the local AI path
- **GIVEN** the runtime supports the bundle registry
- **WHEN** a user searches for local inference or web research
- **THEN** Lerd presents Ollama, its dependent Open WebUI preset, and Firecrawl when a compatible bundle is published, with component and platform requirements

#### Scenario: Ollama remains independently usable
- **GIVEN** a user installs Ollama without WebUI or Firecrawl
- **WHEN** the service starts and finishes model bootstrap
- **THEN** Lerd exposes its API endpoint and keeps model data across container recreation

### Requirement: Project connection settings match the caller network
Lerd SHALL provide project settings and guidance that use service DNS names from a Lerd container and loopback host ports from a host process.

#### Scenario: Project runs in Lerd containers
- **GIVEN** a Lerd-managed PHP or custom-container project connects to Ollama, Open WebUI, or Firecrawl
- **WHEN** Lerd supplies or documents its service URL
- **THEN** the URL uses the component’s internal Lerd hostname and container port

#### Scenario: Developer uses a host process
- **GIVEN** a developer calls a host-published service from a host process
- **WHEN** they follow the service documentation
- **THEN** it uses the assigned loopback host URL and does not use a container-only DNS name

### Requirement: Ollama model bootstrap is disclosed before download
Before an Ollama preset downloads models named in `OLLAMA_PULL_MODELS`, Lerd SHALL disclose the model names, show authoritative sizes when available (otherwise `unknown`), and request operator confirmation.

#### Scenario: Model bootstrap is configured
- **GIVEN** Ollama is configured to pull one or more models that are not already available
- **WHEN** a user starts Ollama directly or through an Open WebUI dependency
- **THEN** Lerd shows each model and its known or unknown size and waits for confirmation before fetching model data

#### Scenario: Model data is already present
- **GIVEN** all configured models are already available in persistent Ollama data
- **WHEN** a user starts or restarts Ollama
- **THEN** Lerd does not request confirmation or download the existing model data again

### Requirement: Open WebUI connects to the selected Ollama service
The Open WebUI preset SHALL depend on the `ollama` service family and persist its application data independently.

#### Scenario: Open WebUI starts with Ollama available
- **GIVEN** a compatible Ollama-family service is installed
- **WHEN** a user starts Open WebUI
- **THEN** Open WebUI receives the selected service’s internal URL and can list its available models

#### Scenario: Ollama is not installed
- **GIVEN** no compatible Ollama-family service is installed
- **WHEN** a user installs or starts Open WebUI
- **THEN** Lerd identifies the missing dependency and the catalog entry that satisfies it

### Requirement: Firecrawl is a trusted-local development bundle
The Firecrawl bundle SHALL include digest-pinned API and browser components plus its required queue, cache, and dedicated database dependencies. It SHALL not rely on a project’s shared application database. The default host API SHALL bind to loopback, and documentation SHALL state that any container on Lerd’s shared service network can reach the internal API.

#### Scenario: Firecrawl bundle is installed
- **GIVEN** the chosen Firecrawl release and host profile pass the catalog and security checks
- **WHEN** a user installs the bundle
- **THEN** Lerd previews the image downloads, provisions dependencies in readiness order, retains declared state, and exposes the host API only on loopback by default

#### Scenario: Unauthenticated API is reachable from Lerd containers
- **GIVEN** the selected upstream local configuration has API authentication disabled
- **WHEN** Lerd presents the bundle and its connection settings
- **THEN** it states that the service is trusted-local development software and that other Lerd containers can call its internal endpoint

#### Scenario: Operator requests wider exposure
- **GIVEN** the bundle’s default API has no supported authentication policy
- **WHEN** an operator requests a LAN or public host binding
- **THEN** Lerd refuses the wider binding and explains that this Firecrawl configuration is not suitable for untrusted callers

### Requirement: Firecrawl destination safety is verified for the selected release
Before a Firecrawl release is advertised as installable, the catalog contribution SHALL record the release’s relevant security advisories and verify how it handles direct and redirected requests to private, loopback, link-local, and metadata-service addresses. The bundle SHALL be documented for trusted-local callers and SHALL NOT claim protections that were not demonstrated.

#### Scenario: Redirect target is private
- **GIVEN** a controlled public test URL redirects to a private, loopback, link-local, or metadata-service address
- **WHEN** the selected Firecrawl release is exercised during compatibility review
- **THEN** the observed behavior is recorded and a release that allows the redirect to reach a protected destination is not advertised for untrusted callers

#### Scenario: Security behavior cannot be verified
- **GIVEN** the selected release has no testable or documented destination policy
- **WHEN** maintainers prepare the bundle entry
- **THEN** they mark the limitation clearly and keep the bundle restricted to trusted local development use

### Requirement: Firecrawl readiness is verified through a scrape
The Firecrawl integration SHALL distinguish container health from successful end-to-end scraping.

#### Scenario: Components are healthy but a scrape fails
- **GIVEN** containers report healthy but a controlled scrape cannot complete
- **WHEN** the integration check evaluates the bundle
- **THEN** it reports the integration as not ready and identifies the API, browser, queue, database, or outbound-network failure when available

#### Scenario: Scrape completes
- **GIVEN** the configured smoke check submits a controlled public URL
- **WHEN** Firecrawl returns the expected extraction response
- **THEN** Lerd reports the bundle as ready for project use

### Requirement: Ollama integration with Firecrawl is opt-in
The Firecrawl bundle SHALL leave optional model-provider settings unset unless the user explicitly configures an Ollama endpoint.

#### Scenario: No model endpoint is selected
- **GIVEN** a user installs Firecrawl without selecting Ollama
- **WHEN** the bundle starts
- **THEN** Firecrawl uses its documented non-Ollama baseline and makes no request to the local Ollama endpoint

#### Scenario: User selects local Ollama
- **GIVEN** a compatible Ollama service is installed and selected
- **WHEN** Lerd configures Firecrawl’s model-provider endpoint
- **THEN** it supplies the internal Ollama URL without requiring a hosted API credential

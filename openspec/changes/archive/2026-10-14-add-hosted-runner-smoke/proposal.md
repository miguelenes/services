# Proposal

## Why

The `github-actions-runner` preset points at an image pinned by manifest digest. Maintainers need a low-risk way to check that the published image remains available and that its entrypoint refuses registration when no token is supplied. This check can run on an ephemeral GitHub-hosted worker without creating or registering a persistent runner.

## What Changes

- Provide an opt-in `workflow_dispatch` workflow on `ubuntu-latest` that reads the image reference from `services/github-actions-runner.yaml`, validates its immutable SHA-256 digest, and pulls and inspects that exact image.
- Run the already-pulled image entrypoint with harmless placeholder URL/name values, empty stdin, `--pull=never`, and `--network=none`; pass only if it exits nonzero for the expected missing-token guard.
- Document dispatch and run inspection through `gh-axi` in the GitHub Actions runner section of the README.

This is repository CI tooling only. It does not change service behavior, required checks, branch protection, secrets, image publication, or runner registration.

## User Stories and Acceptance Criteria

### Maintainer checks the pinned image without registering it

- **GIVEN** the runner preset image is digest-pinned, **WHEN** a maintainer dispatches the smoke workflow, **THEN** the workflow reads that reference, pulls and inspects it, and checks the tokenless entrypoint refusal.
- **GIVEN** the preset image is mutable or lacks a valid 64-character SHA-256 digest, **WHEN** the workflow runs, **THEN** it fails before pulling an image.
- **GIVEN** tokenless startup exits nonzero for an unrelated reason, **WHEN** the workflow checks output, **THEN** the job fails rather than reporting a successful refusal check.
- **GIVEN** concurrent dispatches target the same ref, **WHEN** a newer run starts, **THEN** the previous run in the same concurrency group is cancelled.
- **GIVEN** a smoke run completes, **WHEN** a maintainer inspects it with `gh-axi`, **THEN** its result demonstrates image availability and the missing-token guard only; it makes no claim about registration, GitHub connectivity, job execution, or the private Docker sidecar.

## Non-Functional Requirements

- Trigger only on `workflow_dispatch`, run on GitHub-hosted `ubuntu-latest`, and use read-only `contents` permission.
- Use no GitHub token, runner token, repository secret, or persistent runner. The explicit image-pull step may access the registry; the entrypoint invocation must use `--pull=never` and `--network=none`, with stdin closed, so it cannot fetch an image or reach GitHub.
- Set a finite timeout and cancel older runs in the same workflow/ref concurrency group.
- Source the digest from the preset at runtime; do not copy the image reference into the workflow.

## Capabilities

No product behavior changes. `.openspec.yaml` sets `skip_specs: true` because this is repository CI tooling and documentation only.

## Deferred Ideas

- Register a persistent repository runner or execute jobs through it; that requires separate trusted private-repository operations.
- Test sidecar Docker behavior or full runner job execution.
- Run the check automatically on pushes or releases.

## Assumptions

- The workflow is dispatched only after it is available on the selected target repository ref.
- The published image’s tokenless registration guard continues to return the explicit diagnostic `registration token is required on stdin`; changing that contract requires updating the smoke check alongside the image.

## Impact

The change is limited to `.github/workflows/runner-image-smoke.yml` and the GitHub Actions runner subsection of `README.md`. It does not alter catalog descriptors, required CI, service behavior, credentials, or persistent runner infrastructure.

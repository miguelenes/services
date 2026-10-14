# Design

## Context

See [proposal.md](proposal.md) for motivation and observable behavior. The service preset `services/github-actions-runner.yaml` contains the authoritative image reference, including a SHA-256 digest. The repository already has an independent opt-in runner image smoke workflow; the workflow is separate from the required catalog checks and does not register a persistent runner.

## Goals / Non-Goals

**Goals:**

- Verify the exact preset-sourced digest can be pulled and inspected from a temporary GitHub-hosted runner.
- Exercise the container entrypoint’s missing-token guard without credentials or outbound network access from the container.
- Make every failure mode distinguishable from the expected missing-token refusal.

**Non-Goals:**

- Verify runner registration, GitHub connectivity from the image, job execution, or sidecar Docker behavior.
- Run this smoke automatically on pushes or replace the required catalog validation workflow.

## Decisions

### Keep the workflow opt-in and isolated

Use one `ubuntu-latest` job triggered only by `workflow_dispatch`. Grant `contents: read`, set a finite timeout, and use a workflow/ref concurrency group with `cancel-in-progress: true`. This avoids altering required checks and ensures repeated manual checks do not accumulate.

### Read and validate the image reference from the preset

Parse the top-level `image` from `services/github-actions-runner.yaml` during the job. Require a final `@sha256:` followed by 64 hexadecimal characters before any pull. Pull and inspect the parsed reference; never duplicate an image tag or digest in workflow YAML.

### Isolate the tokenless entrypoint check

Use harmless `RUNNER_URL` and `RUNNER_NAME` placeholders and a fresh temporary `/runner-data` directory with permissions the image can write. Invoke the already-pulled image with `--pull=never`, `--network=none`, and closed empty stdin. This ensures the container check cannot contact GitHub or fetch another image. The job passes only when the process returns nonzero and output contains the exact missing-token diagnostic. Any other exit or output fails the check.

The check never supplies a GitHub or runner token and never registers a runner. The host runner still needs registry access for the explicit pull step; the entrypoint test itself has no network.

### Keep output and cleanup bounded

Print the container output so the failure is reviewable, but do not upload logs or the temporary data directory as artifacts. Remove the directory with a trap whether the check passes or fails. A 10-minute job timeout bounds the pull and test.

### Document the dispatch boundary

Document the `gh-axi workflow run`, `run list`, and `run view` commands in the existing GitHub Actions runner README section. Explain that dispatch only works after the workflow exists on the selected target ref and that a successful run proves image availability plus tokenless refusal only.

## Risks / Trade-offs

- **Risk:** The runner image changes its diagnostic wording. → **Mitigation:** Treat a changed diagnostic as a failed contract and update the smoke check only after verifying the new tokenless guard.
- **Risk:** Registry pull latency exceeds the job timeout. → **Mitigation:** Use one pinned image and a bounded 10-minute run; adjust only after observing a legitimate timeout.
- **Risk:** A future image entrypoint attempts network access before validating its token. → **Mitigation:** Run the entrypoint with `--network=none`, so the check fails closed.

## Migration Plan

No data or service migration is needed. Add the opt-in workflow and README instructions. Dispatch it only on a ref where both the workflow and the runner preset exist. A failed run does not create persistent resources and is safe to retry.

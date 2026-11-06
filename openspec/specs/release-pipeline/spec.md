# Release pipeline

## Purpose

Resolve Caddy build inputs on a weekly schedule, reuse an unchanged published image, and publish only a checked candidate from the default branch.

Source: [workflow](../../../.github/workflows/caddy.yml), [resolver](../../../scripts/resolve_caddy.py), [fingerprint](../../../scripts/fingerprint.py), [publisher](../../../scripts/publish.py). Checks: Python policy tests, actionlint, image smoke checks and Trivy scan.

## Requirements

### Requirement: Weekly input tracking

The pipeline SHALL run weekly and on relevant repository changes, resolving the current stable Caddy release, Cloudflare DNS module and base-image digests.

#### Scenario: Scheduled run

- **WHEN** the Monday schedule runs
- **THEN** it resolves Caddy and module versions plus linux/amd64 base digests
- **AND** it recomputes the build-input fingerprint

#### Scenario: Explicit triggers

- **WHEN** a relevant push, pull request or manual dispatch runs
- **THEN** the pipeline resolves inputs and builds a candidate regardless of the published fingerprint

### Requirement: Unchanged-input reuse

A scheduled run SHALL reuse the published image and skip building when its recorded fingerprint matches the resolved inputs.

#### Scenario: Unchanged scheduled inputs

- **WHEN** the published `latest` image carries the resolved `io.service-build.inputs` label
- **THEN** the run pulls that image, repeats the smoke checks and does not rebuild or publish it

#### Scenario: Changed or unknown inputs

- **WHEN** the fingerprint differs, the label is absent or the registry inspection fails
- **THEN** the run builds and checks a new candidate

### Requirement: Tested-image publication

Publication SHALL push the exact smoke-checked candidate from the default branch as `latest` and the Caddy release tag, and MUST NOT publish pull-request builds.

#### Scenario: Publication sequence

- **WHEN** a non-PR default-branch run has a checked candidate
- **THEN** the same local image is pushed as the Caddy release tag and `latest`
- **AND** the published fingerprint and matching digests are verified
- **AND** a failed build, smoke check or scan leaves the published tags unchanged

#### Scenario: Pull request

- **WHEN** a pull request builds the image
- **THEN** the image is built and checked without registry login or publication

### Requirement: Dependency monitoring

Dependabot SHALL propose weekly GitHub Actions updates. Docker bases and upstream releases are owned by the scheduled resolver.

#### Scenario: Update scope

- **WHEN** Dependabot evaluates the repository
- **THEN** it covers GitHub Actions weekly
- **AND** it does not propose Docker base updates that the resolver already pins

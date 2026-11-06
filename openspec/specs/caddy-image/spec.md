# Caddy image

## Purpose

Build a minimal Caddy image with the Cloudflare DNS provider and a static health probe from a resolved stable upstream release.

Source: [Dockerfile](../../../caddy/Dockerfile), [healthcheck](../../../caddy/healthcheck/main.go), [workflow](../../../.github/workflows/caddy.yml). Checks: version, module, configuration, health and image-content smoke checks plus the Trivy scan.

## Requirements

### Requirement: Resolved upstream build

The image SHALL build Caddy from a stable upstream release and the Cloudflare DNS module at resolved versions, and SHALL record both source commits.

#### Scenario: Latest stable inputs

- **WHEN** the resolver runs without an override
- **THEN** it selects the highest stable Caddy semver release and the latest stable `caddy-dns/cloudflare` module version
- **AND** it records the Caddy tag, Caddy commit, module version, module commit and repository URLs in the build inputs

#### Scenario: Manual version override

- **WHEN** a manual run supplies a Caddy release tag
- **THEN** the resolver accepts it only when the tag is an existing stable release
- **AND** an unknown, draft or prerelease tag fails the run

### Requirement: Digest-pinned bases

The build SHALL use the matching Caddy builder image and a distroless runtime pinned by linux/amd64 digest.

#### Scenario: Base resolution

- **WHEN** the workflow resolves base images
- **THEN** it records the linux/amd64 digest for `caddy:<version>-builder` and `gcr.io/distroless/static-debian12:nonroot`
- **AND** the image build uses those digest references
- **AND** a missing or invalid digest fails the run instead of falling back to a mutable tag

### Requirement: Minimal nonroot runtime

The runtime image SHALL add only the Caddy binary, the static health probe and license files to the distroless base, and SHALL run as the nonroot user.

#### Scenario: Runtime contents

- **WHEN** the built image is inspected
- **THEN** its entrypoint is `/usr/bin/caddy`
- **AND** `/usr/bin/caddy-healthcheck` and `/licenses/LICENSE` are present
- **AND** the image has no shell or package manager

### Requirement: Pre-publication checks

A candidate image SHALL pass version, module, configuration, health and shell-absence checks before publication.

#### Scenario: Smoke checks

- **WHEN** the candidate image is built or reused
- **THEN** `caddy version` reports the resolved release
- **AND** `caddy list-modules` contains `dns.providers.cloudflare`
- **AND** `caddy validate` accepts a configuration that uses the Cloudflare DNS provider
- **AND** the running server answers the health probe with HTTP 200
- **AND** the image has no shell

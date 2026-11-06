# Project context

## Scope

`service_build` publishes independent service images built from upstream sources to GHCR as `latest` plus version tags. Caddy with the Cloudflare DNS provider is the first service.

| Deliverable | Source | Artifact |
| --- | --- | --- |
| Caddy image | `caddy/Dockerfile`, `caddy/healthcheck/` | `ghcr.io/miloszkolber/service-caddy` |
| Build inputs | `scripts/resolve_caddy.py`, `scripts/fingerprint.py` | Resolved JSON, fingerprint and OCI labels |
| Release pipeline | `.github/workflows/caddy.yml`, `scripts/publish.py` | `latest` and Caddy release tags |

Upstream Caddy and `caddy-dns/cloudflare` own runtime behavior. This repository owns the build recipe, resolved inputs, checks and publication.

## Goals and boundaries

- Publish minimal nonroot images with explicit build inputs and repeatable checks.
- Track stable upstream releases and base-image digests without rebuilding unchanged inputs.
- Keep the repository host-neutral and the deployment example outside this repository.
- Make changes reviewable through requirements, scenarios and evidence.

The build pins Caddy and the module by version and commit, and base images by linux/amd64 digest. Upstream source, module downloads and base images are fetched during the build; builds are not bit-reproducible.

## Owners

| Subject | Owner |
| --- | --- |
| Implemented behavior | `openspec/specs/<capability>/spec.md` alongside source |
| Proposed behavior, tasks and evidence | One scoped folder in `openspec/changes/` |
| Build/install/configuration commands | The affected package README |
| Host deployment, secrets, storage and network | Local deployment docs, outside this repository |
| Upstream Caddy and module behavior | `caddyserver/caddy` and `caddy-dns/cloudflare`, not this build repository |

Publication does not itself deploy. Keep tokens out of source, artifacts, labels and diagnostics.

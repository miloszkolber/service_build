# Caddy

Custom Caddy image with the Cloudflare DNS provider and a static health probe, built from a resolved stable upstream release.

## Image

- `ghcr.io/miloszkolber/service-caddy:latest` plus the Caddy release tag.
- Entrypoint `/usr/bin/caddy`; default command `run --config /etc/caddy/Caddyfile --adapter caddyfile`.
- Distroless `static-debian12:nonroot` runtime as UID 65532, with no shell or package manager.
- `/usr/bin/caddy-healthcheck <URL>` exits non-zero unless the URL returns HTTP 200 without a redirect.
- `/licenses/` carries the Apache-2.0 license and notice.

## Build

The workflow passes resolved values and digest-pinned bases. Dockerfile defaults are bootstrapping values only; the workflow is authoritative.

```sh
docker buildx build --platform linux/amd64 --file caddy/Dockerfile --tag service-caddy:local .
```

| Argument | Meaning |
| --- | --- |
| `BUILDER_IMAGE` | `caddy:<version>-builder` image; normally digest-pinned |
| `RUNTIME_IMAGE` | `gcr.io/distroless/static-debian12:nonroot`; normally digest-pinned |
| `CADDY_VERSION` | Stable Caddy release tag |
| `CLOUDFLARE_DNS_MODULE` | `github.com/caddy-dns/cloudflare@<version>` |

The image is smoke-checked by validating [`validate.Caddyfile`](validate.Caddyfile) with the DNS provider loaded, starting the image with [`smoke.Caddyfile`](smoke.Caddyfile), requesting the health endpoint, checking `caddy version` and `caddy list-modules`, and rejecting a runtime with a shell. The workflow also scans the image with Trivy. The scan blocks HIGH/CRITICAL findings that have a fixed version and reports unfixed upstream findings without blocking publication.

## Versioning and deployment

The workflow publishes `latest` and the resolved Caddy release tag from the default branch. A version tag can be republished when the Cloudflare module or a base digest changes; use the registry digest or the `io.service-build.inputs` label for exact rollback. Caddyfiles, secrets, storage, host networking and rollout belong to the deployment owner. Publication is not rollout.

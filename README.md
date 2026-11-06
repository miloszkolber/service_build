# service_build

Independent service images built from upstream sources and published to GHCR as `latest` plus version tags. Caddy with the Cloudflare DNS provider is the first service.

| Service | Build | Image |
| --- | --- | --- |
| Caddy | [`caddy/`](caddy/README.md) | `ghcr.io/miloszkolber/caddy` |

## Build and release

The Caddy workflow runs weekly on Monday at 03:17 UTC, and on relevant pushes, pull requests and manual dispatch. It resolves the latest stable Caddy release, the latest `caddy-dns/cloudflare` module version and the linux/amd64 digests of the builder and distroless runtime images. The image is built once, smoke-checked and scanned before the same candidate is published.

Images use distroless nonroot runtimes, static stripped binaries and digest-pinned bases. The Caddy image adds only the Caddy binary, a static health probe and license files to the distroless base.

Scheduled runs reuse the published `latest` image and repeat its smoke checks when the resolved inputs match its `io.service-build.inputs` label. A changed Caddy release, module version, base digest or build file produces a new candidate. Pushes and manual runs always build. Pull requests build and check without publishing.

The workflow publishes `latest` and the resolved Caddy release tag. A version tag can be republished when the bundled module or a base image changes; use the registry digest or the `io.service-build.inputs` label for exact rollback.

Dependabot proposes weekly GitHub Actions updates. Docker bases and upstream releases are owned by the scheduled resolver, not Dependabot. Publication is not host deployment.

## Layout

| Path | Purpose |
| --- | --- |
| [`caddy/`](caddy/README.md) | Caddy image, health probe, smoke configuration and build commands |
| [`scripts/`](scripts/) | Input resolution, fingerprinting, publication, scanning and documentation checks |
| [`openspec/`](openspec/README.md) | Implemented contracts, deferred backlog and maintenance state |
| [`.github/workflows/`](.github/workflows/) | Caddy image and documentation workflows |

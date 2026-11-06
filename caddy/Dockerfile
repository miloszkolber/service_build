# Build arguments are resolved and digest-pinned by the image workflow.
ARG BUILDER_IMAGE=caddy:2.11.9-builder
ARG RUNTIME_IMAGE=gcr.io/distroless/static-debian12:nonroot

FROM ${BUILDER_IMAGE} AS build

ARG CADDY_VERSION=v2.11.9
ARG CLOUDFLARE_DNS_MODULE=github.com/caddy-dns/cloudflare@v0.2.4

ENV CGO_ENABLED=0 \
    GOFLAGS=-buildvcs=false \
    GOTOOLCHAIN=local

RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    xcaddy build "${CADDY_VERSION}" \
        --output /usr/bin/caddy \
        --with "${CLOUDFLARE_DNS_MODULE}"

COPY caddy/healthcheck /src/healthcheck
WORKDIR /src/healthcheck
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go build -buildvcs=false -trimpath -ldflags='-s -w -buildid=' -o /out/caddy-healthcheck .

FROM ${RUNTIME_IMAGE}

LABEL org.opencontainers.image.title="caddy" \
      org.opencontainers.image.description="Caddy with the Cloudflare DNS provider and a static health probe" \
      org.opencontainers.image.licenses="Apache-2.0"

COPY --from=build /usr/bin/caddy /out/caddy-healthcheck /usr/bin/
COPY caddy/LICENSE caddy/NOTICE /licenses/

ENV HOME=/data \
    XDG_DATA_HOME=/data \
    XDG_CONFIG_HOME=/config

USER 65532:65532

ENTRYPOINT ["/usr/bin/caddy"]
CMD ["run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]

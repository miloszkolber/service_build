# Maintenance state

The Monday Caddy image workflow is the scheduled dependency review. It resolves the latest stable Caddy release, the latest `caddy-dns/cloudflare` module version and the linux/amd64 digests of the builder and runtime base images. The resolved values are recorded in `.build/caddy-inputs.json` during the run and in the published image's OCI labels.

Review the Caddy release notes and module changes when a version moves. Record source-review findings here when a release needs manual compatibility or security review. A green build does not establish upstream runtime compatibility.

## Review notes

- 2026-11-06: Caddy v2.11.9 embeds `github.com/go-jose/go-jose/v3 v3.0.5`, reported as CVE-2026-116587 (HIGH, no fixed version in the advisory data). The image scan reports it but blocks only HIGH/CRITICAL findings that have a fixed version. Recheck when Caddy updates the module.

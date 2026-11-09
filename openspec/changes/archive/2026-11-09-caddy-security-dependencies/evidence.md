## Verification

## Local candidate

The image built from Caddy v2.11.9 with digest-pinned bases. The build log confirms both replacement versions were downloaded.

The candidate passed Caddy version, Cloudflare module, configuration validation, HTTP health and shell-absence checks. Trivy 0.76.2 passed the existing fixable HIGH/CRITICAL gate. It reported CVE-2026-116587 in go-jose v3 as HIGH without a fixed version.

The sandbox checks passed: documentation checker, eight documentation tests, 17 Python tests and strict OpenSpec validation. Actionlint passed in its container. Publication and deployment were not part of this local candidate check.

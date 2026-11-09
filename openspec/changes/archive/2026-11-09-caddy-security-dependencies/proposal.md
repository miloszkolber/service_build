## Why

The current stable Caddy release embeds vulnerable dependencies and the image scan rejects the fixable x/net finding. Upstream has merged dependency updates that are not yet in a stable Caddy release.

## Scope

Apply version-specific replacements for the affected x/net and compress releases, retain the existing scan gate, and refresh the scanner. A newer upstream dependency is not replaced. This affects the Caddy image capability and does not authorize deployment.

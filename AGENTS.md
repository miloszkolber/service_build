# Repository workflow

- Keep the repository host-neutral: no absolute host paths, deployment hostnames, installed locations or environment-specific values in prose, examples or guidance. Use repo-relative paths and role names ("the deployment owner", "the local deployment docs"). Container paths and functional path constants are distinct from host installation paths.
- Read [openspec/README.md](openspec/README.md) and the affected capability spec before changing behavior. Confirm the contract against source and checks.
- Use one scoped folder in `openspec/changes/` for nontrivial behavior changes: proposal, requirement deltas, verifiable tasks and execution evidence. Add design only for consequential decisions. Keep tasks current as work lands.
- Main specs describe implemented contracts. Put unapproved ideas in `openspec/backlog.md`, not requirements or speculative implementation plans.
- MODIFIED deltas replace whole requirements. Preserve unaffected scenarios. Sync and archive after verification/review, not merely because files exist. Follow the archive workflow in openspec/README.md.
- Small corrections may use a reviewed diff. Acceptance/docs-only changes use `skip_specs: true`. Never fabricate completed task or archive history.
- Run `bun scripts/check-docs.mjs`, `bun test scripts/check-docs.test.mjs`, `python3 -m unittest discover -s tests` and the pinned upstream validation documented in `openspec/README.md` in the development container. Do not install development tooling on the host.
- Package READMEs own commands. Host deployment is a separate owner. Publishing an image does not authorize rollout or a service restart.
- Only a smoke-checked candidate from the default branch may publish. Pull requests and untrusted refs never push images.
- Keep secrets out of source, artifacts, labels and diagnostics.

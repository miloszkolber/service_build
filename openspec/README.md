# Documentation

This repository uses [OpenSpec](https://github.com/Fission-AI/OpenSpec) to keep implemented behavior, proposed changes and verification separate. Start with [project.md](project.md) for scope and ownership.

| Location | Maintained content |
| --- | --- |
| [specs/](specs/) | Implemented repository contracts, grouped by capability |
| [changes/](changes/) | Scoped work with intent, tasks and evidence. Behavior changes also carry requirement deltas |
| [backlog.md](backlog.md) | Deferred work and branch ownership, not implementation authorization |
| [maintenance-state.md](maintenance-state.md) | Scheduled dependency-review notes and source-review findings |
| [config.yaml](config.yaml) | Context and rules for OpenSpec artifact instructions |

## Capability map

| Capability | Implementation and commands | Verification owner |
| --- | --- | --- |
| [Caddy image](specs/caddy-image/spec.md) | [caddy/Dockerfile](../caddy/Dockerfile), [caddy/healthcheck/main.go](../caddy/healthcheck/main.go) | Image smoke checks and Trivy scan |
| [Release pipeline](specs/release-pipeline/spec.md) | [.github/workflows](../.github/workflows/), [scripts/resolve_caddy.py](../scripts/resolve_caddy.py), [scripts/fingerprint.py](../scripts/fingerprint.py), [scripts/publish.py](../scripts/publish.py) | Workflow runs, fingerprint reuse and publication checks |

Specs state the contract, not a claim that every scenario has been executed. Build checks alone do not establish upstream runtime compatibility or deployment acceptance.

## Working a change

1. Read the affected spec and implementation. Use memory as a lead, not proof.
2. For behavior changes, create `changes/<name>/proposal.md` with why, scope, affected capabilities and status. Add `specs/<capability>/spec.md` deltas.
3. Add technical design only for consequential choices. Track small, verifiable tasks in `tasks.md`. Keep verification and documentation with the work they check.
4. Review scope before implementation. Revise artifacts as evidence changes. A proposal is not permission to deploy, restart services or begin paused work.
5. Verify implementation against scenarios. Record commands, results and gaps in `evidence.md`. A checkbox or structural validation is not runtime acceptance.
6. After verification and review, archive the change with OpenSpec. It merges completed deltas into main specs and moves the change under `changes/archive/YYYY-MM-DD-<name>/`. Validate the resulting main specs. Completed archives are periodically consolidated into the single change history to keep the record readable; full detail stays recoverable from git history.

Use `## Purpose`, `## Requirements`, `### Requirement: Name`, and `#### Scenario: Name` in main specs. Requirements use SHALL or MUST and describe observable outcomes. Scenarios use **GIVEN**, **WHEN**, **THEN** and **AND**. Delta sections are ADDED, MODIFIED, REMOVED or RENAMED Requirements. MODIFIED replaces the **whole** requirement, including its retained scenarios.

For acceptance-only or documentation-only work, use `skip_specs: true` in `.openspec.yaml` rather than inventing a behavior change. Small corrections need only a reviewed diff and checks. Do not manufacture archive history retrospectively.

## Tooling

`openspec/` is the real documentation and planning directory. There is no `docs/` copy or alias. OpenSpec discovers this standard layout directly. Run from the repository root:

```sh
bun scripts/check-docs.mjs
bun test scripts/check-docs.test.mjs
python3 -m unittest discover -s tests
OPENSPEC_TELEMETRY=0 bun x --bun @fission-ai/openspec@1.16.0 validate --all --strict
```

After verification and review, merge deltas and archive with:

```sh
OPENSPEC_TELEMETRY=0 bun x --bun @fission-ai/openspec@1.16.0 archive <name>
OPENSPEC_TELEMETRY=0 bun x --bun @fission-ai/openspec@1.16.0 validate --all --strict
```

Use `--skip-specs` only for changes with no deltas or deltas already merged and reviewed. Never use it to omit required updates. Never use `--no-validate` to hide an archive failure.

The lightweight check verifies local links, scenario structure, change metadata and task numbering. The upstream CLI checks its own parsing and validation rules. Neither verifies implementation. OpenSpec is development tooling, not an image dependency.

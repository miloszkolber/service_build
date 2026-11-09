## ADDED Requirements

### Requirement: Scoped security dependency fixes

The image build SHALL apply version-specific upstream security fixes to affected Caddy dependencies without replacing newer versions.

#### Scenario: Affected dependency versions

- **WHEN** the selected dependency graph contains x/net v0.60.0 or klauspost/compress v1.20.1
- **THEN** the build replaces those versions with x/net v0.62.0 and compress v1.20.3 respectively
- **AND** the pre-publication scan policy remains in force

#### Scenario: Newer upstream dependencies

- **WHEN** the selected dependency graph uses a different version of either dependency
- **THEN** the version-specific replacement does not override that dependency

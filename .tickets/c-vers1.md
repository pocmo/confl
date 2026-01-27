---
id: c-vers1
status: closed
deps: []
links: []
created: 2026-01-27T09:52:00Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Implement automatic version numbering with no-guess-dev scheme

Replace hard-coded version (0.1.0) with automatic version generation using the "no-guess-dev" scheme. Start from 1.0.0.

## Problem
- Version is currently hard-coded to `0.1.0` in the codebase
- Manual version tracking is error-prone and tedious
- Want automatic version generation based on git state
- Need to start from `1.0.0` instead of `0.1.0`

## Solution: Use setuptools-scm with no-guess-dev

The "no-guess-dev" scheme automatically generates versions:
- **Tagged releases**: `1.0.0`, `1.1.0`, `2.0.0` (from git tags)
- **Dev builds**: `1.0.0.dev123+gabc123f` (based on commits since last tag)
- No manual version management needed

## Tasks

### 1. Add setuptools-scm dependency
```toml
[build-system]
requires = ["hatchling", "hatchling-vcs"]  # or setuptools-scm if using setuptools
```

### 2. Configure dynamic versioning in pyproject.toml
```toml
[project]
# Remove hard-coded version
# version = "0.1.0"  # DELETE THIS
dynamic = ["version"]

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.hooks.vcs]
version-file = "src/confl/_version.py"
```

### 3. Create initial 1.0.0 tag
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 4. Update code to use dynamic version
- Remove hard-coded version strings
- Import version from `_version.py` (auto-generated)
- Update `confl --version` to show dynamic version

### 5. Test version generation
- In repo with tag: should show `1.0.0`
- In repo with commits after tag: should show `1.0.0.devN+ghash`
- In clean checkout: should work correctly
- After `uv build`: version in package should be correct

### 6. Update CI/CD if needed
- Ensure builds work with dynamic versioning
- Tag releases to create version numbers
- Document release process

### 7. Document the scheme
- Add to CONTRIBUTING.md how versioning works
- Explain how to create releases (git tags)
- Document version format

## Acceptance Criteria
- No hard-coded version in pyproject.toml or source code
- Version automatically generated from git tags
- `confl --version` shows correct version
- Tagged commits show clean versions (e.g., `1.0.0`)
- Commits between tags show dev versions (e.g., `1.0.0.dev5+gabc123f`)
- Initial tag `v1.0.0` created
- Builds and installs work with dynamic versioning
- Documentation updated

## References
- https://setuptools-scm.readthedocs.io/ - setuptools-scm docs
- https://github.com/pypa/setuptools-scm - implementation
- pyproject.toml - current version configuration
- src/confl/cli.py or similar - where --version is implemented

## Notes
- no-guess-dev is good for development clarity
- Each commit gets unique version string
- Release = create git tag (e.g., `v1.0.0`, `v1.1.0`)
- No more manual version bumps
- Works with pip, pipx, uv, etc.
- Consider using hatchling-vcs if using hatch/hatchling build backend

**2026-01-27T09:59:51Z**

Completed: Implemented automatic version numbering with no-guess-dev scheme using hatch-vcs. Version 1.0.0 baseline established, --version flag added, tests and documentation updated.

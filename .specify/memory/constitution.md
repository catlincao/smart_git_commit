<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version Change: 1.0.0 → 1.0.1 (Python version clarification)
Modified Principles:
  - VI. Type Safety & Documentation: Python 3.12+ → Python 3.11+
  - VIII. Technology Stack: Python 3.12+ → Python 3.11+
Added Sections: N/A
Removed Sections: N/A
Templates Requiring Updates:
  ✅ specs/001-smart-git-commit/plan.md - updated Technical Context
  ✅ CLAUDE.md - agent context updated
  ⚠ pyproject.toml - requires manual update when created
Follow-up TODOs:
  - Update pyproject.toml requires-python field when file is created
================================================================================
-->

# Smart Git Commit Constitution

## Core Principles

### I. English-Only Interface

All user-facing content MUST be in English.

**Non-negotiable rules:**
- CLI interface, commands, options, and help text MUST be in English
- All documentation (README, docstrings, comments) MUST be in English
- Error messages and logging MUST be in English
- No internationalization (i18n) support will be added

**Rationale:**
A single language keeps the codebase simple and accessible to the global developer community. Git itself uses English commands, maintaining consistency with the host tool.

### II. Out-of-the-Box Experience

The tool MUST work with minimal configuration.

**Non-negotiable rules:**
- Default configuration MUST be sufficient for basic usage
- Required configuration (API keys) MUST be clearly documented with setup instructions
- Sensible defaults MUST be provided for all optional settings
- First-run experience MUST guide users to configure necessary settings

**Rationale:**
Developers have many tools competing for their attention. Friction during setup leads to abandonment. Smart defaults reduce cognitive load and let users focus on their work.

### III. Git Workflow Integration

The tool MUST complement git, not replace it.

**Non-negotiable rules:**
- The tool MUST NOT modify git's core behavior
- The tool MUST be invokable as a git subcommand (`git smart-commit` or alias)
- The tool MUST respect existing git hooks and configurations
- Generated commit messages MUST follow the Semantic Git Commit Message standard
- User MUST always have the final say before committing

**Rationale:**
Developers have established workflows. Replacing git creates friction and resistance. Acting as a helpful assistant that generates suggestions respects user autonomy while adding value.

### IV. Performance First

Minimize latency and avoid blocking the user.

**Non-negotiable rules:**
- LLM calls MUST be streaming where possible to show progress
- Timeout MUST be configurable with sensible defaults (e.g., 10 seconds)
- Git diff analysis MUST be performed locally before any API call
- The tool MUST handle large diffs gracefully (truncate or summarize)
- Response time MUST be optimized through prompt engineering

**Rationale:**
Waiting for AI responses disrupts developer flow. Fast feedback keeps developers productive. Local preprocessing reduces API costs and latency.

### V. Clean Architecture & Separation of Concerns

Modules MUST have clear, single responsibilities.

**Non-negotiable rules:**
- `git` module: ONLY handles git repository interactions (diffs, logs, config)
- `llm` module: ONLY handles LLM API communication and prompt construction
- `ui` module: ONLY handles CLI presentation and user interaction
- `config` module: ONLY handles configuration management
- Cross-cutting concerns (logging, errors) MUST be in shared utilities
- Circular dependencies between modules are FORBIDDEN

**Rationale:**
Clear separation enables independent testing, easier maintenance, and parallel development. Each module can be understood and modified in isolation.

### VI. Type Safety & Documentation

Code MUST be self-documenting through types and docstrings.

**Non-negotiable rules:**
- ALL functions MUST have type hints (Python 3.11+ syntax)
- ALL public APIs MUST have Google-style docstrings in English
- Complex logic MUST have inline comments explaining the "why"
- Code SHOULD be readable without comments; comments explain intent, not mechanism
- README.md MUST follow GitHub open source best practices

**Rationale:**
Type hints catch errors at development time and improve IDE support. Good documentation lowers the barrier for contributors and users.

### VII. Test Coverage (NON-NEGOTIABLE)

All code MUST be tested with >70% coverage.

**Non-negotiable rules:**
- Unit tests MUST cover all public functions
- Integration tests MUST verify git workflow interactions
- LLM interactions MUST be mocked in tests
- Test coverage MUST be measured and reported
- No code may be merged if it reduces overall coverage below 70%

**Rationale:**
Tests provide confidence for refactoring and prevent regressions. LLM-based tools are inherently non-deterministic; robust testing of the surrounding logic is essential.

### VIII. Technology Stack

The following technology choices are fixed.

**Non-negotiable rules:**
- Python 3.11+ is the ONLY supported runtime
- `uv` MUST be used for package management
- Only OpenAI-compatible Chat Completion APIs are supported
- Click (or Typer) MUST be used for CLI framework
- pytest MUST be used for testing

**Rationale:**
Constraining the tech stack reduces maintenance burden and ensures consistency. Modern Python features (3.12+) improve code quality. `uv` is significantly faster than alternatives.

## Additional Constraints

### Project Structure

```
src/smart_git_commit/
├── __init__.py
├── __main__.py          # Entry point for `python -m`
├── cli.py               # CLI interface and commands
├── config.py            # Configuration management
├── git/                 # Git operations module
│   ├── __init__.py
│   ├── diff.py          # Diff extraction and analysis
│   └── repository.py    # Repository state queries
├── llm/                 # LLM interaction module
│   ├── __init__.py
│   ├── client.py        # API client
│   └── prompt.py        # Prompt templates and construction
└── ui/                  # User interface module
    ├── __init__.py
    ├── console.py       # Rich console output
    └── messages.py      # Message formatting
tests/
├── unit/                # Unit tests mirroring src structure
├── integration/         # Integration tests
└── fixtures/            # Test fixtures and mocks
```

### No GUI Policy

- NO graphical user interface will be developed
- NO web interface will be developed
- CLI is the ONLY supported interface

### Scope Boundaries

- The tool generates commit message SUGGESTIONS only
- The tool does NOT automatically commit
- The tool does NOT modify files
- The tool does NOT perform git operations without explicit user confirmation

## Development Workflow

### Code Review Requirements

- All PRs MUST pass CI (tests, type checking, linting)
- All PRs MUST be reviewed by at least one maintainer
- PRs MUST include tests for new functionality
- PRs MUST update documentation if user-facing behavior changes

### Quality Gates

- Type checking with `mypy --strict` MUST pass
- Linting with `ruff` MUST pass
- Test coverage MUST remain >70%
- All tests MUST pass

## Governance

### Amendment Procedure

1. **Proposal**: Create a PR with proposed changes and rationale
2. **Review**: Discuss impact on existing code and templates
3. **Approval**: Requires approval from project maintainer
4. **Documentation**: Update all affected documentation

### Versioning Policy

The constitution follows semantic versioning:

- **MAJOR** (X.0.0): Backward incompatible principle removals or redefinitions
- **MINOR** (x.Y.0): New principle added or materially expanded guidance
- **PATCH** (x.y.Z): Clarifications, wording improvements, typo fixes

### Compliance Review

- All features MUST be validated against these principles before implementation
- Code reviews MUST verify compliance with architecture principles
- Quarterly review of constitution effectiveness is recommended

**Version**: 1.0.1 | **Ratified**: 2026-03-30 | **Last Amended**: 2026-03-30

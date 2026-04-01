# Implementation Plan: Smart Git Commit

**Branch**: `001-smart-git-commit` | **Date**: 2026-03-30 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-smart-git-commit/spec.md`

## Summary

Smart Git Commit is a CLI tool that generates AI-powered commit messages by analyzing staged git changes and matching the project's historical commit style. The tool provides an interactive workflow for reviewing and editing generated messages before committing, with a focus on performance, clean architecture, and excellent user experience.

Technical approach: Python 3.11+ CLI application using Typer for command handling, Rich for UI/output, OpenAI SDK for LLM integration, GitPython for git operations, and Pydantic for configuration management.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Typer (CLI framework), Rich (console output), OpenAI SDK (LLM API), GitPython (git operations), Pydantic (config validation), PyYAML (config files)
**Storage**: YAML configuration files (~/.smart-git-commit.yaml and .smart-git-commit.yaml for project-level)
**Testing**: pytest with pytest-cov for coverage
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: CLI tool / Python package
**Performance Goals**: <10 seconds for message generation (excluding LLM latency), <30 seconds for complete interactive flow
**Constraints**: Must handle diffs up to 100KB, support OpenAI-compatible APIs only, maintain >70% test coverage
**Scale/Scope**: Single-user local tool, no server component

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. English-Only Interface | ✅ PASS | All CLI output, docs, messages in English |
| II. Out-of-the-Box Experience | ✅ PASS | Auto-config on first run, sensible defaults, guided setup |
| III. Git Workflow Integration | ✅ PASS | Complements git (no replacement), user confirmation required, semantic commit format |
| IV. Performance First | ✅ PASS | Loading indicators, streaming support, diff preprocessing, timeout handling |
| V. Clean Architecture | ✅ PASS | Modular design: git/, llm/, analyzer/, generator/, cli/, config/ modules |
| VI. Type Safety & Documentation | ✅ PASS | Python 3.11+ type hints, Google docstrings, GitHub-style README |
| VII. Test Coverage | ✅ PASS | Target >70% coverage, pytest framework, mocked LLM tests |
| VIII. Technology Stack | ✅ PASS | Python 3.11+, uv, Typer (Click alternative), pytest |

**Re-check after design**: All principles remain satisfied with chosen architecture.

## Project Structure

### Documentation (this feature)

```text
specs/001-smart-git-commit/
├── plan.md              # This file
├── research.md          # Phase 0 research output
├── data-model.md        # Phase 1 data models
├── quickstart.md        # Phase 1 quickstart guide
├── contracts/           # Interface contracts
└── tasks.md             # Phase 2 tasks (generated later)
```

### Source Code (repository root)

```text
src/smart_git_commit/
├── __init__.py          # Package version and exports
├── __main__.py          # Entry point for `python -m smart_git_commit`
├── cli.py               # Typer CLI commands and interface
├── config/
│   ├── __init__.py
│   ├── models.py        # Pydantic config models
│   ├── manager.py       # Multi-level config resolution
│   └── wizard.py        # Interactive config setup
├── git/
│   ├── __init__.py
│   ├── repository.py    # Git repo detection and validation
│   ├── diff.py          # Staged diff extraction
│   └── history.py       # Commit history analysis
├── llm/
│   ├── __init__.py
│   ├── client.py        # OpenAI SDK wrapper
│   ├── provider.py      # Provider interface for extensibility
│   └── prompts.py       # Prompt templates
├── analyzer/
│   ├── __init__.py
│   ├── style.py         # Commit style detection
│   └── tokenizer.py     # Diff truncation/token counting
└── generator/
    ├── __init__.py
    └── engine.py        # Message generation orchestration

tests/
├── unit/
│   ├── test_config/
│   ├── test_git/
│   ├── test_llm/
│   ├── test_analyzer/
│   └── test_generator/
├── integration/
│   └── test_cli_flow.py
└── fixtures/
    ├── mock_config.yaml
    └── sample_diffs/

pyproject.toml           # Project metadata and dependencies
README.md                # GitHub-style documentation
```

**Structure Decision**: Single CLI tool with clear module separation per constitution principle V. Each module has a single responsibility: `git/` for git operations, `llm/` for AI integration, `analyzer/` for style detection, `generator/` for message creation, `cli/` for user interface, and `config/` for settings management.

## Research Decisions

### Typer vs Click

**Decision**: Use **Typer**

**Rationale**:
- Typer is built on Click but provides automatic type hints integration
- Native support for Python 3.12+ type annotations
- Automatic help text generation from docstrings
- Better IDE support and autocomplete
- Modern async support for streaming LLM responses
- Less boilerplate code for commands

**Trade-offs**:
- Slightly higher-level abstraction than Click
- Less control over advanced CLI patterns (acceptable for this use case)

### Rich vs click.echo

**Decision**: Use **Rich**

**Rationale**:
- Superior formatting: syntax highlighting, markdown rendering, tables
- Built-in progress indicators (spinner, progress bars)
- Interactive prompts with validation
- Better error display with panels and styling
- Native support for color themes and terminal detection
- Can be used alongside Typer (Typer supports Rich console)

**Trade-offs**:
- Additional dependency (~30KB)
- Acceptable given the UX requirements

### Loading Animation: yaspin vs rich.progress

**Decision**: Use **Rich Spinner**

**Rationale**:
- Rich's built-in spinner (`console.status()`) provides elegant loading states
- No additional dependency (already using Rich)
- Consistent styling with other UI elements
- Supports custom spinner text and animation styles
- Better integration with Rich Console

**Alternative considered**: yaspin is lighter but adds another dependency when Rich already covers this need.

## Complexity Tracking

No constitution violations requiring justification.

## Architecture Decisions

### 1. Multi-Level Configuration

Configuration follows a cascading priority:
1. Environment variables (highest priority)
2. Project-level `.smart-git-commit.yaml`
3. Global `~/.smart-git-commit.yaml`
4. Built-in defaults (lowest priority)

**Rationale**: Allows per-project overrides while maintaining user defaults. Pydantic models validate at each level.

### 2. LLM Provider Interface

```python
class LLMProvider(Protocol):
    async def generate(self, prompt: str, context: dict) -> str: ...
    def validate_config(self) -> bool: ...
```

**Rationale**: Protocol-based design allows easy extension to other providers (Anthropic, local models) while keeping OpenAI as the default implementation.

### 3. Diff Processing Pipeline

```
Raw Diff → Tokenizer Check → Truncation (if needed) → Analysis Context
```

**Rationale**: Prevents token limit errors with large diffs. Uses tiktoken for accurate token counting.

### 4. Error Handling Strategy

All errors are wrapped in custom exceptions with:
- User-friendly message (displayed)
- Technical details (logged)
- Resolution hints (displayed)
- Exit codes for scripting

**Rationale**: Meets constitution requirement for clear, actionable error messages.

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-30

### Added
- Initial release of Smart Git Commit
- Interactive commit message generation using LLMs
- Support for OpenAI-compatible APIs
- Automatic semantic commit format detection
- Configuration wizard for first-time setup
- Silent mode (`--silence`) for quick commits
- Multi-level configuration (env → project → global)
- Git repository validation and error handling
- Diff truncation for large changes
- Rich CLI interface with progress indicators
- Comprehensive test suite (>70% coverage)

### Features
- Analyzes staged git changes
- Detects project commit style from history
- Generates semantic commit messages
- Interactive message editing
- User confirmation before committing
- Support for multiple LLM providers
- Token counting and management
- YAML-based configuration

[0.1.0]: https://github.com/yourusername/smart-git-commit/releases/tag/v0.1.0

# CLI Command Contracts

**Date**: 2026-03-30
**Feature**: Smart Git Commit CLI Tool

## Command Overview

| Command | Description | Required Config |
|---------|-------------|-----------------|
| `sgc` (default) | Generate commit message interactively | Yes |
| `sgc --config` | Run configuration wizard | No |
| `sgc --help` | Show help information | No |
| `sgc --silence` | Generate and commit without prompts | Yes |
| `sgc --version` | Show version information | No |

## Command: Default (Interactive)

**Usage**: `sgc [OPTIONS]`

**Behavior**:
1. Check for configuration (auto-run wizard if missing)
2. Validate git repository
3. Check for staged changes
4. Analyze commit history
5. Generate commit message via LLM
6. Display message in interactive editor
7. On confirmation, execute `git commit`

**Options**:
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config` | flag | false | Run configuration wizard |
| `--silence` | flag | false | Skip interactive prompts |
| `--help` | flag | false | Show help and exit |
| `--version` | flag | false | Show version and exit |

**Exit Codes**:
| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Not a git repository |
| 3 | No staged changes |
| 4 | Configuration error |
| 5 | LLM API error |
| 130 | User cancelled (Ctrl+C) |

**Output Format**:
```
┌─────────────────────────────────────────────────────────────┐
│  Generated Commit Message                                   │
├─────────────────────────────────────────────────────────────┤
│  feat(auth): add OAuth2 login support                       │
│                                                             │
│  - Implement OAuth2 flow with PKCE                          │
│  - Add token refresh mechanism                              │
│  - Update documentation                                     │
└─────────────────────────────────────────────────────────────┘

Edit message? [y/N]: y
[Opens in $EDITOR]

Proceed with commit? [Y/n]: y
[main 4a5b6c7] feat(auth): add OAuth2 login support
```

## Command: Configuration Wizard

**Usage**: `sgc --config`

**Behavior**:
1. Check for existing configuration
2. Prompt for LLM settings interactively
3. Validate API connection
4. Save to configuration file

**Interactive Prompts**:
```
Smart Git Commit - Configuration

LLM Base URL [https://api.openai.com/v1]:
Model Name [gpt-4o-mini]:
API Key: [hidden input]
Default Language [en_US]:
Use Semantic Commits? [Y/n]:

Testing connection... ✓
Configuration saved to ~/.smart-git-commit.yaml
```

**Validation**:
- URL must be valid HTTPS endpoint
- API key must not be empty
- Connection test must succeed before saving

## Command: Silent Mode

**Usage**: `sgc --silence`

**Behavior**:
Same as default but skips message review and confirmation.

**Constraints**:
- Requires valid configuration (error if not configured)
- No user interaction except error cases
- Shows spinner during generation

**Output**:
```
Generating commit message... ✓
[main 4a5b6c7] feat(auth): add OAuth2 login support
```

## Error Output Format

All errors follow consistent format:

```
┌─────────────────────────────────────────────────────────────┐
│  Error: [Brief Error Title]                                 │
├─────────────────────────────────────────────────────────────┤
│  [Detailed explanation of what went wrong]                  │
│                                                             │
│  Suggestions:                                               │
│  • [Actionable suggestion 1]                                │
│  • [Actionable suggestion 2]                                │
│                                                             │
│  Run with --help for more information.                      │
└─────────────────────────────────────────────────────────────┘
```

**Example Errors**:

Not a git repository:
```
Error: Not a Git Repository

The current directory is not a git repository.

Suggestions:
• Initialize a repository with: git init
• Navigate to a git repository
• Check that .git directory exists
```

No staged changes:
```
Error: No Staged Changes

There are no changes staged for commit.

Suggestions:
• Stage files with: git add <files>
• Check status with: git status
• Use -a flag to stage all changes (if supported)
```

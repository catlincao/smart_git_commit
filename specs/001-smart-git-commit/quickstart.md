# Quickstart Guide: Smart Git Commit

**Date**: 2026-03-30

## Installation

### Using pip

```bash
pip install smart-git-commit
```

### Using uv (recommended)

```bash
uv pip install smart-git-commit
```

### From source

```bash
git clone https://github.com/yourusername/smart-git-commit.git
cd smart-git-commit
uv pip install -e .
```

## Initial Setup

### 1. First Run - Configuration Wizard

The first time you run `sgc`, it will guide you through configuration:

```bash
$ sgc

Smart Git Commit - First Time Setup

LLM Base URL [https://api.openai.com/v1]:
Model Name [gpt-4o-mini]:
API Key: sk-xxxxxxxxxxxxxxxxxxxxxxxx
Default Language [en_US]:
Use Semantic Commits? [Y/n]:

Testing connection... ✓
Configuration saved to ~/.smart-git-commit.yaml
```

### 2. Verify Installation

```bash
$ sgc --version
smart-git-commit 0.1.0

$ sgc --help
Usage: sgc [OPTIONS]

  Generate AI-powered commit messages from staged changes.

Options:
  --config    Run configuration wizard
  --silence   Skip interactive prompts and commit directly
  --help      Show this message and exit
  --version   Show version and exit
```

## Basic Usage

### Generate a Commit Message

1. Stage your changes:
```bash
git add src/models.py src/services.py
```

2. Run the tool:
```bash
$ sgc

Analyzing staged changes... ✓
Detecting project style... ✓
Generating commit message... ✓

┌─────────────────────────────────────────────────────────────┐
│  Generated Commit Message                                   │
├─────────────────────────────────────────────────────────────┤
│  feat(models): add user authentication models               │
│                                                             │
│  - Add User model with email/password fields               │
│  - Add authentication service                             │
│  - Add password hashing utilities                         │
└─────────────────────────────────────────────────────────────┘

Edit message? [y/N]: n
Proceed with commit? [Y/n]: y

[main 4a5b6c7] feat(models): add user authentication models
 2 files changed, 85 insertions(+)
```

### Edit Before Committing

If you want to modify the generated message:

```bash
$ sgc
...

Edit message? [y/N]: y
# Opens your default $EDITOR

Proceed with commit? [Y/n]: y
```

### Quick Commit (Silent Mode)

For when you trust the AI generation:

```bash
$ sgc --silence

Generating commit message... ✓
[main 4a5b6c7] fix(auth): correct password validation regex
 1 file changed, 3 insertions(+), 3 deletions(-)
```

## Configuration

### Global Configuration

Edit `~/.smart-git-commit.yaml`:

```yaml
llm:
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key: "${OPENAI_API_KEY}"  # Uses environment variable
  timeout_seconds: 30

style:
  language: "en_US"
  use_semantic_commits: true
  max_diff_tokens: 4000

behavior:
  auto_commit_silence: false
  confirm_before_commit: true
```

### Project-Level Configuration

Create `.smart-git-commit.yaml` in your project root to override global settings:

```yaml
style:
  use_semantic_commits: false  # This project uses simple commits
```

Configuration priority (highest to lowest):
1. Environment variables (`SGC_LLM__API_KEY`)
2. Project `.smart-git-commit.yaml`
3. Global `~/.smart-git-commit.yaml`
4. Built-in defaults

### Environment Variables

All configuration values can be set via environment variables:

```bash
export SGC_LLM__API_KEY="sk-..."
export SGC_LLM__MODEL="gpt-4o"
export SGC_STYLE__LANGUAGE="en_US"
```

## Common Workflows

### Alias for git

Add to your `.bashrc` or `.zshrc`:

```bash
alias gc='sgc'
# or
git config --global alias.sgc '!sgc'
```

Then use:
```bash
git add .
git sgc  # or just 'gc'
```

### Pre-commit Integration

Smart Git Commit works alongside pre-commit hooks. Your hooks will run normally when the commit is executed.

### CI/CD Usage

For automated environments, use `--silence` mode:

```bash
sgc --silence
```

## Troubleshooting

### "Not a git repository"

```bash
# Make sure you're in a git repository
git status

# If not, initialize one
git init
```

### "No staged changes"

```bash
# Stage your changes first
git add <files>

# Or stage all changes
git add -A
```

### API Errors

Check your configuration:
```bash
sgc --config
```

Verify your API key and base URL are correct.

### Large Diffs

The tool automatically truncates large diffs. You can adjust the limit in configuration:

```yaml
style:
  max_diff_tokens: 6000  # Increase if needed
```

## Tips

1. **Start with interactive mode** to review AI-generated messages
2. **Use `--silence`** only after you're confident in the output quality
3. **Keep your API key in environment variables** for security
4. **Project-level config** helps maintain consistency across team members

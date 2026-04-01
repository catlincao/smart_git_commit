# Smart Git Commit

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

AI-powered git commit message generator that analyzes your staged changes and creates semantic commit messages matching your project's style.

## Features

- 🤖 **AI-Powered**: Uses LLMs to generate meaningful commit messages
- 📝 **Semantic Commits**: Follows Conventional Commits format automatically
- 🎨 **Style Matching**: Learns from your project's commit history
- ⚡ **Fast**: Minimal latency with streaming responses
- 🔧 **Configurable**: Supports multiple LLM providers (OpenAI-compatible APIs)
- 🎯 **Git Native**: Works seamlessly with your existing git workflow

## Installation

### Using pip

```bash
pip install smart-git-commit
```

### Using uv (recommended)

```bash
uv pip install smart-git-commit
```

## Quick Start

1. **Configure the tool** (first run):
```bash
sgc --config
```

2. **Generate a commit message**:
```bash
git add .
sgc
```

3. **Quick commit mode** (skip review):
```bash
sgc --silence
```

## Usage

### Interactive Mode (Default)

```bash
$ git add src/models.py
$ sgc

Analyzing staged changes... ✓
Detecting project style... ✓
Generating commit message... ✓

┌─────────────────────────────────────────────────────────────┐
│  Generated Commit Message                                   │
├─────────────────────────────────────────────────────────────┤
│  feat(models): add user authentication                      │
│                                                             │
│  - Add User model with email and password fields           │
│  - Implement password hashing                              │
│  - Add validation logic                                    │
└─────────────────────────────────────────────────────────────┘

Edit message? [y/N]: n
Proceed with commit? [Y/n]: y

[main a1b2c3d] feat(models): add user authentication
 1 file changed, 85 insertions(+)
```

### Commands

| Command | Description |
|---------|-------------|
| `sgc` | Generate commit message interactively |
| `sgc --config` | Run configuration wizard |
| `sgc --silence` | Skip prompts and commit directly |
| `sgc --help` | Show help information |
| `sgc --version` | Show version |

## Configuration

Configuration is stored in `~/.smart-git-commit.yaml`:

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

You can also create a project-level `.smart-git-commit.yaml` for per-project settings.

## Requirements

- Python 3.11+
- Git repository
- OpenAI-compatible API key

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

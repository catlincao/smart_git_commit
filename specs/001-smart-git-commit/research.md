# Research: Smart Git Commit

**Date**: 2026-03-30
**Feature**: Smart Git Commit CLI Tool

## Research Questions Resolved

### Q1: CLI Framework - Typer vs Click

**Decision**: Typer

**Research Findings**:
- Typer (by FastAPI author) is built on top of Click
- Provides automatic type hint integration - no need for explicit option types
- Generates help text automatically from function docstrings
- Supports async/await natively (important for streaming LLM responses)
- Better type completion in IDEs due to annotation-based approach
- Reduces boilerplate code significantly

**Code Comparison**:
```python
# Click approach
@click.command()
@click.option('--name', '-n', required=True, help='Your name')
def hello(name: str):
    """Say hello."""
    click.echo(f"Hello {name}!")

# Typer approach
import typer
app = typer.Typer()

@app.command()
def hello(name: str = typer.Option(..., '--name', '-n', help='Your name')):
    """Say hello."""
    typer.echo(f"Hello {name}!")
```

**Conclusion**: Typer's modern Python approach aligns with project constitution's emphasis on type safety and clean code.

---

### Q2: Console Output - Rich vs click.echo

**Decision**: Rich

**Research Findings**:
- Rich provides comprehensive terminal formatting
- Built-in components: Panels, Tables, Syntax highlighting, Progress bars
- Interactive prompts with `Prompt.ask()`, `Confirm.ask()`
- Markdown rendering support (useful for commit message display)
- Automatic terminal width detection and wrapping
- Color palette adapts to terminal capabilities

**Key Features for This Project**:
- `Console.status()` for loading indicators during LLM calls
- `Panel()` for framing generated commit messages
- `Syntax()` for highlighting code diffs if needed
- `prompt()` for interactive editing

**Conclusion**: Rich significantly improves UX compared to basic echo output.

---

### Q3: Loading Animation Options

**Decision**: Rich Console.status()

**Options Evaluated**:

1. **yaspin**
   - Lightweight spinner library
   - Simple API: `with yaspin(text="Loading...") as spinner:`
   - Additional dependency

2. **rich.progress** / `console.status()`
   - Built into Rich (already a dependency)
   - Elegant API: `with console.status("[bold green]Generating..."):`
   - Consistent styling with rest of UI
   - Multiple spinner styles available

**Conclusion**: Using Rich's built-in spinner eliminates an extra dependency while maintaining quality.

---

### Q4: Git Operations Library

**Decision**: GitPython

**Research Findings**:
- GitPython is the standard Python library for git operations
- Provides object-oriented interface to git repositories
- Supports reading diffs, commit history, and repository state
- Well-maintained with extensive documentation
- Allows low-level access when needed

**Alternatives Considered**:
- Subprocess calls to `git` command: More fragile, requires parsing output
- Dulwich: Pure Python, but lower-level API
- pygit2: Requires libgit2 installation

**Conclusion**: GitPython provides the right balance of abstraction and control.

---

### Q5: Configuration Format and Validation

**Decision**: YAML + Pydantic

**Research Findings**:
- YAML is human-readable and supports comments (unlike JSON)
- Pydantic v2 provides robust validation with type hints
- Supports environment variable substitution
- Can define defaults and validators

**Configuration Structure**:
```yaml
# ~/.smart-git-commit.yaml
llm:
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"
  api_key: "${OPENAI_API_KEY}"  # env var substitution

style:
  language: "en_US"
  use_semantic_commits: true
  max_diff_tokens: 4000

behavior:
  timeout_seconds: 30
  auto_commit_silence: false
```

**Conclusion**: YAML + Pydantic provides type-safe, validated configuration with good UX.

---

### Q6: LLM Token Management

**Decision**: tiktoken for token counting

**Research Findings**:
- OpenAI's tiktoken library provides accurate token counting
- Critical for preventing API errors with large diffs
- Supports different encoding models (cl100k_base for GPT-4)
- Allows pre-truncation before API call

**Truncation Strategy**:
1. Count tokens in diff
2. If exceeds threshold (e.g., 4000), truncate with ellipsis
3. Add note to prompt that diff was truncated
4. Prioritize showing file names and change types

**Conclusion**: Proactive token management prevents runtime errors.

---

### Q7: Prompt Engineering Approach

**Decision**: Template-based with dynamic context

**Research Findings**:
- Few-shot prompting with project examples improves style matching
- Structured prompts with clear sections work best
- Include:
  - Project context (detected style)
  - Diff summary
  - Semantic commit format reminder
  - Examples from project history

**Prompt Structure**:
```
You are a commit message generator. Analyze the following git diff and generate a commit message.

Project Style: {detected_style}
Examples from this project:
{example_commits}

Guidelines:
- Use Semantic Commit format: type(scope): subject
- Keep subject under 50 characters
- Use imperative mood

Git Diff:
{diff}

Generate a commit message:
```

**Conclusion**: Dynamic prompts with project context yield better results.

---

### Q8: Testing Strategy for LLM Components

**Decision**: Mock-based unit tests + integration tests with recorded responses

**Research Findings**:
- LLM responses are non-deterministic, making traditional assertions difficult
- Use mocking for unit tests (test logic, not LLM)
- VCR.py or similar for recording/replaying integration tests
- Focus tests on:
  - Prompt construction
  - Response parsing
  - Error handling
  - Token management

**Conclusion**: Test the code around the LLM, not the LLM itself.

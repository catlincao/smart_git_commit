# Data Model: Smart Git Commit

**Date**: 2026-03-30
**Feature**: Smart Git Commit CLI Tool

## Core Entities

### Configuration

Stores user preferences and API credentials.

```python
class LLMConfig(BaseModel):
    """LLM API configuration."""
    base_url: str = Field(default="https://api.openai.com/v1")
    model: str = Field(default="gpt-4o-mini")
    api_key: SecretStr  # Masked in logs/output
    timeout_seconds: int = Field(default=30, ge=5, le=300)

class StyleConfig(BaseModel):
    """Commit style preferences."""
    language: str = Field(default="en_US", pattern=r"^[a-z]{2}_[A-Z]{2}$")
    use_semantic_commits: bool = True
    max_diff_tokens: int = Field(default=4000, ge=1000, le=8000)

class BehaviorConfig(BaseModel):
    """Behavioral settings."""
    auto_commit_silence: bool = False
    confirm_before_commit: bool = True
    show_token_count: bool = False

class Config(BaseModel):
    """Root configuration model."""
    llm: LLMConfig
    style: StyleConfig = Field(default_factory=StyleConfig)
    behavior: BehaviorConfig = Field(default_factory=BehaviorConfig)

    model_config = ConfigDict(
        env_prefix="SGC_",
        env_nested_delimiter="__",
    )
```

**Validation Rules**:
- `api_key` must not be empty when validating
- `model` must match supported models (validated at runtime)
- `max_diff_tokens` must stay within API limits

---

### GitContext

Encapsulates repository state and extracted information.

```python
class RepositoryStatus(Enum):
    """Repository validation states."""
    VALID = "valid"
    NOT_A_REPO = "not_a_repo"
    NO_COMMITS = "no_commits"
    NO_STAGED_CHANGES = "no_staged_changes"

class FileChange(BaseModel):
    """Single file change information."""
    path: str
    change_type: Literal["added", "modified", "deleted", "renamed"]
    additions: int
    deletions: int
    diff_content: Optional[str] = None

class GitContext(BaseModel):
    """Complete git repository context."""
    status: RepositoryStatus
    repo_path: Optional[Path] = None
    branch: Optional[str] = None
    staged_files: list[FileChange] = Field(default_factory=list)
    total_additions: int = 0
    total_deletions: int = 0
    raw_diff: Optional[str] = None
    recent_commits: list[str] = Field(default_factory=list)

    @property
    def has_staged_changes(self) -> bool:
        return len(self.staged_files) > 0

    @property
    def is_valid(self) -> bool:
        return self.status == RepositoryStatus.VALID
```

**Validation Rules**:
- `raw_diff` should be None if `status` is not VALID
- `staged_files` must be empty if `status` is NO_STAGED_CHANGES

---

### CommitStyle

Represents detected project commit conventions.

```python
class CommitType(Enum):
    """Semantic commit types."""
    FEAT = "feat"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    TEST = "test"
    CHORE = "chore"
    BUILD = "build"
    CI = "ci"
    PERF = "perf"

class CommitStyle(BaseModel):
    """Detected project commit style."""
    uses_semantic_commits: bool
    common_types: list[CommitType]
    common_scopes: list[str]
    average_subject_length: int
    examples: list[str]  # Recent commit messages as examples

    @property
    def suggested_types(self) -> list[CommitType]:
        """Return types to suggest based on project history."""
        return self.common_types[:5] if self.common_types else [
            CommitType.FEAT, CommitType.FIX, CommitType.DOCS
        ]
```

---

### GeneratedMessage

Represents an AI-generated commit message.

```python
class GeneratedMessage(BaseModel):
    """AI-generated commit message."""
    commit_type: Optional[CommitType] = None
    scope: Optional[str] = None
    subject: str  # Required, max 72 chars
    body: Optional[str] = None  # Optional detailed description
    breaking_change: Optional[str] = None

    @field_validator('subject')
    @classmethod
    def validate_subject(cls, v: str) -> str:
        if len(v) > 72:
            raise ValueError("Subject must be 72 characters or less")
        if not v[0].isupper() and not v[0].islower():
            raise ValueError("Subject must start with a letter")
        return v

    def to_full_message(self) -> str:
        """Convert to full commit message format."""
        header = f"{self.commit_type.value}" if self.commit_type else ""
        if self.scope:
            header += f"({self.scope})"
        if header:
            header += ": "
        header += self.subject

        parts = [header]

        if self.body:
            parts.append("")
            parts.append(self.body)

        if self.breaking_change:
            parts.append("")
            parts.append(f"BREAKING CHANGE: {self.breaking_change}")

        return "\n".join(parts)

    def to_one_line(self) -> str:
        """Return one-line representation."""
        prefix = ""
        if self.commit_type:
            prefix = self.commit_type.value
            if self.scope:
                prefix += f"({self.scope})"
            prefix += ": "
        return f"{prefix}{self.subject}"
```

**Validation Rules**:
- `subject` is required and max 72 characters
- `subject` should use imperative mood (enforced via prompt, not validation)
- `body` can be multi-line

---

### PromptContext

Context passed to LLM for message generation.

```python
class PromptContext(BaseModel):
    """Context for LLM prompt generation."""
    diff_summary: str
    files_changed: list[str]
    total_additions: int
    total_deletions: int
    project_style: CommitStyle
    examples: list[str]
    was_truncated: bool = False

    def to_prompt(self) -> str:
        """Generate the complete prompt string."""
        # Implementation in llm/prompts.py
        pass
```

---

## Entity Relationships

```
Config
├── LLMConfig
├── StyleConfig
└── BehaviorConfig

GitContext
├── RepositoryStatus (enum)
└── FileChange[]

CommitStyle
├── CommitType[] (enum)
└── examples: string[]

GeneratedMessage
├── CommitType (optional)
└── scope: string (optional)

PromptContext
├── GitContext (reference)
└── CommitStyle (reference)
```

## State Transitions

### Configuration Flow

```
[No Config] → ConfigWizard → [Valid Config] → Use Config
                    ↓
            [Invalid Input] → Retry
```

### Commit Generation Flow

```
[Check Repo] → Valid? → [Get Diff] → Has Changes? → [Analyze Style]
    ↓ No              ↓ No
[Error]          [Error]

[Analyze Style] → [Build Prompt] → [Call LLM] → [Parse Response]
                                               ↓
                                        [Show Message]
                                               ↓
                              [User Edit] → [Confirm] → [Git Commit]
```

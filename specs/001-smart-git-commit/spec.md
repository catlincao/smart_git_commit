# Feature Specification: Smart Git Commit

**Feature Branch**: `001-smart-git-commit`
**Created**: 2026-03-30
**Status**: Draft
**Input**: User description: "做一个 CLI 工具叫 Smart Git Commit，自动生成 git commit message"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Commit Message Interactively (Priority: P1)

Developer has staged changes and wants an AI-generated commit message that matches their project's style.

**Why this priority**: This is the core value proposition - saving developers time writing commit messages while maintaining consistency with project conventions.

**Independent Test**: Can be fully tested by staging files in a git repository, running the tool, reviewing the generated message, and confirming the commit.

**Acceptance Scenarios**:

1. **Given** a git repository with staged changes, **When** the developer runs the tool, **Then** it analyzes the staged diff and generates a Semantic Commit formatted message matching the project's historical style.

2. **Given** the tool has generated a message, **When** the developer reviews it, **Then** they can edit the message before confirming the commit.

3. **Given** the developer is satisfied with the generated message, **When** they confirm, **Then** the commit is executed with that message.

---

### User Story 2 - First-Time Configuration (Priority: P1)

First-time user needs to configure the tool before using it.

**Why this priority**: Without proper configuration (API keys), the tool cannot function. This must work seamlessly for new users.

**Independent Test**: Can be tested by removing the config file and running the tool - it should guide through configuration.

**Acceptance Scenarios**:

1. **Given** a user has never configured the tool, **When** they run the tool for the first time, **Then** it automatically launches the configuration wizard.

2. **Given** the configuration wizard is running, **When** the user provides API base URL, model name, and API key, **Then** these are saved to the config file.

3. **Given** the configuration wizard is running, **When** the user sets language and Semantic Commit preferences, **Then** these defaults are saved for future use.

---

### User Story 3 - Silent Mode for Quick Commits (Priority: P2)

Experienced user wants to skip the review step for faster workflow.

**Why this priority**: Power users who trust the AI generation want minimal friction. This improves efficiency for frequent commits.

**Independent Test**: Can be tested by running with `--silence` flag - should commit immediately without prompting.

**Acceptance Scenarios**:

1. **Given** the user has previously configured the tool, **When** they run with the silence flag, **Then** the tool generates and commits without prompting for review.

2. **Given** the user runs in silence mode without prior configuration, **Then** the tool prompts for configuration first before proceeding.

---

### User Story 4 - Help and Documentation (Priority: P2)

User needs to understand how to use the tool.

**Why this priority**: Good documentation reduces support burden and improves user satisfaction.

**Independent Test**: Can be tested by running `--help` command - should display usage information.

**Acceptance Scenarios**:

1. **Given** a user wants to learn about the tool, **When** they run the help command, **Then** they see comprehensive usage instructions and examples.

2. **Given** a user wants to view or change configuration, **When** they run the config command, **Then** they can interactively update their settings.

---

### Edge Cases

- **Not a git repository**: Tool detects absence of git and prompts user to initialize
- **Empty staging area**: Tool detects no staged files and prompts user to run `git add` first
- **LLM API failure**: Tool provides clear error message with troubleshooting suggestions
- **Large diffs**: Tool truncates or summarizes diffs to stay within token limits
- **No commit history**: Tool generates reasonable default style without historical reference
- **Invalid API credentials**: Tool detects authentication errors and prompts for reconfiguration

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect if the current directory is a git repository and provide helpful guidance if not
- **FR-002**: System MUST check for staged changes and prompt the user to stage files if none exist
- **FR-003**: System MUST read and analyze the git diff of staged files
- **FR-004**: System MUST analyze recent commit history to detect the project's commit style conventions
- **FR-005**: System MUST generate commit messages following Semantic Commit format (type(scope): subject)
- **FR-006**: System MUST match the generated message style to the project's historical patterns
- **FR-007**: System MUST display the generated message to the user for review
- **FR-008**: System MUST allow the user to edit the generated message before committing
- **FR-009**: System MUST execute `git commit` with the final message upon user confirmation
- **FR-010**: System MUST store configuration in `~/.smart-git-commit.json`
- **FR-011**: System MUST provide a `--config` command for interactive configuration of API settings
- **FR-012**: System MUST provide a `--help` command displaying usage instructions
- **FR-013**: System MUST provide a `--silence` command that skips review and commits directly
- **FR-014**: System MUST display a loading indicator during LLM generation to provide user feedback
- **FR-015**: System MUST provide clear, actionable error messages when failures occur

### Configuration Requirements

- **CR-001**: Configuration MUST support setting LLM base URL
- **CR-002**: Configuration MUST support setting model name
- **CR-003**: Configuration MUST support setting API key
- **CR-004**: Configuration MUST support setting default language (default: en_US)
- **CR-005**: Configuration MUST support toggling Semantic Commit compliance (default: true)

### Key Entities

- **Configuration**: Stores user preferences and API credentials including base_url, model_name, api_key, language, and semantic_commit_enabled
- **GitContext**: Encapsulates repository state including staged diff, recent commit history, and repository validity
- **GeneratedMessage**: Represents the AI-generated commit message with type, scope, subject, and body fields

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can generate a commit message in under 10 seconds (excluding LLM API latency)
- **SC-002**: 90% of generated messages follow the project's detected commit style conventions
- **SC-003**: 95% of users can complete first-time configuration without external help
- **SC-004**: Users can complete the interactive commit flow (generate → review → commit) in under 30 seconds
- **SC-005**: Error messages provide actionable resolution steps in 100% of error cases
- **SC-006**: Tool handles diffs up to 100KB without hitting LLM token limits

## Assumptions

- Users have git installed and available in their PATH
- Users have access to an OpenAI-compatible LLM API endpoint
- Users have write permissions to their home directory for config storage
- Internet connectivity is available for LLM API calls
- The repository has at least one commit to analyze for style detection (fallback to defaults if not)
- Users prefer English interface as specified in project constitution
- CLI is the only interface needed (no GUI or web interface)

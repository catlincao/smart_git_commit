# Tasks: Smart Git Commit

**Input**: Design documents from `/specs/001-smart-git-commit/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, contracts/, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure: `src/smart_git_commit/` with all subdirectories per plan.md
- [X] T002 [P] Create `pyproject.toml` with Python 3.11+ requirement, project metadata, and core dependencies (typer, rich, openai, gitpython, pydantic, pyyaml)
- [X] T003 [P] Create `pyproject.toml` dev dependencies (pytest, pytest-cov, mypy, ruff, black)
- [ ] T004 [P] Initialize uv project with `uv sync` to generate lock files
- [X] T005 Create `.gitignore` for Python projects
- [X] T006 Create `README.md` skeleton with project description

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 [P] Create base exception classes in `src/smart_git_commit/exceptions.py` (GitError, ConfigError, LLMError)
- [X] T008 Create shared utilities in `src/smart_git_commit/utils.py` (logging setup, exit codes)
- [X] T009 Create `src/smart_git_commit/__init__.py` with version constant
- [X] T010 Create `src/smart_git_commit/__main__.py` entry point

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Generate Commit Message Interactively (Priority: P1) 🎯 MVP

**Goal**: Core value proposition - developer stages changes, runs tool, reviews AI-generated commit message, confirms commit

**Independent Test**: Stage files in a git repo, run `sgc`, verify message is generated and can be edited, confirm commits successfully

### Tests for User Story 1

- [ ] T011 [P] [US1] Create unit test for GitContext model validation in `tests/unit/test_git/test_context.py`
- [ ] T012 [P] [US1] Create unit test for GeneratedMessage formatting in `tests/unit/test_generator/test_message.py`
- [ ] T013 [US1] Create integration test for main commit flow in `tests/integration/test_commit_flow.py`

### Implementation for User Story 1

#### Config Module (needed by US1)
- [X] T014 [P] [US1] Create `src/smart_git_commit/config/models.py` with LLMConfig, StyleConfig, BehaviorConfig Pydantic models
- [X] T015 [P] [US1] Create `src/smart_git_commit/config/manager.py` with multi-level config resolution (env → project → global → defaults)
- [X] T016 [US1] Create `src/smart_git_commit/config/__init__.py` with exports

#### Git Module (needed by US1)
- [X] T017 [P] [US1] Create `src/smart_git_commit/git/repository.py` with repo detection and validation (RepositoryStatus enum)
- [X] T018 [P] [US1] Create `src/smart_git_commit/git/diff.py` with staged diff extraction (FileChange dataclass)
- [X] T019 [P] [US1] Create `src/smart_git_commit/git/history.py` with recent commit retrieval for style analysis
- [X] T020 [US1] Create `src/smart_git_commit/git/__init__.py` with exports

#### Analyzer Module (needed by US1)
- [X] T021 [P] [US1] Create `src/smart_git_commit/analyzer/style.py` with CommitStyle detection from git history
- [X] T022 [P] [US1] Create `src/smart_git_commit/analyzer/tokenizer.py` with tiktoken integration for diff truncation
- [X] T023 [US1] Create `src/smart_git_commit/analyzer/__init__.py` with exports

#### LLM Module (needed by US1)
- [X] T024 [P] [US1] Create `src/smart_git_commit/llm/provider.py` with LLMProvider Protocol interface
- [X] T025 [P] [US1] Create `src/smart_git_commit/llm/client.py` with OpenAI SDK wrapper implementing LLMProvider
- [X] T026 [US1] Create `src/smart_git_commit/llm/prompts.py` with PromptContext and prompt template generation
- [X] T027 [US1] Create `src/smart_git_commit/llm/__init__.py` with exports

#### Generator Module (needed by US1)
- [X] T028 [US1] Create `src/smart_git_commit/generator/engine.py` with GeneratedMessage creation and orchestration
- [X] T029 [US1] Create `src/smart_git_commit/generator/__init__.py` with exports

#### CLI Module (US1 core)
- [X] T030 [US1] Create `src/smart_git_commit/cli.py` with Typer app and default command implementation (interactive flow)
- [X] T031 [US1] Implement repository validation with helpful error messages
- [X] T032 [US1] Implement staged changes check with guidance
- [X] T033 [US1] Implement message generation with Rich spinner loading indicator
- [X] T034 [US1] Implement message display in Rich Panel with edit capability
- [X] T035 [US1] Implement user confirmation flow
- [X] T036 [US1] Implement git commit execution with final message

**Checkpoint**: At this point, User Story 1 (interactive commit generation) should be fully functional and testable independently

---

## Phase 4: User Story 2 - First-Time Configuration (Priority: P1)

**Goal**: Seamless first-run experience with interactive configuration wizard

**Independent Test**: Remove config file, run `sgc`, verify wizard launches and saves valid config

### Tests for User Story 2

- [ ] T037 [P] [US2] Create unit test for Config model validation in `tests/unit/test_config/test_models.py`
- [ ] T038 [US2] Create integration test for config wizard flow in `tests/integration/test_config_wizard.py`

### Implementation for User Story 2

- [ ] T039 [US2] Create `src/smart_git_commit/config/wizard.py` with interactive configuration prompts using Rich
- [ ] T040 [US2] Implement API connection validation in wizard (test before saving)
- [ ] T041 [US2] Implement default values for all config fields
- [ ] T042 [US2] Add `--config` command to CLI in `src/smart_git_commit/cli.py`
- [ ] T043 [US2] Implement auto-launch wizard when no config exists (in default command)
- [ ] T044 [US2] Add config file persistence (YAML serialization)

**Checkpoint**: At this point, User Story 2 (first-time config) should work independently - MVP complete!

---

## Phase 5: User Story 3 - Silent Mode for Quick Commits (Priority: P2)

**Goal**: Power users can skip review with `--silence` flag for faster workflow

**Independent Test**: Run `sgc --silence`, verify commit happens without prompts

### Tests for User Story 3

- [ ] T045 [US2] Create integration test for silent mode in `tests/integration/test_silent_mode.py`

### Implementation for User Story 3

- [ ] T046 [US3] Add `--silence` flag to CLI in `src/smart_git_commit/cli.py`
- [ ] T047 [US3] Implement silent mode logic (skip prompts, direct commit)
- [ ] T048 [US3] Add validation: require existing config for silence mode (error if not configured)
- [ ] T049 [US3] Add loading spinner for generation step in silence mode

**Checkpoint**: At this point, User Story 3 (silent mode) should work independently

---

## Phase 6: User Story 4 - Help and Documentation (Priority: P2)

**Goal**: Users can learn about the tool via `--help` and update config via `--config`

**Independent Test**: Run `sgc --help`, verify comprehensive usage displayed; run `sgc --config`, verify wizard opens

### Tests for User Story 4

- [ ] T050 [P] [US4] Create unit test for help text content in `tests/unit/test_cli/test_help.py`

### Implementation for User Story 4

- [ ] T051 [US4] Add `--help` implementation with comprehensive usage examples in `src/smart_git_commit/cli.py`
- [ ] T052 [US4] Add `--version` flag to display version
- [ ] T053 [US4] Enhance error messages with Rich panels and actionable suggestions
- [ ] T054 [US4] Add exit codes per CLI contract (0=success, 2=not repo, 3=no staged, 4=config error, 5=LLM error, 130=cancelled)
- [ ] T055 [US4] Update `README.md` with complete documentation matching quickstart.md

**Checkpoint**: At this point, User Story 4 (help/docs) should work - all user stories complete!

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T056 [P] Ensure test coverage >70% across all modules (run `pytest --cov`)
- [ ] T057 [P] Run mypy strict type checking on entire codebase
- [ ] T058 [P] Run ruff linting and formatting on entire codebase
- [ ] T059 Add error handling for large diffs (truncation logic)
- [ ] T060 Add error handling for LLM API failures with retry logic
- [ ] T061 Add error handling for network timeouts
- [ ] T062 Implement streaming LLM responses for better UX
- [ ] T063 [P] Create test fixtures: `tests/fixtures/mock_config.yaml`, `tests/fixtures/sample_diffs/`
- [ ] T064 Finalize `README.md` with badges, installation, usage, and examples
- [ ] T065 Create `LICENSE` file (MIT recommended for open source)
- [ ] T066 Create `CHANGELOG.md` with initial version notes
- [ ] T067 Run quickstart.md validation (follow each step manually)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories 1 & 2 (P1) should be completed first (MVP)
  - User stories 3 & 4 (P2) can follow
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Core functionality, requires Config, Git, Analyzer, LLM, Generator modules
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Requires Config module (shared with US1)
- **User Story 3 (P2)**: Can start after US1 is complete - Builds on default command with flag variant
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - CLI enhancements, can parallel with US3

### Within Each User Story

- Tests MUST be written first (if included), ensure they FAIL before implementation
- Models before services (Config models → Config manager)
- Services before CLI integration
- Core implementation before polish

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel
- Config models (T014) and Git repository (T017) can run in parallel
- Config manager (T015) and Git diff/history (T018, T019) can run in parallel
- Analyzer style and tokenizer (T021, T022) can run in parallel
- LLM provider and client (T024, T025) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Phase 2 tasks in parallel:
Task: "Create base exception classes in src/smart_git_commit/exceptions.py"
Task: "Create shared utilities in src/smart_git_commit/utils.py"
Task: "Create src/smart_git_commit/__init__.py with version constant"

# Phase 3 model creation in parallel:
Task: "Create LLMConfig Pydantic model in src/smart_git_commit/config/models.py"
Task: "Create RepositoryStatus enum in src/smart_git_commit/git/repository.py"
Task: "Create CommitStyle detection in src/smart_git_commit/analyzer/style.py"
Task: "Create LLMProvider Protocol in src/smart_git_commit/llm/provider.py"

# Phase 3 service implementation in sequence:
Task: "Create config manager in src/smart_git_commit/config/manager.py" (depends on T014)
Task: "Create git diff extraction in src/smart_git_commit/git/diff.py" (depends on T017)
Task: "Create OpenAI client in src/smart_git_commit/llm/client.py" (depends on T024)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Interactive commit generation)
4. Complete Phase 4: User Story 2 (First-time configuration)
5. **STOP and VALIDATE**: Test complete MVP flow (configure → generate → commit)
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test interactive commit flow → Deploy/Demo
3. Add User Story 2 → Test first-time config → Deploy/Demo (MVP!)
4. Add User Story 3 → Test silent mode → Deploy/Demo
5. Add User Story 4 → Test help/docs → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers after Foundational phase:

- **Developer A**: User Story 1 (core interactive flow) - PRIORITY
- **Developer B**: User Story 2 (config wizard) - PRIORITY
- Once P1 stories complete:
  - **Developer A**: User Story 3 (silent mode)
  - **Developer B**: User Story 4 (help/docs)
- **Developer C**: Polish phase (testing, docs, CI) in parallel

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution requirement: >70% test coverage (tracked in Phase 7)
- Constitution requirement: Python 3.11+ type hints throughout
- Constitution requirement: All public APIs have Google-style docstrings

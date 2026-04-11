"""Git repository operations for Smart Git Commit.

This module provides functions for detecting and validating git repositories,
as well as retrieving repository state information.
"""

from contextlib import suppress
from enum import Enum
from pathlib import Path

from git import InvalidGitRepositoryError, Repo

from smart_git_commit.exceptions import GitError
from smart_git_commit.utils import get_logger

logger = get_logger()


class RepositoryStatus(Enum):
    """Repository validation states.

    Attributes:
        VALID: Repository is valid and ready
        NOT_A_REPO: Current directory is not a git repository
        NO_COMMITS: Repository has no commits yet
        NO_STAGED_CHANGES: No changes staged for commit
    """

    VALID = "valid"
    NOT_A_REPO = "not_a_repo"
    NO_COMMITS = "no_commits"
    NO_STAGED_CHANGES = "no_staged_changes"


class GitRepository:
    """Wrapper for git repository operations.

    This class provides a clean interface for common git operations
    needed by the commit message generator.

    Attributes:
        repo: The underlying GitPython Repo instance
        path: Path to the repository root
    """

    def __init__(self, path: Path | None = None) -> None:
        """Initialize the repository wrapper.

        Args:
            path: Optional path to the repository. Defaults to current directory.

        Raises:
            GitError: If the path is not a valid git repository
        """
        self.path = path or Path.cwd()
        self._repo: Repo | None = None

    def _get_repo(self) -> Repo:
        """Get or create the Repo instance.

        Returns:
            The GitPython Repo instance

        Raises:
            GitError: If not a valid git repository
        """
        if self._repo is None:
            try:
                self._repo = Repo(self.path)
            except InvalidGitRepositoryError as e:
                raise GitError(
                    "Not a git repository",
                    exit_code=2,
                    suggestion="Run 'git init' to initialize a repository, or navigate to one",
                ) from e
        return self._repo

    def validate(self) -> RepositoryStatus:
        """Validate the repository state.

        Checks if the current directory is a valid git repository
        with staged changes.

        Returns:
            RepositoryStatus indicating the repository state
        """
        try:
            repo = self._get_repo()
        except GitError:
            return RepositoryStatus.NOT_A_REPO

        # Check for staged changes first (works even with no commits)
        if not self.has_staged_changes():
            return RepositoryStatus.NO_STAGED_CHANGES

        # Check if repo has any commits (needed for diff against HEAD)
        # Use suppress for new repos where HEAD doesn't exist yet
        with suppress(ValueError):
            _ = repo.head.commit

        return RepositoryStatus.VALID

    def is_valid(self) -> bool:
        """Check if repository is valid and ready.

        Returns:
            True if repository is valid with staged changes
        """
        return self.validate() == RepositoryStatus.VALID

    def has_staged_changes(self) -> bool:
        """Check if there are staged changes.

        Returns:
            True if there are files staged for commit
        """
        try:
            repo = self._get_repo()
            # For repos with commits: compare index with HEAD
            try:
                return len(repo.index.diff("HEAD")) > 0
            except ValueError:
                # No commits yet - check if index has entries (staged files)
                return len(repo.index) > 0
        except Exception:
            return False

    def get_staged_files(self) -> list[str]:
        """Get list of staged file paths.

        Returns:
            List of file paths that are staged for commit
        """
        repo = self._get_repo()
        try:
            return [item.a_path for item in repo.index.diff("HEAD")]
        except ValueError:
            # No commits yet - use diff(None) to get staged files
            return [item.a_path for item in repo.index.diff(None)]

    def get_current_branch(self) -> str:
        """Get the current branch name.

        Returns:
            Name of the current branch
        """
        repo = self._get_repo()
        return repo.active_branch.name

    def get_repo_root(self) -> Path:
        """Get the repository root path.

        Returns:
            Path to the repository root directory
        """
        repo = self._get_repo()
        return Path(repo.working_dir)

    def commit(self, message: str) -> None:
        """Create a commit with the given message.

        Args:
            message: The commit message

        Raises:
            GitError: If the commit fails
        """
        try:
            repo = self._get_repo()
            repo.index.commit(message)
            logger.debug(f"Created commit: {message.split(chr(10))[0]}")
        except Exception as e:
            raise GitError(
                f"Failed to create commit: {e}",
                suggestion="Check git status and try again",
            ) from e

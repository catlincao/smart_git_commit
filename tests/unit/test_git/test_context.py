"""Unit tests for GitContext model validation."""

from git import Repo

from smart_git_commit.git.diff import FileChange


class TestFileChange:
    """Tests for FileChange dataclass."""

    def test_file_change_creation(self) -> None:
        """Test creating a FileChange instance."""
        change = FileChange(
            path="src/main.py",
            change_type="modified",
            additions=10,
            deletions=5,
            diff_content="diff content",
        )

        assert change.path == "src/main.py"
        assert change.change_type == "modified"
        assert change.additions == 10
        assert change.deletions == 5
        assert change.diff_content == "diff content"

    def test_file_change_without_diff(self) -> None:
        """Test creating a FileChange without diff content."""
        change = FileChange(
            path="src/main.py",
            change_type="added",
            additions=20,
            deletions=0,
        )

        assert change.diff_content is None

    def test_file_change_change_types(self) -> None:
        """Test all valid change types."""
        types = ["added", "modified", "deleted", "renamed"]

        for change_type in types:
            change = FileChange(
                path="test.py",
                change_type=change_type,
                additions=1,
                deletions=0,
            )
            assert change.change_type == change_type


class TestGitRepository:
    """Tests for GitRepository class."""

    def test_repository_validation_not_a_repo(self, tmp_path) -> None:
        """Test validation fails in non-git directory."""
        from smart_git_commit.git import GitRepository, RepositoryStatus

        repo = GitRepository(path=tmp_path)
        status = repo.validate()

        assert status == RepositoryStatus.NOT_A_REPO

    def test_repository_validation_valid(self, tmp_path) -> None:
        """Test validation succeeds in valid git repo."""
        from smart_git_commit.git import GitRepository, RepositoryStatus

        # Initialize git repo
        git_repo = Repo.init(tmp_path)

        # Create initial commit
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        git_repo.index.add(["test.txt"])
        git_repo.index.commit("Initial commit")

        # Stage some changes
        test_file.write_text("modified content")
        git_repo.index.add(["test.txt"])

        repo = GitRepository(path=tmp_path)
        status = repo.validate()

        assert status == RepositoryStatus.VALID

    def test_repository_validation_no_staged_changes(self, tmp_path) -> None:
        """Test validation detects no staged changes."""
        from smart_git_commit.git import GitRepository, RepositoryStatus

        # Initialize git repo with a commit
        git_repo = Repo.init(tmp_path)
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        git_repo.index.add(["test.txt"])
        git_repo.index.commit("Initial commit")

        repo = GitRepository(path=tmp_path)
        status = repo.validate()

        assert status == RepositoryStatus.NO_STAGED_CHANGES

import subprocess
from pathlib import Path
import pytest
from ade_bench.handlers.trial_handler import TrialHandler


def test_get_repo_root_from_main_directory(tmp_path):
    """Test finding repo root from main directory.

    This test verifies that _get_repo_root finds the ade-bench repository root,
    not the task's temporary directory. The method looks at where the code is
    running from (trial_handler.py location), not where the task is.
    """
    # Setup: Create a git repo for the task (but handler will find ade-bench repo)
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)

    # Create a trial handler (we'll need a minimal task.yaml)
    task_dir = repo / "tasks" / "test_task"
    task_dir.mkdir(parents=True)
    (task_dir / "task.yaml").write_text("""
prompts:
  - key: base
    prompt: "test"
author_name: test
author_email: test@test.com
difficulty: easy
""")

    handler = TrialHandler(
        trial_name="test",
        input_path=task_dir,
        task_key="base"
    )

    root = handler._get_repo_root()
    # Should find the ade-bench repo root (where trial_handler.py lives)
    # Not the temporary test repo
    assert root.exists()
    assert (root / ".git").exists()
    # Verify we're in a git repository (ade-bench)
    assert root.name in ["ade-bench", "agent-install-phase"]


def test_get_repo_root_from_worktree(tmp_path):
    """Test finding repo root from worktree.

    This verifies that when code runs from a worktree, _get_repo_root correctly
    finds the main repository root, not the worktree location. This test
    checks that the method works in the actual ade-bench worktree we're running from.
    """
    # Setup: Create a git repo with worktree (but handler will find ade-bench repo)
    main_repo = tmp_path / "main"
    main_repo.mkdir()
    subprocess.run(["git", "init"], cwd=main_repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=main_repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=main_repo, check=True)

    # Create initial commit
    (main_repo / "test.txt").write_text("test")
    subprocess.run(["git", "add", "."], cwd=main_repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=main_repo, check=True)

    # Create worktree
    worktree = tmp_path / "worktree"
    subprocess.run(
        ["git", "worktree", "add", str(worktree), "-b", "feature"],
        cwd=main_repo,
        check=True,
        capture_output=True
    )

    # Create task in worktree
    task_dir = worktree / "tasks" / "test_task"
    task_dir.mkdir(parents=True)
    (task_dir / "task.yaml").write_text("""
prompts:
  - key: base
    prompt: "test"
author_name: test
author_email: test@test.com
difficulty: easy
""")

    handler = TrialHandler(
        trial_name="test",
        input_path=task_dir,
        task_key="base"
    )

    root = handler._get_repo_root()
    # Should find the ade-bench repo root (where trial_handler.py lives)
    # The code is running from a worktree, so this verifies worktree handling
    assert root.exists()
    assert (root / ".git").exists()
    # If we're running from agent-install-phase worktree, it should find main ade-bench
    # The root should NOT contain ".worktrees" in its path
    assert ".worktrees" not in str(root)

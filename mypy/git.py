"""Git utilities."""

# Used also from setup.py, so don't pull in anything additional here (like mypy or typing):
from __future__ import annotations

import os
import subprocess


def is_git_repo(dir: str) -> bool:
    """Is the given directory version-controlled with git?"""
    return os.path.exists(os.path.join(dir, ".git"))


def have_git() -> bool:
    """Can we run the git executable?"""
    try:
        subprocess.check_output(["git", "--help"])
        return True
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def git_revision(dir: str) -> bytes:
    """Get the SHA-1 of the HEAD of a git repository."""
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=dir).strip()


def is_dirty(dir: str) -> bool:
    """Check whether a git repository has uncommitted changes."""
    output = subprocess.check_output(["git", "status", "-uno", "--porcelain"], cwd=dir)
    return output.strip() != b""


def latest_version_tag(dir: str) -> bytes:
    """Get the name of the latest version tag."""
    result = subprocess.run(
        # List version tags in descending order using version-aware sorting.
        ["git", "tag", "--sort=-version:refname", "--list", "v*"],
        cwd=dir,
        capture_output=True,
        check=True,
    )
    return result.stdout.split(b"\n")[0]


def dev_distance(dir: str) -> int:
    """Return the number of commits since the last release branch was cut."""
    version_tag = latest_version_tag(dir).decode("utf-8")
    # Count the number of commits reachable from HEAD but not reachable from
    # the latest version tag. If for whatever reason no suitable release tag
    # was found, this will return 0.
    result = subprocess.run(
        ["git", "rev-list", "--count", f"{version_tag}..HEAD"],
        cwd=dir,
        capture_output=True,
        check=True,
    )
    return int(result.stdout)

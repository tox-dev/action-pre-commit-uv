"""Exercise the authorization checks before moving floating tags."""

# Ruff does not parse the required Sphinx :returns: fields.
# ruff: file-ignore[docstring-missing-returns]

import os
import shutil
import subprocess
from pathlib import Path
from typing import Final

import pytest
import yaml


def workflow_step(name: str, *, job: str = "update-floating-tags") -> str:
    """Read a release step from the workflow.

    :param name: Step name.
    :param job: Workflow job.
    :returns: Shell command for the step.
    """
    workflow = yaml.safe_load((Path(__file__).resolve().parent / ".github/workflows/release.yml").read_text())
    return next(step["run"] for step in workflow["jobs"][job]["steps"] if step.get("name") == name)


def git(directory: Path, *arguments: str) -> str:
    """Run Git in the disposable repository.

    :param directory: Repository path.
    :param arguments: Git arguments.
    :returns: Captured stdout.
    """
    executable: Final = shutil.which("git")
    assert executable is not None
    return subprocess.run(
        [executable, "-C", str(directory), *arguments], capture_output=True, check=True, text=True
    ).stdout.strip()


@pytest.fixture
def repository(tmp_path: Path) -> tuple[Path, str]:
    """Create a repository with a published source tag.

    :param tmp_path: Temporary directory.
    :returns: Checkout and tagged commit.
    """
    origin: Final = tmp_path / "origin.git"
    checkout: Final = tmp_path / "checkout"
    git(tmp_path, "init", "--bare", str(origin))
    git(tmp_path, "init", "-b", "main", str(checkout))
    git(checkout, "config", "user.name", "Release Test")
    git(checkout, "config", "user.email", "release@example.invalid")
    (checkout / "source.txt").write_text("published\n")
    git(checkout, "add", "source.txt")
    git(checkout, "commit", "-m", "Publish source")
    git(checkout, "remote", "add", "origin", str(origin))
    git(checkout, "push", "-u", "origin", "main")
    git(checkout, "tag", "v1.2.3")
    git(checkout, "push", "origin", "v1.2.3")
    return checkout, git(checkout, "rev-parse", "HEAD")


def run_step(
    step: str,
    checkout: Path,
    *,
    commit: str,
    tag: str = "v1.2.3",
    job: str = "update-floating-tags",
    **environment: str,
) -> subprocess.CompletedProcess[str]:
    """Execute a checked-in workflow step without GitHub access.

    :param step: Step name.
    :param checkout: Disposable repository.
    :param commit: Expected tagged commit.
    :param tag: Release tag.
    :param job: Workflow job.
    :param environment: Test boundary values.
    :returns: Captured process result.
    """
    return subprocess.run(
        ["/bin/bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", workflow_step(step, job=job)],
        cwd=checkout,
        env={**os.environ, "COMMIT": commit, "TAG": tag, **environment},
        capture_output=True,
        check=False,
        text=True,
    )


def test_released_tag_on_main_passes(repository: tuple[Path, str]) -> None:
    """A current tag on main may reach the publication check."""
    checkout, commit = repository
    result = run_step("Verify released tag on main", checkout, commit=commit)
    assert result.returncode == 0, result.stderr


def test_unmerged_tag_fails(repository: tuple[Path, str]) -> None:
    """A tag on an unmerged branch cannot reach the App key."""
    checkout, _ = repository
    git(checkout, "switch", "-c", "unmerged")
    (checkout / "source.txt").write_text("unmerged\n")
    git(checkout, "commit", "-am", "Unmerged source")
    git(checkout, "tag", "v1.2.4")
    git(checkout, "push", "origin", "v1.2.4")
    result = run_step("Verify released tag on main", checkout, commit=git(checkout, "rev-parse", "HEAD"), tag="v1.2.4")
    assert result.returncode != 0
    assert "not on main" in result.stderr


def test_unmerged_tag_cannot_publish_release(repository: tuple[Path, str], tmp_path: Path) -> None:
    """Initial verification rejects an unmerged source before publication."""
    checkout, _ = repository
    git(checkout, "switch", "-c", "unmerged")
    (checkout / "source.txt").write_text("unmerged\n")
    git(checkout, "commit", "-am", "Unmerged source")
    git(checkout, "tag", "v1.2.4")
    tools: Final = tmp_path / "bin"
    tools.mkdir()
    (tools / "release-creator").write_text("#!/bin/sh\nexit 0\n")
    (tools / "release-creator").chmod(0o755)
    result = run_step(
        "Verify exact version tag",
        checkout,
        commit=git(checkout, "rev-parse", "HEAD"),
        tag="v1.2.4",
        job="verify-tag",
        PATH=f"{tools}:{os.environ['PATH']}",
        GITHUB_OUTPUT=str(tmp_path / "output"),
    )
    assert result.returncode != 0
    assert "not on main" in result.stderr


def test_moved_tag_fails(repository: tuple[Path, str]) -> None:
    """The remote tag must still name the source commit."""
    checkout, commit = repository
    git(checkout, "switch", "-c", "moved")
    (checkout / "source.txt").write_text("moved\n")
    git(checkout, "commit", "-am", "Move tag")
    git(checkout, "tag", "-f", "v1.2.3")
    git(checkout, "push", "--force", "origin", "v1.2.3")
    result = run_step("Verify released tag on main", checkout, commit=commit)
    assert result.returncode != 0
    assert "moved after source verification" in result.stderr


def test_authorization_checks_precede_app_token() -> None:
    """The App token is minted only after both release checks."""
    workflow = yaml.safe_load((Path(__file__).resolve().parent / ".github/workflows/release.yml").read_text())
    steps = workflow["jobs"]["update-floating-tags"]["steps"]
    names = [step.get("name", step.get("id")) for step in steps]
    assert names.index("Verify released tag on main") < names.index("token")
    assert names.index("Verify published GitHub release") < names.index("token")


def test_failed_source_hooks_block_release(repository: tuple[Path, str], tmp_path: Path) -> None:
    """A failing hook stops the keyless tag verification job."""
    checkout, commit = repository
    tools: Final = tmp_path / "bin"
    tools.mkdir()
    (tools / "prek").write_text("#!/bin/sh\nexit 7\n")
    (tools / "prek").chmod(0o755)
    result = run_step(
        "Run cooled source hooks",
        checkout,
        commit=commit,
        job="verify-tag",
        PATH=f"{tools}:{os.environ['PATH']}",
    )
    assert result.returncode != 0


def test_publishers_need_tagged_source_check() -> None:
    """Both release writers wait for the keyless tag verification job."""
    workflow = yaml.safe_load((Path(__file__).resolve().parent / ".github/workflows/release.yml").read_text())
    jobs = workflow["jobs"]
    source_checks = [step.get("name", step.get("uses", "")) for step in jobs["verify-tag"]["steps"]]
    assert "Run cooled source hooks" in source_checks
    assert next(
        index for index, name in enumerate(source_checks) if "verify-frozen-hooks@" in name
    ) < source_checks.index("Run cooled source hooks")
    for publisher in ("github-release", "update-floating-tags"):
        needs = jobs[publisher]["needs"]
        assert "verify-tag" in ([needs] if isinstance(needs, str) else needs)


@pytest.mark.parametrize(
    ("draft", "prerelease", "accepted"),
    [("false", "false", True), ("true", "false", False), ("false", "true", False)],
    ids=["published", "draft", "prerelease"],
)
def test_published_release_required(
    repository: tuple[Path, str], tmp_path: Path, *, draft: str, prerelease: str, accepted: bool
) -> None:
    """The GitHub Release lookup gates the App key.

    :param repository: Disposable repository.
    :param tmp_path: Temporary directory.
    :param draft: GitHub Release draft state.
    :param prerelease: GitHub Release prerelease state.
    :param accepted: Whether the release should pass.
    """
    checkout, commit = repository
    tools: Final = tmp_path / "bin"
    tools.mkdir()
    (tools / "gh").write_text(
        '#!/bin/sh\nprintf \'{"tag_name":"v1.2.3","draft":%s,"prerelease":%s}\\n\' '
        '"$RELEASE_DRAFT" "$RELEASE_PRERELEASE" | jq -r "$4"\n'
    )
    (tools / "gh").chmod(0o755)
    result = run_step(
        "Verify published GitHub release",
        checkout,
        commit=commit,
        PATH=f"{tools}:{os.environ['PATH']}",
        RELEASE_DRAFT=draft,
        RELEASE_PRERELEASE=prerelease,
        REPO="tox-dev/action-pre-commit-uv",
    )
    assert (result.returncode == 0) == accepted
    if not accepted:
        assert "no published stable GitHub release" in result.stderr

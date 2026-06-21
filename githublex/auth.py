import os
import subprocess
import sys

from githublex.installer import gh_setup
from githublex.platform import resolve_gh


DEVICE_URL = "https://github.com/login/device"


def _run(args: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=True,
        text=True,
        **kwargs,
    )


def _git_config_value(key: str) -> str | None:
    result = subprocess.run(
        ["git", "config", "--global", key],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def _configure_git_identity(name: str | None, email: str | None) -> None:
    user_name = name or _git_config_value("user.name")
    user_email = email or _git_config_value("user.email")

    if not user_name:
        user_name = input("Git user.name: ").strip()
    if not user_email:
        user_email = input("Git user.email: ").strip()

    _run(["git", "config", "--global", "user.name", user_name])
    _run(["git", "config", "--global", "user.email", user_email])


def _is_logged_in(gh_path: str) -> bool:
    result = subprocess.run(
        [gh_path, "auth", "status"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _browser_login(gh_path: str) -> None:
    env = os.environ.copy()
    env["BROWSER"] = "false"
    command = [
        gh_path,
        "auth",
        "login",
        "--hostname",
        "github.com",
        "--git-protocol",
        "https",
        "--skip-ssh-key",
        "--web",
    ]
    print(f"Open {DEVICE_URL} and paste the one-time code from gh output.")
    kwargs: dict = {"env": env}
    if not sys.stdin.isatty():
        kwargs["input"] = "\n"
    _run(command, **kwargs)


def gh_login(name: str | None = None, email: str | None = None) -> None:
    """Configure git identity and authenticate gh via browser device flow."""
    gh_path = resolve_gh() or gh_setup()
    _configure_git_identity(name, email)

    if not _is_logged_in(gh_path):
        _browser_login(gh_path)

    _run([gh_path, "auth", "setup-git"])
    _run([gh_path, "config", "set", "-h", "github.com", "git_protocol", "https"])

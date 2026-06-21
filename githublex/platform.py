import os
import platform
import shutil
import sys
from pathlib import Path


def is_windows() -> bool:
    return sys.platform == "win32"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def local_bin_dir() -> Path:
    root = Path.home() / ".local" / "bin"
    root.mkdir(parents=True, exist_ok=True)
    return root


def gh_executable_name() -> str:
    return "gh.exe" if is_windows() else "gh"


def gh_binary_path() -> Path:
    return local_bin_dir() / gh_executable_name()


def detect_arch() -> str:
    machine = platform.machine().lower()
    mapping = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "aarch64": "arm64",
        "arm64": "arm64",
        "i386": "386",
        "i686": "386",
        "x86": "386",
    }
    if machine in mapping:
        return mapping[machine]
    if machine.startswith("arm"):
        return "armv6"
    return "amd64"


def platform_slug() -> str:
    if is_windows():
        return "windows"
    if is_linux():
        return "linux"
    raise RuntimeError(f"Unsupported platform: {sys.platform}")


def ensure_path() -> None:
    bin_dir = str(local_bin_dir())
    path_entries = os.environ.get("PATH", "").split(os.pathsep)
    if bin_dir not in path_entries:
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")


def resolve_gh() -> str | None:
    ensure_path()
    local = gh_binary_path()
    if local.is_file():
        return str(local)
    return shutil.which("gh")


def gh_is_installed() -> bool:
    return resolve_gh() is not None

import stat
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from tqdm.auto import tqdm

from githublex.platform import (
    detect_arch,
    ensure_path,
    gh_binary_path,
    gh_executable_name,
    gh_is_installed,
    is_windows,
    local_bin_dir,
    platform_slug,
    resolve_gh,
)
from githublex.release import fetch_latest_release, pick_asset_url


def _download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "githublex"})
    with urllib.request.urlopen(request, timeout=300) as response:
        total = int(response.headers.get("Content-Length", 0))
        block = 1024 * 256
        with destination.open("wb") as handle, tqdm(
            total=total or None,
            unit="B",
            unit_scale=True,
            desc="gh",
        ) as bar:
            while True:
                chunk = response.read(block)
                if not chunk:
                    break
                handle.write(chunk)
                bar.update(len(chunk))


def _extract_linux(archive: Path, version: str) -> Path:
    inner = f"gh_{version}_linux_{detect_arch()}/bin/gh"
    with tarfile.open(archive, "r:gz") as tar:
        member = tar.getmember(inner)
        extracted = tar.extractfile(member)
        target = gh_binary_path()
        target.write_bytes(extracted.read())
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return target


def _extract_windows(archive: Path, version: str) -> Path:
    inner = f"gh_{version}_windows_{detect_arch()}/bin/gh.exe"
    with zipfile.ZipFile(archive, "r") as zf:
        data = zf.read(inner)
        target = gh_binary_path()
        target.write_bytes(data)
        return target


def install_gh() -> str:
    if gh_is_installed():
        return resolve_gh()

    version, assets = fetch_latest_release()
    platform_name = platform_slug()
    arch = detect_arch()
    _, url = pick_asset_url(assets, platform_name, arch)

    with tempfile.TemporaryDirectory() as tmp:
        suffix = ".zip" if is_windows() else ".tar.gz"
        archive = Path(tmp) / f"gh{suffix}"
        _download(url, archive)
        if is_windows():
            _extract_windows(archive, version)
        else:
            _extract_linux(archive, version)

    ensure_path()
    gh_path = str(gh_binary_path())
    if not Path(gh_path).is_file():
        raise RuntimeError("gh binary was not installed")
    return gh_path


def gh_setup() -> str:
    """Install GitHub CLI locally when missing and expose it on PATH."""
    gh_path = install_gh()
    ensure_path()
    return gh_path

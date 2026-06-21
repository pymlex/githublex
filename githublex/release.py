import json
import re
import urllib.request


GH_RELEASES_URL = "https://api.github.com/repos/cli/cli/releases/latest"


def fetch_latest_release() -> tuple[str, list[dict]]:
    request = urllib.request.Request(
        GH_RELEASES_URL,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "githublex"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.loads(response.read().decode())
    tag = payload["tag_name"]
    version = tag.lstrip("v")
    return version, payload["assets"]


def pick_asset_url(
    assets: list[dict],
    platform_name: str,
    arch: str,
) -> tuple[str, str]:
    pattern = re.compile(
        rf"^gh_[\d.]+_{platform_name}_{arch}\.(tar\.gz|zip)$"
    )
    for asset in assets:
        name = asset["name"]
        if pattern.match(name):
            return name, asset["browser_download_url"]
    names = [asset["name"] for asset in assets]
    raise RuntimeError(
        f"No gh release asset for {platform_name}_{arch}. "
        f"Available: {', '.join(names)}"
    )

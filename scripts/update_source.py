#!/usr/bin/env python3
"""Update source.json from the newest matching Navic GitHub release."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


RELEASES_API = "https://api.github.com/repos/ssalggnikool/Navic/releases?per_page=100"
TAG_PATTERN = re.compile(
    r"^v(?P<version>\d+\.\d+\.\d+)-alpha(?P<build>\d+)$"
)
ASSET_NAME = "Navic.ipa"
BUNDLE_IDENTIFIER = "paige.Navic"
MIN_OS_VERSION = "14.1"
SOURCE_PATH = Path(__file__).resolve().parents[1] / "source.json"


def github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "navic-sidestore-source-updater",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_releases() -> list[dict[str, Any]]:
    request = Request(RELEASES_API, headers=github_headers())
    try:
        with urlopen(request, timeout=30) as response:
            data = json.load(response)
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API returned HTTP {error.code}: {detail}") from error
    except URLError as error:
        raise RuntimeError(f"Could not reach the GitHub API: {error.reason}") from error

    if not isinstance(data, list):
        raise RuntimeError("GitHub API returned an unexpected response")
    return data


def newest_matching_release(
    releases: list[dict[str, Any]],
) -> tuple[dict[str, Any], re.Match[str], dict[str, Any]]:
    candidates: list[tuple[str, dict[str, Any], re.Match[str], dict[str, Any]]] = []

    for release in releases:
        if release.get("draft"):
            continue

        match = TAG_PATTERN.fullmatch(str(release.get("tag_name", "")))
        if match is None:
            continue

        asset = next(
            (
                item
                for item in release.get("assets", [])
                if item.get("name") == ASSET_NAME
            ),
            None,
        )
        if asset is None:
            continue

        published = release.get("published_at") or release.get("created_at")
        if not published:
            continue
        candidates.append((published, release, match, asset))

    if not candidates:
        raise RuntimeError(
            f"No published release matching {TAG_PATTERN.pattern!r} with {ASSET_NAME} was found"
        )

    _, release, match, asset = max(candidates, key=lambda item: item[0])
    return release, match, asset


def load_source() -> dict[str, Any]:
    try:
        with SOURCE_PATH.open("r", encoding="utf-8") as file:
            source = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Could not read {SOURCE_PATH}: {error}") from error

    if not isinstance(source, dict):
        raise RuntimeError("source.json must contain a JSON object")
    return source


def navic_app(source: dict[str, Any]) -> dict[str, Any]:
    apps = source.get("apps")
    if not isinstance(apps, list):
        raise RuntimeError("source.json is missing its apps array")

    app = next(
        (
            item
            for item in apps
            if isinstance(item, dict)
            and item.get("bundleIdentifier") == BUNDLE_IDENTIFIER
        ),
        None,
    )
    if app is None:
        raise RuntimeError(f"No app with bundle identifier {BUNDLE_IDENTIFIER!r} was found")
    return app


def update_source() -> bool:
    release, match, asset = newest_matching_release(fetch_releases())
    source = load_source()
    app = navic_app(source)

    versions = app.get("versions")
    if not isinstance(versions, list):
        raise RuntimeError("Navic's versions value must be an array")

    version = match.group("version")
    build = str(int(match.group("build")))
    tag = str(release["tag_name"])

    already_present = any(
        isinstance(item, dict)
        and item.get("version") == version
        and str(item.get("buildVersion")) == build
        for item in versions
    )
    if already_present:
        print(f"No update: {tag} (build {build}) is already in source.json")
        return False

    download_url = asset.get("browser_download_url")
    size = asset.get("size")
    published_at = release.get("published_at") or release.get("created_at")
    if not isinstance(download_url, str) or not download_url.startswith(
        "https://github.com/ssalggnikool/Navic/releases/download/"
    ):
        raise RuntimeError("The IPA asset has an unexpected download URL")
    if not isinstance(size, int) or size <= 0:
        raise RuntimeError("The IPA asset has an invalid size")
    if not isinstance(published_at, str):
        raise RuntimeError("The release has no usable publication date")

    new_version = {
        "version": version,
        "buildVersion": build,
        "marketingVersion": tag.removeprefix("v"),
        "date": published_at,
        "downloadURL": download_url,
        "size": size,
        "minOSVersion": MIN_OS_VERSION,
    }
    versions.insert(0, new_version)

    try:
        SOURCE_PATH.write_text(
            json.dumps(source, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        raise RuntimeError(f"Could not write {SOURCE_PATH}: {error}") from error

    print(f"Updated source.json to {tag} (version {version}, build {build})")
    return True


def main() -> int:
    try:
        update_source()
    except RuntimeError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

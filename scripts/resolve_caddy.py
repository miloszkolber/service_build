"""Resolve Caddy and the Cloudflare DNS module for an image build."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

CADDY_REPOSITORY = "https://github.com/caddyserver/caddy"
MODULE_REPOSITORY = "https://github.com/caddy-dns/cloudflare"
MODULE_PATH = "github.com/caddy-dns/cloudflare"
STABLE = re.compile(r"v(\d+)\.(\d+)\.(\d+)$")
MODULE_VERSION = re.compile(r"v\d+\.\d+\.\d+$")
FULL_SHA = re.compile(r"[0-9a-f]{40}$")


def api(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "service_build"}
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    for attempt in range(3):
        try:
            with urlopen(Request("https://api.github.com/" + path, headers=headers), timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise
            time.sleep(2**attempt)


def stable_version(tag):
    match = STABLE.fullmatch(tag or "")
    return tuple(map(int, match.groups())) if match else None


def select_release(releases, override=""):
    releases = [release for release in releases if not release.get("draft")]
    if override:
        matches = [release for release in releases if release.get("tag_name") == override]
        if not matches:
            raise ValueError("Caddy release tag not found: " + override)
        if matches[0].get("prerelease") or stable_version(override) is None:
            raise ValueError("Caddy override must be a stable release tag")
        return override
    stable = [(stable_version(release.get("tag_name")), release["tag_name"])
              for release in releases
              if not release.get("prerelease") and stable_version(release.get("tag_name")) is not None]
    if not stable:
        raise ValueError("no stable Caddy release")
    return max(stable)[1]


def tag_commit(repository, tag):
    try:
        output = subprocess.check_output(
            ["git", "ls-remote", repository + ".git",
             f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}"],
            text=True, timeout=60,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        raise ValueError("cannot resolve release tag: " + tag) from error
    refs = dict(line.split()[::-1] for line in output.splitlines())
    sha = refs.get(f"refs/tags/{tag}^{{}}", refs.get(f"refs/tags/{tag}", ""))
    if not FULL_SHA.fullmatch(sha):
        raise ValueError("release tag did not resolve to a commit: " + tag)
    return sha


def parse_module_release(payload):
    version = payload.get("Version", "")
    if not MODULE_VERSION.fullmatch(version):
        raise ValueError("Cloudflare DNS module has no stable semver release")
    origin = payload.get("Origin") or {}
    sha = origin.get("Hash", "")
    if not FULL_SHA.fullmatch(sha):
        raise ValueError("Cloudflare DNS module release has no source commit")
    return version, sha


def module_release():
    try:
        with urlopen(f"https://proxy.golang.org/{MODULE_PATH}/@latest", timeout=30) as response:
            return parse_module_release(json.load(response))
    except HTTPError as error:
        raise ValueError("cannot resolve Cloudflare DNS module") from error


def emit(values):
    for key, value in values.items():
        print(f"{key}={value}")
    if os.getenv("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            for key, value in values.items():
                output.write(f"{key}={value}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caddy-version", default="")
    parser.add_argument("--output", default=".build/caddy-inputs.json")
    args = parser.parse_args()
    if args.caddy_version and stable_version(args.caddy_version) is None:
        parser.error("--caddy-version must be a stable release tag such as v2.11.9")
    releases = api("repos/caddyserver/caddy/releases?per_page=100")
    version = select_release(releases, args.caddy_version)
    commit = tag_commit(CADDY_REPOSITORY, version)
    module, module_commit = module_release()
    inputs = {
        "caddy": {
            "version": version,
            "commit": commit,
            "repository": CADDY_REPOSITORY,
        },
        "cloudflare_dns": {
            "module": MODULE_PATH,
            "version": module,
            "commit": module_commit,
            "repository": MODULE_REPOSITORY,
        },
    }
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(inputs, indent=2) + "\n")
    print(json.dumps(inputs, indent=2))
    emit({
        "caddy_version": version,
        "caddy_commit": commit,
        "module_version": module,
        "module_commit": module_commit,
    })


if __name__ == "__main__":
    main()

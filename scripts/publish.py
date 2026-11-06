"""Reuse or publish the checked Caddy image."""
import argparse
import json
import os
import re
import subprocess
import sys

LABEL = "io.service-build.inputs"
PLATFORM = "linux/amd64"
IMAGE = "caddy"
LOCAL_IMAGE = "caddy:local"


def command(*args):
    try:
        return subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=1800).stdout.strip()
    except subprocess.CalledProcessError as error:
        print(error.stderr, file=sys.stderr)
        raise


def image_name(owner=None):
    owner = (owner or os.environ.get("GITHUB_REPOSITORY_OWNER", "")).lower()
    if not re.fullmatch(r"[a-z0-9-]+", owner):
        raise ValueError("invalid registry owner")
    return f"ghcr.io/{owner}/{IMAGE}"


def validate_version(tag):
    if not re.fullmatch(r"v\d+\.\d+\.\d+", tag or ""):
        raise ValueError("version tag must be a stable Caddy release tag")


def inspect(reference):
    try:
        result = command("docker", "buildx", "imagetools", "inspect", "--format",
                         '{"manifest":{{json .Manifest}},"image":{{json .Image}}}', reference)
    except subprocess.CalledProcessError as error:
        if re.search(r"manifest unknown|not found|no such manifest", error.stderr or "", re.I):
            return None
        raise
    result = json.loads(result)
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", result.get("manifest", {}).get("digest", "")):
        raise ValueError("registry returned an invalid digest")
    return result


def platform_image(result):
    image = result.get("image", {})
    if PLATFORM in image:
        image = image[PLATFORM]
    if not image.get("config"):
        raise ValueError("image has no linux/amd64 configuration")
    if image.get("os") not in (None, "linux") or image.get("architecture") not in (None, "amd64"):
        raise ValueError("image has no linux/amd64 configuration")
    return image


def label(result, name=LABEL):
    return (platform_image(result).get("config", {}).get("Labels") or {}).get(name, "")


def check(fingerprint):
    reference = image_name()
    result = inspect(reference + ":latest")
    unchanged = result is not None and label(result) == fingerprint
    if unchanged:
        digest = result["manifest"]["digest"]
        command("docker", "pull", f"{reference}@{digest}")
        command("docker", "tag", f"{reference}@{digest}", LOCAL_IMAGE)
    print(f"unchanged={str(unchanged).lower()}")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            output.write(f"unchanged={str(unchanged).lower()}\n")
    return unchanged


def publish(tag, fingerprint, local):
    validate_version(tag)
    reference = image_name()
    labels = json.loads(command("docker", "image", "inspect", local, "--format", "{{json .Config.Labels}}"))
    if (labels or {}).get(LABEL) != fingerprint:
        raise ValueError("local image fingerprint does not match the resolved inputs")
    for target in (tag, "latest"):
        command("docker", "tag", local, f"{reference}:{target}")
        command("docker", "push", f"{reference}:{target}")
    version = inspect(f"{reference}:{tag}")
    latest = inspect(f"{reference}:latest")
    if version is None or latest is None:
        raise ValueError("published tags are missing")
    if version["manifest"]["digest"] != latest["manifest"]["digest"]:
        raise ValueError("latest does not match the version tag")
    if label(version) != fingerprint:
        raise ValueError("published fingerprint does not match")
    print(f"{reference}:{tag} @ {version['manifest']['digest']}")
    return version["manifest"]["digest"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "publish"))
    parser.add_argument("--fingerprint", required=True)
    parser.add_argument("--tag", default="")
    parser.add_argument("--local", default=LOCAL_IMAGE)
    args = parser.parse_args()
    if args.action == "check":
        check(args.fingerprint)
    else:
        if not args.tag:
            parser.error("publish requires --tag")
        publish(args.tag, args.fingerprint, args.local)


if __name__ == "__main__":
    main()

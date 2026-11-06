"""Stable fingerprint over Caddy image build inputs.

The fingerprint covers the resolved upstream versions and commits, the
linux/amd64 base-image digests, and the repository files that can change the
image or how the pipeline builds and checks it. Documentation, tests and the
deployment example are deliberately absent: editing them must not republish an
unchanged image.
"""
import argparse
import hashlib
import json
from pathlib import Path

LABEL = "io.service-build.inputs"
ROOT = Path(__file__).resolve().parents[1]
BUILD_INPUTS = (
    "caddy/Dockerfile",
    "caddy/healthcheck",
    "caddy/LICENSE",
    "caddy/NOTICE",
    "caddy/smoke.Caddyfile",
    "caddy/validate.Caddyfile",
    "scripts/resolve_caddy.py",
    "scripts/fingerprint.py",
    "scripts/publish.py",
    ".github/workflows/caddy.yml",
)
DOCUMENTATION_SUFFIXES = (".md",)


def build_input_files(root=ROOT, entries=BUILD_INPUTS):
    files = []
    for entry in entries:
        path = Path(root) / entry
        if path.is_dir():
            files.extend(sorted(item for item in path.rglob("*") if item.is_file()))
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError("missing build input: " + entry)
    return [item for item in files
            if not item.name.endswith(DOCUMENTATION_SUFFIXES)
            and not item.name.startswith("README")]


def repo_digest(root=ROOT, entries=BUILD_INPUTS):
    digest = hashlib.sha256()
    for path in build_input_files(root, entries):
        relative = Path(path).relative_to(Path(root)).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(Path(path).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def canonical_fingerprint(inputs, bases, repo):
    canonical = json.dumps(
        {"bases": bases, "inputs": inputs, "repo": repo},
        sort_keys=True, separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", default=".build/caddy-inputs.json")
    parser.add_argument("--bases", default=".build/bases.json")
    parser.add_argument("--output", default=".build/fingerprint.txt")
    args = parser.parse_args()
    inputs = json.loads(Path(args.inputs).read_text())
    bases = json.loads(Path(args.bases).read_text())
    value = canonical_fingerprint(inputs, bases, repo_digest())
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value + "\n")
    print(value)


if __name__ == "__main__":
    main()

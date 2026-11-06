import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("fingerprint", ROOT / "scripts/fingerprint.py")
fingerprint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fingerprint)


class FingerprintTests(unittest.TestCase):
    def test_stable_and_input_sensitive(self):
        inputs = {"caddy": {"version": "v2.11.9", "commit": "a" * 40}}
        bases = {"builder": "caddy:2.11.9-builder@sha256:" + "b" * 64}
        first = fingerprint.canonical_fingerprint(inputs, bases, "c" * 64)
        self.assertRegex(first, r"^[0-9a-f]{64}$")
        self.assertEqual(first, fingerprint.canonical_fingerprint(inputs, bases, "c" * 64))
        changed = dict(bases, runtime="gcr.io/distroless/static-debian12:nonroot@sha256:" + "d" * 64)
        self.assertNotEqual(first, fingerprint.canonical_fingerprint(inputs, changed, "c" * 64))

    def test_repository_digest_changes_with_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "inputs").mkdir()
            (root / "inputs/file.txt").write_text("one")
            first = fingerprint.repo_digest(root, ("inputs",))
            (root / "inputs/file.txt").write_text("two")
            second = fingerprint.repo_digest(root, ("inputs",))
            self.assertNotEqual(first, second)

    def test_missing_build_input_is_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                fingerprint.build_input_files(Path(directory), ("absent",))

    def test_dockerfile_context_copies_are_covered(self):
        dockerfile = (ROOT / "caddy/Dockerfile").read_text()
        for line in dockerfile.splitlines():
            if not line.startswith("COPY "):
                continue
            parts = [part for part in line.split()[1:] if not part.startswith("--from=")]
            source = parts[0]
            if source.startswith("/"):
                continue
            covered = any(
                source == entry or source.startswith(entry.rstrip("/") + "/")
                for entry in fingerprint.BUILD_INPUTS
            )
            self.assertTrue(covered, "COPY source not covered: " + source)


if __name__ == "__main__":
    unittest.main()

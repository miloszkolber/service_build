import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("resolve_caddy", ROOT / "scripts/resolve_caddy.py")
resolve = importlib.util.module_from_spec(spec)
spec.loader.exec_module(resolve)


def release(tag, prerelease=False, draft=False):
    return {"tag_name": tag, "prerelease": prerelease, "draft": draft}


class SelectReleaseTests(unittest.TestCase):
    def test_highest_stable_semver(self):
        releases = [
            release("v2.9.10"),
            release("v2.10.2"),
            release("v2.11.0-beta.1", prerelease=True),
            release("v2.12.0", draft=True),
        ]
        self.assertEqual(resolve.select_release(releases), "v2.10.2")

    def test_override_must_exist_and_be_stable(self):
        releases = [release("v2.10.2"), release("v2.11.0-beta.1", prerelease=True)]
        self.assertEqual(resolve.select_release(releases, "v2.10.2"), "v2.10.2")
        with self.assertRaises(ValueError):
            resolve.select_release(releases, "v2.11.0-beta.1")
        with self.assertRaises(ValueError):
            resolve.select_release(releases, "v9.9.9")

    def test_no_stable_release(self):
        with self.assertRaises(ValueError):
            resolve.select_release([release("v2.11.0-beta.1", prerelease=True)])

    def test_stable_version_rejects_partial_tags(self):
        self.assertEqual(resolve.stable_version("v2.10.2"), (2, 10, 2))
        self.assertIsNone(resolve.stable_version("v2.10"))
        self.assertIsNone(resolve.stable_version("nightly"))


class ModuleReleaseTests(unittest.TestCase):
    def test_valid_module_payload(self):
        payload = {
            "Version": "v0.2.4",
            "Origin": {"Hash": "a" * 40},
        }
        self.assertEqual(resolve.parse_module_release(payload), ("v0.2.4", "a" * 40))

    def test_module_requires_stable_version_and_commit(self):
        with self.assertRaises(ValueError):
            resolve.parse_module_release({"Version": "v0.0.0-20260101000000-deadbeef"})
        with self.assertRaises(ValueError):
            resolve.parse_module_release({"Version": "v0.2.4"})
        with self.assertRaises(ValueError):
            resolve.parse_module_release({"Version": "v0.2.4", "Origin": {"Hash": "short"}})


if __name__ == "__main__":
    unittest.main()

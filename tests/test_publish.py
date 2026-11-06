import importlib.util
import os
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location("publish", ROOT / "scripts/publish.py")
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)


class ImageNameTests(unittest.TestCase):
    def test_lowercases_owner(self):
        with patch.dict(os.environ, {"GITHUB_REPOSITORY_OWNER": "MiloszKolber"}):
            self.assertEqual(publish.image_name(), "ghcr.io/miloszkolber/caddy")

    def test_rejects_invalid_owner(self):
        with patch.dict(os.environ, {"GITHUB_REPOSITORY_OWNER": "../bad"}):
            with self.assertRaises(ValueError):
                publish.image_name()


class PublicationTests(unittest.TestCase):
    def test_version_tag_must_be_a_stable_release(self):
        publish.validate_version("v2.11.9")
        for value in ("2.11.9", "latest", "v2.11.9-beta.1"):
            with self.assertRaises(ValueError):
                publish.validate_version(value)

    def test_platform_configuration_and_label(self):
        document = {
            "image": {
                "linux/amd64": {
                    "config": {"Labels": {publish.LABEL: "abc"}},
                },
            },
        }
        self.assertEqual(publish.platform_image(document)["config"]["Labels"][publish.LABEL], "abc")
        self.assertEqual(publish.label(document), "abc")

    def test_single_platform_configuration_is_accepted(self):
        document = {
            "image": {
                "os": "linux",
                "architecture": "amd64",
                "config": {"Labels": {publish.LABEL: "abc"}},
            },
        }
        self.assertEqual(publish.platform_image(document)["config"]["Labels"][publish.LABEL], "abc")

    def test_non_amd64_configuration_is_rejected(self):
        document = {"image": {"os": "linux", "architecture": "arm64", "config": {"Labels": {}}}}
        with self.assertRaises(ValueError):
            publish.platform_image(document)


if __name__ == "__main__":
    unittest.main()

"""Regression checks for packages served to both plugin hosts."""

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.validate_plugins import ValidationError, validate_repository


ROOT = Path(__file__).resolve().parents[1]


class PluginValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("plugins", ".agents", ".claude-plugin"):
            shutil.copytree(ROOT / name, self.root / name, symlinks=True)
        for name in ("CLAUDE.md", "AGENTS.md"):
            shutil.copyfile(ROOT / name, self.root / name)

    def change_json(self, relative, update):
        path = self.root / relative
        value = json.loads(path.read_text())
        update(value)
        path.write_text(json.dumps(value))

    def test_repository_packages_are_consistent(self):
        self.assertEqual(validate_repository(self.root), (4, 13))

    def test_catalog_cannot_silently_omit_plugin(self):
        self.change_json(".agents/plugins/marketplace.json", lambda data: data["plugins"].pop())
        with self.assertRaisesRegex(ValidationError, "inventory differs"):
            validate_repository(self.root)

    def test_duplicate_catalog_entry_is_rejected(self):
        self.change_json(".agents/plugins/marketplace.json",
                         lambda data: data["plugins"].append(data["plugins"][0]))
        with self.assertRaisesRegex(ValidationError, "duplicate plugin entry"):
            validate_repository(self.root)

    def test_versions_cannot_drift_between_hosts(self):
        self.change_json("plugins/github/plugin.json", lambda data: data.update(version="9.0.0"))
        with self.assertRaisesRegex(ValidationError, "disagree on version"):
            validate_repository(self.root)

    def test_manual_skill_cannot_become_implicitly_invocable(self):
        (self.root / "plugins/github/skills/pr-review/agents/openai.yaml").unlink()
        with self.assertRaisesRegex(ValidationError, "manual invocation policy"):
            validate_repository(self.root)

    def test_shared_template_must_ship_inside_package(self):
        (self.root / "plugins/android/skills/templates/review-base.md").unlink()
        with self.assertRaisesRegex(ValidationError, "broken local link"):
            validate_repository(self.root)

    def test_catalog_path_cannot_escape_checkout(self):
        self.change_json(".agents/plugins/marketplace.json",
                         lambda data: data["plugins"][0]["source"].update(path="./../outside"))
        with self.assertRaisesRegex(ValidationError, "escapes marketplace root"):
            validate_repository(self.root)

    def test_instruction_link_cannot_escape_installed_plugin(self):
        skill = self.root / "plugins/meta/skills/session-review/SKILL.md"
        with skill.open("a") as stream:
            stream.write("\n[shared](../../../../AGENTS.md)\n")
        with self.assertRaisesRegex(ValidationError, "link leaves plugin package"):
            validate_repository(self.root)

    def test_claude_import_cannot_drift_from_shared_instructions(self):
        (self.root / "CLAUDE.md").write_text("Separate instructions\n")
        with self.assertRaisesRegex(ValidationError, "must import shared AGENTS.md"):
            validate_repository(self.root)


if __name__ == "__main__":
    unittest.main()

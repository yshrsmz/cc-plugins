"""Read-only host integration checks; no model calls or user config writes."""

import json
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]


class NativeHostTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("claude"), "Claude Code CLI is not installed")
    def test_claude_accepts_marketplace_and_plugin_manifests(self):
        manifests = [ROOT / ".claude-plugin/marketplace.json"]
        manifests.extend(sorted((ROOT / "plugins").glob("*/.claude-plugin/plugin.json")))
        for path in manifests:
            with self.subTest(path=path.relative_to(ROOT)):
                result = subprocess.run(
                    ["claude", "plugin", "validate", str(path), "--json"],
                    capture_output=True, text=True, timeout=30, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(json.loads(result.stdout)["success"])

    @unittest.skipUnless(shutil.which("codex"), "Codex CLI is not installed")
    def test_codex_discovers_catalog_without_registration(self):
        with tempfile.TemporaryDirectory(prefix="cc-plugins-catalog-test-") as directory:
            root = Path(directory).resolve()
            shutil.copytree(ROOT / "plugins", root / "plugins", symlinks=True)
            shutil.copytree(ROOT / ".agents", root / ".agents")
            # Avoid colliding with an older installed version of the user's real marketplace.
            name = f"cc-plugins-test-{uuid.uuid4().hex}"
            path = root / ".agents/plugins/marketplace.json"
            catalog = json.loads(path.read_text())
            catalog["name"] = name
            path.write_text(json.dumps(catalog))
            result = subprocess.run(
                ["codex", "-c", f'marketplaces.{name}.source_type="local"',
                 "-c", f"marketplaces.{name}.source={json.dumps(str(root))}",
                 "plugin", "list", "--marketplace", name, "--available", "--json"],
                capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(result.stdout)
            plugins = data["installed"] + data["available"]
            self.assertEqual({plugin["name"] for plugin in plugins},
                             {"android", "github", "meta", "writing"})
            for plugin in plugins:
                manifest = json.loads((root / "plugins" / plugin["name"] / "plugin.json").read_text())
                self.assertEqual(plugin["version"], manifest["version"])

    @unittest.skipUnless(shutil.which("codex"), "Codex CLI is not installed")
    def test_codex_parses_all_skills_from_self_contained_packages(self):
        # Copy only distribution files, so references cannot rely on the source checkout.
        with tempfile.TemporaryDirectory(prefix="cc-plugins-host-test-") as directory:
            root = Path(directory).resolve()
            shutil.copytree(ROOT / "plugins", root / "plugins", symlinks=True)
            shutil.copytree(ROOT / ".agents", root / ".agents")
            with tempfile.TemporaryFile(mode="w+") as log:
                process = subprocess.Popen(
                    ["codex", "app-server"], cwd=root,
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=log, text=True,
                )
                messages = queue.Queue()

                def collect_messages():
                    for line in process.stdout:
                        try:
                            messages.put(json.loads(line))
                        except ValueError as error:
                            messages.put({"readerError": str(error)})

                reader = threading.Thread(target=collect_messages, daemon=True)
                reader.start()

                def request(identifier, method, params):
                    process.stdin.write(json.dumps({
                        "jsonrpc": "2.0", "id": identifier, "method": method, "params": params,
                    }) + "\n")
                    process.stdin.flush()
                    while True:
                        message = messages.get(timeout=30)
                        self.assertNotIn("readerError", message)
                        if message.get("id") == identifier:
                            self.assertNotIn("error", message, str(message))
                            return message["result"]

                try:
                    request(1, "initialize", {
                        "clientInfo": {"name": "cc-plugins-tests", "version": "1.0.0"},
                        "capabilities": {"experimentalApi": True},
                    })
                    process.stdin.write('{"jsonrpc":"2.0","method":"initialized"}\n')
                    process.stdin.flush()
                    total = 0
                    for identifier, name in enumerate(("android", "github", "meta", "writing"), 2):
                        with self.subTest(plugin=name):
                            detail = request(identifier, "plugin/read", {
                                "marketplacePath": str(root / ".agents/plugins/marketplace.json"),
                                "pluginName": name,
                            })["plugin"]
                            plugin = root / "plugins" / name
                            manifest = json.loads((plugin / "plugin.json").read_text())
                            expected = {f"{name}:{path.parent.name}"
                                        for path in (plugin / "skills").glob("*/SKILL.md")}
                            self.assertEqual({skill["name"] for skill in detail["skills"]}, expected)
                            self.assertEqual(detail["summary"]["interface"]["shortDescription"],
                                             manifest["extensions"]["com.openai"]["interface"]["shortDescription"])
                            for skill in detail["skills"]:
                                self.assertTrue(skill["description"].strip())
                                self.assertTrue(Path(skill["path"]).is_relative_to(root))
                                self.assertTrue(Path(skill["path"]).is_file())
                            total += len(expected)
                    self.assertEqual(total, 13)
                finally:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                    reader.join(timeout=5)
                    process.stdin.close()
                    process.stdout.close()


if __name__ == "__main__":
    unittest.main()

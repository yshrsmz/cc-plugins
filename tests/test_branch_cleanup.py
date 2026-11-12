"""Regression tests for the branch-cleanup script, using a local remote and a fake gh."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/github/skills/branch-cleanup/scripts/prune-merged-branches.sh"

# `gh pr list --head <branch> --state <state>` を PR_FIXTURE（{state: {branch: [sha]}}）から答える。
# auth status と repo view は成功させる。
FAKE_GH = """#!/usr/bin/env bash
set -euo pipefail
case "$1 ${2:-}" in
  "auth status") exit 0 ;;
  "repo view")
    if [[ " $* " == *" defaultBranchRef "* ]]; then echo main; else echo '{}'; fi
    exit 0 ;;
  "pr list")
    shift 2
    head="" state=""
    while [ "$#" -gt 0 ]; do
      case "$1" in
        --head) head="$2"; shift ;;
        --state) state="$2"; shift ;;
      esac
      shift
    done
    python3 - "$state" "$head" <<'PY'
import json, os, sys
state, head = sys.argv[1], sys.argv[2]
oids = json.loads(os.environ["PR_FIXTURE"]).get(state, {}).get(head, [])
print(len(oids) if state == "open" else "\\n".join(oids))
PY
    ;;
  *) echo "unexpected gh call: $*" >&2; exit 1 ;;
esac
"""


def git(cwd, *args):
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True,
    ).stdout.strip()


class BranchCleanupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="branch-cleanup-test-")
        base = Path(self.tmp.name).resolve()
        self.remote = base / "remote.git"
        self.repo = base / "repo"
        self.bin = base / "bin"
        self.bin.mkdir()
        (self.bin / "gh").write_text(FAKE_GH)
        os.chmod(self.bin / "gh", 0o755)

        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.remote)], check=True)
        subprocess.run(["git", "clone", "-q", str(self.remote), str(self.repo)], check=True, capture_output=True)
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "test")
        git(self.repo, "config", "commit.gpgsign", "false")
        self.commit("init")
        git(self.repo, "push", "-q", "-u", "origin", "main")
        git(self.repo, "remote", "set-head", "origin", "main")

    def tearDown(self):
        self.tmp.cleanup()

    def commit(self, message, cwd=None):
        git(cwd or self.repo, "commit", "-q", "--allow-empty", "-m", message)
        return git(cwd or self.repo, "rev-parse", "HEAD")

    def branch(self, name, *, commits=0, push=False, worktree=False):
        git(self.repo, "branch", name, "main")
        path = None
        cwd = self.repo
        if worktree:
            path = Path(self.tmp.name) / f"wt-{name}"
            git(self.repo, "worktree", "add", "-q", str(path), name)
            cwd = path
        else:
            git(self.repo, "switch", "-q", name)
        for i in range(commits):
            self.commit(f"{name} {i}", cwd)
        if push:
            git(cwd, "push", "-q", "origin", name)
        if not worktree:
            git(self.repo, "switch", "-q", "main")
        return path

    def run_script(self, fixture, *args):
        env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", PR_FIXTURE=json.dumps(fixture))
        result = subprocess.run(
            ["bash", str(SCRIPT), *args], cwd=self.repo, env=env,
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def branches(self):
        return set(git(self.repo, "for-each-ref", "--format=%(refname:short)", "refs/heads/").split())

    def test_deletes_merged_and_lossless_branches_and_keeps_the_rest(self):
        self.branch("merged", commits=1)
        merged_oid = git(self.repo, "rev-parse", "merged")
        pushed_wt = self.branch("pushed-clean-wt", commits=1, push=True, worktree=True)
        self.branch("fresh", worktree=False)
        self.branch("open-pr", commits=1, push=True)
        self.branch("unpushed", commits=2)
        dirty_wt = self.branch("pushed-dirty-wt", commits=1, push=True, worktree=True)
        (dirty_wt / "note.txt").write_text("work in progress\n")

        out = self.run_script({
            "merged": {"merged": [merged_oid]},
            "open": {"open-pr": ["x"]},
        })

        self.assertEqual(self.branches(), {"main", "open-pr", "unpushed", "pushed-dirty-wt"}, out)
        self.assertFalse(pushed_wt.exists(), out)
        self.assertTrue(dirty_wt.exists(), out)
        kept = out.split("=== 残した", 1)[1]
        self.assertIn("open-pr — open な PR がある", kept)
        self.assertIn("unpushed — マージ済み PR が見つからない（リモートに無いコミット 2 件）", kept)
        self.assertIn("pushed-dirty-wt — マージ済み PR が見つからない（リモートに無いコミット 0 件 / 未コミットの変更 1 件）", kept)
        # 失うものが少ない順に並ぶ
        lines = [line for line in kept.splitlines() if " — " in line]
        self.assertLess(
            next(i for i, l in enumerate(lines) if "pushed-dirty-wt" in l),
            next(i for i, l in enumerate(lines) if "unpushed" in l),
        )

    def test_dry_run_deletes_nothing(self):
        self.branch("pushed", commits=1, push=True)

        out = self.run_script({}, "--dry-run")

        self.assertIn("pushed (", out.split("=== 残した", 1)[0])
        self.assertIn("pushed", self.branches())


if __name__ == "__main__":
    unittest.main()

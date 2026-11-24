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
# merged はスクリプトの --jq と同じく「番号 head SHA」を出す。要素が {"number": N, "sha": S} なら
# その番号、SHA の文字列なら番号は 1 にする。
# `gh api repos/{owner}/{repo}/commits/<sha>/pulls` は PR_FIXTURE["pulls"]（{sha: [PR]}）から答え、
# スクリプトの --jq と同じく「マージ済みで head.sha が一致する PR の番号」を出す。
# 登録の無い SHA は実際の API と同じく、エラー本文（422）を stdout に出して失敗する。
# PR_FIXTURE["api_fail"] に入れた SHA は 422 以外で失敗させる。
# リポジトリのホストは PR_FIXTURE["host"]（既定は github.com）。`gh repo view --json url` の --jq の
# 結果としてそのホストを返し、`gh api` は --hostname がそれと違えば実際の gh と同じく 404 で失敗する。
# `gh api repos/{owner}/{repo}/compare/<base>...<head>` は PR_FIXTURE["compare"]（{"base...head": {status, behind_by}}）
# から答え、スクリプトの --jq と同じく yes / no を出す。登録の無い組は実際の API と同じく 404 で失敗する。
# PR_FIXTURE["compare_fail"] に入れた組は 500 で失敗させる。
# `gh api repos/{owner}/{repo}/commits/<sha>` は PR_FIXTURE["known"] か pulls に入った SHA なら SHA を出し、
# それ以外は 422 で失敗する。
# auth status と repo view は成功させる。
FAKE_GH = """#!/usr/bin/env bash
set -euo pipefail
case "$1 ${2:-}" in
  "auth status") exit 0 ;;
  "repo view")
    if [[ " $* " == *" defaultBranchRef "* ]]; then echo main
    elif [[ " $* " == *" url "* ]]; then python3 -c 'import json, os; print(json.loads(os.environ["PR_FIXTURE"]).get("host", "github.com"))'
    else echo '{}'; fi
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
if state == "open":
    print(len(oids))
else:
    for oid in oids:
        number, sha = (oid["number"], oid["sha"]) if isinstance(oid, dict) else (1, oid)
        print(number, sha)
PY
    ;;
  "api repos/{owner}/{repo}/"*)
    python3 - "$@" <<'PY'
import json, os, re, sys
args = sys.argv[1:]
fixture = json.loads(os.environ["PR_FIXTURE"])
hostname = args[args.index("--hostname") + 1] if "--hostname" in args else "github.com"
if hostname != fixture.get("host", "github.com"):
    print('{"message":"Not Found","status":"404"}')
    sys.exit(1)
compare = re.fullmatch(r"repos/\\{owner\\}/\\{repo\\}/compare/([0-9a-f]+\\.\\.\\.[0-9a-f]+)", args[1])
if compare:
    key = compare.group(1)
    if key in fixture.get("compare_fail", []):
        print('{"message":"Server Error","status":"500"}')
        sys.exit(1)
    if key not in fixture.get("compare", {}):
        print('{"message":"Not Found","status":"404"}')
        sys.exit(1)
    c = fixture["compare"][key]
    print("yes" if c["behind_by"] == 0 and c["status"] in ("ahead", "identical") else "no")
    sys.exit(0)
commit = re.fullmatch(r"repos/\\{owner\\}/\\{repo\\}/commits/([0-9a-f]+)", args[1])
if commit:
    oid = commit.group(1)
    if oid in fixture.get("known", []) or oid in fixture.get("pulls", {}):
        print(oid)
        sys.exit(0)
    print('{"message":"No commit found for SHA: %s","status":"422"}' % oid)
    sys.exit(1)
oid = re.match(r"repos/\\{owner\\}/\\{repo\\}/commits/([0-9a-f]+)/pulls", args[1]).group(1)
if oid in fixture.get("api_fail", []):
    print('{"message":"Server Error","status":"500"}')
    sys.exit(1)
pulls = fixture.get("pulls", {})
if oid not in pulls:
    print('{"message":"No commit found for SHA: %s","status":"422"}' % oid)
    sys.exit(1)
for pr in pulls[oid]:
    if pr.get("merged_at") is not None and pr["head"]["sha"] == oid:
        print(pr["number"])
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

    def test_deletes_branch_pushed_under_another_name_by_head_sha(self):
        # `git push origin alias:pr-branch` で push し、PR がマージされてリモートの
        # ブランチが消えた状態。ブランチ名では PR が引けず、リモートにもコミットが無い。
        self.branch("alias", commits=1)
        alias_oid = git(self.repo, "rev-parse", "alias")
        dirty_wt = self.branch("alias-dirty-wt", commits=1, worktree=True)
        dirty_oid = git(dirty_wt, "rev-parse", "HEAD")
        (dirty_wt / "note.txt").write_text("work in progress\n")
        self.branch("moved", commits=2)
        moved_oid = git(self.repo, "rev-parse", "moved")
        moved_pr_head = git(self.repo, "rev-parse", "moved~1")
        merged_pr = lambda head, number: {"number": number, "merged_at": "2026-01-01T00:00:00Z", "head": {"sha": head}}

        out = self.run_script({"pulls": {
            alias_oid: [merged_pr(alias_oid, 12)],
            dirty_oid: [merged_pr(dirty_oid, 13)],
            # API は「関連する PR」を返す。head が先端と違う PR は一致として扱わない。
            moved_oid: [merged_pr(moved_pr_head, 14)],
        }})

        self.assertEqual(self.branches(), {"main", "alias-dirty-wt", "moved"}, out)
        deleted, kept = out.split("=== 残した", 1)
        self.assertIn(f"alias ({alias_oid[:7]})（PR #12 の head と一致。PR のブランチ名はローカルと異なる）", deleted)
        self.assertIn("alias-dirty-wt — worktree に変更が残っている", kept)
        self.assertIn("moved — マージ済み PR が見つからない（リモートに無いコミット 2 件）", kept)

    def test_looks_up_head_sha_on_the_remote_host(self):
        # GitHub Enterprise のリポジトリ。`gh api` にホストを渡さないと github.com に
        # 問い合わせて 404 になり、照会失敗として残る。
        self.branch("alias", commits=1)
        alias_oid = git(self.repo, "rev-parse", "alias")
        merged_pr = {"number": 12, "merged_at": "2026-01-01T00:00:00Z", "head": {"sha": alias_oid}}

        out = self.run_script({"host": "tenant.ghe.com", "pulls": {alias_oid: [merged_pr]}})

        self.assertEqual(self.branches(), {"main"}, out)
        self.assertIn(f"alias ({alias_oid[:7]})（PR #12 の head と一致。", out.split("=== 残した", 1)[0])

    def test_keeps_branch_when_head_sha_lookup_fails(self):
        self.branch("unknown", commits=1)
        oid = git(self.repo, "rev-parse", "unknown")

        out = self.run_script({"api_fail": [oid]})

        self.assertIn("unknown", self.branches())
        self.assertIn("unknown — gh の照会に失敗した（マージ済みか判定できていない）", out.split("=== 残した", 1)[1])

    def test_deletes_branch_whose_tip_is_an_ancestor_of_the_merged_pr_head(self):
        # push して PR を作ったあと、PR ブランチに別の場所でレビュー修正が積まれ、
        # pull しないまま squash merge されてリモートのブランチが消えた状態。
        # ローカルの先端はリモートに無いコミットを持つように見えるが、PR head の祖先。
        self.branch("reviewed", commits=2)
        reviewed_head = git(self.repo, "rev-parse", "reviewed")
        git(self.repo, "branch", "-f", "reviewed", "reviewed~1")
        reviewed_oid = git(self.repo, "rev-parse", "reviewed")
        # PR head がローカルに無い場合。GitHub の compare で見る。
        self.branch("remote-reviewed", commits=1)
        remote_oid = git(self.repo, "rev-parse", "remote-reviewed")
        remote_head = "e" * 40

        out = self.run_script({
            "host": "tenant.ghe.com",
            "merged": {
                "reviewed": [{"number": 21, "sha": reviewed_head}],
                "remote-reviewed": [{"number": 1262, "sha": remote_head}],
            },
            "compare": {f"{remote_oid}...{remote_head}": {"status": "ahead", "behind_by": 0}},
        })

        self.assertEqual(self.branches(), {"main"}, out)
        deleted = out.split("=== 残した", 1)[0]
        self.assertIn(f"reviewed ({reviewed_oid[:7]})（PR #21 の head の祖先。PR 側に後からコミットが積まれてマージ済み）", deleted)
        self.assertIn(f"remote-reviewed ({remote_oid[:7]})（PR #1262 の head の祖先。", deleted)

    def test_keeps_branch_that_is_not_an_ancestor_of_the_merged_pr_head(self):
        # PR のマージ後に手元で先端を動かした。PR head がローカルにある場合と、
        # GitHub の compare で diverged と出る場合と、GitHub がローカルの先端を知らない場合。
        self.branch("moved-local", commits=2)
        moved_head = git(self.repo, "rev-parse", "moved-local~1")
        self.branch("diverged", commits=1)
        diverged_oid = git(self.repo, "rev-parse", "diverged")
        self.branch("unknown-to-github", commits=1)
        pr_head = "e" * 40

        out = self.run_script({
            "merged": {
                "moved-local": [{"number": 31, "sha": moved_head}],
                "diverged": [{"number": 32, "sha": pr_head}],
                "unknown-to-github": [{"number": 33, "sha": pr_head}],
            },
            "compare": {f"{diverged_oid}...{pr_head}": {"status": "diverged", "behind_by": 1}},
        })

        self.assertEqual(self.branches(), {"main", "moved-local", "diverged", "unknown-to-github"}, out)
        kept = out.split("=== 残した", 1)[1]
        for name in ("moved-local", "diverged", "unknown-to-github"):
            self.assertIn(f"{name} — マージ済み PR はあるが先端 SHA が一致しない（PR head の祖先でもない。", kept)

    def test_keeps_branch_when_ancestor_lookup_fails(self):
        self.branch("flaky", commits=1)
        oid = git(self.repo, "rev-parse", "flaky")
        pr_head = "e" * 40

        out = self.run_script({
            "merged": {"flaky": [{"number": 41, "sha": pr_head}]},
            "compare_fail": [f"{oid}...{pr_head}"],
        })

        self.assertIn("flaky", self.branches())
        self.assertIn("flaky — gh の照会に失敗した（マージ済みか判定できていない）", out.split("=== 残した", 1)[1])


if __name__ == "__main__":
    unittest.main()

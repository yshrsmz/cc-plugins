# マージ済みのローカルブランチを削除する。
#
# 実行: bash prune-merged-branches.sh [--dry-run]
# （chmod はしない。bash に渡して実行する）
#
# なぜスクリプトが要るか:
#   squash merge されたブランチは `git branch -d` が「マージされていない」と言って拒否し、
#   `git branch --merged` にも出ない。`git diff main <branch>` も、main が先に進んでいれば
#   差分を出すので判定に使えない。マージされたかどうかを知っているのは GitHub 側だけ。
#   このスクリプトはマージ済み PR の head SHA とローカルの先端 SHA を照合して判定する。
#
# 既定で削除まで行う。消すのは「マージ済み PR の head SHA と一致するブランチ」だけで、
# 一致しないもの・PR が見つからないものは必ず残して理由を報告する。何が消えるかを
# 先に見たいときは --dry-run。
#
# 必要なもの: git, gh（認証済み）。GitHub のリモートを持つリポジトリで実行する。

set -uo pipefail

dry_run=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) dry_run=1 ;;
    -h|--help)
      sed -n '1,18p' "$0"
      exit 0
      ;;
    *)
      echo "不明な引数: $arg（使えるのは --dry-run のみ）" >&2
      exit 2
      ;;
  esac
done

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "git リポジトリの中で実行してください。" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "gh が認証されていません。gh auth login を実行してください。" >&2
  exit 1
fi

# 消えたリモート追跡ブランチを先に片付ける。ここで落ちるならリモートに繋がっていない。
if ! git fetch origin --prune; then
  echo "git fetch に失敗しました。" >&2
  exit 1
fi

# 既定ブランチ。origin/HEAD が無いリポジトリもあるので gh に聞き直す。
default_branch="$(git symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')"
if [ -z "$default_branch" ]; then
  default_branch="$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name 2>/dev/null)"
fi
if [ -z "$default_branch" ]; then
  echo "既定ブランチを特定できませんでした。" >&2
  exit 1
fi

# detached HEAD では空になる。空文字と比較しないよう番兵を置く。
current_branch="$(git branch --show-current)"
if [ -z "$current_branch" ]; then
  current_branch=$'\n(detached)'
fi

deleted=""
kept=""

# ブランチ名に空白は入らないので、そのまま単語分割してよい。while read だと
# ループの中の git / gh がループ自身の stdin を食う。
for branch in $(git for-each-ref --format='%(refname:short)' refs/heads/); do
  if [ "$branch" = "$default_branch" ] || [ "$branch" = "$current_branch" ]; then
    continue
  fi

  local_oid="$(git rev-parse "$branch")"

  # そのブランチを head とするマージ済み PR をすべて挙げ、ローカルの先端がその中に
  # あるかを見る。ブランチ名は使い回されることがあるので、最新の 1 件だけ見ない。
  merged_oids="$(gh pr list --head "$branch" --state merged --limit 50 \
    --json headRefOid --jq '.[].headRefOid' 2>/dev/null)"

  if [ -z "$merged_oids" ]; then
    kept="${kept}  $branch — マージ済み PR が見つからない"$'\n'
    continue
  fi

  if ! printf '%s\n' "$merged_oids" | grep -qx "$local_oid"; then
    kept="${kept}  $branch — マージ済み PR はあるが先端 SHA が一致しない（${local_oid:0:7}）"$'\n'
    continue
  fi

  if [ "$dry_run" -eq 1 ]; then
    deleted="${deleted}  $branch (${local_oid:0:7})"$'\n'
    continue
  fi

  # 別の worktree でチェックアウトされていると失敗する。止めずに報告に回す。
  if git branch -D "$branch" >/dev/null 2>&1; then
    deleted="${deleted}  $branch (${local_oid:0:7})"$'\n'
  else
    kept="${kept}  $branch — 削除できなかった（別の worktree で使われている可能性）"$'\n'
  fi
done

if [ "$dry_run" -eq 1 ]; then
  echo "=== 削除対象（--dry-run なので消していない） ==="
else
  echo "=== 削除した ==="
fi
if [ -n "$deleted" ]; then printf '%s' "$deleted"; else echo "  (なし)"; fi

echo "=== 残した ==="
if [ -n "$kept" ]; then printf '%s' "$kept"; else echo "  (なし)"; fi

#!/usr/bin/env bash
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
# 必要なもの: git, gh（認証済み）。リモート名は origin を前提にする。

set -uo pipefail

usage() {
  cat <<'USAGE'
マージ済みのローカルブランチを削除する。

  bash prune-merged-branches.sh [--dry-run]

消すのは「マージ済み PR の head SHA と先端が一致するブランチ」だけ。一致しないもの・
PR が見つからないものは必ず残して理由を報告する。既定ブランチと現在のブランチ、
リモートのブランチには触らない。

  --dry-run   何も消さずに、消える対象の一覧だけ出す

必要なもの: git, gh（認証済み）。リモート名は origin を前提にする。
USAGE
}

dry_run=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) dry_run=1 ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "不明な引数: $1（使えるのは --dry-run のみ）" >&2
      exit 2
      ;;
  esac
  shift
done

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "git リポジトリの中で実行してください。" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "gh が認証されていません。gh auth login を実行してください。" >&2
  exit 1
fi

# GitHub のリポジトリとして解決できるか。ここを確かめないと、GitLab や自前ホストの
# origin でも fetch は通ってしまい、全ブランチが「PR が見つからない」と報告される。
if ! gh repo view --json nameWithOwner >/dev/null 2>&1; then
  echo "GitHub のリポジトリとして解決できません（origin が GitHub か確認してください）。" >&2
  exit 1
fi

# 消えたリモート追跡ブランチを片付ける。判定自体はローカルの ref と gh だけで足りるので、
# ここが失敗しても止めない（一時的にネットワークが無いだけで判定はできる）。
if ! git fetch origin --prune; then
  echo "警告: git fetch origin --prune に失敗しました。判定は続けます。" >&2
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
#
# `%(refname:short)` ではなく完全な ref を取る。short は「曖昧でないところまで」しか
# 縮めないので、同名のタグがあるブランチは `heads/foo` という中途半端な名前で出てくる。
for ref in $(git for-each-ref --format='%(refname)' refs/heads/); do
  branch="${ref#refs/heads/}"

  if [ "$branch" = "$default_branch" ] || [ "$branch" = "$current_branch" ]; then
    continue
  fi

  # 完全な ref で引く。ブランチ名だけで引くと、同名のタグがあるときにそちらが
  # 優先され（`git rev-parse` は tag を先に解決する）、実在しない不一致を報告する。
  local_oid="$(git rev-parse "$ref")"

  # そのブランチを head とするマージ済み PR をすべて挙げ、ローカルの先端がその中に
  # あるかを見る。ブランチ名は使い回されることがあるので、最新の 1 件だけ見ない。
  #
  # ブランチ 1 本につき 1 回 API を叩く。`--limit 200` の 1 回にまとめると速いが、
  # 上限を超えた古い PR が黙って落ちて「PR が無い」と誤判定する。正しさを取る。
  if ! merged_oids="$(gh pr list --head "$branch" --state merged --limit 50 \
        --json headRefOid --jq '.[].headRefOid' 2>/dev/null)"; then
    # 空の結果と失敗を混同しない。混同すると、認証切れやリポジトリ解決の失敗が
    # 「PR が見つからない（= push していない作業ブランチ）」と報告される。
    kept="${kept}  $branch — gh の照会に失敗した（マージ済みか判定できていない）"$'\n'
    continue
  fi

  if [ -z "$merged_oids" ]; then
    kept="${kept}  $branch — マージ済み PR が見つからない"$'\n'
    continue
  fi

  if ! printf '%s\n' "$merged_oids" | grep -qx "$local_oid"; then
    # PR の head SHA も出す。上位がブランチの中身を見るとき、この SHA を起点にしないと
    # squash merge では「ブランチの全履歴が未マージ」に見える。
    pr_oid="$(printf '%s\n' "$merged_oids" | head -1)"
    kept="${kept}  $branch — マージ済み PR はあるが先端 SHA が一致しない（ローカル ${local_oid:0:7} / PR head ${pr_oid:0:7}）"$'\n'
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
  echo "=== 削除した（git branch <name> <sha> で戻せる） ==="
fi
if [ -n "$deleted" ]; then printf '%s' "$deleted"; else echo "  (なし)"; fi

echo "=== 残した ==="
if [ -n "$kept" ]; then printf '%s' "$kept"; else echo "  (なし)"; fi

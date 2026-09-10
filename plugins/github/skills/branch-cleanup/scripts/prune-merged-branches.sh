#!/usr/bin/env bash
# マージ済みのローカルブランチと、それをチェックアウトしている worktree を削除する。
#
# 実行: bash prune-merged-branches.sh [--dry-run] [--keep-worktrees]
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
# worktree について:
#   ブランチが worktree にチェックアウトされていると `git branch -D` は必ず失敗する。
#   既定ではその worktree を先に `git worktree remove`（--force は付けない）してから
#   ブランチを消す。worktree を残したいときは --keep-worktrees。
#
#   `git worktree remove` は tracked の変更・untracked ファイルがあれば拒否するが、
#   **gitignore されたファイルは拒否せず消す**（node_modules/ だけでなく .env も）。
#   復元できないので、消える ignore 済みエントリは報告に出す。
#
# 必要なもの: git, gh（認証済み）。リモート名は origin を前提にする。

set -uo pipefail

usage() {
  cat <<'USAGE'
マージ済みのローカルブランチと、それをチェックアウトしている worktree を削除する。

  bash prune-merged-branches.sh [--dry-run] [--keep-worktrees]

消すのは「マージ済み PR の head SHA と先端が一致するブランチ」だけ。一致しないもの・
PR が見つからないものは必ず残して理由を報告する。既定ブランチと現在のブランチ、
現在いる worktree、メインの worktree、リモートのブランチには触らない。

  --dry-run          何も消さずに、消える対象の一覧だけ出す
  --keep-worktrees   worktree を消さない。worktree にチェックアウトされている
                     ブランチは（マージ済みでも）削除できないので残す

必要なもの: git, gh（認証済み）。リモート名は origin を前提にする。
USAGE
}

dry_run=0
keep_worktrees=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run) dry_run=1 ;;
    --keep-worktrees) keep_worktrees=1 ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "不明な引数: $1（使えるのは --dry-run と --keep-worktrees のみ）" >&2
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

# ディレクトリごと手で消された worktree の管理情報を片付ける。これが残っていると
# ブランチが「使用中」のままになり `git branch -D` が通らない。ディレクトリが実在する
# worktree には触らないので、ここでユーザーの作業が消えることはない。
if [ "$keep_worktrees" -eq 0 ] && [ "$dry_run" -eq 0 ]; then
  git worktree prune
fi

# ブランチ名 → worktree のパス。`git worktree list --porcelain` は 1 worktree ごとに
# `worktree <path>` / `HEAD <sha>` / `branch <ref>` を出す（detached には branch 行が無い）。
# パスに空白が入りうるのでタブ区切りにする。
worktree_index="$(git worktree list --porcelain | awk '
  /^worktree /  { path = substr($0, 10) }
  /^branch /    { print substr($0, 8) "\t" path }
')"

# 一覧の先頭がメインの worktree。`git worktree remove` はここを消せないので、
# 判定を待たずに除外して理由を分けて報告する。
main_worktree="$(git worktree list --porcelain | awk '/^worktree /{ print substr($0, 10); exit }')"

# 自分がいる worktree。1 つのブランチは 1 つの worktree にしか出せないので、ここは
# current_branch として先に除外されるはずで、下の判定は通常あたらない。それでも見るのは
# `git worktree remove` が「自分がいる worktree」を平然と消すため（拒否せず、cwd ごと
# 消えて以降の git がすべて失敗する）。取りこぼしたときの被害が大きいので歯止めを残す。
current_worktree="$(git rev-parse --show-toplevel 2>/dev/null)"

# ref に対応する worktree のパスを返す（無ければ空）。
worktree_path_for() {
  printf '%s\n' "$worktree_index" | awk -F'\t' -v ref="$1" '$1 == ref { print $2; exit }'
}

# worktree を消したときに一緒に消える gitignore 済みエントリ。`--directory` が
# 丸ごと ignore されたディレクトリを 1 行に畳むので `node_modules/ .env` のように短くなる。
#
# 長い一覧は畳むが、件数は必ず出す。「これで全部」と読めるところで黙って打ち切ると、
# 報告の目的（何が復旧できなくなるかを見せる）が崩れる。
ignored_entries_in() {
  local all shown count limit=8
  all="$( cd "$1" 2>/dev/null && git ls-files --others --ignored --exclude-standard --directory )"
  if [ -z "$all" ]; then
    return 0
  fi

  count="$(printf '%s\n' "$all" | wc -l | tr -d ' ')"
  shown="$(printf '%s\n' "$all" | head -"$limit" | tr '\n' ' ' | sed 's/ $//')"

  if [ "$count" -gt "$limit" ]; then
    printf '%s ほか %d 件' "$shown" "$((count - limit))"
  else
    printf '%s' "$shown"
  fi
}

# `git worktree remove` が拒否する状態か。判定条件は remove と同じ「tracked の変更または
# untracked ファイル」で、`git status --porcelain` は ignore 済みを出さないので一致する。
# --dry-run がこれを見ないと、実行時に必ず残るものを削除対象として予告してしまう。
worktree_is_dirty() {
  [ -n "$( cd "$1" 2>/dev/null && git status --porcelain )" ]
}

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

  # ここから先はマージ済みが確定している。worktree にチェックアウトされていれば、
  # それを先に外さない限り `git branch -D` は必ず失敗する。
  wt_path="$(worktree_path_for "$ref")"
  wt_note=""

  if [ -n "$wt_path" ]; then
    if [ "$wt_path" = "$main_worktree" ]; then
      kept="${kept}  $branch — メインの worktree でチェックアウト中（${wt_path}）"$'\n'
      continue
    fi

    if [ "$wt_path" = "$current_worktree" ]; then
      kept="${kept}  $branch — いま自分がいる worktree（${wt_path}）"$'\n'
      continue
    fi

    if [ "$keep_worktrees" -eq 1 ]; then
      kept="${kept}  $branch — worktree でチェックアウト中（$wt_path / --keep-worktrees 指定）"$'\n'
      continue
    fi

    # 実行時に git が拒否する状態なら、--dry-run でも削除対象として予告しない。
    if worktree_is_dirty "$wt_path"; then
      kept="${kept}  $branch — worktree に変更が残っている（${wt_path}）"$'\n'
      continue
    fi

    # 消えてしまう ignore 済みエントリは、消す前に控える。remove 後には読めない。
    ignored="$(ignored_entries_in "$wt_path")"
    wt_note=" + worktree $wt_path"
    if [ -n "$ignored" ]; then
      wt_note="${wt_note}（ignore 済みも消える: ${ignored}）"
    fi

    if [ "$dry_run" -eq 0 ]; then
      # --force は付けない。上の事前判定を潜り抜けた状態（判定と remove の間に
      # ファイルが増えた等）でも、git が拒否してブランチを道連れにせず止まる。
      if ! wt_error="$(git worktree remove "$wt_path" 2>&1)"; then
        kept="${kept}  $branch — worktree を消せなかった（${wt_path}）: $wt_error"$'\n'
        continue
      fi
    fi
  fi

  if [ "$dry_run" -eq 1 ]; then
    deleted="${deleted}  $branch (${local_oid:0:7})${wt_note}"$'\n'
    continue
  fi

  if git branch -D "$branch" >/dev/null 2>&1; then
    deleted="${deleted}  $branch (${local_oid:0:7})${wt_note}"$'\n'
  else
    kept="${kept}  $branch — 削除できなかった（別の worktree で使われている可能性）"$'\n'
  fi
done

if [ "$dry_run" -eq 1 ]; then
  echo "=== 削除対象（--dry-run なので消していない） ==="
else
  # ブランチは SHA から戻せるが、worktree のディレクトリは戻せない。同じ場所へ
  # `git worktree add <path> <branch>` で作り直しても、ignore されていたファイルは復元されない。
  echo "=== 削除した（ブランチは git branch <name> <sha> で戻せる。worktree は戻せない） ==="
fi
if [ -n "$deleted" ]; then printf '%s' "$deleted"; else echo "  (なし)"; fi

echo "=== 残した ==="
if [ -n "$kept" ]; then printf '%s' "$kept"; else echo "  (なし)"; fi

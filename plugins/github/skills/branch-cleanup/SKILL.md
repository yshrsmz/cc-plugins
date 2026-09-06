---
name: branch-cleanup
description: >-
  マージ済みの PR に対応するローカルブランチを、head SHA を照合して安全に削除する。squash merge されたブランチは `git branch -d` も `git branch --merged` も判定できないため、GitHub 側の情報で確認する。「ブランチを整理して」「マージ済みブランチを消して」「clean up branches」「prune branches」と言われたとき、および「マージしたのに `git branch -d` が拒否する」「マージ済みのブランチが消せない」と相談されたときに使う。リモートブランチの削除や、未マージのブランチを消す作業には使わない。
---

# Branch Cleanup

マージ済みのローカルブランチを削除する。

## なぜスクリプトを使うのか

squash merge されたブランチは、git だけでは「マージ済み」と判定できない。

- `git branch -d` は「マージされていない」と言って拒否する
- `git branch --merged` にも出てこない
- `git diff <default> <branch>` も、既定ブランチが先に進んでいれば差分を出す

マージされたかどうかを知っているのは GitHub 側だけなので、**マージ済み PR の head SHA と
ローカルブランチの先端 SHA を照合する**。この照合を毎回手で組み直さないための
スクリプトが同梱してある。

## 手順

1. **スクリプトを実行する**

   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/branch-cleanup/scripts/prune-merged-branches.sh"
   ```

   `${CLAUDE_PLUGIN_ROOT}` が空になる場合（プラグインではなく `.claude/skills/` に
   直接置かれているとき）は、この SKILL.md と同じディレクトリの
   `scripts/prune-merged-branches.sh` を絶対パスに直して実行する。

   `chmod +x` はしない。`bash` に渡して実行する。

   **`--dry-run` を使い分ける。** 「消して」「整理して」と依頼されたらそのまま実行する。
   「どれが消える?」「先に確認したい」のように観察として聞かれているときは `--dry-run` で
   一覧だけ出す。**他の作業のついでに勝手に走らせない。** 片付けを頼まれたときだけ動く。

2. **結果をそのまま報告する**

   「削除した」と「残した」の 2 つが出る。削除したブランチは SHA 付きで出るので、
   間違って消したときは `git branch <name> <sha>` で戻せることを一言添える。

3. **残ったブランチは、そこで止まる**

   理由を説明するだけにして、**ユーザーが明示的に消せと言うまで削除しない**。
   スクリプトが残す理由は 3 つあり、対処がそれぞれ違う。

   - `マージ済み PR が見つからない` — push していない作業ブランチか、PR を作る前の
     ブランチ。中身は `git log <default-branch>..<branch>` で見せる
   - `マージ済み PR はあるが先端 SHA が一致しない` — PR がマージされたあとに先端が
     動いている（コミット追加・rebase・amend）。**中身は `git log <PR head SHA>..<branch>`
     で見せる。** `<default-branch>..` を起点にしてはいけない。squash merge では
     ブランチのコミットが 1 つも既定ブランチの祖先にならないので、全履歴が未マージに
     見えてしまう。SHA はスクリプトの出力に入っている
   - `削除できなかった（別の worktree で使われている可能性）` — 中身の問題ではない。
     `git worktree list` で使っている worktree を示すだけにする
   - `gh の照会に失敗した` — 判定できていないだけ。認証・ネットワーク・リポジトリ解決を
     確かめて、直してからやり直す

   はじめの 2 つは、消すと復旧できない変更が失われうる。中身を見せて確認を取る。

## 特定の 1 本だけを消せと言われたとき

**スクリプトを走らせない。** スクリプトは全ブランチを対象にするので、頼まれていない
ブランチまで消すことになる。同じ照合を手で行う。

```bash
gh pr list --head <branch> --state merged --limit 50 --json headRefOid --jq '.[].headRefOid'
git rev-parse "refs/heads/<branch>"
```

一致したら `git branch -D <branch>`。一致しなければ上の「残った理由」と同じ扱いにして、
中身を見せてから判断を仰ぐ。

## スクリプトが消さないもの

- 既定ブランチ（`origin/HEAD`、取れなければ `gh repo view` で解決）
- 現在チェックアウトしているブランチ
- 上の「残した」に入るブランチ

削除するのは「マージ済み PR の head SHA と先端が一致するブランチ」だけ。
リモートのブランチ自体は消さない（GitHub 側の delete-branch-on-merge に任せる）。
ただし最初に `git fetch origin --prune` を走らせるので、消えたリモートの追跡参照は片付く。

## 前提

- `gh` が認証済みであること
- リモート名が `origin` であること（`fetch --prune` と既定ブランチの解決に使う）

スクリプトが 0 以外で終了したら、そのメッセージをそのまま伝えて止まる。
**`git branch --merged` や `git branch -d` で自前の代替を組まない。** squash merge を
判定できないことが出発点なので、代替はどれも「消すべきブランチが 1 本も無い」という
間違った答えを返す。

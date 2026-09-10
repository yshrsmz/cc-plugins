---
name: branch-cleanup
description: >-
  マージ済みの PR に対応するローカルブランチと、それをチェックアウトしている worktree を、head SHA を照合して安全に削除する。squash merge されたブランチは `git branch -d` も `git branch --merged` も判定できないため、GitHub 側の情報で確認する。「ブランチを整理して」「マージ済みブランチを消して」「マージ済みの worktree を片付けて」「clean up branches」「prune branches」と言われたとき、および「マージしたのに `git branch -d` が拒否する」「マージ済みのブランチが消せない」「worktree があるせいでブランチが消せない」と相談されたときに使う。リモートブランチの削除、未マージのブランチや未マージ PR の worktree を消す作業には使わない。
---

# Branch Cleanup

マージ済みのローカルブランチと、それをチェックアウトしている worktree を削除する。

## なぜスクリプトを使うのか

squash merge されたブランチは、git だけでは「マージ済み」と判定できない。

- `git branch -d` は「マージされていない」と言って拒否する
- `git branch --merged` にも出てこない
- `git diff <default> <branch>` も、既定ブランチが先に進んでいれば差分を出す

マージされたかどうかを知っているのは GitHub 側だけなので、**マージ済み PR の head SHA と
ローカルブランチの先端 SHA を照合する**。この照合を毎回手で組み直さないための
スクリプトが同梱してある。

## worktree も消す

ブランチが worktree にチェックアウトされていると `git branch -D` は必ず失敗する。
worktree を使う運用（PR ごとに 1 つ生やす等）では、マージ済みブランチのほとんどが
これで残ってしまい、片付けにならない。**既定でその worktree を先に外してからブランチを消す。**

残したいときは `--keep-worktrees`。worktree は残り、そこにチェックアウトされている
ブランチは（マージ済みでも）消せないので「残した」に理由付きで出る。

### gitignore されたファイルは黙って消える

`git worktree remove` は `--force` を付けなくても **gitignore されたファイルを消す**。
拒否してくれるのは tracked の変更と untracked ファイルだけで、`.env` や `node_modules/` は
警告なしに消える。ブランチは SHA から戻せるが、**これは戻せない**。

スクリプトは消える直前に ignore 済みエントリを控えて報告に出す
（`（ignore 済みも消える: .env node_modules/）`）。**worktree に再生成できない
ignore 済みファイル（`.env`、ローカル DB、認証情報）を置く運用なら、`--dry-run` で
先に一覧を見せて確認を取る。**

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

   **worktree を消したくないと言われたら `--keep-worktrees` を付ける。** 逆に「ブランチだけ
   でいい」と言われていないなら既定のまま走らせてよい（worktree が残るとブランチも残るため、
   既定を外すと片付かない）。

2. **結果をそのまま報告する**

   「削除した」と「残した」の 2 つが出る。削除したブランチは SHA 付きで出るので、
   間違って消したときは `git branch <name> <sha>` で戻せることを一言添える。
   **worktree は戻せない。** 同じ場所へ `git worktree add` し直しても、ignore されていた
   ファイルは復元されない。報告に `ignore 済みも消える:` が出ていたら、そこは省略せずに伝える。

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
   - `worktree に変更が残っている` — tracked の変更か untracked ファイルがある。
     その worktree へ `cd` して `git status` の中身を見せる（`git -C` は使わない。
     `github:git-operations` を参照）。**消すなら `git worktree remove --force` だが、
     これは自分から提案しない。** ユーザーがその変更を要らないと明言してから使う
   - `worktree を消せなかった` — 事前判定を潜り抜けた場合。git のエラーがそのまま出るので、
     それを伝える
   - `メインの worktree でチェックアウト中` / `いま自分がいる worktree` — 消せない場所に
     いるだけ。別のブランチへ切り替えてから、あるいはメインのリポジトリから走らせ直す
   - `worktree でチェックアウト中（--keep-worktrees 指定）` — 指定どおりの動作。
     消してよいなら `--keep-worktrees` 無しで走らせ直す
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

worktree に載っているブランチなら、先に `git worktree list` でパスを引いて
`git worktree remove <path>`（`--force` は付けない）を通してから削除する。
拒否されたら中身が残っているということなので、そこで止まって中身を見せる。

## スクリプトが消さないもの

- 既定ブランチ（`origin/HEAD`、取れなければ `gh repo view` で解決）
- 現在チェックアウトしているブランチ
- メインの worktree、および実行時に自分がいる worktree
- 上の「残した」に入るブランチ

削除するのは「マージ済み PR の head SHA と先端が一致するブランチ」だけ。
リモートのブランチ自体は消さない（GitHub 側の delete-branch-on-merge に任せる）。
ただし最初に `git fetch origin --prune` を走らせるので、消えたリモートの追跡参照は片付く。
同様に `git worktree prune` も走らせるが、これはディレクトリが既に無い worktree の
管理情報を消すだけで、実在する worktree には触らない。

## 前提

- `gh` が認証済みであること
- リモート名が `origin` であること（`fetch --prune` と既定ブランチの解決に使う）

スクリプトが 0 以外で終了したら、そのメッセージをそのまま伝えて止まる。
**`git branch --merged` や `git branch -d` で自前の代替を組まない。** squash merge を
判定できないことが出発点なので、代替はどれも「消すべきブランチが 1 本も無い」という
間違った答えを返す。

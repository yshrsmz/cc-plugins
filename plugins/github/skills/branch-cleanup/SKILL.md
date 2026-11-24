---
name: branch-cleanup
description: >-
  マージ済みの PR に対応するローカルブランチと、それをチェックアウトしている worktree を、head SHA を照合して安全に削除する。マージ済みと確定できなくても、コミットがすべてリモートにあり未コミットの変更も open な PR も無い（消して失うものが無い）ブランチは一緒に削除する。squash merge されたブランチは `git branch -d` も `git branch --merged` も判定できないため、GitHub 側の情報で確認する。「ブランチを整理して」「マージ済みブランチを消して」「マージ済みの worktree を片付けて」「clean up branches」「prune branches」と言われたとき、および「マージしたのに `git branch -d` が拒否する」「マージ済みのブランチが消せない」「worktree があるせいでブランチが消せない」と相談されたときに使う。リモートブランチの削除、リモートに無いコミットや未コミットの変更を持つブランチ・worktree を消す作業には使わない。
---

Before executing, read the [Claude Code / Codex runtime instructions](../../references/runtime.md).

# Branch Cleanup

マージ済みのローカルブランチと、それをチェックアウトしている worktree を削除する。消して失うものが無いブランチも一緒に削除する。

## なぜスクリプトを使うのか

squash merge されたブランチは、git だけでは「マージ済み」と判定できない。

- `git branch -d` は「マージされていない」と言って拒否する
- `git branch --merged` にも出てこない
- `git diff <default> <branch>` も、既定ブランチが先に進んでいれば差分を出す

マージされたかどうかを知っているのは GitHub 側だけなので、**マージ済み PR の head SHA とローカルブランチの先端 SHA を照合する**。この照合を毎回手で組み直さないためのスクリプトが同梱してある。

PR はまずブランチ名（`gh pr list --head <branch>`）で探す。先端が PR の head と一致するか、**head の祖先なら**マージ済みとして消す。

祖先も見るのは、次の流れがよくあるからである。手元で commit して push し PR を作ったあと、別の場所（別の worktree、pod-agent、GitHub 上）で PR ブランチにレビュー修正が積まれ、手元に pull しないまま squash merge されてリモートのブランチが消える。手元の先端は PR head の祖先なので失うものは無いが、どのリモート追跡ブランチからも辿れないので「リモートに無いコミット」に数えられる。祖先かどうかは、PR head がローカルにあれば `git merge-base --is-ancestor <先端> <PR head>` で、無ければ GitHub の `gh api --hostname <host> repos/{owner}/{repo}/compare/<先端>...<PR head>` で見る（`behind_by` が 0 で `status` が `ahead` か `identical` なら祖先）。compare は GitHub が知らないコミットに 404 を返すので、そのときは `repos/{owner}/{repo}/commits/<先端>` が 422（`No commit found for SHA`）になることを確かめてから「祖先でない」とする。照会に失敗したら祖先でないとは扱わず `gh の照会に失敗した` で残す。祖先で一致したブランチは、報告に `（PR #N の head の祖先。PR 側に後からコミットが積まれてマージ済み）` が付く。

ブランチ名で引いた PR の head と一致も祖先もしなければ、先端 SHA を head に持つマージ済み PR を `gh api repos/{owner}/{repo}/commits/<sha>/pulls` で探す。ローカルと別の名前で push した（`git push origin foo:bar`）ブランチはブランチ名では引けず、マージ後にリモートのブランチも消えるので「コミットはすべてリモートにある」にも当たらない。先端 SHA で引けば、これもマージ済みとして消せる。この API は squash merge の merge commit や PR 途中のコミットにも PR を返すので、head SHA が先端と一致する PR だけを数える。fork からの PR も base のリポジトリから引ける。先端 SHA で一致したブランチは、報告に `（PR #N の head と一致。PR のブランチ名はローカルと異なる）` が付く。

## 失うものが無いブランチも消す

マージ済み PR と照合できないブランチの多くは、消しても何も失わない。サブエージェントが作った作業用 worktree、PR を手元で見るために作ったブランチ、PR がマージされた後に先端だけ動いた（main を取り込んだが push しなかった等）ブランチなどである。これを「マージ済みと確定できない」として全部残すと、何十本も残って 1 本ずつ中身を見る羽目になり、片付けにならない。

そこでスクリプトは、次の 3 つをすべて満たすブランチを、マージ済みと同じように worktree ごと消す。

- コミットがすべてリモートのどれかのブランチから辿れる（`git rev-list --count <branch> --not --remotes` が 0）
- worktree にチェックアウトされているなら、未コミットの変更（tracked の変更と untracked ファイル）が無い
- そのブランチを head とする open な PR が無い（失うものが無くても、作業中のブランチなので消さない）

報告では `（マージ済みと確定できないが、コミットはすべてリモートにある）` が付く。

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

   この SKILL.md の絶対パスをもとに、同じディレクトリ内の `scripts/prune-merged-branches.sh` を絶対パスに解決する。ホストが読み込んだインストール済みスキルの場所を使い、対象リポジトリの cwd から相対解決しない。

   ```bash
   bash "<absolute-path-to-this-skill>/scripts/prune-merged-branches.sh"
   ```

   `<absolute-path-to-this-skill>` は実際のスキルのディレクトリに置き換える。Claude Code と Codex のどちらでもこの方法を使い、プラグイン固有の環境変数には依存しない。

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

3. **残ったものは、そこで止まる**

   理由を説明するだけにして、**ユーザーが明示的に消せと言うまで削除しない**。

   「残した」は、消したら失うものが少ない順に並んでいる。失うものがあるブランチには `（リモートに無いコミット N 件 / 未コミットの変更 M 件）` が付く（worktree に載っていないブランチはコミットの件数だけ）。**1 本ずつ中身を見せて確認を取らない。** 件数で群に分けて要約し（例: 「リモートに無いコミットが 1〜3 件のもの 10 本、worktree に変更があるもの 2 本」）、ユーザーが中身を見たいと言ったブランチだけ中身を見せる。

   スクリプトが残す理由は次のとおりで、対処がそれぞれ違う。

   - `マージ済み PR が見つからない` — ブランチ名でも先端 SHA でもマージ済み PR が引けなかった。push していない作業ブランチか、PR を作る前のブランチか、PR がマージされたあとに手元で先端を動かした（コミット追加・rebase）別名 push のブランチ。中身を見せるときは `git log <branch> --not --remotes` で、リモートに無いコミットだけを出す
   - `マージ済み PR はあるが先端 SHA が一致しない（PR head の祖先でもない…）` — 先端が PR head と一致せず、その祖先でもない。PR がマージされたあとに手元で先端を動かした（コミット追加・rebase・amend）ということ。PR 側に後から積まれたコミットを pull していないだけのブランチは、祖先としてマージ済みに数えて消しているので、ここには入らない。中身を見せるときは `git log <PR head SHA>..<branch>` を使う。`<default-branch>..` を起点にしてはいけない。squash merge ではブランチのコミットが 1 つも既定ブランチの祖先にならないので、全履歴が未マージに見えてしまう。SHA はスクリプトの出力に入っている
   - `worktree に変更が残っている` — マージ済みだが、tracked の変更か untracked ファイルがある。中身を見せるときは、その worktree へ `cd` して `git status` を見せる（`git -C` は使わない。`github:git-operations` を参照）。**消すなら `git worktree remove --force` だが、これは自分から提案しない。** ユーザーがその変更を要らないと明言してから使う
   - `open な PR がある` — 失うものは無いが作業中のブランチ。消す対象にしない
   - `worktree を消せなかった` — 事前判定を潜り抜けた場合。git のエラーがそのまま出るので、それを伝える
   - `メインの worktree でチェックアウト中` / `いま自分がいる worktree` — 消せない場所にいるだけ。別のブランチへ切り替えてから、あるいはメインのリポジトリから走らせ直す
   - `worktree でチェックアウト中（--keep-worktrees 指定）` — 指定どおりの動作。消してよいなら `--keep-worktrees` 無しで走らせ直す
   - `削除できなかった（別の worktree で使われている可能性）` — 中身の問題ではない。`git worktree list` で使っている worktree を示すだけにする
   - `gh の照会に失敗した` — 判定できていないだけ。認証・ネットワーク・リポジトリ解決を確かめて、直してからやり直す

   はじめの 3 つは、消すと復旧できない変更が失われうる。ユーザーが群ごとに消すと言ったら、そのブランチだけを下の「特定のブランチだけを消せと言われたとき」の手順で消す。

## 特定のブランチだけを消せと言われたとき

**スクリプトを走らせない。** スクリプトは全ブランチを対象にするので、頼まれていないブランチまで消すことになる。

「残した」に出たブランチをユーザーが名指しで（または群として）消せと言ったなら、その判断は済んでいるので、そのまま消す。それ以外のブランチを名指しされたときは、同じ照合を手で行う。

```bash
gh pr list --head <branch> --state merged --limit 50 --json number,headRefOid --jq '.[] | "\(.number) \(.headRefOid)"'
git rev-parse "refs/heads/<branch>"
gh repo view --json url --jq '.url | split("/")[2]'
git merge-base --is-ancestor <sha> <PR head SHA>
gh api "repos/{owner}/{repo}/compare/<sha>...<PR head SHA>" --hostname <host> --jq '{status, behind_by}'
gh api "repos/{owner}/{repo}/commits/<sha>/pulls?per_page=100" --hostname <host> --jq '.[] | select(.merged_at != null and .head.sha == "<sha>") | .number'
git rev-list --count "refs/heads/<branch>" --not --remotes
```

`<sha>` は `git rev-parse` で得た先端 SHA、`<host>` は `gh repo view` で得た remote のホスト。`gh api` は `--hostname` が無いと（`GH_HOST` も無ければ）github.com に問い合わせるので、GitHub Enterprise（`<tenant>.ghe.com`）のリポジトリでは 404 になる。4 つ目は先端が PR head の祖先か（終了コード 0 なら祖先）を見る。PR head がローカルに無ければ（`git cat-file -e <PR head SHA>` が失敗する）5 つ目を使い、`behind_by` が 0 で `status` が `ahead` か `identical` なら祖先。404 なら `gh api "repos/{owner}/{repo}/commits/<sha>" --hostname <host>` が 422 になることを確かめてから「GitHub が先端を知らない＝祖先でない」とする。6 つ目はブランチ名で PR が引けなかったときに使い、`No commit found for SHA`（HTTP 422）なら GitHub がそのコミットを知らない（push していない）ということで、マージ済み PR は無い。

マージ済み PR の head と一致する（ブランチ名・先端 SHA のどちらで引いた PR でもよい）か、ブランチ名で引いたマージ済み PR の head の祖先か、リモートに無いコミットが 0 件なら `git branch -D <branch>`。どちらでもなければ、リモートに無いコミットの件数を添えて判断を仰ぐ。

worktree に載っているブランチなら、先に `git worktree list` でパスを引いて
`git worktree remove <path>`（`--force` は付けない）を通してから削除する。
拒否されたら中身が残っているということなので、そこで止まって中身を見せる。

## スクリプトが消さないもの

- 既定ブランチ（`origin/HEAD`、取れなければ `gh repo view` で解決）
- 現在チェックアウトしているブランチ
- メインの worktree、および実行時に自分がいる worktree
- 上の「残した」に入るブランチ

削除するのは「マージ済み PR の head SHA と先端が一致するブランチ」（PR のブランチ名がローカルと違ってもよい）、「先端がマージ済み PR の head の祖先であるブランチ」と「消して失うものが無いブランチ」だけ。リモートのブランチ自体は消さない（GitHub 側の delete-branch-on-merge に任せる）。ただし最初に `git fetch origin --prune` を走らせるので、消えたリモートの追跡参照は片付く。同様に `git worktree prune` も走らせるが、これはディレクトリが既に無い worktree の管理情報を消すだけで、実在する worktree には触らない。

## 前提

- `gh` が認証済みであること
- リモート名が `origin` であること（`fetch --prune` と既定ブランチの解決に使う）

スクリプトが 0 以外で終了したら、そのメッセージをそのまま伝えて止まる。
**`git branch --merged` や `git branch -d` で自前の代替を組まない。** squash merge を
判定できないことが出発点なので、代替はどれも「消すべきブランチが 1 本も無い」という
間違った答えを返す。

---
name: review-pr
description: PR をレビューし、結果を GitHub にインラインコメントとして投稿する。PR 番号を引数に取る。
argument-hint: "[PR number]"
disable-model-invocation: true
---

PR をレビューし、GitHub にインラインコメント付きレビューとして投稿する。

## 1. PR 番号の解決

- `$ARGUMENTS` が指定されていればそれを PR 番号として使用する
- 指定がなければ `gh pr list` で現在のリポジトリの PR 一覧を表示し、AskUserQuestion でユーザーにレビュー対象を選択させる

## 2. PR 情報の取得

以下を **並列で** 取得する:

- `gh pr view <number>` でタイトル、説明、ステータスを取得
- `gh pr diff <number>` で差分を取得
- `gh pr view <number> --json headRefOid` で head commit SHA を取得（レビュー投稿に必要）

## 3. サブエージェントによる並列レビュー

以下の 3 つのサブエージェントを **Task ツールで並列に** spawn する。各エージェントには PR のタイトル・説明・差分をプロンプトとして渡す。

### review-pr-bugs（subagent_type: review-pr-bugs）

バグ・セキュリティ問題の検出。Opus モデルで深い推論を行う。

### review-pr-rules（subagent_type: review-pr-rules）

CLAUDE.md / `.claude/rules/` への準拠チェック。Sonnet モデルで規約パターンマッチングを行う。

### review-pr-quality（subagent_type: review-pr-quality）

コード品質（DRY・一貫性・パフォーマンス）のレビュー。Sonnet モデル。

**プロンプトに含める情報:**

```
PR #<number>: <title>

## 説明
<PR description>

## 差分
<diff output>
```

## 4. 結果の統合

全エージェントから返された JSON 配列をマージし、以下を行う:

1. 同一ファイル・同一行への重複指摘を統合（より高い severity を採用）
2. confidence 70 未満の指摘がもし含まれていれば除外
3. severity 順（Critical → Medium → Low）でソート

## 5. レビュー内容の確認

投稿前に、レビュー内容をチャットに表示する。表示形式:

```
## レビュー結果 — PR #<number>

**総合コメント:**
（サマリテキスト）

**インラインコメント (N件):**

1. [Critical] `path/to/file.ts` L42
   （コメント内容）

2. [Medium] `path/to/file.ts` L78
   （コメント内容）
```

指摘がない場合は、レビューした内容の概要と良い点のみの総合コメントで LGTM とする旨を表示する。

その後 AskUserQuestion で以下の選択肢を提示する:

- **投稿する** — そのまま GitHub に投稿
- **修正してから投稿** — ユーザーのフィードバックを受けて内容を調整
- **キャンセル** — 投稿せずに終了

## 6. GitHub への投稿

**重要: `gh api` の `--field` は `comments` 配列を正しく扱えない（文字列として送信され 422 エラーになる）。必ず JSON ファイル + `--input` 方式を使うこと。**

1. Bash の `cat > /tmp/pr-review.json << 'EOF'` で JSON ファイルを作成する
2. `gh api ... --input /tmp/pr-review.json` で投稿する

```bash
# 1. JSON ファイルを作成
cat > /tmp/pr-review.json << 'EOF'
{
  "commit_id": "<head_commit_sha>",
  "body": "<総合コメント>",
  "event": "COMMENT",
  "comments": [
    {
      "path": "<file>",
      "line": <line>,
      "side": "RIGHT",
      "body": "**[severity]** comment"
    }
  ]
}
EOF

# 2. 投稿
gh api repos/{owner}/{repo}/pulls/{number}/reviews \
  --method POST \
  --input /tmp/pr-review.json \
  --jq '.html_url'
```

- `body`: 総合レビューコメント（サマリ + 各指摘の概要）
- `comments`: インラインコメントの配列。各コメントに `path`、`line`、`side: "RIGHT"`、`body`（重要度プレフィックス付き）を含める
- `event`: `"COMMENT"`
- 指摘がない場合はインラインコメントなしで総合コメント（LGTM）のみ投稿する（`comments` を空配列 `[]` にするか省略する）

## 7. 完了報告

投稿が成功したら、レビューの URL をユーザーに表示する。

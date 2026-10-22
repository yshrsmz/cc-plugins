# code-quality

Claude Code と Codex で使える、言語に依存しないコード改善スキル。

## simplify

変更したコードを再利用・品質・効率の3観点でレビューし、振る舞いを維持して修正・検証する。明示起動限定で、実装後に自動実行しない。

Claude Code ではマーケットプレースの登録後に `/plugin install code-quality@yshrsmz-cc-plugins` で導入し、`/code-quality:simplify` を実行する。Codex では同マーケットプレースから `code-quality` を導入し、スキル選択から `simplify` を選ぶか、依頼文で明示する。

| 依頼例 | 動作 |
|---|---|
| `simplify` | ベースブランチとの差分全体と未コミット変更をレビューして修正 |
| `simplify base: origin/main` | 明示したベースとの merge-base 以降を対象にする |
| `simplify src/parser.py` | 指定ファイルを対象にする |
| `simplify レビューのみ。I/O の重複を重点的に確認` | 編集せず、指摘を報告 |

ベースが確定しなければ質問する。未追跡ファイルは依頼との関連を確認し、生成物や機密情報を無差別に読まない。Git 管理外でも明示したファイルを対象にできる。

## 実行環境

ブランチの差分を使う場合は Git が必要。PR のベースを調べる場合に限り、利用可能な GitHub ツールと認証を使う。PR 情報がなくてもベースを明示でき、GitHub 接続は必須ではない。追加パッケージや MCP は不要。

3担当は読み取り専用でレビューし、親が指摘を検証して修正する。Claude Code ではプラグインの名前付きエージェントを使い、Codex では同じ定義本文を汎用サブエージェントに渡す。同時実行枠が足りなければ分割し、委譲機能がなければ逐次レビューする。

プロジェクトの規約と検証コマンドに従い、出力・エラー・副作用・実行順序・公開 API を維持する。検証できない項目は報告する。コミット・push・PR 投稿はこのスキルの動作に含まれない。

## 設計の参考

Claude Code の旧 `/simplify` の再利用・品質・効率というレビュー観点と、[Anthropic の code-simplifier](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md) の振る舞い維持・可読性優先の考え方を参考に、両ホスト向けの指示を独自に記述した。旧 `/simplify` と現行 `/code-review` の関係は [公式 changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) を参照。

## License

Apache-2.0。リポジトリのライセンスを適用する。

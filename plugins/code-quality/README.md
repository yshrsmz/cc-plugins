# code-quality

Claude Code と Codex で使える、言語に依存しないコード改善とテスト精査のスキル。

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

## prune-tests

コードベース内の全テストを精査し、積極的に削除・統合できるテストをすべてリストアップする。明示起動限定で、テストの削除・統合は行わず一覧の報告で終了する。

Claude Code では `/code-quality:prune-tests` を実行する。Codex ではスキル選択から `prune-tests` を選ぶか、依頼文で明示する。

| 依頼例 | 動作 |
|---|---|
| `prune-tests` | リポジトリ内の全テストを精査 |
| `prune-tests src/billing/` | 指定ディレクトリのテストに絞る。重複の確認には他のテストも読む |
| `prune-tests E2E を重点的に` | 重点観点を担当に伝える |

削る対象は、実装のコピー、モックの自己検証、型・ライブラリの保証の再確認、他テストとの重複、内部実装への過度な依存、過剰なケース分け。判断基準は「削除すると、どんな現実的な不具合を見逃すか」で、念のためという理由では残さず、実行時間・不安定さ・修正負担と保証の価値を比較する。テスト件数やカバレッジの維持は目的にしない。

テストファイルをモジュールなどの単位で区画に分け、区画ごとに読み取り専用の担当（[prune-tests-auditor](agents/prune-tests-auditor.md)）が精査する。区画をまたぐ重複と各候補は親が実コードで検証し、両方を消して保証を失う提案を出さない。報告はテストごとに、分類・提案（削除・統合先・パラメータ化）・削除で見逃す現実的な不具合・削減できるコスト・確度を並べた表になる。テストの実行は自動で行わず、実行時間や不安定さはリポジトリ内の CI レポートや retry・skip の指定から判断する。実測値がなければ推定と明記する。

## 実行環境

ブランチの差分を使う場合は Git が必要。PR のベースを調べる場合に限り、利用可能な GitHub ツールと認証を使う。PR 情報がなくてもベースを明示でき、GitHub 接続は必須ではない。追加パッケージや MCP は不要。

3担当は読み取り専用でレビューし、親が指摘を検証して修正する。Claude Code ではプラグインの名前付きエージェントを使い、Codex では同じ定義本文を汎用サブエージェントに渡す。同時実行枠が足りなければ分割し、委譲機能がなければ逐次レビューする。

プロジェクトの規約と検証コマンドに従い、出力・エラー・副作用・実行順序・公開 API を維持する。検証できない項目は報告する。コミット・push・PR 投稿はこのスキルの動作に含まれない。

## 設計の参考

Claude Code の旧 `/simplify` の再利用・品質・効率というレビュー観点と、[Anthropic の code-simplifier](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md) の振る舞い維持・可読性優先の考え方を参考に、両ホスト向けの指示を独自に記述した。旧 `/simplify` と現行 `/code-review` の関係は [公式 changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) を参照。

## License

Apache-2.0。リポジトリのライセンスを適用する。

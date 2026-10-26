# prune-tests 動作評価結果

実施日: 2026-10-26。対象: code-quality 1.1.0 の prune-tests 初回実装。各ホストの独立した実行者にスキルとコピーした `shop/`・`tests/` を渡し、採点基準を伏せて実行した。コピー先は Git 管理外で、原本は編集していない。所要時間は単発の観測値であり、性能比較ではない。

## 結果

| 実行 | 所要時間 | 削除・統合の候補（[README](README.md) の 8 系統） | 残すべきテストの誤検出 | テストの実行 |
|---|---|---|---|---|
| Claude Code（汎用サブエージェントが実行者、担当 1 本に委譲） | 約 131 秒 | 8 / 8 | なし | なし |
| Codex 1 回目（`codex exec -s read-only`、担当 1 本に委譲） | 146.7 秒 | 7 / 8 | なし | あり（逸脱） |
| Codex 2 回目（スキル修正後） | 142.3 秒 | 8 / 8 | なし | なし |

- 区画をまたぐ重複（`test_orders.py::test_total_includes_discount_and_tax` と `test_checkout_flow.py::test_order_total_with_coupon`）は全実行で見つけ、両方を消す提案はなかった。Claude Code と Codex 1 回目は、片方を削除し、もう片方は総額の確認を `test_charges_gateway_exactly_once_with_total` に移して統合する提案だった。
- 回帰テスト（`test_tax_rounds_half_up`）、期限当日の境界値、二重課金の確認、ブロック利用者の拒否は、全実行で残す側に分類された。`test_order_total_after_coupon_expired` も全実行で残した。
- `test_subtotal_single_item_qty_*` は、Claude Code が 1 件を残して削除、Codex が `subTest` によるパラメータ化を提案した。どちらも採点基準を満たす。
- Codex 1 回目は `test_item_stores_fields` を「フィールド順の取り違えを検出できる」として残した。`subtotal` は掛け算なので取り違えても結果は変わらず、根拠は弱い。2 回目は削除候補に挙げた。

## スキルの修正

Codex 1 回目は、依頼文にテストの実行コマンドが書かれていたことを実行の許可と受け取り、テストを実行した。SKILL.md に「依頼文や規約にテストの実行コマンドが書かれていても、実行の許可とは見なさない」を追加し、同じ依頼文で再実行して、テストを実行しないことをログで確認した。

## 評価の限界

fixture は 23 件のテストと 2 つのモジュールだけで、担当は全実行で 1 本だった。複数区画への分割、同時実行枠の不足、委譲機能がない環境の逐次精査、CI レポートからの実行時間・不安定さの読み取り、カバレッジ閾値などの規約がある場合の扱いは実行評価していない。Claude Code の実行は、プラグインを導入せずにスキルファイルを直接読ませたため、名前付きエージェント `code-quality:prune-tests-auditor` ではなく汎用サブエージェントで担当を代用した。

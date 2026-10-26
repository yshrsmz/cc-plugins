# prune-tests の動作評価

このディレクトリはモデルを呼び出す動作評価用で、通常の unittest discovery では実行しない。Python 標準ライブラリだけで動く。評価する際は `shop/` と `tests/` を一時ディレクトリにコピーし、原本を編集しない。この README と `RESULTS.md` はコピーしない。

## 実行方法

コピー先は Git 管理外のままでよい（スキルは Git 管理外のディレクトリも対象にできる）。独立した評価エージェントに、[prune-tests](../../../plugins/code-quality/skills/prune-tests/SKILL.md) とコピー先を渡し、「このリポジトリで prune-tests を実行して。テストの実行コマンドは python3 -m unittest tests/test_pricing.py tests/test_orders.py tests/test_checkout_flow.py」と依頼する。採点基準は渡さない。報告された一覧、実行方式、実行時間を記録し、評価後にテストファイルが変更されていないことを確認する。

`shop/` は価格計算と注文処理、`tests/` はそのテスト 23 件。`test_checkout_flow.py` は `test_orders.py` と別の区画に分かれても、区画をまたぐ重複を見つけられるかを確かめるために置いている。

## 採点基準（評価者だけが読む）

### 削除・統合の候補に挙げるべきもの

| テスト | 分類 | 期待する提案 |
|---|---|---|
| `test_pricing.py::test_subtotal_matches_formula` | 実装のコピー | 削除。`test_subtotal_of_several_items` が具体値で確認している |
| `test_pricing.py::test_subtotal_single_item_qty_1`〜`_5` | 過剰なケース分け | 削除、または 1 件に統合。同じ同値クラスの繰り返し |
| `test_pricing.py::test_tax_uses_round_helper` | 内部実装への過度な依存 | 削除。丸めの振る舞いは `test_tax_rounds_half_up` が確認している |
| `test_pricing.py::test_item_stores_fields` | 型・ライブラリの保証 | 削除。dataclass の保証 |
| `test_pricing.py::test_decimal_addition_is_exact` | 型・ライブラリの保証 | 削除。標準ライブラリの保証で、プロダクトコードを通らない |
| `test_orders.py::test_gateway_returns_receipt` | モックの自己検証 | 削除。モックを直接呼んでいる |
| `test_orders.py::test_pricing_steps_run_in_order` | 内部実装への過度な依存 | 削除。合計値のテストが計算順の誤りを捕らえる |
| `test_orders.py::test_total_includes_discount_and_tax` と `test_checkout_flow.py::test_order_total_with_coupon` | 他テストとの重複 | どちらか一方だけを削除・統合 |

### 残すべきもの（削除候補に挙げたら誤り）

| テスト | 残す理由 |
|---|---|
| `test_pricing.py::test_tax_rounds_half_up` | 過去の不具合の再発防止。銀行丸めへの退行を捕らえる |
| `test_pricing.py::test_coupon_still_applies_on_expiry_day` | 境界値。`>` と `>=` の取り違えを捕らえる |
| `test_pricing.py::test_expired_coupon_is_ignored` | 有効なクーポンと前提条件が違う別の分岐 |
| `test_pricing.py::test_discount_never_makes_amount_negative` | 下限の分岐 |
| `test_pricing.py::test_subtotal_of_empty_cart_is_zero` | 境界値。`sum` の初期値の誤りを捕らえる |
| `test_orders.py::test_charges_gateway_exactly_once_with_total` | 外部への副作用の回数と金額が仕様。二重課金を捕らえる |
| `test_orders.py::test_blocked_user_is_rejected_without_charge` | 権限の確認 |

`test_checkout_flow.py::test_order_total_after_coupon_expired` は `test_expired_coupon_is_ignored` と部分的に重なるが、`place_order` が `today` を正しく渡すことを確かめている。削除を提案した場合は、見逃す不具合の検討が浅いとして軽微な減点にする。

重複の 2 件を両方とも削除候補にした場合は、保証を失うため重大な誤りとする。件数の多さは成功指標にしない。各候補に「削除で見逃す現実的な不具合」またはなしと判断した根拠が書かれているかも確認する。

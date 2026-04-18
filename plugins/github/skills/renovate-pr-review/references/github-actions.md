# GitHub Actions — Renovate Review Reference

## 対象ファイル

- `.github/workflows/*.yml` / `*.yaml`
- `.github/actions/**/action.yml`（Composite Action を自作している場合）
- reusable workflow の呼び出し先

## 変更差分の抽出

```bash
git diff origin/<base>...HEAD -- '.github/workflows/**' '.github/actions/**'
```

変更は通常 `uses: owner/repo@version` の version 部分。

## 調査対象の判定

| action の種類 | 優先度 | 調査内容 |
|--------------|-------|---------|
| 公式 actions (`actions/checkout`, `actions/setup-node` 等) | 高 | ランタイム変化 (Node 20→24 等)、input 仕様変化、output 仕様変化 |
| setup 系 (`actions/setup-java`, `dtolnay/rust-toolchain` 等) | 高 | default version の変化、toolchain 解決ロジック |
| reviewdog / sonarqube / codecov 等 | 中 | レポート仕様の変化 |
| 自作 composite action | 中 | 内部実装変化、依存更新 |
| release / deploy 系 | 高 | secrets 扱い、permission 要件変化 |

## よくある MIGRATE 対応

### ランタイム変更 (Node ベース action)

`actions/checkout@v4` (Node 20) → `actions/checkout@v5` (Node 24) のように、action の JavaScript ランタイムが上がることがある。

- self-hosted runner の Node バージョンが追いついているか確認
- 同じ workflow 内で古い Node 版 action と新しい Node 版 action が混在しても問題ないが、self-hosted runner 側での対応が必要なら Issue を立てる

### Input / Output 仕様変化

major bump で input が削除・改名されることがある。changelog を読み、workflow 側で使っている `with:` の値を更新。

### Permission 要件

action が `permissions:` の明示を要求するように変わっているケース。`GITHUB_TOKEN` の scope 絞り込みは security 的に歓迎するが、workflow 側の `permissions:` セクション更新が必要。

## よくある ADOPT 候補

- `actions/cache@v4`: `save-always` オプション、restore-keys の挙動改善
- `actions/setup-node@v4`: built-in cache の活用（別途 `actions/cache` を呼ばなくて良くなる）
- reusable workflow への置き換え（同じ処理を複数 workflow で重複定義している場合）

## 破壊的変更の頻出パターン

- deprecated input の削除
- output 名の変更
- default shell の変更（Windows runner 等）
- action の archive（別 action への移行促進）

## version ピン方針

プロジェクトの方針に従う:

| 方針 | 例 | メリット / デメリット |
|------|----|-------------------|
| Tag pin | `@v5` | 自動で patch/minor 追随、破壊的変更リスクあり |
| Commit SHA pin | `@abc123...` | 完全固定、security 的に最強だが更新頻度高 |

`.github/renovate.json` / `renovate.json5` の設定で指定されているはず。Renovate PR 自体がピン方式に合わせた更新を提案している。

## 検証

GitHub Actions は手元で完全に再現できないが、以下で事前検証可能:

```bash
# workflow syntax check
gh workflow view <workflow-name>

# actionlint でセマンティックチェック
actionlint .github/workflows/*.yml
```

手元で `act` による実行も可能だが、secret や environment の再現が困難なため、実 CI での最初の run は注視する。

## 注意

Renovate が更新する action は、実行時に **GITHUB_TOKEN を使って API 叩く** ものも多い。supply chain 攻撃を防ぐため、major bump では特に信頼できる author / maintainer かを changelog から確認する。

よく知られた action（`actions/*`, `docker/*`, `softprops/*`, `peaceiris/*` など）以外で major bump が来た場合は、ユーザーに実行して良いか確認する。

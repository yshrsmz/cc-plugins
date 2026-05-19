---
name: renovate-pr-review
description: >-
  Renovate (や Dependabot) が作成した依存更新 PR を対象に、各パッケージの changelog を並列調査し、破壊的変更への追随・新 API の採用判断・関連ファイルの同期更新までを行う。npm/pnpm/yarn・Cargo・Gradle/Maven・GitHub Actions の manifest を自動検出し、プロジェクトの実行基盤（CLAUDE.md / CI 設定）に従ってビルドとテストを走らせる。「この Renovate PR 見て」「依存更新 PR 対応して」「bump 系 PR の中身チェック」といった依頼で必ず使用する。
argument-hint: "[PR number] [--auto-push]"
disable-model-invocation: true
---

# Renovate PR Review

Renovate / Dependabot 由来の依存更新 PR を「機械的に merge する」のではなく、**各パッケージの更新内容を読み解き、必要に応じて我々のコードを新しい API に追従させる** ためのスキル。

このスキルが前提とする価値観:

- 既存コードの保存は目的ではない。**新 API が保守性・パフォーマンス・安全性を改善するなら積極的に採用する**。
- ただしコード変更には対応するテストを用意する。
- 一時しのぎの workaround より**根本的な修正**を優先する。**vendor が提供する deprecation-silencer フラグ（`ignoreDeprecations` 等）も workaround に含む** — 「公式が用意してくれたから OK」ではない。
- 破壊的変更が既存コードに影響する場合は、その影響を明確に説明し、修正する。

## 1. Identify the PR

引数で PR 番号を受け取る場合はそれを使う。未指定なら現在のブランチを確認:

```bash
gh pr view --json number,title,headRefName,author
```

Renovate / Dependabot 以外の author の PR に対してこのスキルを適用しない。ユーザーに確認する。

## 2. Checkout & baseline snapshot

```bash
gh pr checkout <PR_NUMBER>
```

プロジェクト規約 (`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`) を読み、以下を把握する:

- パッケージマネージャの指定 (pnpm 固定など)
- ビルド / テスト / lint / format コマンド
- commit hook の扱い
- **コミット対象ビルド成果物の有無とその再生成手順**（例: GitHub Actions JS の `dist/`）

成果物の再生成手順や必須検証コマンドはプロジェクトの指示に必ず記載されている前提。読み落とさない。

## 3. Detect ecosystem & list changed packages

manifest file の diff から変更されたパッケージ一覧を抽出する。複数のエコシステムが混在する可能性もある (例: Node + GitHub Actions)。

```bash
git diff origin/<base-branch>...HEAD --name-only
```

エコシステムごとの手順は以下を参照:

- **npm / pnpm / yarn**: `references/npm.md`
- **Cargo (Rust)**: `references/cargo.md`
- **Gradle / Maven (JVM)**: `references/gradle-maven.md`
- **GitHub Actions**: `references/github-actions.md`

## 4. Fetch changelogs in parallel

`dependencies`（runtime に影響する = コード挙動が変わり得る）と `devDependencies`（ビルド/テスト時のみ）で優先度を分ける。

**サブエージェント並列実行** で各パッケージの changelog を取得する。同一メッセージ内に複数の Agent 呼び出しを並べることで並列化される。

### サブエージェント依頼テンプレート

```
Fetch the release notes / changelog for <package> between versions <old> and <new>.

Our project uses <package> for <use-case>. Our actual usage in code:
  <パッケージをどう import/呼び出しているかの要約>

Report under 400 words. Focus on:
1. New APIs / features that could simplify our code or improve maintainability/performance
2. Breaking changes or deprecations relevant to our usage
3. Bug fixes affecting our scenarios
4. Deprecations: if any are introduced, report BOTH (a) the recommended migration path and (b) any vendor-provided escape hatch (e.g., `ignoreDeprecations`, `--allow-deprecated`, peer override). Mark the escape hatch explicitly as "WORKAROUND — do not adopt as the fix".

Sources:
- GitHub Releases page of the project
- CHANGELOG.md in the repo

Exclude noise (internal refactors, unrelated feature areas).
```

### 並列実行する範囲

- Runtime 依存 (dependencies 相当): **全件必須**
- Dev 依存 (devDependencies 相当): **minor 以上**もしくはビルド/テスト/linter の主要ツール（rollup, vitest, biome, tsc 等）のみ。typo 系 `@types/*` の patch は report を省略して良い。
- GitHub Actions: `uses:` 行が変わっているもの全件。

## 5. Evaluate & decide per package

各パッケージについて、以下のどれに該当するかを判定する:

| 判定 | 条件 | アクション |
|------|------|----------|
| **ADOPT** | 新 API が保守性/パフォーマンス/安全性を明確に改善し、我々のコードに適用可能 | コード修正 + 対応テスト追加 |
| **MIGRATE** | 破壊的変更 or deprecation が我々の使用箇所/設定に影響する | 根本的な書き換え（deprecated 設定値の差し替えを含む） |
| **FOLLOW-UP** | 振る舞いを保つために新フラグを追加する必要が無い、純粋な schema/バージョン番号追随（`$schema` URL、lockfile-only など） | 設定ファイルを更新 |
| **NONE** | 既存コードに影響せず、導入メリットも乏しい | 何もしない |

### 判定を表形式でユーザーに提示

```
## Changelog Review Summary

| Package | 旧 → 新 | 種別 | 判定 | 根拠 / アクション |
|---------|---------|------|------|------------------|
| fast-xml-parser | 5.5.8 → 5.7.1 | runtime | NONE | Kover XML は entity を含まず、既存の processEntities: false 設定が高速パスに乗っている。新 API なし。 |
| @biomejs/biome | 2.4.8 → 2.4.12 | dev | FOLLOW-UP | biome.json の $schema URL をバージョン追従 |
| vitest | 4.1.0 → 4.1.4 | dev | NONE | 新 API なし、既存テスト全件 pass |
| actions/checkout | v4 → v5 | actions | MIGRATE | Node 20 → Node 24 ランタイム切替。影響なし、そのまま追随 |
```

### 判定基準の補足

**ADOPT すべきシグナル**:
- Promise-based / async API が追加されて callback を置き換えられる
- 型安全な API が追加されて `as any` が消せる
- 新しい matcher / helper でテストが簡潔になる
- performance 系オプション（streaming, lazy, batch 等）で hot path が改善する

**NONE に留めるべきシグナル**:
- 該当機能が我々のユースケースで不要
- 既存 API が引き続きサポートされ、変更の正当化が弱い
- experimental / unstable 扱い

迷ったら ADOPT せず NONE とし、「将来的に検討」と記録する。

**FOLLOW-UP に見えるが MIGRATE のシグナル**:
- deprecation 警告に対し、vendor 提供の escape hatch（TS `ignoreDeprecations`, ESLint `--quiet`, peer override, `--legacy-peer-deps` 等）を足すだけで「設定ファイル更新」に見える変更。**deprecated 設定値そのものを置き換えるのが正解** で、escape hatch は禁じ手。

## 6. Apply modifications

判定が **ADOPT / MIGRATE / FOLLOW-UP** のものについて修正を実施する。

### 実施順序

1. Manifest の整合性確認 (`pnpm install` / `cargo fetch` / `./gradlew build --dry-run` 等)
2. コード修正 (ADOPT / MIGRATE)
3. 対応テスト追加 / 既存テスト更新 (ADOPT の場合**必ずテストを伴わせる**)
4. 設定ファイル追随 (FOLLOW-UP)
5. プロジェクト指示にあるビルド成果物の再生成（手順は CLAUDE.md / CONTRIBUTING.md 等に記載されているはず）

### テストなしの ADOPT は禁止

新 API を導入したが対応するテストが書けない、もしくは書くべきテストが存在しない場合は ADOPT しない。その場合は NONE に格下げし、後続タスクとしてメモする。

### Workaround 禁止

破壊的変更を受けた際、以下のような workaround を用いない:

- 型/lint 抑止: `as unknown as T`, `@ts-ignore`, `// eslint-disable-next-line` を新規追加
- **Deprecation-silencer フラグ: `ignoreDeprecations`, `skipLibCheck` を新規に true 化, `--allow-deprecated-*`, peer override, `--legacy-peer-deps` 等 — deprecated 設定値そのものを差し替えるのが正解**
- version pinning / lockfile 巻き戻しによる bump の事実上の撤回
- 代替ライブラリの臨時導入

根本的な書き換えで対応する。書き換え量が大きいと判断した場合は、その旨をユーザーに提示して方針を確認する。

### コミット前 self-check

`git diff --cached` を以下のパターンで grep し、ヒットした場合は Step 5 に戻って MIGRATE 判定が正しいか再評価する。新規追加なら高確率で workaround:

- `ignoreDeprecations`
- `skipLibCheck.*true`
- `@ts-ignore`, `@ts-expect-error`
- `eslint-disable`
- `--legacy-peer-deps`, `--force`, `--no-deprecation`
- `package.json` の `overrides` / `resolutions` セクションへの新規追加

## 7. Verify

プロジェクトの CLAUDE.md / CI 設定に記載された検証コマンドを実行する。典型的には以下のような組み合わせ:

| エコシステム | 検証コマンド (例) |
|------------|-----------------|
| pnpm / npm | `pnpm run format:check && pnpm run lint && pnpm run test --run && pnpm run build` |
| Cargo | `cargo fmt --check && cargo clippy -- -D warnings && cargo test && cargo build --release` |
| Gradle | `./gradlew spotlessCheck detekt test assembleDebug` |
| Maven | `mvn verify` |
| GitHub Actions | `act` もしくは workflow の dry-run |

**CI でのみ実行される検証項目（ビルド成果物の差分チェック等）も手元で実行しておく**。CI 失敗で往復するより手元で発見する方が安い。プロジェクトの CI 設定 (`.github/workflows/*.yml` など) に目を通して、CI で走るが CLAUDE.md 未記載のチェックがないか確認する。

検証中にエラーが出たら、それは workaround で隠すべきではない新たな対応事項。Step 5 に戻って再評価する。

## 8. Commit

Renovate の元コミットは**改変しない**。その上に追加コミットを積む (amend / force-push 禁止)。

### コミット粒度

判定の種類ごとに分ける:

- `refactor(<area>): adopt <new-api>` — ADOPT による書き換え（コード変更 + テストを同一コミットに含める）
- `chore(config): sync <schema-version>` — FOLLOW-UP
- `build: rebuild <artifact> for <reason>` — プロジェクト指示によるビルド成果物更新

1 つの判定で複数ファイルに変更が及ぶ場合でも、**別判定のファイルは別コミット**に分ける。レビュアーが独立に判断できるようにするため。

### コミットメッセージ

プロジェクトのスタイルに従う (`git log --oneline -10` で直近のスタイルを把握)。Conventional Commits を使う repo では type を合わせる。

Claude Code の attribution は、プロジェクトの直近 commit が付与していれば同じ形式で付ける。

## 9. Pre-push summary（ユーザー確認）

**push の前に必ずサマリを提示してユーザー確認を取る**。自動化したい場合のみ、引数に `--auto-push` が指定されていれば確認を省略して push まで実行する。

### サマリ形式

```
## Renovate PR #XXX Review Summary

- 調査対象: N パッケージ
- 判定内訳: ADOPT=A, MIGRATE=M, FOLLOW-UP=F, NONE=X
- 追加コミット: <count> 件
- 手元検証結果: format ✅ / lint ✅ / test ✅ / build ✅

## 追加コミット

- <hash> <subject>
- <hash> <subject>

## 採用した新 API (ADOPT)

- <package@version>: <変更内容の要約>
  - テスト: <テストファイル:関数名>

## 破壊的変更への追随 (MIGRATE)

- <package@version>: <何がどう変わって、どこを修正したか>

## 追随した設定 (FOLLOW-UP)

- <file>: <old> → <new>

## 見送った項目 (NONE)

- <package@version>: <見送り理由を 1 行で>

## 所感 / 懸念点

<あれば記載。特に major bump の有無、CI でしか再現しないリスク等>

---
push してよいか確認してください（`git push` 実行前）。
```

### ユーザー確認後の push

```bash
git push
```

`--force` / `--force-with-lease` は使わない。push 後、PR URL を提示して完了。

### --auto-push モード

スキル起動引数に `--auto-push` が含まれていた場合のみ、サマリを表示した**直後に自動で push まで実行**する。ただしサマリ表示は省略しない — ログとして残す。

#### --auto-push でも確認を挟むべきケース

以下の場合は `--auto-push` 指定があっても**必ずユーザー確認を挟む**:

- Major version bump が 1 つでも含まれている
- MIGRATE が発生している（破壊的変更への追随）
- 手元検証のいずれかが失敗している
- main / master など保護ブランチに直接 push しようとしている

これらは「自動化しても安全」とは言えない。合図として必ず停止する。

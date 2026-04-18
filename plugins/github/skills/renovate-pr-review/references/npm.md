# Node.js (npm / pnpm / yarn) — Renovate Review Reference

## Manifest & lock files

- Manifest: `package.json`
- Lock files: `package-lock.json` (npm) / `pnpm-lock.yaml` (pnpm) / `yarn.lock` (yarn)

プロジェクトの `packageManager` フィールドか lock ファイルの種類で判定。CLAUDE.md に指定がある場合はそれを最優先。

## 変更差分の抽出

```bash
git diff origin/<base>...HEAD -- package.json
```

`dependencies` / `devDependencies` / `peerDependencies` / `optionalDependencies` を分けて把握する。

## Install

プロジェクトの package manager で実行:

```bash
pnpm install        # pnpm プロジェクト
npm install         # npm プロジェクト
yarn install        # yarn プロジェクト
```

`pnpm` プロジェクトで `npm` / `npx` を使わない。CLAUDE.md で明示的に禁止されているケースが多い。

## 調査優先度

| カテゴリ | 優先度 | 調査内容 |
|---------|-------|---------|
| `dependencies` (runtime) | 高 | breaking change / 新 API 全件 |
| ビルドツール (rollup / webpack / vite / esbuild / tsc) | 高 | 出力変化 / 新 plugin API |
| テスト/リンタ (vitest / jest / biome / eslint / prettier) | 中 | 新 matcher / ルール / schema 変更 |
| 型定義のみ (`@types/*`) | 低 (patch なら省略可) | major / minor のみ型シグネチャ変化を確認 |
| 開発支援 (lefthook / husky 等) | 低 | patch 省略可 |

## よくある FOLLOW-UP 対応

- `biome.json` の `$schema` URL: biome CLI バージョンに合わせる
- `.prettierrc` / `tsconfig.json` の新オプション対応（changelog に記載があれば）
- `eslint.config.js` (flat config) の schema 変化
- `vitest.config.ts` の新 API 適用（`pool` 設定など）
- `tsc` の新 strict オプションが追加された場合、採用するかプロジェクト方針で判断

## よくある ADOPT 候補

- Promise-based API の追加（callback / sync API から移行）
- Built-in fetch / AbortSignal の活用（node-fetch 依存削除など）
- Vitest: `vi.waitFor` / `expect.poll` / `expect.soft` の活用
- TypeScript: `satisfies` 演算子、`const` type parameter
- Rollup: `experimentalLogSideEffects` 等の性能オプション

## 破壊的変更の頻出パターン

- default export → named export への切替
- CJS → ESM 専用化
- Node.js 最小要件引き上げ（`engines.node`）
- 型定義の引き締め（`unknown` 化、`readonly` 追加）

## 検証コマンド (典型)

```bash
pnpm run format:check
pnpm run lint
pnpm run test --run
pnpm run build
```

プロジェクトの `package.json > scripts` と CLAUDE.md の指示に従う。CI workflow (`.github/workflows/ci.yml` 等) で実行されているコマンドと整合しているか確認する。

## コミット成果物の注意

`dist/` を git に含めるプロジェクト（GitHub Actions の JS runner 等）では、ビルド後に必ず `git status` で dist 差分を確認してコミットに含める。プロジェクトの指示に手順が書かれている前提。

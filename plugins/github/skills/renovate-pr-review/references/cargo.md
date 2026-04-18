# Cargo (Rust) — Renovate Review Reference

## Manifest & lock file

- Manifest: `Cargo.toml` (workspace の場合はルート + 各 crate の `Cargo.toml`)
- Lock file: `Cargo.lock` (binary crate は commit 対象、library crate は通常無視)

## 変更差分の抽出

```bash
git diff origin/<base>...HEAD -- '**/Cargo.toml' Cargo.lock
```

`[dependencies]` / `[dev-dependencies]` / `[build-dependencies]` を分けて把握。workspace なら `[workspace.dependencies]` も対象。

## Install / Resolve

```bash
cargo fetch
cargo build        # 依存解決と型チェック同時
```

`cargo update` は**追加実行しない**（Renovate が既に意図した lock を作成済み）。

## 調査優先度

| カテゴリ | 優先度 | 調査内容 |
|---------|-------|---------|
| `dependencies` (runtime) | 高 | breaking change / 新 API |
| proc-macro crate (`syn`, `quote`, `serde_derive` 等) | 高 | マクロ出力の変化 |
| `dev-dependencies` (test / bench) | 中 | テスト API 変化 |
| `build-dependencies` | 中 | `build.rs` への影響 |

## よくある FOLLOW-UP 対応

- `rust-toolchain.toml` の MSRV 引き上げ追随
- `clippy.toml` / `rustfmt.toml` の新オプション対応
- `Cargo.toml` の `edition` / `resolver` アップグレード（major 相当、ユーザー確認必須）

## よくある ADOPT 候補

- `anyhow` / `thiserror` の新エラー型変換
- `tokio` の新タスク API（`JoinSet`, `tokio::select!` の改善など）
- `serde` の新 attribute（`rename_all_fields` 等）
- `clap` v4 の derive API 改善

## 破壊的変更の頻出パターン

- trait object 化 / `dyn Trait` への切替必須化
- default feature flag の変更（自動で有効だった機能が opt-in 化）
- generic bound の追加（`Send + Sync` 要件など）
- MSRV の引き上げ

## 検証コマンド (典型)

```bash
cargo fmt --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test --all-features
cargo build --release
```

プロジェクトの CLAUDE.md / `justfile` / `Makefile` / `.github/workflows/*.yml` に具体的な検証コマンドが定義されている。それに従う。

## proc-macro 更新の注意

proc-macro crate の更新は `.rs` ファイル内のマクロ展開結果が変わる可能性がある。コンパイル成功 = 変更なし ではない。`cargo expand` で生成コードを差分確認するか、テストで挙動を担保する。

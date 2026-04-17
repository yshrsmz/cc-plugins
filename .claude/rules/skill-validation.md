---
description: スキルの "slim 化 / trust-the-model 化" を提案する前に実測で検証する
globs: plugins/**/skills/**
---

スキル（特に既存スキル）を「短くする / モデルを信用する / skill-creator 的ベストプラクティスに寄せる」方向で refactor しようとする場合は、**提案と同時に実測による検証計画を必ずセットで出すこと**。

- 最低限の検証: 改変前後の 2 バージョンを用意し、実際の PR / 差分に対してそれぞれのプロンプトで subagent を走らせ、出力の ⚠️ / 🔴 指摘の substantive な抜け漏れを比較する
- 検証対象は 1 パターンだけに頼らない: 単純 PR（整形・単一ファイル修正）と複雑 PR（architecture refactor・multi-module）の両方で見る
- 結果ベースで採否を判断する。skill-creator の「500 行以内」「heavy-handed MUSTs を避けろ」などは一般論であり、このプロジェクトの具体で品質が落ちるなら採用しない

## なぜ

2026-04-18 に `plugins/android/skills/agent-review` / `codex-review` を skill-creator 助言に沿って ~576 行 → ~129 行へ slim 化する PR #11 を作成した。整形系 PR #440 では slim 版が tokens -25% / time -34% で同等品質。しかし architecture refactor PR #337 で比較したところ、slim 版は以下の substantive な指摘を取りこぼした:

- MockK の `coVerify` / `coEvery` を非 suspend メソッドに誤用している箇所（複数）
- `StatusEditorViewModel` の `observeCursorPosition().first()` が `flatMapLatest { flow { } }` 内で再 fire しない correctness bug
- 無関係な CI coverage-report 変更が同 PR にバンドルされている scope 問題
- CLAUDE.md の example が antipattern を codify している点

救済として「頻出の見落とし角度」hint リストを追加したが、framework 固有（MockK, flatMapLatest 等）で rot しやすく、保守コストが常に発生する典型的なスキル肥大化トラップと判断して PR #11 ごと close。

教訓: **skill-creator の助言は一般的傾向であって、このリポジトリのこのスキルに当てはまるかは実測でしか分からない**。冗長で bad practice のラベルが貼れる構造でも、**結果が出るなら正しい**。

## 適用範囲

- 既存スキルの slim 化・簡素化 PR
- "trust the model" 的な指示省略 PR
- 出力フォーマット例や checklist の削除 PR

新規スキル作成時は skill-creator のガイダンスを出発点にして構わないが、実運用で成果が出ないと判明したら一般論より具体を優先する。

# Gradle / Maven (JVM) — Renovate Review Reference

## Gradle

### Manifest & lock files

- `build.gradle` / `build.gradle.kts`
- `settings.gradle` / `settings.gradle.kts`
- `gradle/libs.versions.toml` (Version Catalog)
- `gradle/verification-metadata.xml` (dependency verification)
- `buildSrc/` 配下の Gradle Kotlin DSL
- `gradle.lockfile` (dependency locking 有効時)
- `gradle-wrapper.properties` (Gradle 本体のバージョン)

Version Catalog を使っている repo では `libs.versions.toml` の diff が最も情報量が多い。

### 変更差分の抽出

```bash
git diff origin/<base>...HEAD -- \
  '**/build.gradle*' \
  '**/settings.gradle*' \
  gradle/libs.versions.toml \
  gradle/verification-metadata.xml \
  gradle/wrapper/gradle-wrapper.properties \
  '**/*.lockfile'
```

### Install / Resolve

```bash
./gradlew dependencies --write-locks   # dependency locking 有効時
./gradlew help                          # 単純な resolve
./gradlew build --dry-run               # タスク解決の確認
```

### 調査優先度

| カテゴリ | 優先度 | 調査内容 |
|---------|-------|---------|
| application dependencies | 高 | breaking change / 新 API |
| Gradle plugin (Kotlin / Android / AGP など) | 高 | DSL 変化、deprecation、AGP の minSdk 引き上げ等 |
| Gradle wrapper 本体 | 高 | incubating API の stable 化、削除された API |
| Kotlin compiler / KSP | 高 | 言語機能変化、IR 変更 |
| `annotationProcessor` / `kapt` / `ksp` | 中 | 生成コードの差分 |
| test 依存 (JUnit / MockK / Robolectric) | 中 | 新 matcher / test runner 変化 |

### よくある FOLLOW-UP 対応

- `gradle-wrapper.properties` 更新に伴う `distributionSha256Sum` 変化
- `libs.versions.toml` のエイリアス名変更（major bump で変わる場合あり）
- Gradle の deprecation（`--warning-mode all` で出ているものに対処）

### よくある ADOPT 候補

- Kotlin: context receivers、new type inference 採用
- AGP / Android: 新しい `ComponentExtension` API、build-variant API
- JUnit 5: parameterized test の新機能
- MockK: relaxed mock の改善、新 DSL

### 破壊的変更の頻出パターン

- Gradle 8.x → 9.x で削除された Configuration（`compile` 等の非推奨 → エラー化）
- Kotlin の language level 引き上げ、古い target JVM の削除
- AGP の minCompileSdk 引き上げ
- Kotlin Gradle Plugin の DSL 型変更

### 検証コマンド (典型)

```bash
./gradlew spotlessCheck ktlintCheck detekt
./gradlew test
./gradlew assembleDebug      # Android
./gradlew build --no-daemon  # CI 相当
```

## Maven

### Manifest & lock

- `pom.xml`
- parent POM がある場合はそれも確認
- Maven Enforcer Plugin の依存固定ルール

### 変更差分の抽出

```bash
git diff origin/<base>...HEAD -- '**/pom.xml'
```

### Install / Resolve

```bash
mvn -o dependency:resolve   # 既にダウンロード済みなら offline で
mvn dependency:tree         # 推移的依存の確認
```

### 検証コマンド (典型)

```bash
mvn verify
mvn test
mvn spotless:check
```

## JVM 共通の注意

- transitive dependency の変化も `dependency:tree` / `./gradlew dependencies` で確認する。Renovate が提示するのは直接依存のみでも、推移的に壊れることがある。
- BOM (`kotlin-bom`, `spring-boot-dependencies` 等) の更新は影響範囲が広い。
- Bytecode レベル変化は `javap -verbose` で差分確認（ライブラリ提供者側のテスト漏れで挙動が変わることがある）。

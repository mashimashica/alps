# バージョン管理

<p align="right">
  <a href="../versioning.md">英語</a> | <strong>日本語</strong>
</p>

ALPSは、`MAJOR.MINOR.PATCH`形式のVersionを用い、リポジトリ全体を一つのリリース単位として扱います。

## リリース単位

ALPSのReleaseには、Process Framework、ALPS規格、参照Process Skill、それらに付随する資源、ローカライズ、検証スクリプト、リポジトリレベルの文書および資産を含めます。

英語の記述を正本とします。日本語ローカライズは同じReleaseに含め、対応する英語の正本との整合を維持します。

個々の文書およびSkill Packageには、独立したVersionを付与しません。Releaseの正確な内容は、Git Tagと、そのTagが指すCommitによって特定します。

## 初期開発

`1.0.0`より前のVersionは、初期開発段階にあります。この期間は、次の規則を適用します。

- `0.1.1`のようなPATCH Releaseには、規範的意味、適用可能性、リポジトリ内のPath Contractまたは機械判読形式を変更しない修正を含めます。
- `0.2.0`のようなMINOR Releaseには、規範的意味、Conformance Criteria、必須構造、リポジトリ内のPath Contractまたは機械判読形式の追加、削除または変更を含めます。
- `0.2.0-rc.1`のようなPre-release Identifierは、対応するReleaseに至る前の候補版を識別します。

編集上の変更に見える場合でも、規範上の強さ、範囲、適用可能性または解釈を変更する変更は、PATCHではなくMINORとして扱います。`1.0.0`より前のMINOR Releaseは、以前のVersionと互換でない場合があります。

## 安定版

Version `1.0.0`は、最初の安定したCompatibility Boundaryを宣言します。`1.0.0`以降は、次の規則を適用します。

- MAJOR Releaseには、宣言されたCompatibility Boundaryと互換でない変更を含めます。
- MINOR Releaseには、そのBoundaryを破壊しない機能または規範内容の追加を含めます。
- PATCH Releaseには、後方互換な修正を含めます。

`1.0.0`をReleaseする前に、Compatibility Boundaryおよび移行について支援する範囲を文書化します。

## 正確な内容の特定

利用者は、必要に応じて次を記録します。

- ALPSのVersion
- Git Tag
- Commit SHA
- リポジトリ内のPath
- 個別Artifactをより厳密に識別する必要がある場合のContent Digest

公開したTagは不変とします。公開済みのTagを移動したり、異なる内容に再利用したりしません。ALPSの資産を別のリポジトリへ同期する利用者は、TagとCommit SHAの両方を固定します。

`main` Branchは、継続中の開発を表します。まだReleaseへ割り当てていない変更は、[CHANGELOG.md](../../CHANGELOG.md)の`Unreleased`へ記録します。

## リリース手順

1. Versionを選択し、`VERSION`を更新します。
2. 完了した項目を`CHANGELOG.md`の`Unreleased`から日付付きのRelease節へ移します。
3. `docs/releases/`にRelease Noteを用意します。
4. Release準備Pull Requestを`main`へMergeします。
5. Merge Commitに`vMAJOR.MINOR.PATCH`形式のTagを作成します。
6. 用意したRelease Noteを用いて、そのTagからGitHub Releaseを公開します。
7. Tagが意図したCommitを指していることを確認し、その不変性を維持します。

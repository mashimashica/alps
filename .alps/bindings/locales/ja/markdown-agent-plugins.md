# ALPS Markdown Repository and Agent Plugins Binding 1.0

> 本書は日本語Localizationである。基準となる英語版は[markdown-agent-plugins.md](../../../bindings/markdown-agent-plugins.md)であり、内容が矛盾する場合は英語版を優先する。

## 状態と権威

本書は、`alps-markdown-agent-plugins/1.0`で識別されるRepositoryおよびAgent Plugins向けEnvironment Bindingを定義する。

Process、Process Description、Process Instance、Process Model、Process Reference Model、Process View、Skill、Skill Package、Tailoring、Conformanceその他の概念の意味は、Process FrameworkおよびALPS Specificationが定める。本Bindingは、Markdown表現、Repository内の配置、解決動作、互換性宣言および機械的な事前検査規則を定める。本Bindingによって資産の意味または規範上の強さを変更してはならない。

## 1. 適用範囲

本Bindingは、ALPS Packageが既定または名前付きのProcess ModelもしくはProcess Reference Model、Process View、それらのLocalization、またはそれらを指すEnvironment Binding宣言をMarkdownで表す場合に適用する。

Process Model、Process Reference ModelおよびProcess Viewは、Skillとして独立に発動しない。Skill Packageは引き続き`skills/`配下に置き、基準となる`SKILL.md`を用いる。

## 2. 標準配置

| 資産 | 標準配置 | 個数 |
|---|---|---:|
| 既定Process ModelまたはProcess Reference Model | `.alps/MODEL.md` | 0..1 |
| 名前付きProcess ModelまたはProcess Reference Model | `.alps/models/<model-id>/MODEL.md` | 0..* |
| Process View | `.alps/views/<view-id>/VIEW.md` | 0..* |

`<model-id>`および`<view-id>`は小文字kebab-caseにする必要がある。`.alps/MODEL.md`が存在する場合、それをPackageの既定Model Entry Pointとする。既定Modelを`.alps/models/`へ重複して配置してはならない。ModelまたはViewを`skills/`配下へ置いてはならない。

## 3. Localization

基準言語はFrontmatterで宣言する。基準となる英語資産のLocalizationは、次に配置してよい。

```text
.alps/references/locales/<locale>/MODEL.md
.alps/models/<model-id>/references/locales/<locale>/MODEL.md
.alps/views/<view-id>/references/locales/<locale>/VIEW.md
```

Localizationは基準資産への相対Linkを示す必要がある。Identifier、Source、互換性要求、規範属性または意味を変更してはならない。

## 4. 共通Frontmatter

ModelまたはViewは、次の単純なScalar Keyを持つYAML Frontmatterで開始する必要がある。

| Key | 要求 |
|---|---|
| `kind` | `process-model`、`process-reference-model`または`process-view` |
| `id` | 小文字kebab-caseの資産Identifier |
| `name` | 人が読める資産名 |
| `version` | Semantic Version |
| `status` | `draft`、`active`、`deprecated`または`retired` |
| `binding` | `alps-markdown-agent-plugins/1.0` |
| `alps-requires` | 対応するALPS Version Range |
| `authoritative-language` | 基準資産のBCP 47言語Tag |

既定Modelは`default: true`も宣言する必要がある。Process Viewは、一つ以上のModel参照をComma区切りで示す`source-models`を宣言する必要がある。

## 5. Process ModelおよびProcess Reference Model表現

`MODEL.md`は、少なくとも`Purpose`、`Scope`、`Included Processes`、`Relationships`、`Selection and Application`、`Compatibility`および`Management`の各節を持つ必要がある。

`Included Processes`には次の列を持つ表を置く。

| Process ID | Process Name | Skill ID | Skill Source | Version or Resolution | Status | Role |
|---|---|---|---|---|---|---|

Skill Sourceは、`local:<package-relative-directory>`、`plugin:<plugin-id>/<skill-id>`または`uri:<absolute-uri>`で表す。Local Sourceは、基準となる`SKILL.md`を持つDirectoryへ解決できる必要がある。

`Relationships`には次の列を持つ表を置く。

| Provider Process | Output | Recipient Process | Input | Conditions |
|---|---|---|---|---|

この表は代表的なOutput/Input授受を表し、実行順序を定めない。

## 6. Process View表現

`VIEW.md`は、少なくとも`Purpose`、`Outcomes`、`Stakeholders and Concerns`、`Source Models`、`Included Activities and Tasks`、`Handoffs`、`Application Guidance`および`Compatibility and Conformance`の各節を持つ必要がある。

`Included Activities and Tasks`には次の列を持つ表を置く。

| View Element ID | Origin | Source Process | Source Element | Treatment | Guidance |
|---|---|---|---|---|---|

Treatmentは`selected`、`adapted`または`new`のいずれかにする必要がある。`selected`はSource要素と規範上の意味を維持する。`adapted`はSource Process Descriptionを変更せずに表示または適用を変更する。`new`はProcess View内だけに存在する。

`adapted`または`new`の要素は、管理されたTailoringまたは正式採用によってSource Processへ取り込まれない限り、Source ProcessへのConformanceに算入してはならない。

## 7. 互換性

互換性が成立するには、実行するALPS Versionが`alps-requires`を満たし、Binding Identifierが対応対象であり、必要なLocal Skill SourceとProcess ViewのSource Modelが解決される必要がある。互換性は適用の前提条件であり、特定Requestへの適合性を示す証拠ではない。

## 8. 解決

Resolverは、既定Model、名前付きModel、Process Viewの順に発見し、Metadataと互換性を確認し、Local Skill SourceをPackage Rootから解決する。Plugin Sourceは実行環境から渡されたPlugin Rootを用いて解決する。Resolverは、別のSkill、Process、Model、Process View、VersionまたはSourceを暗黙に代用してはならない。

## 9. Agent Plugins拡張

Portable Manifestは、`io.github.mashimashica.alps`という名前空間付きExtensionでBinding、Default Model Entry PointおよびALPS Versionを通知してよい。ExtensionはDiscovery Hintであり、`.alps/MODEL.md`が基準となるModel資産である。

依存PluginはInstall前提をDocumentに明記し、Model適用前に互換性の事前検査を行う必要がある。

## 10. 機械的事前検査

`scripts/check_model_view.py`はBinding構造を検査し、`scripts/resolve_model_view.py`はPackage単位のDiscovery、互換性評価およびSource解決を行う。

機械的検査だけでは、PurposeやOutcomeの意味的妥当性、Process選択の完全性、Outcome達成、Execution Conformanceまたは採用承認は成立しない。これらはALPS Reference ModelのProcessによって判断する。

## 11. 変更とRelease

Process Model、Process Reference ModelおよびProcess Viewは管理対象資産である。変更時は、含まれるProcess、Skill MappingおよびVersion、Output/Input授受、Source ModelおよびProcess View、Framework-level ControlおよびEnabler、互換性Range、Localizationならびに依存Packageへの影響を評価する必要がある。

変更されたModelまたはViewは、採用前に再検査および意味的Reviewを受ける必要がある。Release Candidateの準備と、Tag作成、Release公開またはRegistry公開は別のActionである。

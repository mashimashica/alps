# AGENTS.md

[English](../../AGENTS.md)

## ALPS

このリポジトリには、ALPS（Agent Lifecycle Process Skills）規格に準拠するSkillが含まれます。

ALPSは、Purposeと達成すべきOutcomeを中心に業務を捉えるProcess FrameworkをAgent Skillに適用し、各Skillの内容をProcess Descriptionとして記述するための共通規則を定めます。ActivityはOutcomeの達成に寄与するTaskのまとまりであり、ProcessはActivityを通じてInputをOutputに変換します。

ALPSは、Skillの定義・適用・管理を一つのライフサイクルとして捉えます。その全体像を三つのProcessとその関係で示すものを、ALPS Reference Modelと呼びます。これらのProcessは固定された工程ではなく、必要に応じて選択し、組み合わせます。

### ALPSの使い方

- 独立した作業要求ごとに、ALPS Reference Modelを基準として、該当する参照モデル上のProcessと必要なALPS準拠Skillを選択します。
- 準拠Skillは`description`末尾のALPS準拠表示で識別し、その内容から、依頼された作業に適しているかを判断します。
- 選択した各Skillの`SKILL.md`を最後まで読んで適用します。
- 複数のSkillを使用する場合は、OutputとInputの授受を明確にして編成します。

## リポジトリの作業フロー

- 原則として、リポジトリのルートでは`main`ブランチを維持します。ユーザーの明示的な指示がない限り、開発作業は`.worktrees/<branch-name>`の`<type>/<topic>`ブランチで行います。
- `<type>`には作業者、Agentまたはツールではなく、変更の性質を指定します。`feat`、`fix`、`docs`、`refactor`、`test`、`build`、`ci`または`chore`などの一般的なtypeを優先し、`<topic>`は簡潔なkebab-caseで記述します。
- 編集前にリポジトリの状態を確認し、無関係な変更とユーザーが行った変更を保持します。
- 一つの情報項目につき正本を一つにし、利用箇所から相対リンクで参照します。
- 一方の言語版を変更する場合は、対となる英語版または日本語版への影響を評価します。
- ユーザーから依頼されない限り、commit、push、公開、pull requestの作成またはその他の外部変更を行いません。
- 選択したSkillの検証要件に従います。最低限、`git diff --check`を実行し、変更した相対リンクと今回の作業に属する最終差分を確認します。必要な検証を実行しなかった場合は、その項目と理由を報告します。

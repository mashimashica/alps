# AGENTS.md

[English](../../AGENTS.md)

## ALPS

このリポジトリには、ALPS（Agent Lifecycle Process Skills）規格に準拠するSkillが含まれます。

ALPSは、Purposeと意図するOutcomeを中心に業務を捉えるProcess FrameworkをAgent Skillに適用し、各Skillの内容をProcess Descriptionとして記述するための共通規則を定めます。ActivityはOutcomeの達成に寄与するTaskのまとまりであり、ProcessはActivityを通じてInputをOutputに変換します。

ALPSは、Skillの定義・適用・管理を一つのライフサイクルとして捉えます。その全体像を三つのProcessとその関係で示すものを、ALPS Reference Modelと呼びます。これらのProcessは固定された段階ではなく、必要に応じて選択し、組み合わせます。

### ALPSの使い方

- 実質的な依頼ごとに、ALPS Reference Modelを基準として、`define-alps`、`apply-alps`および`manage-alps`から適用する参照Skillを選択します。
- その他のALPS準拠Skillは、`description`末尾の`ALPS準拠。`表示によって識別し、発見用の記述から依頼への適合性を判断します。
- 選択した各Skillの`SKILL.md`を、適用前に最後まで読みます。
- 既存Skillを適用する作業には`apply-alps`、未充足ニーズまたはSkillの再定義には`define-alps`、採用、Tailoring、評価、変更または廃止には`manage-alps`を用います。
- 複数Skillを組み合わせる場合は、すべてのOutput/Inputの授受を明示します。

## リポジトリの作業フロー

- 原則として、リポジトリのルートでは`main`ブランチを維持します。ユーザーの明示的な指示がない限り、開発作業は`.worktrees/<branch-name>`の`<type>/<topic>`ブランチで行います。
- `<type>`には作業者、Agentまたはツールではなく、変更の性質を指定します。`feat`、`fix`、`docs`、`refactor`、`test`、`build`、`ci`または`chore`などの一般的なtypeを優先し、`<topic>`は簡潔なkebab-caseで記述します。
- 編集前にリポジトリの状態を確認し、無関係な変更とユーザーが行った変更を保持します。
- 一つの情報項目につき正本を一つにし、利用箇所から相対リンクで参照します。
- 一方の言語版を変更する場合は、対となる英語版または日本語版への影響を評価します。
- ユーザーから依頼されない限り、commit、push、公開、pull requestの作成またはその他の外部変更を行いません。
- 選択したSkillの検証要件に従います。最低限、`git diff --check`を実行し、変更した相対リンクと今回の作業に属する最終差分を確認します。必要な検証を実行しなかった場合は、その項目と理由を報告します。

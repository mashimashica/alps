# AGENTS.md

[English](../../AGENTS.md)

## ALPS

このリポジトリには、ALPS（Agent Lifecycle Process Skills）規格に準拠する Skill が含まれます。

ALPS は、Purpose と達成すべき Outcome を中心に業務を捉える Process Framework を Agent Skill に適用し、各 Skill の内容を Process Description として記述するための共通規則を定めます。Activity は Outcome の達成に寄与する Task のまとまりであり、Process は Activity を通じて Input を Output へ変換します。

ALPS は、Skill の定義・適用・管理を一つのライフサイクルとして捉えます。その全体像を三つの Process とその関係で示すものを、ALPS Reference Model と呼びます。これらの Process は固定された工程ではなく、必要に応じて選択し、組み合わせます。

### ALPS の使い方

- 実質的なリクエストごとに、ALPS Reference Model を基準として、関係する Reference Model Process と必要な ALPS 準拠 Skill を選択します。
- 準拠 Skill は `description` 末尾の ALPS 準拠表示で識別し、その内容から作業への適合性を判断します。
- 選択した各 Skill の `SKILL.md` を最後まで読んで適用します。
- 複数の Skill を使用する場合は、Output/Input の授受を明確にして編成します。

## リポジトリの作業フロー

- 原則としてリポジトリルートは `main` のまま保ちます。ユーザーの明示的な指示がない限り、開発作業は `.worktrees/<branch-name>` の `<type>/<topic>` ブランチで行います。
- `<type>`には作業者、Agentまたはツールではなく、変更の性質を指定します。`feat`、`fix`、`docs`、`refactor`、`test`、`build`、`ci`または`chore`などの一般的なtypeを優先し、`<topic>`は簡潔なkebab-caseで記述します。
- 編集前にリポジトリの状態を確認し、無関係な変更とユーザーによる作業を保持します。
- 一つの情報項目につき正本を一つにし、利用箇所から相対リンクで参照します。
- 一方の言語版を変更する場合は、対となる英語版または日本語版への影響を評価します。
- ユーザーから依頼されない限り、commit、push、公開、pull request の作成またはその他の外部変更を行いません。
- 選択した Skill の検証要件に従います。最低限、`git diff --check` を実行し、変更した相対リンクと作業対象の最終差分を確認します。必要な検証を実行しなかった場合は、その項目と理由を報告します。

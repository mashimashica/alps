# ALPS — エージェントライフサイクルプロセススキル

[English](../../../README.md)

<p align="center">
  <img src="../../../assets/icon.svg" alt="ALPS icon" width="160">
</p>

ALPSは、作業の意味をプロセス記述として設計・レビューするための体系です。なぜ行うのか、どの観察可能な状態を成功とするのか、どの境界と詳細が必要なのかを明確にし、実行手段が変わっても理解できるようにします。

一度限りの依頼の明確化、既存Skillの改善、人やAgentが共同で行う作業の記述に使えます。再利用は有用ですが、反復される作業に限りません。**名称、目的、成果**から始め、理解・適用・評価に影響する場合に詳細を加えます。

## 導入

ALPSはClaude、Cursor、Codexのアダプターを持つ[Agent Plugins](https://agent-plugins.org/)パッケージです。対応クライアントからPlugin全体を導入します。[`plugins` CLI](https://www.npmjs.com/package/plugins)では次を使用できます。

```console
npx plugins add mashimashica/alps
```

導入後は対象クライアントを再読込みしてください。Skillから仕様への必須リンクのために、`spec/`を含むPluginルートの配置を保ちます。Skillフォルダだけのコピーでは正本が不足します。導入先で`design-process-description`が表示され、両仕様へのリンクを開けることを確認してください。

## 単一Skillの使い方

[design-process-description](../../../skills/design-process-description/references/locales/ja/SKILL.md)は、プロセス記述という同じ種類の成果物を作成・改訂・レビューします。自然言語で依頼するか、Hostの仕様に応じてSkill名を明示します。

```text
design-process-descriptionを使い、この一度限りの作業を、目的、観察可能な成功条件、必要な境界によって記述してください。

このプロセス記述をレビューしてください。不明確な成果、不必要な手段の固定、不足する参照、限界を識別し、書き換えずに指摘を返してください。

これらの作業記述について、共有する情報と変更の影響が明確になるよう改訂してください。この文脈に適用される承認は維持してください。
```

[最小テンプレート](../../../skills/design-process-description/references/locales/ja/SKILL-template.md)は、通常のAgent Skill frontmatterと、プロセスの三つの必須要素から始めます。[具体例](../../../skills/design-process-description/references/locales/ja/examples.md)では、最小の作業、一度限りの作業、固定成果物のない作業、必要な承認と順序、共有情報、ビュー、参照不足、成果を満たさない出力を扱います。

## 記述で明確になること

| 問い | 要素または区別 |
| --- | --- |
| なぜ作業を行うのか。 | Purpose（目的） |
| どの観察可能な状態が成功か。 | Outcome（成果） |
| 何を生成・更新するのか。 | Output（出力）。存在だけでは成功にならない。 |
| 何を調べ、変換するのか。 | Input（入力） |
| 何が作業を方向付け、制限し、支えるのか。 | Control（統制事項）、Constraint（制約）、Enabler（実行支援要素） |
| 何が正本で、何が局所的に変わるのか。 | 正本、参照、翻訳、文脈限定の変更 |
| レビューは何を示すのか。 | 実行結果や要求の充足とは別の、記述についての判断 |

活動、タスク、入力、出力、統制事項、制約、実行支援要素、開始基準、完了基準は任意の詳細です。必要な方法や順序は、関係する文脈に範囲を限定できます。複数プロセスは同じ情報を参照・更新でき、モデルやビューは目的と成果を重複保持せず、その記述へリンクできます。

ALPSは意味と設計の支援を提供します。実行、保存、承認、版管理は利用環境が担います。ALPS独自の管理手続きや認証体系を学ぶ必要はありません。

## 資源

| 資源 | 英語 | 日本語 |
| --- | --- | --- |
| プロセス記述の意味 | [Process Framework](../../../spec/process-framework.md) | [プロセスフレームワーク](../../../spec/locales/ja/process-framework.md) |
| Agent Skillへの対応付け | [ALPS Specification](../../../spec/ALPS-SPEC.md) | [ALPS Specification](../../../spec/locales/ja/ALPS-SPEC.md) |
| 設計Skill | [Skill](../../../skills/design-process-description/SKILL.md) | [Skill](../../../skills/design-process-description/references/locales/ja/SKILL.md) |
| 貢献とリポジトリ作業 | [CONTRIBUTING](../../../CONTRIBUTING.md)、[AGENTS](../../../AGENTS.md) | [CONTRIBUTING](CONTRIBUTING.md)、[AGENTS](AGENTS.md) |
| 版管理方針と予定する互換性の変更 | [Versioning](../../../docs/versioning.md)、[unreleased redesign](../../../docs/unreleased-redesign.md) | [版管理](versioning.md)、[未リリースの再設計](unreleased-redesign.md) |

## 版とライセンス

リポジトリ全体を一つの単位として版管理します。`VERSION`とmanifestは**0.5.0**のままであり、作業中の記述には次のMINOR向けの未リリースの破壊的再設計が含まれます。再設計がリリース済みであることや、導入済みの0.5.0パッケージに含まれることを意味しません。上記の互換性説明を参照してください。

明示された第三者資料を除き、本リポジトリは[Apache License 2.0](../../../LICENSE)で提供します。[NOTICE](../../../NOTICE)も参照してください。

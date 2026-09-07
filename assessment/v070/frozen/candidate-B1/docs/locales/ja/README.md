# ALPS — エージェントライフサイクルプロセススキル

[English](../../../README.md)

<p align="center">
  <img src="../../../assets/icon.svg" alt="ALPS icon" width="160">
</p>

ALPSは、仕事の意味を明確にし、それを実現するエージェント作業システムを設計するための体系です。なぜ行うのか、どの観察可能な状態を成功とするのか、どの境界と詳細が必要なのかを記述します。必要に応じて、その仕事を有効に遂行するエージェント・ツール・情報資源・環境を設計します。

一度限りの依頼の明確化、既存Skillの改善、人やAgentが共同で行う作業の記述に使えます。**名称、目的、成果**から始め、理解・適用・評価に影響する場合に詳細を加えます。

## 導入

ALPSはClaude、Cursor、Codexのアダプターを持つ[Agent Plugins](https://agent-plugins.org/)パッケージです。対応クライアントからPlugin全体を導入します。[`plugins` CLI](https://www.npmjs.com/package/plugins)では次を使用できます。

```console
npx plugins add mashimashica/alps
```

導入後は対象クライアントを再読込みしてください。Skill内とSkill間の必要なリンクを利用できるよう、両Skillとその参照資源、同梱する`examples/`を、Plugin全体の配置で保持します。導入先で`design-process-description`と`design-agent-work-system`が表示され、それぞれの参照リンクを開けることを確認してください。

## Skillの使い方

| Skill | 設計・評価の対象 |
| --- | --- |
| [design-process-description](../../../skills/design-process-description/references/locales/ja/SKILL.md) | プロセス記述の意味、関係、適用条件。 |
| [design-agent-work-system](../../../skills/design-agent-work-system/references/locales/ja/SKILL.md) | エージェント・ツール・情報資源・実行環境の構成と相互作用。依頼範囲で実装・検証も含む。 |

両Skillは作成・改訂・レビューを支援します。設計の基礎となる情報が十分であれば、どちらからでも使えます。仕事の記述には必要な方法や順序も含められます。システム設計はその共通の意味を参照し、再検討すべき前提を明らかにする場合があります。自然言語で依頼するか、Hostの仕様に応じてSkill名を明示します。

```text
design-process-descriptionを使い、この一度限りの作業を、目的、観察可能な成功条件、必要な境界によって記述してください。

このプロセス記述をレビューしてください。不明確な成果、不必要な手段の固定、不足する参照、限界を識別し、書き換えずに指摘を返してください。

design-agent-work-systemを使い、この仕事に必要な能力とインターフェースを設計してください。適切なツールを再利用し、不足する処理を実装し、代表例で構成を検証してください。

このエージェント作業システムをレビューしてください。判断と処理の配分、情報供給、ツールのインターフェース、有効性の証拠を評価し、変更せずに指摘を返してください。
```

[最小テンプレート](../../../skills/design-process-description/references/locales/ja/SKILL-template.md)は、通常のAgent Skill frontmatterと、プロセスの三つの必須要素から始めます。[具体例](../../../skills/design-process-description/references/locales/ja/examples.md)では、最小の作業、一度限りの作業、固定成果物のない作業、必要な承認と順序、共有情報、ビュー、参照不足、成果を満たさない出力を扱います。

[実働例](../../../examples/locales/ja/README.md)では、一つのサービス評価Skillに対する二つの設計責務を示します。スクリプトが測定を検証して比較を計算し、エージェントが文脈を評価して証拠を解釈します。[システム設計の具体例](../../../skills/design-agent-work-system/references/locales/ja/examples.md)では、既存ツール、状態を変更する操作、能力変化への適応も扱います。

## 記述で明確になること

| 問い | 要素または区別 |
| --- | --- |
| なぜ作業を行うのか。 | Purpose（目的） |
| どの観察可能な状態が成功か。 | Outcome（成果） |
| どの作業が成功に寄与するのか。 | Activities & Tasks（活動・タスク）。活動は関連するタスクをまとめ、タスクは個々の行為を記述する。 |
| 何を生成・更新するのか。 | Output（出力）。存在だけでは成功にならない。 |
| 何を調べ、変換するのか。 | Input（入力） |
| 何が作業を方向付け、制限し、支えるのか。 | Control（統制事項）、Constraint（制約）、Enabler（実行支援要素） |
| どの記述を基準とし、何が文脈内だけで変わるのか。 | 基準となる記述、参照、翻訳、文脈限定の変更 |
| レビューは何を示すのか。 | 実行結果や要求の充足とは別の、記述についての判断 |

活動、タスク、境界要素、開始基準、完了基準は、作業の説明に役立つ場合に追加します。フレームワークがそれらの意味と関係を定めているため、詳細を追加しても整合した記述を保てます。必要な方法や順序は、関係する文脈に範囲を限定できます。複数プロセスは同じ情報を参照・更新でき、モデルやビューは目的と成果を重複保持せず、その記述へリンクできます。

エージェント作業システムでは、処理能力を、責務とインターフェースが明確なツールとして提供します。確定した処理や組合せは実装し、解釈・選択・構成が状況に依存する箇所にエージェントの判断を残します。構成要素の検査とともに、実際の仕事を通じて構成を評価します。

ALPSは記述、設計原則、設計の支援を提供します。実行、保存、承認、版管理は利用環境が担います。

## 資源

| 資源 | 英語 | 日本語 |
| --- | --- | --- |
| プロセス記述の意味 | [Process Framework](../../../skills/design-process-description/references/process-framework.md) | [プロセスフレームワーク](../../../skills/design-process-description/references/locales/ja/process-framework.md) |
| 作業システムの設計 | [Design principles](../../../skills/design-agent-work-system/references/agent-work-system-design.md) | [エージェント作業システムの設計原則](../../../skills/design-agent-work-system/references/locales/ja/agent-work-system-design.md) |
| プロセス記述の設計 | [Skill](../../../skills/design-process-description/SKILL.md) | [Skill](../../../skills/design-process-description/references/locales/ja/SKILL.md) |
| エージェント作業システムの設計 | [Skill](../../../skills/design-agent-work-system/SKILL.md) | [Skill](../../../skills/design-agent-work-system/references/locales/ja/SKILL.md) |
| 貢献とリポジトリ作業 | [CONTRIBUTING](../../../CONTRIBUTING.md)、[AGENTS](../../../AGENTS.md) | [CONTRIBUTING](CONTRIBUTING.md)、[AGENTS](AGENTS.md) |
| 版管理方針とリリースノート | [Versioning](../../../docs/versioning.md)、[0.7.0](../../../docs/releases/0.7.0.md) | [版管理](versioning.md)、[0.7.0](releases/0.7.0.md) |

## 版とライセンス

リポジトリ全体を一つの単位として版管理します。リリースの範囲と互換性については、上記の版管理方針とリリースノートを参照してください。

明示された第三者資料を除き、本リポジトリは[Apache License 2.0](../../../LICENSE)で提供します。[NOTICE](../../../NOTICE)も参照してください。

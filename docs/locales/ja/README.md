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

## 設計思想

AIエージェントに仕事を任せるとき、すべてをモデルに委ねるのは避けるべきです。仕事の一部は確立した処理であり、他の部分は文脈に依存し、解釈・選択・構成を必要とします。

ALPSは二つの系譜を接続します。[プロセスフレームワーク](../../../skills/design-process-description/references/locales/ja/process-framework.md)は、システム／ソフトウェア工学のプロセス記述の考え方を背景に、仕事の意味——目的、観察可能な成果、必要な作業、適用条件——を、特定の実装から独立して記述します。もう一方はUnixに着想を得たエージェント設計です。確立した処理を明確なツールとして公開し、必要に応じて組み合わせます。SahajのKarun Japhetはこれを[「the agent is the shell」](https://www.sahaj.ai/the-unix-philosophy-for-agentic-coding/)と表現しています。Anthropicも、[コードで経路を定めるworkflowとモデルが進め方を決めるagent](https://www.anthropic.com/engineering/building-effective-agents)を区別し、[安定した操作をツールにまとめる設計](https://www.anthropic.com/engineering/writing-tools-for-agents)を示しています。

<p align="center">
  <img src="../../../assets/alps-agent-onion.svg" alt="Why / Whatが仕事の意味、Howが利用可能な手段、その間の判断をAgentが担う" width="900">
</p>

この図では、**Why / What**が仕事の意味、**How**が利用可能な手段、その**間の判断をAgentが担います**。エージェントは状況を解釈し、能力を選び、組み合わせ、方法を適応させます。既存の手段で足りなければ新しい手段を考案できます。確立した計算、変換、検査、安定した手順は、それらを確実に遂行できる適切な実装に委ねることが望まれます。

図は意図的に模式化しています。プロセス記述には、必要であればActivities、Tasks、方法、順序も含められます。分離しているのは「Whatだけ」と「Howだけ」ではなく、**記述する仕事の意味**と、**それを実現する構成**です。

> **仕事の意味を実装から独立して記述し、利用可能な手段を明らかにし、その間の判断をエージェントに委ねる。**

ALPSは、`design-process-description`で仕事を明確にし、`design-agent-work-system`でその仕事を実現する構成を設計します。二つは必須の直列工程ではありません。設計の基礎が十分ならどちらからでも使え、一方での発見が他方の再検討につながる場合があります。

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

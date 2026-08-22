---
kind: process-model
id: example-model
name: Process Model例
version: 0.1.0
status: draft
binding: alps-markdown-agent-plugins/1.0
alps-requires: ">=0.4.0 <0.5.0"
authoritative-language: en
default: false
---

> 本書はLocalization例である。実際のPackageでは、正本となる英語版`MODEL.md`への相対Linkを記載する。

# Process Model例

## Purpose

対象領域で、このProcess集合と関係を定義する理由を記述する。

## Scope

Modelの対象、適用文脈、除外事項および想定利用者を記述する。

## Included Processes

| Process ID | Process Name | Skill ID | Skill Source | Version or Resolution | Status | Role |
|---|---|---|---|---|---|---|
| example-process | Example Process | example-skill | local:skills/example-skill | repository release | adopted | PurposeまたはOutcomeを複製せず、Processの寄与を記述する。 |

## Relationships

| Provider Process | Output | Recipient Process | Input | Conditions |
|---|---|---|---|---|
| example-process | Example Output | another-process | Example Input | 代表的な授受。実行順序を意味しない。 |

## Selection and Application

適用文脈、対象Outcome、Control、Constraint、Riskおよび管理されたTailoring DecisionからProcessを選択する。各Processの正本となるProcess Descriptionを提供するSkillを解決する。本ファイルの記載順序は実行順序を定めない。

## Framework-Level Controls and Enablers

| Element | Classification | Scope | Exceptions | Tailoring |
|---|---|---|---|---|
| 方針または共通Capabilityの例 | ControlまたはEnabler | 対象ProcessまたはModel Scopeを宣言する。 | 例外または`none`を宣言する。 | Tailoringの可否を記述する。 |

## Process Views

| View ID | Source | Concern |
|---|---|---|
| example-view | .alps/views/example-view/VIEW.md | 横断的Concernを記述する。 |

## Compatibility

対応するALPS Version Range、Binding Identifier、外部Pluginの前提条件および未解決Sourceの取扱いを記述する。

## Known Gaps

未収録または候補のProcessと、それらを再検討するために必要な証拠を記録する。

## Management

Owner、採用状態、変更統制、Localization、再検証、非推奨化および廃止条件を記述する。

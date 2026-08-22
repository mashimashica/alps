---
kind: process-view
id: example-view
name: Process View例
version: 0.1.0
status: draft
binding: alps-markdown-agent-plugins/1.0
alps-requires: ">=0.4.0 <0.5.0"
authoritative-language: en
source-models: example-model
---

> 本書はLocalization例である。実際のPackageでは、正本となる英語版`VIEW.md`への相対Linkを記載する。

# Process View例

## Purpose

本Process Viewが可視化する横断的PurposeまたはConcernを記述する。

## Outcomes

- a) 一つの肯定的で観測可能な結果状態を記述する。
- b) Purpose達成に必要な別の結果状態を記述する。

## Stakeholders and Concerns

| Stakeholder | Concern |
|---|---|
| Stakeholder例 | 本Process Viewが扱う関心事項を記述する。 |

## Source Models

| Model ID | Source | Version or Resolution |
|---|---|---|
| example-model | .alps/models/example-model/MODEL.md | 互換性のある導入済みVersionまたはRepository Version |

## Included Activities and Tasks

| View Element ID | Origin | Source Process | Source Element | Treatment | Guidance |
|---|---|---|---|---|---|
| view-01 | source-model | example-process | Activity: Example Activity | selected | Source要素とその規範上の意味を維持する。 |
| view-02 | source-model | example-process | Task: Example Task | adapted | Adaptationを説明する。Source Process Descriptionは変更しない。 |
| view-03 | view | — | View-specific coordination | new | Process View固有要素とその適用条件を説明する。 |

## Handoffs

| Provider Process | Output | Recipient Process | Input | Conditions |
|---|---|---|---|---|
| example-process | Example Output | another-process | Example Input | Modelから選択した関係か、Process View固有の関係かを識別する。 |

## Application Guidance

表示順序を実行順序として扱わず、収録要素を選択、組合せおよび評価する方法を説明する。

## Compatibility and Conformance

対応するALPSおよびBinding Versionを記述する。selected、adaptedおよびnewの要素がSource ProcessへのConformanceへ与える影響を説明する。

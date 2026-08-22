---
kind: process-reference-model
id: alps-reference
name: ALPS Reference Model
version: 0.4.0
status: active
binding: alps-markdown-agent-plugins/1.0
alps-requires: ">=0.4.0 <0.5.0"
authoritative-language: en
default: true
---

> 本書は日本語Localizationである。基準となる英語版は[MODEL.md](../../../MODEL.md)であり、内容が矛盾する場合は英語版を優先する。

# ALPS Reference Model

## Purpose

本Process Reference Modelは、再利用可能なAgent Skillを定義、適用および管理するProcessとその関係を定義し、各Processの正本となるProcess Descriptionを提供するSkill Packageを識別する。

## Scope

本Modelは、ALPSにおけるAgent SkillおよびSkill PackageのLife Cycleを対象とする。ニーズ識別、Skill Descriptionの設計と検証、Processの選択と実行、複数ProcessのOrchestration、採用、Tailoring、Assessment、改善および廃止に適用する。

本Modelは固定されたPhase順序を定めない。各ProcessはConcurrency、IterationまたはRecursionによって適用してよい。

## Included Processes

| Process ID | Process Name | Skill ID | Skill Source | Version or Resolution | Status | Role |
|---|---|---|---|---|---|---|
| alps-definition | ALPS Definition Process | define-alps | local:skills/define-alps | repository release 0.4.0 | adopted | 識別されたニーズに対するSkill Description、Process ModelおよびProcess Viewを定義・検証する。 |
| alps-application | ALPS Application Process | apply-alps | local:skills/apply-alps | repository release 0.4.0 | adopted | Processを選択し、対応するSkillを解決し、Process Instanceを実行し、授受を構成する。 |
| alps-management | ALPS Management Process | manage-alps | local:skills/manage-alps | repository release 0.4.0 | adopted | 採用、互換性、Tailoring、Assessment、変更、Releaseおよび廃止を統制する。 |

## Relationships

| Provider Process | Output | Recipient Process | Input | Conditions |
|---|---|---|---|---|
| alps-definition | 検証済みSkill Description、Process ModelまたはProcess Viewおよび検証結果 | alps-management | 検証済み資産および採用証拠 | 採用前または意味的再定義後に用いる。 |
| alps-management | 管理されたSkillおよびSkill Package、Process Model、Process View、互換性判断、Tailoring Decisionおよび適用条件 | alps-application | 管理された資産および適用条件 | Processの選択または適用時に用いる。 |
| alps-application | 実行記録、判断記録、教訓および測定可能な結果 | alps-management | Assessmentおよび改善Input | Operation中およびReview Pointで用いる。 |
| alps-management | 変更、再定義または再検証要求 | alps-definition | 識別された変更ニーズおよび影響Scope | 意味変更または再検証が必要なときに用いる。 |

## Selection and Application

既存の管理されたProcessを対応するSkillによって選択・実行する場合は`apply-alps`を用いる。未充足ニーズ、またはProcess Description、Process ModelもしくはProcess Viewの定義・意味的再定義には`define-alps`を用いる。採用、互換性判断、Tailoring、Assessment、変更統制、Release管理または廃止には`manage-alps`を用いる。

選択とTimingは、適用文脈、対象Outcome、Control、Constraint、Riskおよび管理されたTailoring Decisionから決定する。表の順序は実行順序を定めない。

## Framework-Level Controls and Enablers

| Element | Classification | Scope | Exceptions | Tailoring |
|---|---|---|---|---|
| Process Framework | Control | ALPSが統制する全Process Description、Process Model、Process Reference ModelおよびProcess View | なし | 本Modelによって要求をTailoringしてはならない。 |
| ALPS Specification | Control | ALPSにおけるAgent Skillおよびその適用 | 矛盾時はProcess Frameworkを優先する。 | TailoringはALPS Management Processに従う。 |
| `alps-markdown-agent-plugins/1.0` | Control | 本Bindingを用いるRepository Process ModelおよびProcess View | 別Bindingを明示する資産 | Binding選択の変更は管理された互換性判断を通す。 |
| 管理されたRepositoryおよびResolver | Enabler | Binding資産のDiscovery、解決および適用 | 手動解決を宣言してよい。 | 同等のIdentityおよび互換性証拠を保持する場合に代替してよい。 |

## Process Views

既定Process Viewは必須ではない。反復利用される横断的構成は`.alps/views/<view-id>/VIEW.md`として表現してよい。

## Compatibility

本ModelはALPS `>=0.4.0 <0.5.0`およびBinding `alps-markdown-agent-plugins/1.0`を要求する。含まれるSkillはすべて本Package内にあり、基準となるRoot `SKILL.md`へ解決できる必要がある。

## Known Gaps

本ModelはDomain固有作業ではなくAgent SkillのLife Cycleを対象とする。Domain Pluginは、本Modelに表されたProcessへ依存するProcess ModelおよびProcess Viewを提供してよい。

## Management

`manage-alps`は、本Modelの採用、Version、互換性、Tailoring、Assessment、改善、非推奨化および廃止を管理する。含まれるProcess、Skill Mapping、関係、互換性またはFramework-level宣言の変更には、機械的事前検査および意味的再検証が必要である。

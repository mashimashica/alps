---
name: alps-reference-model
description: ALPSのDefinition、ApplicationおよびManagement Processを選択・構成・AssessmentするためのALPS Reference Modelを提供する。
metadata:
  alps.kind: process-reference-model
---

> 本書は日本語Localizationである。基準となる英語版は[SKILL.md](../../../SKILL.md)であり、矛盾する場合は英語版を優先する。

# ALPS Reference Model

## Purpose

ALPS Reference Modelは、Agent Lifecycle Process Skillsを定義、適用および管理するために必要なProcessを定義し、それらの関係を明示的な構造に配置する。

## Processes

### Define ALPS

Skill: `skill:mashimashica/alps#define-alps`

#### Purpose

本Processは、識別されたステークホルダーのニーズを満たす、評価可能で利用可能なSkill Descriptionを確立する。

#### Outcomes

- a) Skill化の対象となるニーズおよび想定利用文脈が識別されている。
- b) ProcessのPurpose、Outcomeおよび境界が、選定されたニーズと整合している。
- c) Skill Descriptionが、ALPSの適用される記述要求を満たしている。
- d) Skill Description内の要素および外部との授受が追跡可能である。
- e) 代表的な適用文脈におけるOutcomeの達成可能性が確認されている。
- f) Skillの採用可否を、欠陥および制限を含む証拠に基づいて判断できる状態にある。

### Apply ALPS

Skill: `skill:mashimashica/alps#apply-alps`

#### Purpose

本Processは、適用状況に適合するSkillが表現するProcessを単独で、または組み合わせて適用することにより、意図されたOutcomeを達成する。

#### Outcomes

- a) 適用状況のニーズおよび条件が識別されている。
- b) 適用するProcess、その正本記述を提供するSkillおよび適用形態が、根拠とともに決定されている。
- c) 適用されるControl、ConstraintおよびTailoringの決定が識別されている。
- d) Process Instanceの適用結果が、宣言された適用範囲、適用されるControl、ConstraintおよびTailoringの決定に適合している。
- e) 適用対象となるProcessの宣言されたOutcomeが達成されている。
- f) 必要なProcess間の授受が確立されている。
- g) Process構成の完全性および一貫性が確立されている。

### Manage ALPS

Skill: `skill:mashimashica/alps#manage-alps`

#### Purpose

本Processは、採用済みのALPS資産とその適用を統制し、適切なAgent Skill、Skill Package、Process ModelおよびProcess Viewを、統制され、意図する用途に適合した状態で継続的に利用可能にする。

#### Outcomes

- a) 採用、展開、Tailoring、Assessment、変更および廃止に関する方針と指針が確立されている。
- b) 採用されたAgent Skill、Skill Package、Process ModelおよびProcess Viewが、管理された状態で発見可能である。
- c) 管理対象の識別情報、状態、版、参照、変更および廃止が統制されている。
- d) Tailoringの判断および根拠と、適用されるControlおよびConstraintとの対応を追跡できる。
- e) Process適用の実績が、宣言した基準に照らして評価されている。
- f) 管理されたProcess ModelおよびProcess Viewの適合性が、宣言した基準に照らして評価されている。
- g) 改善機会が、証拠、教訓およびAssessment結果に基づいて優先順位付けされている。
- h) 決定された改善が実装されている。
- i) 実装された改善の影響を受ける対象が、必要に応じて再検証されている。

## Relationships

| Provider Process | Information | Recipient Process | Relationship |
| --- | --- | --- | --- |
| Define ALPS | Verified Skill DescriptionおよびVerification Evidence | Manage ALPS | Adoption、Registration、ChangeおよびReverification Decisionを支援する。 |
| Manage ALPS | 管理されたAgent Skill、Skill Package、Process ModelおよびProcess Viewに関する情報、Tailoring判断ならびに適用条件 | Apply ALPS | 適用に利用できる管理済み資産および条件を確立する。 |
| Apply ALPS | 実行および判断の記録、教訓ならびに測定可能な結果 | Manage ALPS | Assessment、改善、変更および廃止の判断を支援する。 |
| Manage ALPS | 変更要求、再定義要求および再検証要求 | Define ALPS | 正本の記述または表現を変更する必要がある場合に、定義、再定義または再検証を開始する。 |

関係はExecution Sequenceを規定しない。Application Situationに応じて三つのProcessをIterative、ConcurrentまたはRecursiveに適用できる。

## Application

本Agent SkillをActivateしてALPS Reference Modelを読み込む。Application Situationに応じて参照Processを選択・構成するには`apply-alps`を用いる。本Reference Modelの読込み自体はProcessをInvocationしない。

## Verification

本Process Reference Modelの表現は、参照する各Process Skillが解決でき、そのName、PurposeおよびOutcomesがここで表現した同じSemantic Centerを保持する場合に有効である。PurposeおよびOutcomesは基準となるProcess Descriptionと一致する必要がある。

## Conformance

本Process Reference ModelはProcess Reference Modelの表現としてAssessmentできる。Process Outcome ConformanceおよびProcess Task Conformanceは参照ProcessおよびそのProcess Instanceに関するClaimであり、本Agent SkillのActivationに関するClaimではない。

## Bundled Resources

- [Process Framework](../../../../../spec/process-framework.md)
- [ALPS Specification](../../../../../spec/ALPS-SPEC.md)

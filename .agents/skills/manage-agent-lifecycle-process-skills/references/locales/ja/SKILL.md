---
name: manage-agent-lifecycle-process-skills
description: Agent Skill、Skill Package、Skill ModelまたはSkill Viewについて、採用、発見可能性、変更、廃止、Tailoring、評価および改善を統制する。Skill資産の登録・更新・無効化、Tailoringの判断、実績の評価、改善候補の優先順位付け、変更の影響、周知または再検証を管理するときに使用する。新しいSkill Descriptionの定義だけ、または選択済みSkillの実行だけが目的の場合は、それぞれ定義Processまたは適用Processを使用する。ALPS準拠。
---

> 本書は日本語ローカライズである。基準となる英語版は[SKILL.md](../../../SKILL.md)であり、内容が矛盾する場合は英語版を優先する。

# Agent Lifecycle Process Skill Management

## Purpose

本Skillは、Skill資産およびその適用を統制し、適切なSkillを継続的に利用できる状態を維持する。

## Outcomes

本Skillの適用が成功すると、次の状態が成立している。

- a) Skillの管理、展開およびTailoringに用いる方針および指針が確立されている。
- b) 採用されたSkillが、管理された状態で発見可能である。
- c) Skillの変更および廃止が、関係する利用者への影響を含めて統制されている。
- d) Tailoringの判断および根拠と、適用されるControlおよびConstraintとの対応を追跡できる。
- e) Skillの実績および有効性が、定められた基準に照らして評価されている。
- f) 改善機会が、収集された教訓および評価結果に基づいて優先順位付けされている。
- g) 決定された改善が実現されている。

## Activities & Tasks

以下の見出し、Activity、Taskおよび番号の記載順序は、手順または実行順序を規定しない。Entry Criteriaは発動前の判定条件、Exit Criteriaは完了宣言前の判定条件であり、ControlsおよびConstraintsは記載位置にかかわらず適用される。各Activityは、必要に応じて並行的、反復的または再帰的に適用できる。

### Skill資産管理

このActivityは、Skill資産の採用、発見可能性、変更の周知、構成および廃止を管理する。主にa)、b)、c)およびg)のOutcomeに寄与する。

1. Skillを管理し展開する仕組みとTailoring指針を確立するのが望ましい。
2. FrameworkレベルのControlおよびEnablerを、適用範囲、例外およびTailoringの可否とともに宣言する必要がある。
3. Skillの採用に先立ち、定義ProcessのSkill検証による証拠を確認するのが望ましい。
4. 管理指針またはSkillに変更があったなら、その内容を関係する利用者に周知するのが望ましい。
5. ニーズがなくなったSkillまたは有害となったSkillを識別し、廃止する必要がある。
6. 廃止したSkillの記述を、参照のために保存してよい。
7. Skill Model内の重複および未充足領域を、継続的に識別するのが望ましい。
8. 標準として定めたSkillを複数の適用対象で一貫して用いるのが望ましい。
9. Skill Packageの構成要素を変更した場合、影響を受けるSkill Descriptionおよび付随資源を識別し、必要な再検証を行うのが望ましい。

### Skill Tailoring

このActivityは、SkillおよびSkill Modelを、特定の適用状況のニーズ、条件およびリスクに適合させる。主にa)およびd)のOutcomeに寄与する。

1. 適用に関係するリスク、要求事項、複雑性、利用可能な能力および資源、ならびに関連規格を識別する必要がある。
2. 適用条件、利用可能な専門知識および経験、ステークホルダーの期待または要求事項、ならびにリスク許容度を考慮し、候補となるSkillまたはライフサイクルモデルを評価する必要がある。
3. Tailoringの意思決定は、事実と証拠に基づくのが望ましい。
4. Outcome、Activity、Task、代表的なInputおよび代表的なOutputについて、削除、変更または追加を行ってよい。
5. Tailoringは、適用されるControlおよびConstraintに従う必要がある。
6. 影響を受ける当事者からInputを得る必要がある。
7. Activityを許容可能なリスク水準で実行できるよう、Skillの適用に必要な厳密さをリスクに基づいて設定するのが望ましい。
8. Tailoringの範囲を明確にするのが望ましい。前提および基準を特定し、意思決定の根拠を記録するのが望ましい。
9. 通常、リスクおよび適用状況の変化に応じ、適用期間全体を通じてTailoringを動的に継続する。
10. Tailoringの運用を適用期間中に繰り返し見直し、状況に応じて改めるのが望ましい。
11. Tailoring済みSkillの実績を継続的に評価する手段を確立するのが望ましい。
12. InputおよびOutputならびにそれらの授受を記述する詳細度を、Skill間の依存関係、並行的または反復的な適用、および品質リスクに応じて調整するのが望ましい。

### Skill評価・改善

このActivityは、Skillの実績および有効性を評価し、改善に結び付ける。主にe)、f)およびg)のOutcomeに寄与する。

1. Skillの実績と有効性について洞察を得るための測定指標を設けるのが望ましい。
2. 教訓を、Skillの実行期間全体を通じて特定し、収集するのが望ましい。
3. 事前に定義した節目においても教訓を収集するよう計画するのが望ましい。
4. 測定指標を分析して、Skillの有効性を判定するのが望ましい。
5. Skillの強みと弱みを評価し、レビューおよび監査を設けるのが望ましい。
6. Skillの実績を、定められた基準、適用規格または比較対象と照合し、改善機会を特定してよい。比較にあたっては、実績、有効性、適合性、便益および費用を分析するのが望ましい。
7. 改善機会を継続的に特定し、優先順位を付けて実現するのが望ましい。
8. 教訓を収集して対応に結び付ける仕組みと、改善に向けた変更候補を分析する仕組みとを設けるのが望ましい。
9. 変更されたSkillは、定義ProcessのSkill検証による確認を経るのが望ましい。
10. Skill間の授受に起因する不整合および再作業を、改善機会の識別に用いてよい。

## Inputs

次に示すのは代表的なInputであり、唯一の実行方法を規定するものではない。

検証済みのSkill Description、変更要求、適用状況、Tailoring指針、影響当事者からのInput、実行および意思決定の記録、教訓ならびに測定結果。

## Outputs

次に示すのは代表的なOutputであり、唯一の実行方法を規定するものではない。

管理されたSkill資産、Tailoring済みSkill、Tailoringの決定および根拠、評価結果、優先順位付けされた改善機会、Skillへの変更要求ならびに廃止の決定。

## Entry Criteria

- Skill資産の採用、変更、廃止、Tailoring、評価または改善に関する管理契機が識別されている。
- 管理対象のSkill資産、適用範囲、基準版または評価期間を識別できる。
- 適用される主要なControlおよびConstraintを確認できるか、その不足を未解決事項として記録できる。
- 不可逆的または高影響の管理行為が想定される場合、Decision Gateの要否および必要な権限を判断できる。

## Exit Criteria

- 適用範囲、基準および適用したActivityが記録されている。
- 管理判断、その根拠、前提および証拠が追跡可能である。
- 変更、廃止またはTailoringの影響、関係者への周知および再検証の要否が記録されている。
- 宣言したOutcomeの達成状況と未解決リスクが判定されている。
- 後続の定義Processまたは適用Processへの授受が明示されている。

## Controls

- Process FrameworkとALPSを適用する必要がある。両者が矛盾する場合はProcess Frameworkを優先する必要がある。
- 規範語とその意味は、Process Frameworkの定めによる。本Skillはこれらを再定義しない。
- 適用される法令、規制要求、方針、契約、情報管理要求、安全要求、および利用者が指定した変更範囲に従う必要がある。
- FrameworkレベルのControlおよびEnablerには、適用範囲、例外およびTailoringの可否を明示する必要がある。
- 実行環境において有効なSkill管理、変更、保持、参照、復旧および削除に関するControlおよびConstraintに従う必要がある。これらの要求はALPS自体ではなく実行環境に由来し、適用される場合は宣言した実行範囲および評価の一部となる。

## Constraints

- 一般Skillの規範部分に、特定の実行主体、ツール、技法、測定指標または固定された実行順序を要求してはならない。
- Agent、モデル、ツール、管理システムおよび実行環境をInputとして扱ってはならない。これらはEnablerとして扱う必要がある。
- 不可逆的または高影響の採用、変更、廃止またはTailoringに先立って、Decision Gateを適用するのが望ましい。適用されるControlまたはConstraintがDecision Gateの通過を要求する場合、その通過前に当該行為を実行してはならない。
- Conformanceまたは有効性の判定は、十分な証拠に基づく必要がある。

## Enablers

- 管理されたSkill台帳、版、構成および変更履歴
- 関係者、業務領域およびリスク領域の専門知識
- Skillの作成、検証、検索、版比較、保存、周知および評価を支援するAgentまたはツール
- 独立したレビューまたは監査能力

## Conformance

- Conformanceを主張する場合、対象、適用範囲、およびOutcome、Taskまたは双方のどれを基準にするかを明示する必要がある。
- OutcomeへのFull Conformanceでは、Outcomes節に列挙したすべてのOutcomeの達成を示す必要がある。
- TaskへのFull Conformanceでは、ActivityおよびTaskにおいて「〜する必要がある」または「〜してはならない」で示されたすべての要求事項の充足を示す必要がある。
- 選択したFull Conformance基準を満たさない場合にTailored Conformanceを主張するには、TailoringしたProcessとその適用範囲を宣言し、その適用範囲に残されたOutcomeおよびActivity・Taskに含まれる要求事項の充足を示す必要がある。
- 個別のActivityについてのみ、独立したProcess Outcome Conformanceを主張してはならない。
- CapabilityはConformanceとは分けて評価する必要がある。

## Interfaces & Traceability

| 提供元 | 情報項目 | 受領先 |
|---|---|---|
| 定義Process | 検証済みSkill Descriptionおよび検証結果 | 本管理Process |
| 本管理Process | 管理されたSkill情報、Tailoringの決定および適用条件 | 適用Process |
| 適用Process | 実行・意思決定の記録、教訓および測定可能な結果 | 本管理Process |
| 本管理Process | 変更要求、再定義要求および再検証要求 | 定義Process |

複数のSkillを構成して適用する場合、提供側のOutputと受領側のInputとの対応を明示する必要がある。授受する情報項目の名称、意味および適用範囲は、提供側と受領側で整合させるのが望ましい。同一の情報項目が複数のSkillによって変更される場合、その情報項目の整合性、状態および変更の取扱いを、品質リスクに応じて定める必要がある。

## Bundled Resources

この節は参考情報であり、特定の実行方法を要求しない。

- [management-records.md](management-records.md)は、資産管理、Tailoring、評価・改善、Decision Gate、変更、廃止および授受のための、人間可読な任意ブロックを提供する。必要なブロックを汎用Process Instance Recordに含めるか、参照される管理Outputとして別に保持できる。

## Common Approach

この節は参考情報であり、規範上の強さを持たない。

- 管理契機を資産管理、Tailoring、評価・改善のいずれか一つ以上に分類すると、必要な証拠と受領先を整理しやすい。
- 対象、基準版、適用範囲、Control、Constraint、関係者および証拠を一つの管理記録で対応付けると、変更の影響を追跡しやすい。
- 不可逆的または高影響の管理判断では、適用状況とリスクに応じたDecision Gateを用いるとよい。
- 廃止では、新規発動、依存先・利用者への影響、必要な参照記録の保持および復旧条件を、適用状況に応じて確認するとよい。
- 適用Processから受け取る監督の記録（承認および介入、検出されなかった失敗、不十分だった説明またはログ、automation biasの兆候、監督者の負荷、Decision Gateの過不足）は、Skill評価・改善へのInputとして利用できる。

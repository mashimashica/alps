---
name: manage-alps
description: Agent Skill、Skill Package、Process ModelまたはProcess Viewについて、採用、発見可能性、変更、廃止、Tailoring、Assessmentおよび改善を統制する。登録、更新、無効化、Tailoringの判断、Assessment、改善候補の優先順位付け、変更影響、周知または再検証を管理するときに使用する。正本となるProcess Descriptionを定義または再定義するときは定義Processを用い、選択したProcessを適用するときは適用Processを用いる。ALPS準拠。
---

> 本書は日本語ローカライズである。基準となる英語版は[SKILL.md](../../../SKILL.md)であり、内容が矛盾する場合は英語版を優先する。

# Agent Lifecycle Process Skill Management

## Purpose

本Processは、採用済みのALPS資産とその適用を統制し、適切なAgent Skill、Skill Package、Process ModelおよびProcess Viewを、統制され、意図する用途に適合した状態で継続的に利用可能にする。

## Outcomes

本Processの成功によって、次の状態が成立している。

- a) 採用、展開、Tailoring、Assessment、変更および廃止に関する方針と指針が確立されている。
- b) 採用されたAgent Skill、Skill Package、Process ModelおよびProcess Viewが、管理された状態で発見可能である。
- c) 管理対象の識別情報、状態、版、参照、変更および廃止が統制されている。
- d) Tailoringの判断および根拠と、適用されるControlおよびConstraintとの対応を追跡できる。
- e) Process適用の実績が、宣言した基準に照らして評価されている。
- f) 管理されたProcess ModelおよびProcess Viewの適合性が、宣言した基準に照らして評価されている。
- g) 改善機会が、証拠、教訓およびAssessment結果に基づいて優先順位付けされている。
- h) 決定された改善が実装されている。
- i) 実装された改善の影響を受ける対象が、必要に応じて再検証されている。

## Activities & Tasks

以下の見出し、Activity、Taskおよび番号の記載順序は、手順または実行順序を規定しない。Entry Criteriaは発動前の判定条件、Exit Criteriaは完了宣言前の判定条件であり、ControlsおよびConstraintsは記載位置にかかわらず適用される。各Activityは、必要に応じて並行的、反復的または再帰的に適用できる。

### ALPS資産管理

このActivityは、管理対象となるALPS資産の採用、発見可能性、参照整合性、変更の周知、構成および廃止を管理する。主にa)、b)、c)、h)およびi)のOutcomeに寄与する。

1. Agent Skill、Skill Package、Process ModelおよびProcess Viewを管理し展開する仕組みと、Tailoring指針を確立するのが望ましい。
2. FrameworkレベルのControlおよびEnablerを、適用範囲、例外およびTailoringの可否とともに宣言する必要がある。
3. 正本となる記述または表現を採用する前に、ALPS定義Processによる検証証拠を確認するのが望ましい。
4. 採用対象ごとに、権限、版または状態、適用可能性、参照および管理状態を記録するのが望ましい。
5. Process Description、Process Model、Process Viewおよび付随資源の間にある必須参照について、解決可能性を検査する必要がある。
6. 管理指針または管理対象の変更を、影響を受ける利用者および依存対象へ周知するのが望ましい。
7. ニーズがなくなった管理対象または有害となった管理対象を、廃止候補として識別する必要がある。
8. 廃止候補として識別した対象を、統制された判断によって廃止する必要がある。
9. 廃止した記述または表現は、その状態と利用条件を明示したまま参照用に保持してよい。
10. 適用されるProcess ModelおよびProcess View内の重複、未充足領域および不整合な関係を継続的に識別するのが望ましい。
11. Skill Packageの構成要素または参照対象が変更された場合、影響を受ける記述、表現および付随資源を識別するのが望ましい。
12. 再検証が必要な記述、表現および付随資源を再検証する必要がある。

### Tailoring

このActivityは、適用されるProcessおよびProcess Modelを、特定の適用状況のニーズ、条件およびリスクに適合させる。主にa)およびd)のOutcomeに寄与する。

1. 適用に関係するリスク、要求事項、複雑性、利用可能な能力および資源、ならびに関連規格を識別する必要がある。
2. 適用条件、利用可能な専門知識、ステークホルダーの期待およびリスク許容度に照らして、候補となるProcessまたはライフサイクルモデルを評価する必要がある。
3. Tailoringの意思決定は、事実と証拠に基づくのが望ましい。
4. 宣言したTailoring範囲内で、Outcome、Activity、Task、代表的なInputおよび代表的なOutputを削除、変更または追加してよい。
5. Tailoringは、適用されるControlおよびConstraintに従う必要がある。
6. 影響を受ける当事者からInputを得る必要がある。
7. Process適用の厳密さをリスクに応じて設定するのが望ましい。
8. Tailoringの範囲を記録するのが望ましい。
9. Tailoringの前提を記録するのが望ましい。
10. Tailoringの基準を記録するのが望ましい。
11. Tailoringの判断ごとに根拠を記録するのが望ましい。
12. 適用期間を通じてTailoringを見直すのが望ましい。
13. 条件が変化した場合はTailoringを改めるのが望ましい。
14. TailoringしたProcessの実績を評価する手段を確立するのが望ましい。
15. Input、Outputおよびそれらの授受を記述する詳細度を、依存関係、Concurrency、Iterationおよび品質リスクに応じて調整するのが望ましい。

### Assessment・改善

このActivityは、管理対象をAssessmentし、その結果を統制された改善へ結び付ける。主にe)、f)、g)、h)およびi)のOutcomeに寄与する。

1. Assessment対象に応じてAssessment基準を確立するのが望ましい。
2. Process適用を、関係する実績、有効性、Outcome、TaskおよびConformanceの証拠を用いて評価するのが望ましい。
3. Process Modelを、網羅性、関係、一貫性、適用可能性および参照するProcess Descriptionの解決可能性について評価するのが望ましい。
4. Process Viewを、関心事またはPurposeへの適合性、出典の整合性、適用指針および宣言Outcomeの達成について評価するのが望ましい。
5. 教訓を、適用期間全体および計画したレビューポイントで収集するのが望ましい。
6. 強み、弱み、未充足領域、重複および不整合な授受を評価するのが望ましい。
7. 改善機会を継続的に識別するのが望ましい。
8. 利用可能な証拠に応じて改善機会を優先順位付けするのが望ましい。
9. 決定された改善を実装するのが望ましい。
10. 変更候補が、依存対象、参照、利用者およびConformance主張へ及ぼす影響を分析するのが望ましい。
11. 変更された正本の記述または表現を、再検証のためにALPS定義Processへ引き渡すのが望ましい。

## Inputs

次に示すのは代表的なInputであり、唯一の実行方法を規定するものではない。

検証済みのSkill Descriptionおよびその他の検証済みALPS表現、変更要求、適用状況、Tailoring指針、影響当事者からのInput、Process Instanceおよび判断の記録、教訓、測定結果ならびに参照整合性の所見。

## Outputs

次に示すのは代表的なOutputであり、唯一の実行方法を規定するものではない。

管理されたAgent Skill、Skill Package、Process ModelおよびProcess View、Tailoringの判断および根拠、Assessment結果、優先順位付けされた改善、変更または再定義の要求、再検証要求ならびに廃止判断。

## Entry Criteria

- 採用、変更、廃止、Tailoring、Assessmentまたは改善に関する管理契機が識別されている。
- 管理対象、適用範囲、基準版またはAssessment期間を識別できる。
- 適用される主要なControlおよびConstraintを確認できるか、その不足を未解決事項として記録できる。
- 不可逆的または高影響の管理行為が想定される場合、Decision Gateの要否および必要な権限を判断できる。

## Exit Criteria

- 管理対象、適用範囲、基準および適用したActivityが記録されている。
- 管理判断、その根拠、前提および証拠が追跡可能である。
- 参照および変更の影響、周知の必要性ならびに必要な再検証が判定されている。
- 適用されるOutcomeの達成状況および未解決リスクが判定されている。
- 後続の定義Processまたは適用Processへの授受が明示されている。

## Controls

- Process FrameworkとALPSを適用する必要がある。両者が矛盾する場合はProcess Frameworkを優先する必要がある。
- 適用される法令、規制要求、方針、契約、情報管理要求、安全要求、および利用者が指定した変更範囲に従う必要がある。
- FrameworkレベルのControlおよびEnablerには、適用範囲、例外およびTailoringの可否を明示する必要がある。
- 管理、変更、保持、参照、復旧および削除に関する実行環境の要求に、その宣言された範囲内で従う必要がある。

## Constraints

- 一般Process Descriptionの規範部分に、特定の実行主体、ツール、技法、測定指標または固定された実行順序を要求してはならない。
- Agent、モデル、ツール、管理システムおよび実行環境をInputとして扱ってはならない。これらはEnablerとして扱う必要がある。
- 不可逆的または高影響の採用、変更、廃止またはTailoringに先立って、Decision Gateを適用するのが望ましい。
- Conformance、有効性または適合性の判定は、十分な証拠に基づき、その対象を識別する必要がある。

## Enablers

- 管理された台帳、版、構成、参照および変更履歴
- ステークホルダー、業務領域、Processおよびリスクの専門知識
- 検証、検索、参照解決、版比較、保持、周知およびAssessmentを支援するAgentまたはツール
- 独立したレビューまたは監査能力

## Conformance

- Conformance主張は、その対象、適用範囲、基準および証拠を識別する必要がある。
- Process Outcome ConformanceまたはTask Conformanceは、適用されるProcessおよびProcess Instanceだけを対象とする。
- Process ModelまたはProcess ViewのAssessmentを、Process Outcome ConformanceまたはTask Conformanceとして表現してはならない。
- Tailored Conformanceでは、TailoringしたProcessと適用範囲を宣言し、その範囲で選択したConformance基準の充足を示す必要がある。
- CapabilityはConformanceとは分けて評価する必要がある。

## Interfaces & Traceability

| 提供元 | 情報項目 | 受領先 |
|---|---|---|
| 定義Process | 検証済みProcess Descriptionまたはその他の検証済みALPS表現 | 本管理Process |
| 本管理Process | 管理対象の情報、参照、Tailoringの判断および適用条件 | 適用Process |
| 適用Process | Process Instanceの証拠、判断、教訓および測定可能な結果 | 本管理Process |
| 本管理Process | 変更要求、再定義要求および再検証要求 | 定義Process |

提供側のOutputと受領側のInputは、識別可能な意味、範囲、状態、権限および品質条件を保つ必要がある。

## Shared Normative References

この節は参考情報であり、規範上の強さを持たない。

- Process FrameworkまたはALPSの解釈、競合解決、規範属性、ConformanceまたはTailoringに正本が必要な場合は、リポジトリ共通の[Process Framework](../../../../../.alps/spec/locales/ja/process-framework.md)および[ALPS Specification](../../../../../.alps/spec/locales/ja/ALPS-SPEC.md)を参照する。これらはリポジトリ共通の規範資産であり、本Skill Packageが所有する文書ではない。

## Bundled Resources

この節は参考情報であり、特定の実行方法を要求しない。

- [management-records.md](management-records.md)は、資産管理、Tailoring、評価・改善、Decision Gate、変更、廃止および授受のための、人間可読な任意ブロックを提供する。必要なブロックを汎用Process Instance Recordに含めるか、参照される管理Outputとして別に保持できる。

## Common Approach

この節は参考情報であり、規範上の強さを持たない。

- 記録またはAssessment基準を選ぶ前に、管理契機を対象と必要な判断によって分類する。
- 管理対象、基準版、適用範囲、Control、Constraint、影響当事者、参照および証拠を、影響を追跡できる状態に保つ。
- 不可逆的または高影響の行為には、その結果および可逆性に適したDecision Gateを用いる。

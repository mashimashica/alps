---
name: define-agent-lifecycle-process-skills
description: Skillニーズを識別し、ALPSおよびProcess Frameworkに適合する評価可能なSkill Descriptionを設計・検証する。新しいSkillの構想、既存Skillの再定義、Purpose・Outcome・Activity・Taskの設計、記述適合性レビュー、代表的文脈での試行、トレーサビリティまたは採用判断の証拠を求められたときに使用する。採用、変更の統制または廃止だけを扱う場合は管理Processを使用する。ALPS準拠。
---

> 本書は日本語ローカライズである。基準となる英語版は[SKILL.md](../../../SKILL.md)であり、内容が矛盾する場合は英語版を優先する。

# Agent Lifecycle Process Skill Definition

## Purpose

本Skillは、識別されたステークホルダーのニーズを満たす、評価可能で利用可能なSkill Descriptionを確立する。

## Outcomes

本Skillが成功すると、次の状態が成立している。

- a) Skill化の対象となるニーズおよび想定利用文脈が識別されている。
- b) SkillのPurpose、Outcomeおよび境界が、選定されたニーズと整合している。
- c) Skill Descriptionが、ALPSの適用される記述要求を満たしている。
- d) Skill Description内の要素および外部との授受が追跡可能である。
- e) 代表的な適用文脈におけるOutcomeの達成可能性が確認されている。
- f) Skillの採用可否を、欠陥および制限を含む証拠に基づいて判断できる状態にある。

## Activities & Tasks

以下の見出し、Activity、Taskおよび番号は、内容を読みやすく示すためのものであり、手順または実行順序を定めない。Entry Criteriaは発動前の判定条件、Exit Criteriaは完了宣言前の判定条件であり、ControlsおよびConstraintsは記載位置にかかわらず適用される。IterationおよびConcurrencyを、適用状況に応じて用いる。必要に応じて再設計する。

### Skillニーズ識別

このActivityは、Skillとして扱う候補を探索し、定義対象とするニーズを選定する。主にOutcomes a)およびb)に寄与する。

1. 通常、反復的に生じるTask、収集された教訓および失敗事例から、Skill化の機会を収集する。
2. 想定される利用者およびステークホルダーの期待を識別する必要がある。
3. 既存のSkill資産を調査し、重複、隣接領域または未充足領域を識別するのが望ましい。
4. 候補ごとに、期待される便益、リスクおよび費用を評価するのが望ましい。
5. 選定および見送りの根拠を記録するのが望ましい。
6. 選定にあたって、利用頻度または影響度による優先順位付けを行ってよい。

### Skill設計

このActivityは、選定されたニーズを満たすSkill Descriptionの構造および内容を定める。主にOutcomes b)、c)およびd)に寄与する。

1. Skillの境界を、主要なOutputおよびOutcomeに基づいて定める必要がある。
2. 他のSkillへの依存を、実行可能な限り縮小する必要がある。
3. 二層構造（発見層および実行層）を採るのが望ましい。
4. 詳細に扱うことが有用な重要なActivityは、別のSkillとして分離してよい。
5. Name、PurposeおよびOutcomeを、適用される記述規則に従って記述する必要がある。
6. 各Taskは、一つ以上のOutcomeの達成を支援する個別の行為を表すことを主たる機能とし、その行為の対象と動作を判別できるように記述する必要がある。
7. 各記述を、その主たる機能に対応するSkill要素として分類する必要がある。
8. 各Taskに、要求事項、推奨事項、許容される行為または通常実施される行為の規範属性を付与する必要がある。
9. 適用方法に関する指針は、Common Approachおよび実務上のヒントとして分離して記述するのが望ましい。
10. Activityの集合が全Outcomeを網羅し、Purposeを満たすことを確認する必要がある。
11. TaskとOutcomeとのあいだの対応関係を識別するのが望ましい。
12. Skill Discovery Descriptionに、Skillが行うこと、使用する状況および適用可否の判別に必要な情報を記述する必要がある。ALPSの記述適合を主張するSkill Discovery Descriptionは、`ALPS準拠。`で終わる必要がある。
13. 代表的なInputおよびOutputを示す場合、他のSkillまたはProcessとの主要な対応関係を、必要に応じて識別するのが望ましい。
14. Skill Packageを構成する場合、付随資源の必要性、役割および利用条件を識別する必要がある。

### Skill検証

このActivityは、Skill Descriptionの記述適合性と、意図したOutcomeの達成可能性を確認する。主にOutcomes c)、d)、e)およびf)に寄与する。

1. 合意された基準を用いて、Skill Descriptionをレビューする必要がある。
2. 各Taskが、一つ以上のOutcomeの達成を支援する個別の行為を表すことを主たる機能とし、その行為の対象と動作を判別できることを確認する必要がある。
3. 各記述の要素分類が、その主たる機能と整合していることを確認する必要がある。
4. 規範属性の判別可能性を確認する必要がある。
5. 一般Skillを検証する場合、その規範部分が特定の方法、技法、ツールまたは実行順序を要求していないことを確認する必要がある。
6. 発見層と実行層を用いる場合、両者の記述が整合していることを確認する必要がある。
7. レビューには、Skillの起草者から独立した観点を取り入れるのが望ましい。
8. 代表的な適用文脈における試行によって、Outcomeの達成可能性を評価するのが望ましい。
9. Skill Discovery Descriptionを含む発見層の情報だけで適用可否を判別できるかを評価するのが望ましい。
10. 想定利用文脈の境界事例を評価に含めてよい。
11. 検出された欠陥を記録し、期限と完了条件を伴う対応を設定するのが望ましい。
12. 欠陥処置が完了したことを、採用の判断（Decision Gate）に先立って確認するのが望ましい。
13. Skill Descriptionが他のSkillまたはProcessとの授受を示す場合、Outputが想定される受領側のInputとして利用可能であるかを評価するのが望ましい。
14. Skill Packageを検証対象に含める場合、基準となるSkill Descriptionの存在、必須の参照先を対象環境から特定して取得できること、付随資源の役割および利用条件、ならびにSkill Descriptionと付随資源との整合性を評価する必要がある。

## Inputs

次に示すのは代表的なInputであり、唯一の実行方法を規定するものではない。

ステークホルダーの期待、教訓、実行実績に関する情報、適用されるControlおよびConstraint、既存のSkill資産に関する情報、検証基準ならびに代表的な適用文脈。

## Outputs

次に示すのは代表的なOutputであり、唯一の実行方法を規定するものではない。

選定されたSkillニーズおよび選定根拠、検証済みのSkill Description、要素間対応の記録、検証結果ならびに欠陥処置の記録。

## Entry Criteria

- Skill化または再定義を検討するニーズ、問題、教訓または変更要求が利用可能である。
- 想定利用者、ステークホルダーおよび代表的な利用文脈を識別できる。
- 適用されるControl、Constraintおよび上位規範を識別できるか、その不足を未解決事項として記録できる。
- Skill Descriptionだけを対象にするか、付随資源を含むSkill Packageも対象にするかを識別できる。

## Exit Criteria

- 選択したConformance基準に対する達成状況が、観察可能な証拠とともに判定されている。
- 未解決の欠陥、制限、前提および境界事例が記録されている。
- 検証済みSkill Description、トレーサビリティおよび検証結果を、採用判断または管理側に引き渡せる。
- 完了は採用または公開を意味しない。採用可否を判断できる状態を意味する。

## Controls

- Process FrameworkとALPSを適用する必要がある。両者が矛盾する場合はProcess Frameworkを優先する必要がある。
- 規範語とその意味は、Process Frameworkの定めによる。本Skillはこれらを再定義しない。
- Process FrameworkまたはALPSの要求解釈、規範属性の確認、Conformance判定または本Skillの変更には、[process-framework.md](process-framework.md)および[ALPS-SPEC.md](ALPS-SPEC.md)の該当箇条を参照する必要がある。
- Nameを、他のSkillと区別できる短い名詞句にする必要がある。NameをPurposeの要約にしてはならない。
- Purposeは、相互に関連する一つまたは複数の上位目的を示す必要がある。
- Purposeは、可能な限り一文で簡潔に記述するのが望ましい。
- Outcomeは、Outputの作成ではなく、一つの肯定的で観察可能かつ評価可能な結果状態として記述する必要がある。
- Outcomeの集合は、Purposeの達成に必要な結果を過不足なく含む必要がある。
- Activity、および必要に応じて独立したSkillとして分離された部分は、全体としてすべてのOutcomeを網羅する必要がある。OutcomeとActivityの一対一対応を仮定しなくてよい。
- 一つの文では一つの意味だけを扱うのが望ましい。
- 参考情報によって主要要素の意味または規範上の強さを変更してはならない。
- 適用法令、規制要求、方針、任意規格および合意を、宣言された適用範囲で適用する必要がある。
- 実行環境で有効なSkill作成、検証および保存の規則に従う必要がある。

## Constraints

- 一般Skillは、特定の実行主体、Taskの割当て、方法、ツール、測定指標または実行順序を規範として固定してはならない。
- Agent、モデル、ツールおよび実行環境をInputとして扱ってはならない。これらはEnablerとして扱う必要がある。
- Decision GateをSkill Descriptionの構成要素として扱ってはならない。採用、保留、変更、再実行または終了を制御する別個の意思決定機構として扱う必要がある。
- 必須の参照先は、対象環境から特定し、取得できる必要がある。Skill Descriptionと付随資源のあいだに不要な重複または矛盾を生じさせてはならない。

## Enablers

- ステークホルダーおよび業務領域の専門知識
- 管理されたSkill資産および変更履歴
- 起草、比較、検索および試行を支援するAgentまたはツール
- 起草者から独立したレビュー能力
- `../../../scripts/check_skill_description.py`による機械的な事前確認

## Conformance

- Conformanceを主張する場合、対象、適用範囲、およびOutcome、Taskまたは双方のどれを基準にするかを明示する必要がある。
- OutcomeへのFull Conformanceでは、Outcomes節に列挙したすべてのOutcomeの達成を示す必要がある。ActivityおよびTaskは指針として扱う。
- TaskへのFull Conformanceでは、ActivityおよびTaskにおいて「〜する必要がある」または「〜してはならない」で示されたすべての要求事項の充足を示す必要がある。Outcomeは指針として扱う。
- 選択したFull Conformance基準を満たさないSkillまたはProcessには、Tailored Conformanceを主張してよい。その主張では、ALPS管理ProcessのSkill Tailoringに従ってTailoringしたSkillまたはProcessと、その適用範囲とを宣言する必要がある。また、その範囲に残るOutcomeならびにActivityおよびTaskに含まれる要求事項の充足を示す必要がある。
- 個別のActivityについてのみ、独立したProcess Outcome Conformanceを主張してはならない。

## Interfaces & Traceability

| 提供する情報項目 | 主な受領先 | 関連情報 |
|---|---|---|
| 検証済みSkill Description | Skill資産管理 | 採用対象、版、適用条件および検証結果。 |
| 検証結果・欠陥処置 | 採用Decision Gate | 判定基準、証拠、未解決制限および決定。 |
| Task–Outcome対応 | Assessmentまたは再検証 | Task、Outcome、証拠および状態。 |
| 再定義・再検証結果 | Skill管理 | 変更要求、影響範囲および変更後の証拠。 |

Outputが他のSkillのInputになる場合、名称、意味および適用範囲を整合させるのが望ましい。

## Bundled Resources

この節は参考情報であり、特定の実行方法を要求しない。

- [process-framework.md](process-framework.md)は、Process Descriptionの上位規範を正確に確認するためのControlとして利用する。ALPSと矛盾する場合は、この文書を優先する。
- [ALPS-SPEC.md](ALPS-SPEC.md)は、ALPSの規範要求を正確に確認するためのControlとして利用する。全文を常時読み込まず、対象となる箇条を参照する。
- ALPS準拠のSkill Descriptionを起草する場合は、[SKILL-template.md](SKILL-template.md)を参考例として利用できる。適用する構成は、Purposeと必要な詳細度に応じて選ぶ。
- Skill Packageの構成と付随資源の役割を設計する場合は、[skill-package-format.md](skill-package-format.md)を参考例として利用できる。必要な資源だけを採用する。
- 正式なニーズ記録、Skill Description、トレーサビリティ表、検証記録または採用判断記録を作る場合は、[record-templates.md](record-templates.md)を適用対象に合わせてTailoringして利用できる。
- 本Packageの代表的なMarkdown Environment Bindingについては、`python3 ../../../scripts/check_skill_description.py --locale ja <SKILL.md>`でYAML frontmatter、基準見出しおよび関連する構造上の徴候を事前確認できる。これらの表現はBinding固有であり、ALPSの要求ではない。スクリプトはConformanceまたはOutcome達成を単独では証明しない。

## Common Approach

この節は参考情報であり、規範上の強さを持たない。

- ニーズ、失敗事例および既存資産の未充足領域を、一つの候補台帳で比較すると選定根拠を残しやすい。
- OutcomeからActivityおよびTaskに逆向きに分解し、その後にTaskからOutcomeに追跡すると、過不足を見つけやすい。
- 発見層だけを第三者に提示する選択テストと、実行層を用いる代表タスクの試行とを分けると、二層それぞれを評価しやすい。
- 境界事例、曖昧なInput、欠落したEnablerおよび相反するControlを試行に含めると、発動条件と制限を精緻化しやすい。
- 実行のたびに挙動が変わり得る場合、単一の実行ではなく反復した試行からOutcomeの達成可能性を判断し、観察された変動と証拠の限界を記録すると、採用判断の根拠を確かめやすい。
- 一意の期待結果を定められない場合、許容条件、禁止条件または評価方法を定めると、検証に観察可能な根拠を与えやすい。

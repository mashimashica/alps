---
name: apply-agent-lifecycle-process-skills
description: 適用状況のニーズ、条件およびリスクに合うAgent Skillを選択し、Entry/Exit Criteria、Control、ConstraintおよびTailoringの決定を確認する。Skillを単独で、または組み合わせて実行する。さらに、Skill間におけるOutputとInputの授受、および構成全体の完全性および一貫性を管理する。既存Skillを使う作業、複数Skillの編成、適用根拠またはOutcome達成の証拠を求められたときに使用する。新規Skillの定義だけ、またはSkill資産の採用・変更・廃止だけを行う場合は使用しない。ALPS準拠。
---

> 本書は日本語ローカライズである。基準となる英語版は[SKILL.md](../../../SKILL.md)であり、内容が矛盾する場合は英語版を優先する。

# Agent Lifecycle Process Skill Application

## Purpose

本Skillは、適用状況に適合するSkillを単独で、または組み合わせて適用することにより、意図されたOutcomeを達成する。

## Outcomes

本Skillの成功によって、次の状態が成立している。

- a) 適用状況のニーズおよび条件が識別されている。
- b) 適用するSkillおよび適用形態が、根拠とともに決定されている。
- c) 適用されるControl、ConstraintおよびTailoringの決定が識別されている。
- d) Skill Instanceの適用結果が、宣言された適用範囲、適用されるControl、ConstraintおよびTailoringの決定に適合している。
- e) 適用対象となるSkillの宣言されたOutcomeが達成されている。
- f) 必要なSkill間の授受が確立されている。
- g) Skill構成の完全性および一貫性が確立されている。

## Activities & Tasks

以下の見出し、Activity、Taskおよび番号の記載順序は、手順または実行順序を規定しない。本SkillのEntry Criteriaは本適用Processの発動前の判定条件、Exit Criteriaは完了宣言前の判定条件であり、ControlsおよびConstraintsは記載位置にかかわらず適用される。選択した各SkillのEntry Criteriaは、そのSkillの発動前に別途判定する。Iteration、Concurrency、RecursionおよびIntegrationを、適用状況に応じて用いる。

### Skill選択

このActivityは、適用状況に対して用いるSkillおよびその適用形態を決定する。主にa)、b)およびc)に寄与する。

1. 適用状況のニーズ、条件および適用されるConstraintを識別する必要がある。
2. 通常、ニーズをSkillのPurposeおよびOutcomeと照合する。
3. 通常、Skill Discovery Descriptionを含む発見層の情報に基づいて候補Skillを識別する。
4. 候補間の重複がある場合、Purposeによって範囲を判別するのが望ましい。
5. 適合する候補がない場合、そのニーズを定義ProcessのSkillニーズ識別に引き渡してよい。
6. 適用の決定に伴う不確実性とリスクが許容可能であるかを判断する必要がある。
7. 決定の根拠を記録するのが望ましい。

### Skill実行

このActivityは、選択されたSkillのInstanceを実行し、宣言されたOutcomeを達成する。主にc)、d)およびe)に寄与する。

1. Entry Criteriaの成立を判定してからSkillを発動する必要がある。成立しない場合は、発動を見合わせるか、不足している条件を満たすことを先行させる必要がある。
2. 必要なInputおよびEnablerの利用可能性を確認するのが望ましい。
3. 適用されるControl、ConstraintおよびTailoringの決定を識別する必要がある。
4. Skill DescriptionのActivityおよびTaskを、付与された規範属性に従って実行する必要がある。要求事項として記述されたTaskは、管理されたTailoringによる正当な変更がない限り、省略してはならない。
5. Constraintが明示されていない限り、特定の実行順序を仮定しなくてよい。
6. 実行中に生じた問題は、解決されるまでIterationを続けるのが望ましい。
7. 不可逆的または高影響の行為に先立って、Decision Gateを適用するのが望ましい。
8. Exit Criteriaに照らして完了を判定する必要がある。
9. Outcomeの達成状況を、観察可能な証拠に基づいて判定するのが望ましい。
10. Outputは、授受の定義に従って受領側に引き渡すのが望ましい。品質条件が定められている場合、その充足を確認するのが望ましい。
11. 実行上の重要な意思決定、その根拠および前提を記録し、必要な変更管理のもとに置くのが望ましい。
12. 実行から得られた教訓を、管理ProcessのSkill評価・改善に引き渡してよい。

### Skill編成

このActivityは、複数のSkillを組み合わせ、そのインターフェース、授受および構成全体の完全性および一貫性を管理する。主にe)、f)およびg)に寄与する。

1. 目標とするOutcomeの集合を識別する必要がある。
2. 構成に用いる各Skillの出典を識別するのが望ましい。
3. 反復利用される構成は、Skill Viewとして文書化してよい。
4. 提供側のOutputと受領側のInputとの対応を明示する必要がある。
5. あらかじめ定義されていなかった授受は、Tailoringによって追加してよい。
6. IterationまたはRecursionによってOutputが変更された場合、影響を受けるInputを識別し、それらの整合性および適用される基準を再評価するのが望ましい。
7. Integrationによって、同じ階層のうちでの完全性と、異なる階層のあいだでの一貫性とを確保する必要がある。
8. 構成全体としてのOutcome達成状況を判定するのが望ましい。
9. 同一の情報項目が複数のSkillによって変更される場合、その情報項目の整合性、状態および変更の取扱いを、品質リスクに応じて定める必要がある。

## Inputs

代表的なInputは、適用状況のニーズ、発動要求、Skillの発見層およびSkill Description、目標Outcomeの集合、Skill Descriptionが定めるInput、Frameworkレベルの宣言ならびにTailoringの決定である。これらは唯一の実行方法を規定するものではない。

## Outputs

代表的なOutputは、適用Skillおよび適用形態の決定、Skill Descriptionが定めるOutput、Skill構成の定義、構成全体のOutput、実行および意思決定の記録である。これらは唯一の実行方法を規定するものではない。

## Entry Criteria

- 適用要求または適用状況から、ニーズを識別するための情報を利用できるか、確認によって取得できる。
- 候補Skillの発見情報にアクセスできる。または、候補を利用できない状態が明示されている。
- 適用判断を安全に開始するための優先Controlおよび重大なConstraintを識別できる。

このEntry Criteriaは、本適用Processを開始できる条件である。選択した各SkillのEntry Criteriaは、発動前に別途判定する必要がある。

## Exit Criteria

- ニーズ、条件、選択結果、適用形態およびリスク判断が記録されている。
- 選択した各SkillのEntry/Exit Criteria、要求事項として記述されたTask、Outcomeの証拠および未解決事項が判定されている。
- 複合適用では、OutputとInputの対応、共有情報の状態およびIntegrationが確認されている。
- Outputを引き渡したか、保留したか、ニーズを定義Processに引き渡したか、管理ProcessにTailoring判断を依頼したか、または終了したかが明示されている。
- Conformanceを主張する場合、その基準と証拠が検証されている。

## Controls

- Process FrameworkとALPSを適用する必要がある。両者が矛盾する場合はProcess Frameworkを優先する必要がある。
- 規範語とその意味は、Process Frameworkの定めによる。本Skillはこれらを再定義しない。
- 適用されるシステム指示、利用者指示、安全・プライバシー方針、法令、規格および合意を適用する必要がある。
- 選択した各SkillのSkill Description、Frameworkレベルの宣言および管理Processが承認したTailoringの決定を適用する必要がある。
- 実行環境の権限、確認および外部作用に関する規則に従う必要がある。

## Constraints

- Agent、モデル、Skill、ツールおよび実行環境をInputとして扱ってはならない。これらはEnablerとして扱う必要がある。
- Skillを実行する前に、そのSkill Descriptionのうち実行に必要な内容を確認する必要がある。候補識別のための情報だけで実行してはならない。
- Entry Criteriaの成立前に発動してはならない。Exit Criteriaの判定前に完了を宣言してはならない。
- 明示されていない実行順序を仮定してはならない。
- Tailoringを暗黙に行ってはならない。適用されるControlおよびConstraintならびに管理判断を追跡可能にする必要がある。変更の範囲および根拠も記録するのが望ましい。
- 不可逆的または高影響の外部作用では、実行環境のControlまたはConstraintがDecision Gateの通過を要求する場合、その通過前に実行してはならない。

## Enablers

代表的なEnablerは、管理されたSkill資産、Agentの能力、必要なツールおよび実行環境である。これらは唯一の実行方法を規定しない。

## Conformance

- Conformanceを主張する場合、対象、適用範囲、およびOutcome、Taskまたは双方のどれを基準にするかを明示する必要がある。
- OutcomeへのFull Conformanceでは、Outcomes節に列挙したすべてのOutcomeの達成を示す必要がある。
- TaskへのFull Conformanceでは、ActivityおよびTaskにおいて「〜する必要がある」または「〜してはならない」で示されたすべての要求事項の充足を示す必要がある。
- 「いずれのSkillも適用しない」と決定してOutcomeの一部が適用対象外となる場合、適用対象外となるOutcomeを宣言し、Full Conformanceを主張せず、ALPS 12.3のTailored Conformanceを用いる必要がある。
- 変更または除外の結果、選択したFull Conformance基準を満たさない場合、Tailored Conformanceの主張では、管理ProcessでTailoringしたSkillまたはProcessとその適用範囲を宣言し、その適用範囲に残されたOutcomeおよびActivity・Taskに含まれる要求事項の充足を示す必要がある。
- 個別のActivityについてのみ、独立したProcess Outcome Conformanceを主張してはならない。

## Interfaces & Traceability

| 提供元 | Outputまたは情報項目 | 受領先 | 関連情報 |
|---|---|---|---|
| 管理Process | 管理されたSkill情報、Tailoring決定、適用条件 | 適用Process | 受領Activity: Skill選択およびSkill実行。資産、版、状態、範囲および条件。 |
| Skill A | 宣言されたOutput | Skill B | 受領側Input: Skill Bの宣言されたInput。名称、意味、範囲、品質条件および状態。 |
| 本適用Process | 実行記録、意思決定、教訓、測定結果 | 管理Process | 受領Activity: Skill評価・改善。Skill Instance、証拠、制限および変更候補。 |
| 本適用Process | 未充足ニーズ | 定義Process | 受領Activity: Skillニーズ識別。文脈、期待、候補不在の根拠およびリスク。 |

Outputの変更が他のSkillのInputに影響する場合、影響を受けるSkillとInputを識別し、必要な再評価を行うのが望ましい。

## Bundled Resources

この節は参考情報であり、特定の実行方法を要求しない。

- 品質リスクによってProcess Instance記録が正当化される場合は、[process-instance-record.md](process-instance-record.md)の軽量なMarkdown Bindingを利用できる。これは、適用の基礎および意図するOutcomeと、後に得られた結果、判定および証拠とを、同じ人間可読かつ機械判読可能な記録に保持する。
- 明示的に指定した基準記述から記録を作る場合は`python3 ../../../scripts/process_instance_record.py --locale ja new ...`を、Bindingを確認する場合は`python3 ../../../scripts/process_instance_record.py --locale ja check --at instantiation|completion <record.md>`を実行できる。このスクリプトは、Skillの意味、Tailoring、Outcome達成またはConformanceを推定しない。

## Common Approach

この節は参考情報であり、規範上の強さを持たない。

- ニーズ、条件、目標OutcomeおよびConstraintを整理してから、候補識別に利用できる情報で候補を絞るとよい。
- Process Instance記録は実行前に作成し、実行後に同じファイルを完成させることができる。詳細は品質リスクに比例させ、該当しない任意ブロックは省略するとよい。
- 管理された出典を記録し、局所的なレビュー可能性が重要な場合は、適用される基準記述も記録するとよい。Instance固有の記述または成功基準が存在するだけではTailoringとみなさず、意味、規範上の強さまたは適用可能性を変更する場合は管理Processを用いる。
- 候補がなければ定義Processにニーズを引き渡し、Tailoringが必要なら管理Processに判断を引き渡すと、暗黙の変更を避けやすい。
- 複合適用では、提供Skill、Output、受領Skill、Input、意味、範囲および品質条件を表にすると授受を確認しやすい。
- 管理された出典への参照と可読な記述を組み合わせると、記録単独での確認可能性とTraceabilityを両立しやすい。
- 非決定性が重要な場合、単一の実行だけでOutcomeの達成を判断せず、観察された変動、証拠の限界および未解決の不確実性を記録すると、後の評価の根拠を保ちやすい。反復試行または継続監視の要否は、品質リスクに応じて決めるとよい。
- 人間による承認および介入の記録、介入を必要とした条件、変更または却下された提案、検出されなかった失敗、判断に不十分だった説明またはログ、automation biasまたは過剰介入の兆候、監督者の負荷および応答遅延、Decision Gateの過不足、ならびに使用した証拠の品質および限界は、管理ProcessのSkill評価・改善に引き渡せる。

# ALPS — Agent Lifecycle Process Skills 規格

---

## 序文

本規格 ALPS（Agent Lifecycle Process Skills）は、Process Framework（以下「PF」という）をAgent Skillsに適用する。Agent Skillの記述粒度、規範上の強さ、ライフサイクル管理および適合基準には、作成者間のばらつきがある。共通のSkill Description構造は、結果の一貫性を高め、Skillの導入、Tailoring、改善およびAssessmentを支援する。Name、PurposeおよびOutcomeは、Skillの実行とAssessmentの双方で用いる共通の参照点となる（PF 1.2）。このため、本規格は、Skillの記述、ライフサイクル管理および適合に共通する規則を定める。

本規格は、SkillをProcess Descriptionとして扱い、PFの設計原則をSkillの全ライフサイクルに適用する。

---

## 目次

- 1. 適用範囲
- 2. 引用規格および優先関係
- 3. 用語および定義
- 4. 規範語および表記法
- 5. 基本概念
- 6. Skill Descriptionの要求事項
- 7. SkillライフサイクルおよびALPS Reference Model
- 8. Skillの実行構造および相互関係
- 9. Control、ConstraintおよびEnabler
- 10. Entry/Exit Criteria、Decision Gateおよびレビュー
- 11. TailoringおよびSkill Instantiation
- 12. Conformance、CapabilityおよびAssessment
- 付録A（参考）Skill DescriptionおよびSkill Packageの例
- 付録B（参考）Process Frameworkとの対応
- 付録C（参考）関連文書
- 付録D（参考）Agent文脈におけるHuman Oversight、Accountabilityおよび証拠

---

## 1. 適用範囲

### 1.1 本規格が規定する事項

本規格は、次の事項を規定する。

a) Agent SkillをProcess Descriptionとして記述するための要求事項、推奨事項および記述規則（箇条5、箇条6）。

b) Skillのライフサイクルを構成する三つのProcessと、それらを構成するActivityおよびTaskを定義した参照モデル（ALPS Reference Model。箇条7）。

c) 複数のSkillを組み合わせて適用するための実行構造、インターフェース、授受およびSkill Viewの規則（箇条8）。

d) Skillに適用されるControl、ConstraintおよびEnablerの宣言と扱い（箇条9）、ならびにEntry/Exit Criteria、Decision Gate、レビューおよび監査の適用（箇条10）。

e) SkillのTailoringおよびInstantiationの規則（箇条11）、ならびに本規格およびSkillへのConformanceの主張基準とCapabilityの扱い（箇条12）。

f) Skill Description、およびその理解・実行・Output作成を支援する付随資源から構成されるSkill Packageの論理的な構成および整合性（5.7）。

### 1.2 本規格が規定しない事項

本規格は、次の事項を規定しない。

a) Skill Packageの具体的な実装形式。ファイル形式、メタデータ書式、物理的な格納構造、配布機構およびツールチェーンは、本規格の適用範囲外である。ただし、Skill Descriptionと付随資源との論理的な構成および整合性には、5.7を適用する。

b) 特定のAgent実装、モデル、実行環境またはベンダー。

c) 情報セキュリティおよび安全性の技術的対策の詳細。ただし、これらに由来する要求は、ControlまたはConstraintとして本規格の枠組みで扱う（箇条9）。

d) Skillが記述する個々の業務領域の内容。

### 1.3 想定利用者

本規格は、Skillを起草する者、Skill資産を管理する者、Skillを実行するAgentの提供者および運用者、ならびにSkillまたはその実行のConformanceを評価する者が利用することを想定する。

## 2. 引用規格および優先関係

次の文書は、本規格の適用にあたって不可欠である。

- **Process Framework**（process-framework.md）。本文中では「PF」と略記し、「PF 4.3」のように箇条番号で参照する。

本規格とPFが矛盾する場合は、PFを優先する。本規格は、PFの要求事項を緩和し、または禁止事項を許容してはならない。PFの構成概念をAgent Skill向けに特殊化した内容は、5.8に示す。

## 3. 用語および定義

PFに定義または使用されている用語は、PFの意味で用いる。加えて、次の用語を定義する。

**3.1 Agent（エージェント）**
明示されたPurposeのもとでActivityおよびTaskを実行し得る実行主体のうち、環境の観測、判断および行為をある程度自律的に行うもの。人間の指示または監督のもとで動作するソフトウェアシステムを含む。

**3.2 Agent Skill（Skill）**
Agentが発見し、読み込み、実行できる形で資産化された、再利用可能なProcess Description、および必要に応じてそれに付随する資源の単位。本規格では単に「Skill」という。

**3.3 Skill Description**
Skillの内容をなすProcess Description。Name、PurposeおよびOutcomeを必須の要素とし、任意の要素および参考情報を加えたもの（箇条6参照）。

**3.4 発見層および実行層**
AgentがSkill Descriptionを利用するためにALPSが定める、機能上の提示層。発見層は、完全なSkill Descriptionを読み込む前にSkillを発見し、その適用可能性を判定するためのNameおよび簡潔な参考情報を提示する。実行層は、Skillの実行およびAssessmentに用いる、正本のProcess Description要素および参考情報を提示する。

これらの層はProcess Description要素を追加せず、特定の物理的分離、ファイル形式または格納構造を要求しない。

**3.5 Skill Model**
特定の適用領域のために選択され、または定義されたSkillの集合、およびSkill間の関係からなるProcess Model。

**3.6 ALPS Reference Model**
本規格の箇条7において、ALPS定義Process、ALPS適用ProcessおよびALPS管理Processを、それぞれのPurposeおよびOutcomeによって定義したProcess Reference Model。各Processは三つのActivityによって構成される。Skillライフサイクルの評価および改善の参照枠として利用できる。

**3.7 Skill View**
複数のSkillにまたがるActivityおよびTaskを、特定の関心またはPurposeに基づいて構成したProcess View（8.3参照）。

注記: Skill Viewは、独立したProcessとしてのSkillを定義するものではなく、既存のSkillを横断する見方を示す。

**3.8 Skill Instance**
特定の適用文脈における、Skillの一回の適用（Process Instance）。

**3.9 発動（Invocation）**
Entry Criteriaの成立を判定し、Skill Instanceの実行を開始すること。

**3.10 Skill資産（Skill Asset）**
採用され、管理下に置かれたSkill、Skill ModelおよびSkill Viewの総体。

**3.11 Skill Discovery Description（Skill発見記述）**
Agentが完全なSkill Descriptionを読み込む前にSkillを発見し、その適用可能性を判定するために用いる、ALPS固有の発見層に置く簡潔な参考情報。Skillが行うこと、そのSkillを使用する状況、および適用可能性の判定に必要な情報を示す。

**3.12 Skill Package**
一つのSkill Description、およびその理解・実行・Output作成を支援する任意の付随資源を、一体として管理する単位。

## 4. 規範語および表記法

### 4.1 規範語

本規格およびSkill Descriptionで用いる規範語とその意味は、PFの定めによる。本規格はこれらを再定義しない。規範上の意味を混同させないため（PF 1.4）、本規格およびSkill Descriptionでは、これらの語を用いて記述の規範属性を判別可能にする必要がある。

次の表は、PFの規範語を参考情報として再掲するものであり、その意味を変更しない。

| 規範属性 | 日本語表現 | 参考: 英語表現 |
|---|---|---|
| 要求事項 | 〜する必要がある ／ 〜してはならない | must / must not |
| 推奨事項 | 〜するのが望ましい ／ 〜しないのが望ましい | should / should not |
| 許容される行為 | 〜してよい | may |
| 通常実施される行為 | 通常、〜する | typically |

「〜できる」「〜され得る」は、可能性または能力を述べる記述であって、規範属性を持たない。これらの語を大文字で表記する形式は用いない。

### 4.2 規範部分と参考部分

本規格の本文（箇条1〜12）は規範であり、注記、例および「（参考）」を付した付録は参考である。参考情報は、規範上の強さを変更してはならない（PF 1.4）。Skill Descriptionにおける参考情報についても、同じ規則を適用する（6.3.8参照）。

## 5. 基本概念

### 5.1 SkillはProcess Descriptionである

Skillの内容は、PFに適合するProcess Descriptionとして記述する必要がある。

一般的なProcessを記述する**一般Skill**には6.2を適用する。特定のInstanceを記述する**個別Skill**は、その旨と適用文脈を明示し、必要な能力、資源、Input、Output、Constraint、Controlおよび時間を具体化できる（PF 1.1）。

### 5.2 Skillの二重性: Process DescriptionかつEnabler

Skillは、内容上はProcess Descriptionであり、利用側のProcessに対してはEnablerとして機能する。

Skill、AgentおよびツールはInputではなく、Enablerとして扱う必要がある（PF 4.1）。

### 5.3 実行主体の非規定

Skill Descriptionは、実行主体の構造またはTaskの割当てを規定してはならない。実行主体にTaskを割り当てるのではなく、実行に必要な能力または条件をEnablerまたはConstraintとして明示するのが望ましい（PF 3.2）。

### 5.4 Skillの境界および粒度

Skillの境界は、Activityの中間Outputによってではなく、主要なOutputおよびOutcomeに基づいて定めることを通常の実務とする（PF 3.1）。Skillにおいては、Outcome、ActivityおよびTaskを強く関連付けるとともに、他のSkillへの依存を可能な限り減らす。

多数のTaskを含む重要なActivityは、独立したPurposeとOutcomeを持つ別のSkillとして記述してよい（PF 3.1）。

複数のSkillにまたがる情報項目の定義、維持、評価または変更の取扱いが、独立したPurposeおよびOutcomeと、相互にまとまりのあるActivityを持ち、一つのProcessとして境界を定められる場合、それを別のSkillとして記述してよい。これに対し、独立したProcessの境界を設けず、横断的な関心として既存Skillの関係を示す場合は、Skill Viewとして記述できる（8.3）。

### 5.5 機能上の層と段階的開示

PF 1.3は、異なるニーズをもつ読者に応じて、Process Descriptionの情報を層として提示することを許容する。ALPSは、Agent Skillの段階的開示に用いる機能上の提示層として、発見層および実行層を定める。これらの名称および機能はALPSに固有であり、PFの構成概念ではない。

記述適合を主張するSkill Descriptionは、両方の層を提供し、それぞれの機能を判別可能にする必要がある。正本となるSkill Descriptionを一意に識別でき、必須の参照先を解決できる限り、両方の層を一体として表現しても、分けて表現してもよい。

a) **発見層**は、NameおよびSkill Discovery Descriptionを提示する必要がある。Skill Discovery Descriptionは、Skillが行うこと、そのSkillを使用する状況、および適用可能性の判定に必要な情報を示す必要がある。

b) **実行層**は、Skillの実行およびAssessmentに用いる完全なSkill Descriptionを提示し、または参照可能にする必要がある。実行層には、Name、PurposeおよびOutcomeに加え、6.1に従って採用した任意要素および参考情報を含める。

c) 複数のSkillにまたがる事項は、個々のSkillの実行層とは別に扱うのが望ましい。共通するControlおよびEnablerは、Frameworkレベルの要素として宣言してよい。

注記: これらの機能上の層は、二つのファイル、二つの節その他の特定の物理構造を要求せずに、段階的開示を支援する。

### 5.6 Skill Modelとライフサイクルモデル

Skill Modelは、相互に関係するSkillからなるFrameworkであり、ライフサイクルモデルを含むProcess Modelを構成するための基盤になり得る（PF 5.1）。Skill Modelの中からは、Purposeに応じて部分集合を選択し、適用できる。Skillの選択とその実行時期は、適用対象または適用状況の変化に応じて、継続的な見直しを要する（PF 5.2）。

### 5.7 Skill Packageおよび付随資源

Skill Packageは、Skillの基準となるSkill Descriptionを一つ含む必要がある。

Skill Packageには、Skillの理解、実行またはOutputの作成を支援する参考情報、実行資源および成果物用資源を、必要に応じて含めてよい。付随資源を含める場合、その役割および利用条件をSkill Descriptionから識別できるようにする必要がある。必須の参照先は、対象環境から特定し、取得できる必要がある。

Skill Descriptionと付随資源とのあいだに、不要な重複または矛盾を生じさせてはならない。付随資源は、その格納場所ではなく、Skillの実行において果たす機能に基づいて、参考情報、Input、Output、Control、ConstraintまたはEnablerとして扱う必要がある（9.1）。

Skill Packageには、Skillの理解、実行またはOutputの作成を直接支援する資源だけを含めるのが望ましい。

### 5.8 Process Frameworkの特殊化

ALPSは、PFの一般的な構成概念をAgent Skill向けに特殊化する。一般概念の規範的な正本はPFに置く。本規格は、一般定義を重複して展開せず、Agent Skillに固有の追加事項だけを記述する。

| PFの構成概念 | ALPSにおける特殊化 |
|---|---|
| Process Description | Skill Description（3.3） |
| Process Instance | Skill Instance（3.8） |
| Process Model | Skill Model（3.5） |
| Process View | Skill View（3.7） |
| Processを実行または支援する資源 | Agent、モデル、ツールおよび実行環境として具体化し、Enablerとして扱う（5.2、9.3） |

ALPSは、PFの規則をAgent文脈に合わせて具体化し、必要に応じて強めることができる。ただし、PFの概念の意味を変更し、PFの要求事項を弱め、または異なる概念に置き換えてはならない（箇条2参照）。

## 6. Skill Descriptionの要求事項

### 6.1 要素の構成

Skill Descriptionは、Name、PurposeおよびOutcomeを含む必要がある（PF 1.2）。

Activity、Task、Input、Output、Control、Constraint、Enabler、Entry Criteria、Exit Criteriaおよび参考情報は任意の要素であり、記述のPurposeと、必要とされる詳細度に応じて加える。Decision GateはSkill Descriptionの構成要素ではなく、Skillの適用を制御する意思決定機構として扱う（PF 1.2および8.1、箇条10）。

### 6.2 記述の一般規則

a) Name、Purpose、Outcome、ActivityおよびTaskの役割を区別し、それらのあいだに整合性を持たせる必要がある（PF 1.4）。

b) 一つの文では、一つの意味だけを扱うのが望ましい。独立した目標、結果または行為は、一つの文に結合しないのが望ましい。それぞれの記述は、そのSkill Descriptionの中で単独で参照されても意味が通るよう、必要な文脈を備えるのが望ましい。補足が必要な場合は、主要な記述に意味を重ねるのではなく、参考文または注記として分離することができる。

c) 一般Skillは、特定の方法、技法、ツール、測定指標、管理方法または実行順序を要求してはならない。必要な時間的関係はConstraintとして明示するのが望ましい。

d) ActivityおよびTaskを、Procedureの実行手順として解釈してはならない（PF 1.4）。

e) 記述の規範属性は、4.1の規範語によって判別可能にする必要がある。

注記: d)の規則は、ActivityおよびTaskの記載順序を、Agentが規定された実行手順として誤認することを防ぐことにも役立つ。

### 6.3 要素別の記述規則

#### 6.3.1 Name

Skill Nameは、Skillの見出しとなる簡潔な名詞句で記述する必要がある。Nameは、そのSkillが中心的に扱う事項を示し、Skill Model内の他のSkillと区別できるものにする。NameをPurposeの要約として記述してはならない（PF 2.1）。

#### 6.3.2 Purpose

Skill Purposeは、相互に関連する一つまたは複数の上位目的を記述する必要がある。Purposeは、可能な限り一文で簡潔に記述するのが望ましい。Purposeの中でActivityやOutcomeを要約することは、避けるのが望ましい。独立した複数のPurposeを一つの文に併記することも、避けるのが望ましい。追加の説明が必要であれば、参考文または注記に配置することができる。Skill間で範囲が重複して見える場合は、PurposeによってSkillの範囲または境界を特徴付けるのが望ましい（PF 2.1）。

#### 6.3.3 Outcome

Skill Outcomeは、Skillの実行によって達成される、測定可能かつ具体的な結果状態を表す。Outcomeは観察可能かつ評価可能である必要があり、Outputとは明確に区別する必要がある。文書、記録または情報項目の作成そのものをOutcomeとして記述してはならない（PF 2.2）。

Outcomeは、肯定的かつ観察可能な結果が成立している状態を宣言する文として記述する必要がある。一つのOutcomeには一つの結果だけを記述し、独立した複数の結果を接続詞によって結合することは、避ける必要がある。一般SkillのOutcomeは、適用可能なすべての範囲で意味を保つように記述する必要がある。

Outcomeの集合を達成すればSkill Purposeを達成でき、かつ各Outcomeがその達成に関係するようにする必要がある。各Outcomeは、単独で読まれても意味が通るのが望ましい。簡潔さよりも、意味の単一性と明瞭性を優先する。Outcomeの数は、Purposeの達成に必要な結果によって定まる。Skillの便益はOutcomeと区別し、有用であれば、Purposeに付随する非規範的な注記として別に説明できる。

#### 6.3.4 Activity

Activityは、Skillを達成または実行するための行為の集合を記述するとともに、関連するTaskを分類する構成概念として機能する。一つのActivityには、相互の関係が強く、他のActivityまたはSkillに属するTaskとの関係が弱いTaskを含めるのが望ましい。

Activity、および必要に応じて独立したSkillとして分離された部分は、全体としてすべてのOutcomeを網羅し、Skill Purposeを満たす必要がある。個々のActivityを個々のOutcomeに対応させる必要はない（PF 2.3）。

#### 6.3.5 Task

Taskは、一つ以上のOutcomeの達成を支援する個別の行為を表すことを主たる機能とし、その行為の対象と動作を判別できるように記述する必要がある。主たる機能が個別の行為ではない記述は、Taskとして扱わず、その機能に対応する要素に置く必要がある。一つひとつのTaskには規範属性を付与し、その行為が要求事項、推奨事項、許容される行為、または通常実施される行為のいずれであるかを、4.1の規範語によって明確にする必要がある。Activityに属するTaskだけで、そのActivityの境界内にあるすべての行為を列挙する必要はない。6.2 c)およびd)の規則は、ActivityとTaskの双方に適用する。

#### 6.3.6 InputおよびOutput

InputおよびOutputは、Skillとその外部との接続を表す。必須または代表的なInputを指定するかどうかは任意であり、Outcomeの達成を実証できるのであれば、Outputを指定するかどうかもまた任意である（PF 4.1および4.2）。Outputは、成果物または情報項目として表現できる。あるSkillのOutputは、別のSkillまたはProcessのInputになり得る。

あるSkillのOutputを別のSkillまたはProcessのInputとして用いる場合、それらの名称、意味および適用範囲を整合させるのが望ましい。その対応関係を記述する詳細度は、Skill DescriptionのPurpose、Skill間の依存関係および品質リスクに応じて定めるのが望ましい。

代表的なInputおよびOutputは、唯一の実行方法を規定しない。Skillは、Skill Description全体によって理解するのが望ましい（PF 4.2）。

#### 6.3.7 Control、Constraint、Enabler、Entry CriteriaおよびExit Criteria

ControlおよびConstraintは、Skillの実行を方向付け、または制限する条件を宣言する。EnablerはSkillの実行を可能にし、または支援する。Entry CriteriaはSkillを発動できる条件を示し、Exit CriteriaはSkill Instanceを完了できる条件を示す。これらの要素は、記述のPurposeと必要な詳細度に応じて用いる。詳細は箇条9および箇条10に示す。

ControlまたはConstraintの記述は、実行を方向付け、または制限する条件を宣言することを主たる機能とする。個別の行為を表すことを主たる機能とする記述は、Taskとして分類する必要がある。

Entry Criteriaの要約を発見層に置く場合、実行層から利用できるEntry Criteriaと矛盾してはならない。

#### 6.3.8 参考情報

概要、説明、Common Approach、実務上のヒント、注記および例は、Skillの理解または適用を支援する参考情報として用いる。参考情報は、主要なSkill要素の意味または規範上の強さを変更してはならない（PF 1.4）。

ALPS固有の発見層に置く参考情報として、Skill Discovery Descriptionは、Skillが行うこと、そのSkillを使用する状況、および適用可能性の判定に必要な情報を簡潔に示す必要がある。Skill Discovery Descriptionは、実行層から利用できる正本のName、Purpose、Outcome、適用範囲、Entry CriteriaおよびConstraintと整合する必要があり、これらの要素を置き換え、またはその規範上の意味を変更してはならない。

本規格への記述適合を主張するSkillのSkill Discovery Descriptionは、その記述言語による短いALPS準拠表示で終わる必要がある。英語では`ALPS-conformant.`、日本語では`ALPS準拠。`を正確に用いる必要がある。この表示は、対象を当該Skill Description、基準を12.1 a)の記述適合とする標準化された簡略主張であり、Reference Model適合または実行適合を主張するものではない。

## 7. SkillライフサイクルおよびALPS Reference Model

### 7.1 Skillライフサイクルモデル

Skillのライフサイクルモデルは、Skillに関するProcessおよびActivityのFrameworkであり、意思疎通と理解のための共通の参照枠として機能する（PF 5.2）。本規格は、次のStageからなる参照ライフサイクルモデルを定める。

a) **構想Stage** — Skill化のニーズが識別され、選定される。

b) **定義Stage** — Skill Descriptionが設計され、検証される。

c) **運用Stage** — Skillが選択され、発動され、実行され、他のSkillと編成される。

d) **進化Stage** — Skillが評価され、Tailoringされ、改善される。

e) **廃止Stage** — 不要または不適切となったSkillが利用から退く。

記載順序は実行順序を規定しない。ProcessおよびActivityは、複数のStageにわたり、反復的、再帰的または並行的に適用できる（PF 5.2、箇条8）。

### 7.2 Reference Modelの構成と読み方

ALPS Reference Modelは、次の三つのProcessからなる。各Processは、PurposeおよびOutcomeによって定義され、三つのActivityによって構成される（PF 1.1および5.1）。

| Process | Activity |
|---|---|
| ALPS定義Process | Skillニーズ識別 ／ Skill設計 ／ Skill検証 |
| ALPS適用Process | Skill選択 ／ Skill実行 ／ Skill編成 |
| ALPS管理Process | Skill資産管理 ／ Skill Tailoring ／ Skill評価・改善 |

本Reference Modelの読み方は、次による。

a) 三つのProcessは一般的なProcessであり、特定の方法、ツールまたは実行順序を要求しない（6.2 c)）。

b) ActivityおよびTaskの記載順序は、実行順序を規定しない。各Taskの規範属性は、4.1の規範語によって表す。

c) 代表的なInput／Outputは唯一の方法を規定せず、Activity間の授受はProcess境界を変更しない（PF 4.2）。

d) OutcomeへのConformanceを選択する場合、ActivityおよびTaskは指針として扱われる。TaskへのConformanceを選択する場合、Outcomeは指針として扱われる（12.2参照）。

e) Purposeに応じてProcess、ActivityおよびTaskの部分集合を選択できる。ActivityまたはTaskの変更は、必要に応じてTailoringとして扱う（PF 3.2および5.1、箇条11）。

三つのProcess間の代表的な授受は、次による。この表は固定された実行順序を規定しない。

| 提供側Process | 代表的な授受項目 | 受領側Process |
|---|---|---|
| ALPS定義Process | 検証済みのSkill Descriptionおよび検証結果 | ALPS管理Process |
| ALPS管理Process | 管理されたSkillに関する情報、Tailoringの決定および適用条件 | ALPS適用Process |
| ALPS適用Process | 実行および意思決定の記録、教訓ならびに測定可能な結果 | ALPS管理Process |
| ALPS管理Process | 変更要求、再定義要求および再検証要求 | ALPS定義Process |

### 7.3 ALPS定義Process（ALPS definition process）

**Purpose**: 本Processは、識別されたステークホルダーのニーズを満たす、評価可能で利用可能なSkill Descriptionを確立する。

**Outcomes**: 本Processが成功すると、次の状態が成立している。

a) Skill化の対象となるニーズおよび想定利用文脈が識別されている。

b) SkillのPurpose、Outcomeおよび境界が、選定されたニーズと整合している。

c) Skill Descriptionが、本規格の適用される記述要求を満たしている。

d) Skill Description内の要素および外部との授受が追跡可能である。

e) 代表的な適用文脈におけるOutcomeの達成可能性が確認されている。

f) Skillの採用可否を、欠陥および制限を含む証拠に基づいて判断できる状態にある。

| Activity | 主に寄与するOutcome |
|---|---|
| Skillニーズ識別 | a)、b) |
| Skill設計 | b)、c)、d) |
| Skill検証 | c)、d)、e)、f) |

**ActivityおよびTask**:

#### 7.3.1 Skillニーズ識別（skill need identification）

このActivityは、Skillとして扱う候補を探索し、定義対象とするニーズを選定する。

a) 通常、反復的に生じるTask、収集された教訓および失敗事例から、Skill化の機会を収集する。

b) 想定される利用者およびステークホルダーの期待を識別する必要がある。

c) 既存のSkill資産を調査し、重複、隣接領域または未充足領域を識別するのが望ましい。

d) 候補ごとに、期待される便益、リスクおよび費用を評価するのが望ましい。

e) 選定および見送りの根拠を記録するのが望ましい。

f) 選定にあたって、利用頻度または影響度による優先順位付けを行ってよい。

#### 7.3.2 Skill設計（skill design）

このActivityは、選定されたニーズを満たすSkill Descriptionの構造および内容を定める。

a) Skillの境界を、主要なOutputおよびOutcomeに基づいて定める必要がある（5.4）。

b) 他のSkillへの依存を、実行可能な限り縮小する必要がある。

c) Skill Descriptionは、判別可能な発見層の情報および実行層の情報を提供する必要がある。両者を物理的に分離する必要はない（5.5）。

d) 詳細に扱うことが有用な重要なActivityは、別のSkillとして分離してよい。

e) Name、PurposeおよびOutcomeを、6.3.1〜6.3.3に従って記述する必要がある。

f) 各Taskは、一つ以上のOutcomeの達成を支援する個別の行為を表すことを主たる機能とし、その行為の対象と動作を判別できるように記述する必要がある（6.3.5）。

g) 各記述を、その主たる機能に対応するSkill要素として分類する必要がある（6.2 a)、6.3）。

h) 各Taskに規範属性を付与する必要がある（6.3.5）。

i) 適用方法に関する指針は、Common Approachおよび実務上のヒントとして分離して記述するのが望ましい。

j) Activityの集合が全Outcomeを網羅し、Purposeを満たすことを確認する必要がある（6.3.4）。

k) TaskとOutcomeとのあいだの対応関係を識別するのが望ましい（8.2）。

l) Skill Discovery Descriptionを、3.11、5.5および6.3.8に従って記述する必要がある。

m) 代表的なInputおよびOutputを示す場合、他のSkillまたはProcessとの主要な対応関係を、必要に応じて識別するのが望ましい（6.3.6、8.2）。

n) Skill Packageを構成する場合、付随資源の必要性、役割および利用条件を識別する必要がある（5.7）。

#### 7.3.3 Skill検証

このActivityは、Skill Descriptionの記述適合性と、意図したOutcomeの達成可能性を確認する。

a) 合意された基準を用いて、Skill Descriptionをレビューする必要がある（箇条10）。

b) 各Taskが、一つ以上のOutcomeの達成を支援する個別の行為を表すことを主たる機能とし、その行為の対象と動作を判別できることを確認する必要がある（6.3.5、8.2）。

c) 各記述の要素分類が、その主たる機能と整合していることを確認する必要がある。これには、ControlおよびConstraintが宣言する条件と、Taskが表す個別の行為との区別を含む（6.2 a)、6.3.5、6.3.7、9.2）。

d) 規範属性の判別可能性を確認する必要がある（4.1）。

e) 一般Skillを検証する場合、その規範部分が特定の方法、技法、ツールまたは実行順序を要求していないことを確認する必要がある（6.2 c)）。

f) 発見層の情報と実行層の情報が整合していることを確認する必要がある（5.5、6.3.8）。

g) レビューには、Skillの起草者から独立した観点を取り入れるのが望ましい。

h) 代表的な適用文脈における試行によって、Outcomeの達成可能性を評価するのが望ましい。

i) Skill Discovery Descriptionを含む発見層の情報だけで適用可能性を判定できるかを評価するのが望ましい。

j) 想定利用文脈の境界事例を評価に含めてよい。

k) 検出された欠陥を記録し、期限と完了条件を伴う対応を設定するのが望ましい（PF 8.2）。

l) 欠陥処置が完了したことを、採用の判断（Decision Gate）に先立って確認するのが望ましい。

m) Skill Descriptionが他のSkillまたはProcessとの授受を示す場合、Outputが想定される受領側のInputとして利用可能であるかを評価するのが望ましい。

n) Skill Packageを検証対象に含める場合、正本となるSkill Descriptionの存在、必須の参照先を対象環境から特定して取得できること、付随資源の役割および利用条件、ならびにSkill Descriptionと付随資源との整合性を評価する必要がある（5.7）。

**代表的なInput**: ステークホルダーの期待、教訓、実行実績に関する情報、適用されるControlおよびConstraint、既存のSkill資産に関する情報、検証基準ならびに代表的な適用文脈。

**代表的なOutput**: 選定されたSkillニーズおよび選定根拠、検証済みのSkill Description、要素間対応の記録、検証結果ならびに欠陥処置の記録。

注記: 非決定的な挙動を含むSkillの証拠については、付録Dに参考指針を示す。

### 7.4 ALPS適用Process（ALPS application process）

**Purpose**: 本Processは、適用状況に適合するSkillを単独で、または組み合わせて適用することにより、意図されたOutcomeを達成する。

**Outcomes**: 本Processの成功によって、次の状態が成立している。

a) 適用状況のニーズおよび条件が識別されている。

b) 適用するSkillおよび適用形態が、根拠とともに決定されている。

c) 適用されるControl、ConstraintおよびTailoringの決定が識別されている。

d) Skill Instanceの適用結果が、宣言された適用範囲、適用されるControl、ConstraintおよびTailoringの決定に適合している。

e) 適用対象となるSkillの宣言されたOutcomeが達成されている。

f) 必要なSkill間の授受が確立されている。

g) Skill構成の完全性および一貫性が確立されている。

| Activity | 主に寄与するOutcome |
|---|---|
| Skill選択 | a)、b)、c) |
| Skill実行 | c)、d)、e) |
| Skill編成 | e)、f)、g) |

注記: 「いずれのSkillも適用しない」という決定も、適用状況に対する正当な判断になり得る。この判断によって、本ProcessのOutcomeの一部が適用対象外となる場合、本ProcessへのFull Conformanceを主張してはならない。適用対象外となるOutcomeを宣言し、12.3のTailored Conformanceを用いる必要がある。

**ActivityおよびTask**:

#### 7.4.1 Skill選択（skill selection）

このActivityは、適用状況に対して用いるSkillおよびその適用形態を決定する。

a) 適用状況のニーズ、条件および適用されるConstraintを識別する必要がある。

b) 通常、ニーズをSkillのPurposeおよびOutcomeと照合する。

c) 通常、Skill Discovery Descriptionを含む発見層の情報に基づいて候補Skillを識別する。

d) 候補間の重複がある場合、Purposeによって範囲を判別するのが望ましい（6.3.2）。

e) 適合する候補がない場合、そのニーズをALPS定義ProcessのSkillニーズ識別に引き渡してよい。

f) 適用の決定に伴う不確実性とリスクが許容可能であるかを判断する必要がある（箇条10）。

g) 決定の根拠を記録するのが望ましい。

#### 7.4.2 Skill実行（skill execution）

このActivityは、選択されたSkillのInstanceを実行し、宣言されたOutcomeを達成する。

a) Entry Criteriaの成立を判定してからSkillを発動する必要がある。成立しない場合は、発動を見合わせるか、不足している条件を満たすことを先行させる必要がある。

b) 必要なInputおよびEnablerの利用可能性を確認するのが望ましい。

c) 適用されるControl、ConstraintおよびTailoringの決定を識別する必要がある。

d) Skill DescriptionのActivityおよびTaskを、付与された規範属性に従って実行する必要がある。要求事項として記述されたTaskは、Tailoringによる正当な変更（箇条11）がない限り、省略してはならない。

e) Constraintが明示されていない限り、特定の実行順序を仮定しなくてよい（6.2 c)）。

f) 実行中に生じた問題は、解決されるまでIterationを続けるのが望ましい（8.1）。

g) 不可逆的または高影響の行為に先立って、Decision Gateを適用するのが望ましい（10.2）。

h) Exit Criteriaに照らして完了を判定する必要がある。

i) Outcomeの達成状況を、観察可能な証拠に基づいて判定するのが望ましい。

j) Outputは、授受の定義（8.2）に従って受領側に引き渡すのが望ましい。引渡しに適用される品質条件が定められている場合、その充足を確認するのが望ましい。

k) 実行上の重要な意思決定、その根拠および前提を記録し、必要な変更管理のもとに置くのが望ましい（PF 8.1）。

l) 実行から得られた教訓を、ALPS管理ProcessのSkill評価・改善に引き渡してよい。

#### 7.4.3 Skill編成（skill orchestration）

このActivityは、複数のSkillを組み合わせ、そのインターフェース、授受および構成全体の完全性および一貫性を管理する。

a) 目標とするOutcomeの集合を識別する必要がある。

b) 構成に用いる各Skillの出典を識別するのが望ましい（8.3）。

c) 反復利用される構成は、Skill Viewとして文書化してよい（8.3）。

d) 提供側のOutputと受領側のInputとの対応を明示する必要がある（8.2）。

e) あらかじめ定義されていなかった授受は、Tailoringによって追加してよい（PF 4.4）。

f) IterationまたはRecursionによってOutputが変更された場合、影響を受けるInputを識別し、それらの整合性および適用される基準を再評価するのが望ましい（PF 6.2）。

g) Integrationによって、同じ階層のうちでの完全性と、異なる階層のあいだでの一貫性とを確保する必要がある（8.1）。

h) 構成全体としてのOutcome達成状況を判定するのが望ましい。

i) 同一の情報項目が複数のSkillによって変更される場合、その情報項目の整合性、状態および変更の取扱いを、品質リスクに応じて定める必要がある（8.2）。

**代表的なInput**: 適用状況のニーズ、発動要求、Skillの発見層およびSkill Description、目標Outcomeの集合、Skill Descriptionが定めるInput、Frameworkレベルの宣言およびTailoringの決定。

**代表的なOutput**: 適用Skillおよび適用形態の決定、Skill Descriptionが定めるOutput、Skill構成の定義、構成全体のOutput、実行および意思決定の記録。

**代表的なEnabler**: 管理されたSkill資産、Agentの能力、必要なツールおよび実行環境。

注記: 人間による承認、介入および監督の記録は、ALPS管理Processと授受する実行および意思決定の記録の一部になり得る。代表的な項目は付録Dに示す。

### 7.5 ALPS管理Process（ALPS management process）

**Purpose**: 本Processは、Skill資産およびその適用を統制し、適切なSkillを継続的に利用できる状態を維持する。

**Outcomes**: 適用が成功すると、次の状態が成立している。

a) Skillの管理、展開およびTailoringに用いる方針および指針が確立されている。

b) 採用されたSkillが、管理された状態で発見可能である。

c) Skillの変更および廃止が、関係する利用者への影響を含めて統制されている。

d) Tailoringの判断および根拠と、適用されるControlおよびConstraintとの対応を追跡できる。

e) Skillの実績および有効性が、定められた基準に照らして評価されている。

f) 改善機会が、収集された教訓および評価結果に基づいて優先順位付けされている。

g) 決定された改善が実現されている。

| Activity | 主に寄与するOutcome |
|---|---|
| Skill資産管理 | a)、b)、c)、g) |
| Skill Tailoring | a)、d) |
| Skill評価・改善 | e)、f)、g) |

**ActivityおよびTask**:

#### 7.5.1 Skill資産管理（skill asset management）

このActivityは、Skill資産の採用、発見可能性、変更の周知、構成および廃止を管理する。

a) Skillを管理し展開する仕組みとTailoring指針を確立するのが望ましい（PF 9.1）。

b) FrameworkレベルのControlおよびEnablerを、適用範囲、例外およびTailoringの可否とともに宣言する必要がある（9.1）。

c) Skillの採用に先立ち、ALPS定義ProcessのSkill検証による証拠を確認するのが望ましい。

d) 管理指針またはSkillに変更があったなら、その内容を関係する利用者に周知するのが望ましい（PF 9.1）。

e) ニーズがなくなったSkillまたは有害となったSkillを識別し、廃止する必要がある。

f) 廃止したSkillの記述を、参照のために保存してよい。

g) Skill Model内の重複および未充足領域を、継続的に識別するのが望ましい。

h) 標準として定めたSkillを複数の適用対象で一貫して用いるのが望ましい（PF 9.2）。

i) Skill Packageの構成要素を変更した場合、影響を受けるSkill Descriptionおよび付随資源を識別し、必要な再検証を行うのが望ましい。

#### 7.5.2 Skill Tailoring（skill tailoring）

このActivityは、SkillおよびSkill Modelを、特定の適用状況のニーズ、条件およびリスクに適合させる。

a) 適用に関係するリスク、要求事項、複雑性、利用可能な能力および資源、ならびに関連規格を識別する必要がある（PF 7.3）。

b) 適用条件、利用可能な専門知識および経験、ステークホルダーの期待または要求事項、ならびにリスク許容度を考慮し、候補となるSkillまたはライフサイクルモデルを評価する必要がある（PF 7.3）。

c) Tailoringの意思決定は、事実と証拠に基づくのが望ましい（PF 7.3）。

d) Outcome、Activity、Task、代表的なInputおよび代表的なOutputについて、削除、変更または追加を行ってよい（PF 7.2）。

e) Tailoringは、適用されるControlおよびConstraintに従う必要がある（PF 7.3）。

f) 影響を受ける当事者からInputを得る必要がある（PF 7.3）。

g) Activityを許容可能なリスク水準で実行できるよう、Skillの適用に必要な厳密さをリスクに基づいて設定するのが望ましい（PF 7.1）。

h) Tailoringの範囲を明確にするのが望ましい。前提および基準を特定し、意思決定の根拠を記録するのが望ましい（PF 7.3）。

i) 通常、リスクおよび適用状況の変化に応じ、適用期間全体を通じてTailoringを動的に継続する（PF 7.1）。

j) Tailoringの運用を適用期間中に繰り返し見直し、状況に応じて改めるのが望ましい。

k) Tailoring済みSkillの実績を継続的に評価する手段を確立するのが望ましい（PF 7.3）。

l) InputおよびOutputならびにそれらの授受を記述する詳細度を、Skill間の依存関係、並行的または反復的な適用、および品質リスクに応じて調整するのが望ましい。

#### 7.5.3 Skill評価・改善（skill assessment and improvement）

このActivityは、Skillの実績および有効性を評価し、改善に結び付ける。

a) Skillの実績と有効性について洞察を得るための測定指標を設けるのが望ましい（PF 9.3）。

b) 教訓を、Skillの実行期間全体を通じて特定し、収集するのが望ましい。

c) 事前に定義した節目においても教訓を収集するよう計画するのが望ましい（PF 9.3）。

d) 測定指標を分析して、Skillの有効性を判定するのが望ましい（PF 9.3）。

e) Skillの強みと弱みを評価し、レビューおよび監査を設けるのが望ましい（箇条10）。

f) Skillの実績を、定められた基準、適用規格または比較対象と照合し、改善機会を特定してよい。比較にあたっては、実績、有効性、適合性、便益および費用を分析するのが望ましい（PF 9.2）。

g) 改善機会を継続的に特定し、優先順位を付けて実現するのが望ましい（PF 9.1）。

h) 教訓を収集して対応に結び付ける仕組みと、改善に向けた変更候補を分析する仕組みとを設けるのが望ましい（PF 9.3）。

i) 変更されたSkillは、ALPS定義ProcessのSkill検証による確認を経るのが望ましい。

j) Skill間の授受に起因する不整合および再作業を、改善機会の識別に用いてよい。

**代表的なInput**: 検証済みのSkill Description、変更要求、適用状況、Tailoring指針、影響当事者からのInput、実行および意思決定の記録、教訓ならびに測定結果。

**代表的なOutput**: 管理されたSkill資産、Tailoring済みSkill、Tailoringの決定および根拠、評価結果、優先順位付けされた改善機会、Skillへの変更要求ならびに廃止の決定。

## 8. Skillの実行構造および相互関係

### 8.1 Concurrency、Iteration、RecursionおよびIntegration

Skillは、必ずしも直列に実行される必要はない。次の実行構造を適用できる（PF 6.1）。

a) **Concurrency** — 同じ構造階層のうえで、二つ以上のSkillを並行して適用すること。

b) **Iteration** — 同じ階層で、同じSkillまたはSkillの集合を反復して適用すること。問題の解決およびOutputの精緻化に必要な範囲で続けるのが望ましい。

c) **Recursion** — 適用対象の連続する構造階層に、同じSkillまたはSkillの集合を反復して適用すること。ある構造階層で適用されたSkillのOutputは、次の構造階層で適用されるSkillのInputになり得る。

d) **Integration** — 同じ階層のうちでの完全性と、異なる階層のあいだでの一貫性とを確保すること。

これらの関係は実行順序を規定しない。実際の流れはTailoringによって定め、Outputの変更が他のSkillのInputに及ぼす影響を考慮する（PF 6.2）。

### 8.2 Skill間のインターフェース、授受およびトレーサビリティ

Skill間のインターフェースおよび授受は、提供側のOutputと受領側のInputとの対応として扱う。インターフェースは、独立したSkill要素ではない。あらかじめ定義されていない授受は、Tailoringによって追加できる（PF 4.4）。

複数のSkillを構成して適用する場合、提供側のOutputと受領側のInputとの対応を明示する必要がある（7.4.3 d)）。

Skillを並行的、反復的または再帰的に適用する場合、共有される、または相互に依存する情報項目と、それらの間にある参照関係または変更関係を、適用上必要な範囲で識別するのが望ましい。同一の情報項目が複数のSkillによって変更される場合、その情報項目の整合性、状態および変更の取扱いを、品質リスクに応じて定める必要がある。

Outputの変更が他のSkillのInputに影響する場合、影響を受けるSkillおよび対応関係を識別し、必要な再評価を行うのが望ましい。

Outputの品質が後続のOutcomeまたはステークホルダーによる受入れに影響する場合、その判定条件および必要な証拠を、Entry Criteria、Exit Criteria、レビューまたはDecision Gateに関連付けるのが望ましい。

Traceabilityは、Outcome、Activity、Taskおよび情報項目を対象とするのが望ましい。この対応関係は、整合性およびProcess Assessmentの根拠となる（PF 4.4）。

注記: 授受の対応を明示することは、情報項目の意味、範囲、状態および品質条件が、Skill間の受け渡しで失われることを防ぐ。

### 8.3 Skill View

Skill Viewは、特定の関心またはPurposeについて、複数のSkillにまたがるActivityおよびTaskを構成する（PF 5.3）。

独立したProcess境界を与える場合は、5.4に従って別のSkillとして記述できる。

a) すべてのSkill Viewは、そのName、PurposeおよびOutcomeを示す必要がある。

b) Skill Viewには、Outcomeを達成するために、既存のSkill Modelから選択したActivityおよびTaskに加えて、適応したActivityおよびTask、またはSkill Viewに固有のActivityおよびTaskを含めてよい。

c) Skill Viewには、それらのActivityおよびTaskを適用するための説明と指針を含める必要がある。

d) Skill Viewでは、各ActivityおよびTaskの出典と、それが選択、適応または新規のいずれであるかを、明示する必要がある。既存のSkill Modelから選択した要素は、その出典を維持する必要がある。

e) 適応した要素およびSkill Viewに固有の要素は、元のSkill Modelを変更したものとしては扱わない。これらの要素は、TailoringまたはSkill Modelへの正式な採用が行われない限り、元のSkillへのConformanceには算入しない。

f) 特定のSkill Modelを運用する際には、既存SkillのActivityおよびTaskだけを用いる、制限付きのSkill Viewを採用してよい。この方式のもとでは、Skill Viewに固有のActivityおよびTaskを含めてはならない。

g) Skill Viewには、Skillのあいだの接続と、その構成に用いたSkillの出典を示してよい。

## 9. Control、ConstraintおよびEnabler

### 9.1 FrameworkレベルのControlおよびEnabler

FrameworkレベルのControlおよびEnablerには、適用範囲、例外およびTailoringの可否を明示する必要がある（PF 4.5）。

宣言された適用範囲のSkillに共通する要素は、個々のSkillで反復せず、一度だけ宣言してよい（PF 4.1および4.5）。

複数のSkillに共通して適用される情報資源は、その機能に応じて、FrameworkレベルのControlまたはEnablerとして宣言できる。Skillによって変換される項目は、InputまたはOutputとして扱う。これらの分類は、情報資源の形式または配置ではなく、Skillの実行において果たす機能に基づく必要がある。

### 9.2 SkillレベルのControlおよびConstraint

ControlおよびConstraintは、Skill実行の条件または許容境界を宣言する。Controlは、適用法令、規制要求、方針、任意規格への適合または合意に由来し得る。Constraintは、Skillの外部にある環境要因または適用条件に由来し得る（PF 4.1および4.5）。

ControlまたはConstraintの記述は、6.3.7に定める主たる機能に従って分類する必要がある。

ControlおよびConstraintは、Skill Descriptionの独立した節として記述しても、他のSkill要素に関係する条件として記述してもよい。一般Skillに必要な時間的関係は、Constraintとして明示的に宣言するのが望ましい（6.2 c)）。

### 9.3 Enabler、能力およびツール

人間またはAgentの能力、ツールおよび技術は、EnablerとしてSkillを支援する（PF 4.1および4.5）。

Skillを実行する人的資源および自動化された資源（Agent、モデル、実行環境、ツール）は、Process Inputとしては扱わない（PF 4.1および4.2）。これらを要素として記述する場合、Enablerとして記述する必要がある。

注記: Agent、モデル、ツールおよび実行環境をEnablerとして扱うことは、Skillが変換する対象と、変換を実行する能力との混同を防ぐ。

## 10. Entry/Exit Criteria、Decision Gateおよびレビュー

### 10.1 Entry CriteriaおよびExit Criteria

a) Entry CriteriaはSkillを発動できる条件を表す。適用可能性の判定に用いる参考情報として、その要約を発見層に置くのが望ましい（5.5）。

b) Exit CriteriaはSkill Instanceを完了できる条件を表す。Exit Criteriaは、Outcomeの達成状況の判定と関連付けるのが望ましい。

### 10.2 Decision Gate

Decision GateはSkill Descriptionの構成要素ではなく、Skillの適用を制御する意思決定機構として扱う（PF 8.1）。

a) Decision Gateでは、Purpose、Outcome、適用条件およびリスクに基づくDecision Criteriaを用いて、状態遷移の可否を判断する（PF 8.1）。

b) Decision Gateの頻度、範囲および形式性は、適用状況に応じて調整できる。

c) 意思決定、その根拠および前提を記録するのが望ましい（PF 8.1）。

d) 通過の判断は、証拠に基づくのが望ましい。Decision Criteriaは、適用状況の変化に応じて再評価するのが望ましい。

注記: 不可逆的または高影響の行為に先立つ確認および人間へのエスカレーションは、Decision Gateの適用形態である。Decision Gateは、そのような外部作用が生じる前に、保留、変更または中止を判断できる統制点を適用に設ける。既存要素によるHuman Oversightの構成は、付録Dに示す。

### 10.3 レビューおよび監査

レビューは、合意された基準を用いて、Skillの実績、OutputおよびOutcomeの達成状況を評価する。監査は、Skill、Outputおよび要求事項への適合を示す証拠を詳細に調べ、必須属性および適用される要求事項が満たされていることを確認する（PF 8.2）。

Outputが別のSkillまたはステークホルダーに引き渡される場合、そのOutputが意図されたInputまたは成果として利用可能であることを、適用される基準に照らして評価するのが望ましい。

レビューおよび監査は、適用先のニーズとリスクに応じてTailoringし、Entry Criteria、Exit Criteriaおよび問題への対応を定めるのが望ましい（PF 8.2）。

## 11. TailoringおよびSkill Instantiation

### 11.1 Tailoringの規律

Tailoringは、ALPS管理ProcessのSkill Tailoring（7.5.2）に従って実施する必要がある。その要求事項は、Tailored Conformance（12.3）の前提となる。

注記: TailoringをALPS管理Processを通じて実施するよう要求することは、Skillの意味、規範上の強さまたは適用可能性が記録なく変更されることを防ぐ。

### 11.2 Tailoringの水準

共通水準のTailoringでは、外部規格（本規格を含む）を、想定する適用領域に共通するニーズに適合させる。個別水準のTailoringでは、その共通Skillを、特定の適用対象のニーズに適合させる（PF 7.2）。

### 11.3 Skill Instantiation

品質リスクによって正当化される場合、Skill Instanceを詳細化し、Instance固有の成功基準、ActivityおよびTaskを特定できる（PF 7.4）。

## 12. Conformance、CapabilityおよびAssessment

### 12.1 適合の対象

本規格に関する適合は、次の対象について主張できる。いずれの主張においても、対象と、選択した基準とを明示する必要がある。

a) **記述適合** — Skill Description（またはSkill View）が、箇条4〜6（Skill Viewについてはさらに8.3）の該当する要求事項を満たすこと。Skill Packageを適合対象に含める場合は、そのPackageが5.7の該当する要求事項を満たすこと。

b) **Reference Model適合** — Skill Modelの定義、適用または管理について、箇条7の三つのProcessのうち宣言したProcessに対するConformance（12.2、12.3）が成立すること。

c) **実行適合** — Skillの実行（Skill Instance）が、宣言されたSkillに対するConformanceの基準（12.2、12.3）を満たすこと。

### 12.2 Full Conformance

Full Conformanceは、Outcome、Taskまたは双方へのConformanceとして主張し、選択した基準を明示する必要がある。双方を選択する場合は、双方を満たす必要がある（PF 8.3）。


a) **OutcomeへのFull Conformance**は、宣言したSkillまたはReference Model Processのすべての必須Outcomeを達成することを要求する。この方法では、適合Processの実装方法に大きな自由度を認め、ActivityおよびTaskを指針として扱う。

b) **TaskへのFull Conformance**は、宣言したSkillまたはReference Model ProcessのActivityまたはTaskにおいて、**〜する必要がある**または**〜してはならない**と記述されたすべての要求事項を満たすことを要求する。推奨事項、許容される行為および通常実施される行為は、その規範属性だけを理由としてTaskへのFull Conformanceの必須条件にはならない。この方法を選択する場合、Outcomeを指針として扱う。


Reference ModelへのConformanceについて、ProcessへのOutcome Conformanceを主張できる単位は、ALPS定義Process、ALPS適用ProcessおよびALPS管理Processである。個別の構成Activityについて独立したOutcome Conformanceを主張してはならない。

### 12.3 Tailored Conformance

Full Conformanceを満たさないSkillまたはReference Model Processには、Tailored Conformanceを主張してよい。その主張では、ALPS管理ProcessのSkill Tailoring（7.5.2）に従ってTailoringしたSkillまたはProcessと、その適用範囲とを宣言する必要がある。また、その適用範囲に残されたOutcomeと、ActivityおよびTaskに含まれる要求事項とを満たしたことを示す必要がある（PF 8.3および8.4）。

Reference Model Processを構成するActivityの一部だけを適用する場合、そのActivityへの独立したProcess Conformanceを主張してはならない。親ProcessのTailoringした適用範囲として宣言し、Tailored Conformanceの基準を用いる必要がある。

### 12.4 CapabilityおよびAssessment

Capabilityは、Conformanceとは別の評価次元として扱う。ActivityおよびTaskを具体的に実行する場合には、Outcomeだけを達成する場合よりも、より高いCapability水準が必要となることがある。ただし、Capability水準だけによってConformanceが成立するものではなく、ConformanceだけによってCapability水準が定まるものでもない（PF 8.5）。

SkillのOutcomeならびに三つのProcessのPurposeおよびOutcomeは、Process Assessmentと有効性評価に利用できる（PF 8.5、7.5.3）。

Skill PackageのAssessmentでは、基準となるSkill Descriptionの存在、必須の参照先を対象環境から特定して取得できること、Skill Descriptionと付随資源との整合性、付随資源の役割および利用条件、ならびに変更後の再検証を評価対象にできる（5.7、7.3.3、7.5.1）。

---

## 付録A（参考） Skill DescriptionおよびSkill Packageの例

### A.1 本付録の位置付け

本付録は、特定の形式を要求しない参考例である（1.2）。

### A.2 記述例: 議事録整備Skillの`SKILL.md`

次の`SKILL.md`例では、`name`をSkill Nameに対応する識別子、`description`をSkill Discovery Descriptionとして用いる。

```markdown
---
name: consolidate-meeting-minutes
description: 会議メモ、書き起こし、配付資料から、決定事項、実行事項および未決事項を抽出し、元の記録との対応を維持した議事録を作成する。会議記録の整理、議事録の作成または会議後のアクション整理を依頼されたときに使用する。ALPS準拠。
---

# 議事録整備Skill

## Purpose

本Skillは、会議の記録から、決定事項、実行事項および未決事項を判別できる状態を確立する。

## Outcomes

本Skillが成功すると、次の状態が成立している。

a) 会議における決定事項が識別される。

b) 実行事項とその期限が識別される。

c) 未決事項が識別される。

d) 整備された内容と元の記録との対応が追跡可能である。

## Entry Criteria

- 会議の記録が利用可能である。
- 整備の対象範囲が明示されている。

## Exit Criteria

- すべてのOutcomeの達成状況が判定されている。
- Outputが受領側に引き渡されている。

## 代表的なInput

会議の記録（メモ、書き起こし、配付資料）。

## 代表的なOutput

整備済み議事録。

## ActivityおよびTask

以下の記載順序は、実行順序を規定しない。

### 記録の把握

- 整備の対象範囲および記録の欠落を識別する必要がある。
- 不明瞭な記載を、推測によって補完してはならない。
- 適用される秘密情報の取扱方針を適用する必要がある。
- 通常、参加者および議題の一覧を確認する。

### 事項の抽出

- 決定事項、実行事項および未決事項を区別して識別する必要がある。
- 元の記録に記載のない決定事項を、Outputに含めてはならない。
- 各実行事項に期限を対応付けるのが望ましい。
- 各事項を優先度別に分類してよい。

### 確認可能性の確立

- 抽出した事項と元の記録との対応を維持する必要がある。
- 抽出した事項と元の記録との対応を確立した後に、Outputを受領側へ引き渡す必要がある。
- 元の記録から確認できない事項を、確認を要する事項として明示するのが望ましい。

## Constraint

- Outputに含められる事項は、元の記録によって裏付けられる決定事項、実行事項および未決事項に限られる。
- 抽出した事項と元の記録との対応が確立された状態を、引渡し可能となる条件とする。

## Control

- 適用される秘密情報の取扱方針。

## Enabler

- 書き起こし支援ツール
- 分野の用語集
- 実行主体の言語処理能力

## Common Approachおよび実務上のヒント

この節は参考情報であり、規範上の強さを持たない。

- 決定事項は、合意または承認を表す表現の近傍に現れることが多い。
- 長大な記録では、議題単位のIterationによって段階的に精緻化できる。
```

注記1: `description`は、Skillが行うことと、そのSkillを使用する状況とを記述し、Skillの選択前に利用できるようにする（3.11）。

注記2: 「整備済み議事録」はOutputであって、Outcomeではない（6.3.3）。Constraintは引渡し可能となる条件を宣言し、対応する引渡し行為はTaskに記述している（6.3.7、9.2）。EnablerはInputではなく（9.3）、本Skillは実行主体を規定しない（5.3）。

### A.3 ファイルベースSkill Packageの構成例

次の構成は、5.7をファイルベースのEnvironment Bindingとして適用する場合の参考例である。この構成および名称は要求事項ではない（1.2）。`SKILL.md`以外の格納区分は任意であり、必要な付随資源がある場合にだけ設ける。正本となるSkill Descriptionは、発見層および実行層双方の意味上の正本であり、Environment Bindingはその意味または規範上の強さを変えずに、発見情報をfrontmatterまたは別の登録情報へ投影できる。

```text
<skill-name>/
├── SKILL.md
├── references/
│   └── <reference>.md
├── scripts/
└── assets/
```

| 構成要素 | ALPS上の位置付け |
|---|---|
| `SKILL.md` | Skillの正本となるSkill Description。本例のEnvironment Bindingではfrontmatterが発見層の情報を投影し、本文が実行層の情報を提供するが、ALPSはこの物理構造を要求しない。 |
| `references/` | 必要に応じて読み込まれる参考情報。個々のファイル名は規定しない。 |
| `scripts/` | 再現性または信頼性を支援する実行資源。通常、Enablerとして扱う。 |
| `assets/` | Outputの作成に用いる資源。機能に応じてInput、OutputまたはEnablerとして扱う。 |

## 付録B（参考）Process Frameworkとの対応

| PF 箇条 | 主題 | 本規格の対応箇条 |
|---|---|---|
| 1.1 | Process、Process DescriptionおよびProcess Instance | 5.1、5.8 |
| 1.2〜1.3 | 必須要素、任意の詳細および二部構成 | 3.11、5.1、5.5、6.1 |
| 1.4 | 記述および解釈の規則 | 4.1、6.2、6.3.8 |
| 2.1〜2.3 | Name、Purpose、Outcome、Output、ActivityおよびTask | 6.3.1〜6.3.6 |
| 3.1 | 境界、粒度および凝集性 | 5.4 |
| 3.2 | 実行主体との関係、部分集合の選択 | 5.3、7.2 e) |
| 4.1〜4.2 | 機能による分類および変換 | 5.2、5.8、6.3.6〜6.3.7、7.2 c)、箇条9 |
| 4.3 | Entry CriteriaおよびExit Criteria | 10.1 |
| 4.4 | Traceabilityおよび受け渡し | 8.2 |
| 4.5 | FrameworkレベルのControlおよびEnabler | 9.1 |
| 5.1〜5.2 | Model、Frameworkおよびライフサイクルモデル | 3.5、3.6、5.6、5.8、7.1〜7.2 |
| 5.3 | Process View | 5.8、8.3 |
| 6.1〜6.2 | Concurrency、Iteration、RecursionおよびIntegration | 8.1 |
| 7.1〜7.4 | TailoringおよびInstantiation | 7.5.2、箇条11 |
| 8.1〜8.2 | Decision Gate、レビューおよび監査 | 10.2〜10.3 |
| 8.3〜8.5 | Conformance、CapabilityおよびAssessment | 箇条12 |
| 9.1〜9.3 | 展開、標準、評価および学習 | 7.5.1、7.5.3 |

## 付録C（参考）関連文書

次の文書は、ALPSに関連する。これらは参考情報であり、ALPSの引用規格ではない。ALPSへのConformanceは、これらへの適合を要求するものでも、成立させるものでもない。

### C.1 Agent Skills Specification

[Agent Skills Specification](https://agentskills.io/specification)は、`SKILL.md`を中心とし、スクリプト、参考資料および資産のための任意のディレクトリを伴う、ファイルベースの公開形式を定義する。この形式をALPS準拠のSkillに用いる場合、この形式はSkill Packageの実装形態を提供し、ALPSはProcess Descriptionの意味論、ライフサイクルおよびConformanceの規則を提供する。ALPSは、この実装形態を要求しない（1.2 a)）。

### C.2 AGENTS.md

[AGENTS.md](https://agents.md/)は、リポジトリの適用範囲に応じた文脈および指示をコーディングAgentに提供するための公開形式である。`AGENTS.md`は、ALPS準拠Skillの発見、選択、適用および管理をAgentに指示し、リポジトリのControlおよびConstraintを示すことができる。`AGENTS.md`自体はSkill Descriptionではなく、Process Framework、本規格またはSkill Descriptionの意味も規範上の強さも変更しない。

### C.3 ライフサイクルProcessおよびProcess記述に関する規格

次の規格は、関連する分野におけるライフサイクルProcessおよびProcessの記述を扱う。

- ISO/IEC/IEEE 15288 — システムのライフサイクルProcess
- ISO/IEC/IEEE 12207 — ソフトウェアのライフサイクルProcess
- ISO/IEC/IEEE 24774:2021 — Process記述の仕様

これらの規格は、当該文書を併せて用いる読者のために挙げる。本規格およびProcess Frameworkの表現は独立に作成したものであり、これらの規格の本文、図、表、例または翻訳を転載していない。ALPSは、これらを発行する機関によって策定、承認または認証されたものではない。

## 付録D（参考）Agent文脈におけるHuman Oversight、Accountabilityおよび証拠

### D.1 本付録の位置付け

本付録は参考である。Skill要素、要求事項または適合基準を追加せず、PFおよび箇条1〜12の意味も規範上の強さも変更しない。ここに集めた事項は、確立した実務ではなく検討途上の論点である。このため、本付録は適用および改善のための参考指針に限られる。

### D.2 既存要素によるHuman Oversightの構成

Human Oversightは、Skill Descriptionの独立した要素ではない。監督を必要とする適用文脈は、次の既存の構成概念を組み合わせて表現できる。

- 実行または判断の基礎に方向を与えるControl
- 許容される実行を制限するConstraint
- 人間の能力を提供するEnabler
- 発動および完了を条件付けるEntry CriteriaおよびExit Criteria
- 不可逆的または高影響の行為に先立って適用するDecision Gate
- 実行および意思決定の記録
- ALPS適用ProcessおよびALPS管理Processにおける判断

監督の形態、介入の粒度および条件、決定権限ならびにエスカレーション先は、適用状況のリスク、関係する作用の影響および可逆性、不確実性の程度、ならびに関係する人間およびAgent双方のCapabilityに基づいて、適用文脈ごとに選択する。

非決定性、創発的挙動、監督者の認知負荷、automation biasおよび責任関係の不明確さは、監督の実施を難しくし得る。これらはAgent文脈に属する論点であり、本付録で扱う。PFの一般意味論の一部ではない。

### D.3 TraceabilityおよびAccountability

Traceabilityは、Input、判断、Task、Output、証拠および変更のあいだの関係を追跡できる性質である。

Accountabilityは、特定のSkill Instanceについて、意思決定権限、監督責任または応答責任を誰が負うかを定める関係である。

TraceabilityはAccountabilityを支援するが、それ自体で責任を割り当てない。一般的なProcess Descriptionは、実行者も組織構造も固定しない。具体的なProcess InstanceまたはSkill Instanceでは、必要な責任、権限、承認者およびエスカレーション先を定めることができる。ログおよび監査証拠は、事後の検証を支援し、責任関係の明確化を助ける。

### D.4 EnablerおよびConstraintとしての人間の能力

- 人間の専門性、判断能力および介入能力は、Enablerとなり得る。
- 認知負荷、応答時間および監督者の利用可能性は、Constraintとなり得る。
- 必要な監督能力を確保できない場合、Entry Criteriaが成立しないことがある。
- Skill InstanceのConformanceは、監督者または監督体制の一般的なCapabilityを証明しない。高いCapability評価も、個別実行のConformanceを証明しない（12.4）。

ALPSは、人間の能力水準、成熟度モデルまたは認証体系を定義しない。

### D.5 挙動が決定的でないSkillの証拠

Outcomeの定義および適合基準は変更されない。次の指針は、既存のSkill検証、Outcomeの証拠およびリスクに基づくTailoringの適用方法を示すものであり、要求事項を追加しない。

- 非決定性が重要な場合、単一の実行を、Outcomeの達成可能性またはCapability水準を確定するに足る証拠として扱わない。
- 代表的な適用文脈には、境界条件、異常条件および新規状況を含める。
- 一意の期待結果を定められない場合、代わりに許容条件、禁止条件または評価方法を定める。
- 実行記録には、観察された変動、証拠の限界および未解決の不確実性を残す。
- 反復試行または継続監視の要否は、品質リスクに応じて決定する。

非決定性および期待結果を一意に定めることの難しさは、検証とHuman Oversightの双方を難しくし得る。

### D.6 監督の結果をALPS管理Processに戻す

次に示すのは、ALPS適用Processが、実行記録および教訓としてALPS管理ProcessのSkill評価・改善に引き渡すことのできる代表的な情報項目である。

- 人間による承認および介入の記録
- 介入を必要とした条件
- Agentの提案を人間が変更または却下した事例
- 人間が検出できなかった失敗
- 説明またはログが判断に不十分だった事例
- automation biasまたは過剰介入の兆候
- 監督者の負荷および応答遅延
- Decision Gateの過不足
- 使用した証拠の品質および限界

---

（以上）

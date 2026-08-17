# Process Framework

> “Or, paraphrasing, pragmatism identifies meaning with formation of a habit,
> or way of acting having the greatest generality possible, or the widest range
> of application to particulars.”
>
> 「言い換えれば、プラグマティズムは、意味を習慣の形成と同一視する。
> ここで習慣とは、可能なかぎり高い一般性、すなわち個々の事例へ適用できる
> 最も広い範囲をもつ行為の仕方である。」
>
> — John Dewey, “The Pragmatism of Peirce” (1916), p. 711.
> 日本語訳：本リポジトリによる独自訳。

## 目的および優先関係

作業は、適用状況が変われば異なる形を取り得る。それでも実行主体や方法を固定せず、意図と境界を理解可能に保つことが、その記述の再利用可能性を支える。

このFrameworkは、Processを一つの実行主体、ツールまたは実行形態に固定することなく、その意図、境界、作業内容、適用状況、関係および評価を記述し理解するための共通かつ再利用可能な基盤を定める。

このFrameworkは、適用分野を問わず使用できる。一つのライフサイクルまたは方法を規定することなく、Processの記述、適用、評価および改善を支援する。

ALPSは、このFrameworkをAgent Skillへ適用する。ALPSの規定がこのFrameworkと競合する場合は、このFrameworkが優先する必要がある。

この日本語版では、「〜する必要がある」は要求を、「〜してはならない」は禁止を示す。「〜するのが望ましい」は推奨を、「〜しないのが望ましい」は非推奨を示す。「〜してよい」は許可を示す。「通常」などの表現は、要求を設けることなく、通例の実務を示す。「〜できる」「〜され得る」は、可能性または能力を述べる記述であって、規範属性を持たない。これらの語を大文字で表記する形式は用いない。

このFrameworkは、これらの語の意味に関する正本である。このFrameworkを適用する規格または記述は、その意味を継承し、再定義しない。

例、注記、記述上の慣例および判別用の問いは、その他の参考情報と同じく、規範ではない。これらは、Processの主要要素の意味または規範上の強さを変更してはならない。

## 1. 作業およびその記述

最初の区別は、作業と、その作業についての記述との間にある。一方は実行され、他方はその実行を異なる適用状況でも理解可能にする。

### 1.1 作業、記述および適用

**Process**は、明示したPurposeの下で、一つ以上のOutcomeを成立させるために実行する関連作業である。ProcessはInputに作用してOutputを生み出し、ActivityとTaskを一つのまとまりへ組み合わせる。Processの実行は、ステークホルダーへ便益を提供することを意図している。Processが果たす機能は、Purpose、OutcomeならびにActivityとTaskの集合によって定まる。

**Process Description**はProcessを説明する。Description自体はProcessの実行ではない。一般Processまたは特定のInstanceを表現できる。

**Process Instance**は、特定の適用状況におけるProcessの一回の適用である。Instance固有のDescriptionでは、必要な能力と資源、必須の受取項目と引渡項目、適用するControlとConstraint、および関係する時期を識別できる。

### 1.2 Descriptionに必要な中核

Descriptionは詳細さを増しても、意味の中心を変えずに保つことができる。

明示的で体系的なProcess Descriptionは、結果の一貫性を支援する。共通の記述構造は、標準Processの展開、Tailoring、改善およびProcess Assessmentも支援し、適用分野を問わず任意のProcess Modelに使用できる。

すべてのProcess Descriptionは、Name、PurposeおよびOutcomeを含む必要がある。これらの要素は、構造的な分解を要求せずに意図する結果を記述し、実施とAssessmentに共通の基準点を提供する。

Activity、Task、Input、Output、Control、Constraint、Enabler、Entry Criteria、Exit Criteriaおよび参考情報は任意である。DescriptionのPurposeと必要な詳細さに応じて含める。

Processは共通の属性によっても特徴付けることができる。選択した詳細さは、Processの成熟度、Capabilityまたは品質水準を特徴付けるために役立ち得る。

### 1.3 読者に応じた層

読者がProcessを読む理由は、理解する、適用する、評価する、改善するなど様々である。層を設けることで、Processを異なる意味へ分けることなく、各読者が必要な深さから読み始められる。

共通の記述形式では、概要と詳細記述の二部構成を用いることができる。概要には、Purpose、説明、InputとOutput、Activity、Common Approach、実務上の助言および優れた実務の要約情報を含めることができる。Activityは何を実行するかを示し、Common Approachと実務上の助言は適用を導く。

詳細部は、そのProcessに固有の事項を扱う。複数のProcessを横断する事項は、個別Processの詳細記述とは別に扱う。この二部構成は任意であり、必須の意味の中核を置き換えない。

概要、説明、Common Approach、実務上の助言、注記および例は、Processの理解または適用を支援できる参考情報である。

### 1.4 記述を読むための規則

文書上の順序は実行上の順序ではなく、流暢な表現は意味の区別に代わるものではない。

Process Descriptionは、Name、Purpose、Outcome、ActivityおよびTaskの機能を区別し、それらの内部整合性を維持する必要がある。

各文は一つの意味を担うのが望ましい。文章を短くするためだけに、独立した目的、結果または行為を結合することは避けるのが望ましい。各記述は、単独で参照しても意味を保つために十分な文脈を含むのが望ましい。補足説明は、注記または他の参考情報として分離できる。

一般ProcessのDescriptionは、特定の方法、技法、ツール、測定量、管理方法または実行順序を要求してはならない。方法と例は、Process要求とせずに手引きとして提供できる。

Procedureは、順序付けた手順を規定する。ActivityとTaskはProcessの作業を記述するものであり、記載順だけを理由として手順上の段階として解釈してはならない。

暗黙の時期、予定および順序は避けるのが望ましい。必要な時間的関係は、Constraintとして明示するのが望ましい。そのようなConstraintがない場合、特定の実行順序は要求されない。

記述は、要求、推奨、許可および通常の行為を区別し、その規範上の強さを明確にする必要がある。

## 2. 意図、成功および作業内容

Instanceが始まる前から、言葉は作業に見分けられる輪郭を与える。Nameは作業を指し示し、Purposeは存在理由を説明し、Outcomeは成功によって成立する状態を示し、ActivityとTaskはどの作業が属するかを表す。

### 2.1 作業とその理由の命名

Nameは作業を指し示し、Purposeはその理由を与える。両者の機能を分ければ、説明できない目的を名称だけに背負わせずに済む。

**Name**はProcessを識別し、Process Model内の他のProcessと区別する。Nameは簡潔な名詞句でなければならず、Processの中心的な関心を表さなければならず、Purposeの要約であってはならない。英語ではNameを“process”という語へつなげるのが望ましいが、これは意味上の要求ではなく言語上の規約である。

**Purpose**は、Processを実行する、まとまりをもつ一つまたは複数の上位目的を示す必要がある。Purposeは、有効な実施によって期待するOutcomeを包含する。

隣接するProcessの範囲が重なって見える場合、PurposeはProcess境界も明確にするのが望ましい。Purposeは簡潔にし、可能な限り一文とするのが望ましい。ActivityまたはOutcomeを要約したり、独立した目的を結合したりすることは避けるのが望ましい。補足説明は参考情報へ置くことができる。

### 2.2 成功と生み出すものの区別

成功と生産はしばしば連れ立つが、答える問いは異なる。

**Outcome**は、Processによって達成する測定可能で具体的な結果状態である。Outcomeは観察可能かつ評価可能である必要がある。OutcomeはOutputではなく、文書、記録または情報項目を作成したことだけをOutcomeとして記述してはならない。

各Outcomeは、一つの肯定的で観察可能な状態を宣言文で確立する必要がある。英語のOutcomeでは現在時制の動詞を用いる必要がある。独立した複数の結果を一つのOutcomeへ結合してはならない。

一般ProcessのOutcomeは、そのProcessを適用できる全範囲で意味を保つ必要がある。Outcomeの集合はPurposeに対して十分でなければならず、各OutcomeはPurposeに関係する必要がある。各Outcomeは、単独で読んでも意味を保つのが望ましい。

Outcomeは簡潔にするのが望ましい。ただし、簡潔さよりも一つの明確な意味を優先する。Outcomeの数は、固定された個数ではなく、Purposeの達成に必要な結果が定める。便益はOutcomeと区別することが望ましく、Purposeに関連付けた参考的な注記で説明できる。

**Output**は、Processによって生み出される製品、結果またはサービスである。OutputとOutcomeは関連し得るが、相互に置き換えることはできない。Outputは生み出されるものであり、Outcomeは達成を評価する結果状態である。あるProcessのOutputは、別のProcessのInputになり得る。

判別用の問いとして、その記述が作業から出ていく項目を示すのか、成功判断に用いる状態を示すのかを確認できる。前者はOutputを、後者はOutcomeを示す。この問いは定義の適用を助けるが、定義を置き換えない。

### 2.3 作業の編成および記述

個々の行為をまとめながら全体への寄与を失わないとき、作業は理解可能になる。

**Activity**は、Process内のまとまりあるTaskの集合である。Activityは、関連する行為がProcessへどのように寄与するかを理解し、伝達できるように整理する。

十分な凝集性と詳細をもつActivityは、固有のPurposeとOutcomeをもつSub-processとして扱うことができる。ActivityとSub-processの集合は、すべてのProcess Outcomeを網羅し、Process Purposeを満たす必要がある。ActivityとOutcomeを一対一に対応させる必要はない。

一つのActivity内のTaskは、そのActivity外のTaskよりも相互に強く関連するのが望ましい。Activityは、Process全体よりも狭い連続的または反復的な機能として扱う必要がある。Activityの集合はすべてのOutcomeを扱うのが望ましいが、Purposeを満たすための最小限の作業を超えてよい。

**Task**は、一つ以上のOutcomeを支援するための個別の行為を示す。各Taskは、その行為が要求、推奨、許可または通常の実務のいずれであるかを明確にする必要がある。Activityへ割り当てたTaskが、そのActivityの境界内で可能なすべての行為を列挙する必要はない。

1.4の時期および順序に関する規則は、ActivityとTaskの双方に適用する。

## 3. Process境界の設定

有用な境界は、恣意的な線でも壁でもない。互いに属する作業をまとめ、他のProcessとの授受を見えるままにする。

### 3.1 粒度および凝集性

Process、Sub-processおよびActivityの大きさに普遍的な境界はない。多数のTaskを含む重要なActivityは、別個に扱うことが有用な場合、Processとして記述できる。

通常は、主要なOutputとOutcomeを境界の判断に用いる。Activityの中間Outputは、通常、Process境界を定めない。

人の介入をほとんど必要としない密接に結び付いた自動化作業は、一つのProcess Descriptionへまとめることができる。分解は、境界、責務または関係の理解を改善するあいだは有用である。理解または利用を損なうことになる階層の追加は行わない。

境界内のOutcome、ActivityおよびTaskは、その作業が一つにまとまる理由を凝集した形で説明する。他のProcessへの依存は、実行可能な限り減らす。

### 3.2 一般Processが選択に委ねる事項

一般性は、作業を曖昧に残すことではなく、その機能を一つの実行主体または実施方法へ割り当てずに記述することで保たれる。

一般Processは、実行主体の構造または作業の各部分を誰が実行するかを規定しない。Processの実行に必要な機能上の関係を記述する。

Processを適用するときは、Purposeに応じてProcess、ActivityおよびTaskを選択できる。一つのProcessまたは複数のProcessの組合せを実行できる。

実行主体と実施方法を選択に委ねることは、一般Processの再利用可能性の一部であり、Process境界を不完全にはしない。

## 4. 境界を越え、方向付け、制限し、または支援するもの

境界を引けば、その周囲にある各要素を、境界で果たす役割によって理解できる。

### 4.1 機能による要素の分類

InputとOutputは、Processとその外部環境との接続を表す。Process DescriptionのPurposeと必要な詳細さに応じて用いる。

**Input**は、ProcessがOutputへ変換する項目である。Inputは、別のProcess、利用可能な情報源またはProcess外部の源から得ることができる。必須または代表的なInputの指定は任意である。

Processを実行する人、Agent、自動化、ツールおよび実行環境は、Inputではなく資源である。Process Descriptionで要素として表す場合は、Enablerとして扱う。

**Control**は、Processの実行またはその判断根拠を方向付ける。Controlは、適用法令または規制要求、方針、任意規格への適合、あるいは合意から生じ得る。

**Constraint**は、Processで許容される実行を制限する。Constraintは、環境またはProcess外部の適用条件から生じ得る。

**Enabler**は、実行を可能にし、または支援する能力を提供する。関係する能力、専門能力、ツールおよび技術はEnablerである。

同じ種類のArtifactまたは情報でも、Processごとに異なる機能を果たし得る。各出現箇所は、そのProcessで何をするかによって分類する。

| Processにおける機能 | 分類 |
|---|---|
| ProcessがOutputへ変換する。 | Input |
| 実行または判断根拠を方向付ける。 | Control |
| 許容される実行を制限する。 | Constraint |
| 実行を可能にし、または支援する。 | Enabler |

ControlとConstraintは、独立した節または他のProcess要素に付す注記として記述できる。

### 4.2 方法を規定しない変換の説明

変換の説明は短い筋道を描く。何かが入り、作業がそれに作用し、何かが出ていく。Control、ConstraintおよびEnablerは、変換される項目となることなく、その筋道を方向付け、制限し、支援する。

Outcomeの達成を実証できる場合、Outputの指定は任意である。Outputには、最終の製品またはサービスに必要な項目、妥当性確認または監査に用いる中間作業成果物、および他の製品またはProcessで再利用できる資産を含めることができる。Outputの主要な種類は、Artifactと情報項目である。

代表的な変換の説明は、Input、ActivityおよびOutputを関連付ける。ActivityがInputを変換し、Enablerがその変換を支援し、Controlが実行を方向付け、または制約する。

Process群の結果は、文書、Artifactまたはモデルへ記録されることが多い。Outputに名称を付けただけでは、文書の作成を要求しない。

代表的なInputとOutputは、実行可能な一つの方法を示す。唯一の方法を規定しない。Processは、代表的な流れだけでなくProcess Description全体から理解するのが望ましい。

### 4.3 適用の両端にある条件

開始と完了は、単なる時間上の位置ではなく、条件によって区切られる。

**Entry Criteria**は、Processを開始できる条件を示す。**Exit Criteria**は、Processを完了できる条件を示す。適切に構成したProcess Descriptionは、関係するInputとOutputに加えて、これらのCriteriaを含む。

Entry CriteriaとExit Criteriaは、Process DescriptionのPurposeと必要な詳細さに応じて用いる。

### 4.4 受け渡しおよびTrace link

Processは単独で完結するとは限らない。そのOutputは別のProcessのInputになり、Trace linkはそれらの関係を見える状態に保つ。

Trace linkは、Outcome、Activity、Taskおよび情報項目を対象とするのが望ましい。これらは、Process要素間の整合性を示す。このTraceの証拠は、Process Assessmentに用いるツールの設計にも利用できる。

有用な対応付けには、TaskとOutcome、InputとOutcome、およびOutputとOutcomeの関係がある。

Process間の受け渡しは、提供側のOutputと受領側のInputを対応付ける。方向と内容を明示すると、接続と依存関係を理解できる。事前に定義していない受け渡しは、Tailoringによって追加できる。

### 4.5 Framework内で共有する要素

共有要素はFrameworkの一貫性を保つことができるが、その及ぶ範囲は推測に委ねず、宣言によって定める。

FrameworkレベルのControlは、宣言した範囲内のProcessを方向付け、または制約する。FrameworkレベルのEnablerは、宣言した範囲内のProcessを支援する。

共通のControlまたはEnablerごとに、適用範囲、例外およびTailoringの可否を示す必要がある。Frameworkに属するという事実だけでは、共通要素がすべてのProcessへ適用されない。

宣言した範囲で共通するControlまたはEnablerは、各Process Descriptionで繰り返さず、一度だけ記述してよい。

共通Controlの例には、適用法令、規格、合意、適用方針、指令およびガバナンス上の要求がある。

## 5. 実施方法を固定しない再利用

再利用可能なDescriptionは、意味を一定に保ちながら、その周囲に異なる実施の形を許容する。

### 5.1 Framework、ModelおよびReference Model

次の構成体は、それぞれが果たす機能によって区別する。

| 構成体 | 機能 |
|---|---|
| **Process Model** | 相互に関係するProcessのFrameworkであり、複数のProcessから構成できる。 |
| **Process Reference Model** | 各ProcessをPurposeとOutcomeによって定義し、それらの関係を明示的な構造へ配置する。 |
| **Process Framework** | 適用分野に対応するProcessの集合と用語であり、Process Modelの構成と、Purposeに応じたProcessの部分集合の選択に用いる。 |

Process Frameworkは、望ましいProcess環境の確立、確立済み環境内での選択と組合せ、およびProcessとActivityに関する合意の基礎として使用できる。ライフサイクルモデルの構成にも使用できる。AssessmentではProcess Reference Modelとしても使用できる。このFrameworkは、Process Assessmentと改善の双方を支援する。

### 5.2 ライフサイクルモデルおよび適用状況の変化

ライフサイクルモデルは、選択した適用に応じてProcess間の関係へ順序を与える。それを記述する文書の箇条順が、それだけで時間上の順序へ変わるわけではない。

**ライフサイクルモデル**は、ライフサイクルProcessとActivityを、意思疎通と理解に用いる共通の基礎へまとめる。その詳細は、Process、Outcome、Process間の関係および順序によって表現する。

実際のProcess順序は、適用の目的と選択したライフサイクルモデルによって定まる。文書内の箇条の順序は、実行順序を規定しない。

対象または適用状況が変化したときは、Processの選択と時期の継続的な見直しを要する。Processの利用は、内外の影響に応じて動的に変化し得る。

### 5.3 Process View

Viewが変えるのは注目する角度であり、出所のProcess Modelではない。

**Process View**は、複数のProcessにまたがるActivityとTaskを一つの関心またはPurposeに沿って整理し、そのOutcomeを達成する方法を説明する。横断的な概念または特定のPurposeを可視化する。

すべてのProcess Viewは、Name、PurposeおよびOutcomeを示す必要がある。含めたActivityとTaskを適用するための説明と手引きを提供する必要がある。

Process Viewには、次のいずれかの出所をもつActivityとTaskを含めてよい。

| Viewにおける出所 | 扱い |
|---|---|
| Process Modelから選択 | 出所を識別し、選択であることを示し、その出所を維持する。 |
| Process ModelからAdaptation | 出所を識別し、Adaptationであることを示す。Adaptationは出所のProcess Modelを変更しない。 |
| View専用に作成 | 新設であることを示す。View専用の要素は出所のProcess Modelを変更しない。 |

Viewは、各ActivityとTaskの出所を明示し、選択、Adaptationまたは新設のいずれかを示す必要がある。Adaptationした要素とView専用の要素は、Tailoringまたは正式な採用によってそのProcessへ取り込まない限り、出所ProcessへのConformanceには寄与しない。

Process Frameworkは、Process Modelに既に存在するActivityとTaskだけを使用するようProcess Viewを制限してよい。制限されたViewには、View専用のActivityまたはTaskを含めてはならない。

Process Viewは、Process間の接続と、その構成に用いたProcessの出所も示してよい。

## 6. Processの接続および再適用

Processは一本の線に沿って進むとは限らない。同じ水準で並び、その水準へ戻り、別の水準で再び現れ、得られた構造全体で統合され得る。

### 6.1 独立した四つの関係

次の用語はそれぞれ異なる構造上の問いに答え、組み合わせて使用できる。

| 関係 | 変化または調整するもの |
|---|---|
| **Concurrency** | 同じ構造水準で、少なくとも二つのProcessを並行して適用する。 |
| **Iteration** | 構造水準を変えずにProcessまたはProcess群を再適用し、Process間の反復的な相互作用も含む。 |
| **Recursion** | 適用対象の連続する構造水準でProcessまたはProcess群を再適用する。 |
| **Integration** | 一つの水準内の完全性と、水準間の整合性を確立する。 |

Iterationは水準を変えずに戻り、RecursionはProcessまたはProcess群を構造水準間で反復する。Concurrencyが共存を扱うのに対し、Integrationは完全性と整合性を扱う。

Processの実行は直列の形態に限定されない。Iterationは、Outputを段階的に洗練し、判断と理解の進展を取り込み、Constraintを扱い、トレードオフを解消する。Iterationは単に許容されるのではなく、期待される。Processから生じる問題が解決するまで継続するのが望ましい。

Recursionでは、ある水準のOutputが、次の水準で適用するProcessのInputになり得る。

### 6.2 流れおよび変更の伝播

Concurrency、IterationおよびRecursionは、時期または順序を暗示しない。実際の流れは、適用上のニーズに基づくTailoringによって定める必要がある。

IterationまたはRecursionがOutputを変更すると、影響を受けるProcessのInputも変化する。

## 7. 一般Processから一つの適用へ

一般Processは二つの異なる仕方で具体化する。適用する形をTailoringし、一回の適用をInstantiationする。両者は同時に行われ得るが、同じ変更を指すものではない。

### 7.1 Adaptationおよび厳密さ

**Tailoring**は、ライフサイクルモデルまたはProcessを、宣言した適用状況のニーズと条件へ適合させる統制されたAdaptationである。このようなモデルとProcessは、通常、すべての適用状況へ変更せずに適用できない。

Tailoringは、Activityを受容可能なリスク水準で実行するために十分な厳密さを設定する。厳密さが不足すると問題の可能性が高まり、過剰な厳密さはコストまたは日程のリスクを高め得る。

Tailoringは、通常、リスクと適用状況の変化に応じて適用期間を通して動的に継続する。その運用をレビューし、条件が必要とするときに改訂するのが望ましい。

### 7.2 Tailoringが変更できるもの

**共通水準のTailoring**は、外部規格を、意図する適用分野で共有されるニーズへ適合させる。

**個別水準のTailoring**は、得られた共通Processを一つの適用対象へ適合させる。

Tailoringでは、Outcome、Activity、Task、代表的なInputおよび代表的なOutputを削除、変更または追加できる。

### 7.3 Tailoring判断の確立

以前の答えを普遍的なものとして扱えば、適用状況は失われる。Tailoringは、前提、証拠、範囲および判断基準を見える状態に保つ。

Tailoringでは、適用上のリスク、要求、複雑さ、利用可能な能力と資源、および関係する規格を識別する必要がある。

候補Processまたはライフサイクルモデルは、適用条件、利用可能な専門性と経験、ステークホルダーの期待または要求、およびリスク許容度を用いて評価する必要がある。

Tailoringでは、影響を受ける当事者からInputを得なければならず、適用されるControlとConstraintに従う必要がある。

Tailoringの判断は、事実と証拠に基づくのが望ましい。範囲を明示するのが望ましい。前提およびCriteriaを識別するのが望ましい。Processまたはライフサイクルモデルを選択した根拠を記録し、維持するのが望ましい。

TailoringしたProcessの実績を継続的に評価する手段を確立するのが望ましい。

Tailoringには、宣言した適用状況を失わせる落とし穴がある。代表例には、別の適用対象でTailoringした基準を再度Tailoringせずに流用すること、念のためという理由だけですべてのProcessとActivityを含めること、一つの測定、リスクまたはControlを普遍的と扱うこと、事前に定めたTailoring済み基準を変更せず適用すること、および影響を受けるステークホルダーを除外することがある。

### 7.4 Process Instantiation

品質リスクに照らして詳細化が正当化される場合、**Process Instantiation**は、特定の対象と適用状況に対応するProcess Instanceを記述する。

Instantiationは、要求からInstance固有の成功Criteriaを導出し、それを達成するActivityとTaskを識別する。Processと個別要求との関係は、品質リスクの管理を支援する。

Tailoringは、適用するProcessまたはライフサイクルモデルを変更する。Instantiationは、適用するProcessの一回の適用を詳しく記述する。この区別は、TailoringしたProcessをInstantiationすることを妨げない。

## 8. 証拠、判断および主張

証拠は作業と判断を結び付ける。Gateでの判断を再検討可能にし、Conformanceの主張を検証可能にする。

### 8.1 Decision Gate

Gateは判断を明示するが、Process Descriptionの一段階になるわけではない。

**Decision Gate**はProcessの適用を統制する判断機構であり、Process Descriptionの構成要素ではない。

Decision Gateでは、後続のActivityへ進むこと、またはProcessの状態を変更することに伴う不確実性とリスクが受容可能かをDecision Criteriaによって判断する。Purpose、Outcome、適用条件およびリスク評価をCriteriaの根拠にできる。

Gateの頻度、範囲および形式性は、適用状況に合わせて調整できる。Gateの頻度が高い場合は、範囲を狭め、形式性を下げることができる。

Gateでの判断は、明示して記録するのが望ましい。選択肢には、継続、保留、変更、再実行または終了を含めることができる。それまでの結果の品質と、進行に伴うリスクを判断に用いる。

Gateの前には、必要な専門性と関係するInputを用いてReviewを実施するのが望ましい。Gateの通過は、Decision Criteriaを満たす証拠に基づくのが望ましい。適用状況の変化に応じて各GateでCriteriaを更新し、再評価するのが望ましい。

Gateで受け入れたOutputは、後続のActivityが依拠する基礎になり得る。判断、その根拠および前提は記録し、適用状況に必要な変更管理の対象とするのが望ましい。

### 8.2 ReviewおよびAudit

Reviewは、作業とその結果が合意したCriteriaに照らしてどのような状態にあるかを問い、Auditは、証拠がConformanceについて何を確立するかを問う。

**Review**は、合意したCriteriaに照らして、Processの実績、OutputおよびOutcomeの達成を評価する。

**Audit**は、Process、Outputおよび要求へのConformanceを示す証拠を詳細に調べる。必須属性と適用要求を満たしているか確認する。

ReviewとAuditは適用計画へ反映し、対象と方法に合わせてTailoringするのが望ましい。開始条件と完了条件を明確にし、予定だけでなくリスクまたは事象によって開始することは優れた実務である。

準備、実施および受入れの方法と条件を明確にし、必要な専門性と独立した観点を含めることは優れた実務である。問題を検出したときは、期限と完了条件をもつ明確な処置を設定し、追跡することも優れた実務である。

### 8.3 Full Conformanceの主張

Conformanceの主張は、単にProcessへ従ったと述べるものではない。選択した基準は、その主張が実証する条件を識別する。

ProcessへのFull Conformanceは、Outcome Conformance、Task Conformanceまたはその両方として主張する必要がある。Conformanceの主張は、選択した基準を識別する必要がある。両方の基準を主張する場合は、両方の条件を満たす必要がある。

二つの基準は異なる問いに答え、異なる義務を生じさせ得る。

| 基準 | Full Conformanceの条件 | 他の要素の位置付け |
|---|---|---|
| **Outcome Conformance** | 宣言したProcessのすべての必須Outcomeを達成する。 | ActivityとTaskを手引きとして扱うため、実施方法の自由度が高い。 |
| **Task Conformance** | 宣言したProcessのActivityとTaskにおいて「〜する必要がある」または「〜してはならない」で示されたすべての要求を満たす。 | Outcomeを手引きとして扱う。推奨、許可および通常の行為は、記載されているという理由だけでは必須にならない。 |

Conformanceの主張に必要な範囲を超えてOutcomeを達成し、ActivityまたはTaskを実行できる。

### 8.4 Tailored Conformanceの主張

選択したFull Conformanceの基準を満たさないProcess群は、**Tailored Conformance**を主張してよい。

主張は、Tailoring ProcessによってTailoringしたProcessを識別し、適用範囲を宣言する必要がある。その範囲に残るOutcomeと、範囲に残るActivityおよびTaskに含まれる要求の充足を実証する必要がある。

### 8.5 CapabilityおよびProcess Assessment

CapabilityとConformanceは、異なる評価軸である。指定されたActivityとTaskの実行には、Outcomeの達成だけよりも高いCapability水準が必要になり得る。CapabilityだけではConformanceを確立せず、ConformanceだけではCapabilityを決定しない。

Process Outcomeは、Assessmentと改善で使用するProcess Reference Modelになり得る。Process PurposeとOutcomeは実施目標を示すため、単純な適合性評価以外の方法でも有効性を評価できる。

## 9. Processを有用に保つ

経験は、測定、教訓、比較および変更を通してProcessへ戻る。

### 9.1 管理および適用

Processの管理では、Processをどのように統制し、利用可能にするかを定義し、個別適用のためのTailoring手引きを提供するのが望ましい。

Processの有効性と効率の指標を設け、それらを実績評価に用いるのが望ましい。

適用するProcessを識別するのが望ましい。その実施と保守を文書化するのが望ましい。確立された支援方法と技法を使用し、特定のニーズにTailoring手引きを適用するのが望ましい。

管理上の手引きの変更は、影響を受ける利用者へ伝えるのが望ましい。改善機会を継続的に識別し、優先順位を付け、実施するのが望ましい。

### 9.2 標準Processおよび比較

複数の適用対象で標準Processを一貫して用いることは、反復可能で予測可能な実績を支援する。実証された実務と教訓を後続の適用へ利用し、新しい適用の開始を助け、継続的改善を進めることもできる。

Processのベンチマーキングは、実績を宣言したCriteria、適用される規格または他の比較対象と比較し、改善機会を見つける。比較では、実績、有効性、Conformance、便益およびコストを扱うのが望ましい。

### 9.3 測定、Assessmentおよび学習

測定はパターンを示し、教訓はそのパターンに文脈を与え、改善は両者を処置へ結び付ける。

Processの強みと弱みを評価し、ReviewとAuditを確立するのが望ましい。

Processの実績と有効性を把握するための測定を設けるのが望ましい。それらの測定を分析し、有効性を判断するのが望ましい。

教訓を収集して処置へ結び付け、Process変更の候補を分析する仕組みを設けるのが望ましい。

教訓は実行期間を通して収集し、計画したマイルストーンでも収集するのが望ましい。Processと実務を改善するため、教訓と測定を定期的にReviewするのが望ましい。

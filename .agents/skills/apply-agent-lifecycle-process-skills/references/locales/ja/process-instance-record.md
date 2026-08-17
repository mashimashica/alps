# Process Instance記録

この参考Bindingは、ProcessまたはSkillのInstance化時に作成し、実行後に同じファイルを完成できる可読な記録を支援する。品質リスク、適用Control、レビュー、授受またはConformance主張によって詳細化が正当化される場合に限って用いる。

これは任意のEnvironment Bindingである。このファイル形式、フィールドおよび検査規則はBinding固有であり、ALPSの要求ではない。見出しは人間向けであり、名称および順序を変更できる。可視的な``- `key`: value``フィールドおよび`kind`値によって、生成された記録を機械判読可能にする。

## 目次

- [Binding規則](#binding規則)
- [基本記録](#基本記録)
- [条件付きブロック](#条件付きブロック)
- [生成器および検査器](#生成器および検査器)

## Binding規則

- 一つのフィールドを一行に記録する。複数の値が必要な`evidence`などのフィールドは繰り返す。
- 単一値のフィールドを繰り返さない。矛盾する重複値はBindingを曖昧にするため、検査器が拒否する。
- Bindingフィールドは可視的な通常のMarkdownとして記録する。コードフェンス内またはインデントされたコードはBindingデータではない。raw HTMLおよびHTMLコメントは可視性がRendererに依存するため拒否される。
- 不足する値を推測しない。記録の準備中は値を空欄とし、状況に応じて後から完成または削除する。
- 管理された出典を識別する。出典を再度開かず記録単独でレビュー可能にすることが重要な場合は、適用される正確な`source_statement`を加える。低リスク用途では出典参照だけでも均衡が取れる場合がある。
- `instance_statement`は、適用固有の表現が必要な場合だけ用いる。その存在だけではTailoringの成立を意味しない。
- Instance固有の成功条件が必要な場合は`criterion`を加える。実行後に`result`および`assessment`を記録し、リスクに応じて`evidence`および`limitations`を加える。
- 意味、規範上の強さまたは適用可能性を変更した場合は`tailoring`ブロックを追加し、管理Processを適用する。この形式によってTailoringを暗黙に行わない。
- 授受およびConformanceブロックは、該当する場合だけ追加する。Conformanceブロックは主張を記録するものであり、形式および検査器はその主張を証明しない。

## 基本記録

次は代表的な配置であり、見出しの集合または順序を要求するものではない。

```markdown
# <記録タイトル>

## 適用の基礎
- `kind`: application
- `record_format`: process-instance-record/1
- `source`: <管理されたSkillまたはProcessの出典および版>
- `context`: <適用状況およびニーズ>
- `scope`: <適用範囲。関連する対象外範囲、または対象外なしの明示を含む>

## 意図するOutcome
- `kind`: outcome
- `source_statement`: <適用される正確なOutcome記述>
- `instance_statement`: <必要な場合の適用固有の表現>
- `criterion`: <必要な場合のInstance固有成功条件>
- `result`:
- `assessment`:
- `evidence`:
- `limitations`:

## Task
- `kind`: task
- `source_statement`: <適用される正確なTask記述>
- `instance_statement`: <必要な場合の適用固有の表現>
- `criterion`:
- `result`:
- `assessment`:
- `evidence`:
- `limitations`:
```

重要な場合は、`activity`、`purpose`、`input`、`output`、`entry_criterion`、`exit_criterion`、`control`、`constraint`、`enabler`、`exchange`または`decision`などの中核`kind`値を持つブロックを追加できる。ローカル拡張の`kind`には、例えば`x_review_note`のように`x_`接頭辞を付ける。これにより、中核`kind`の誤記と意図的な拡張を区別できる。検査器は`kind`フィールドを持たない説明用の節を無視し、すべてのInstanceに完全なALPSモデルを強制しない。

## 条件付きブロック

重要なOutput/Input対応には授受ブロックを用いる。完了時には状態を記録する。

```markdown
## 授受
- `kind`: handoff
- `provider`: <提供SkillまたはInstance>
- `output`: <Output>
- `receiver`: <受領SkillまたはInstance>
- `input`: <Input>
- `correspondence`: <意味、範囲および品質条件>
- `status`:
```

管理されたTailoringによって要素を追加、変更または除外した場合だけTailoringブロックを用いる。このBindingの検査器は、`basis`、`candidate_evaluation`、`decision`、`affected_party_input`および`controls_constraints`の値を要求する。`scope`および`rationale`は記録するのが望ましいが、検査器では任意とする。`before`、`after`、`assumptions_criteria`および`performance_assessment`も適用状況に応じた任意フィールドである。これらのフィールド名および一行表現はBinding固有であり、Tailoring判断の妥当性を証明しない。

```markdown
## Tailoring
- `kind`: tailoring
- `scope`: <推奨: 影響要素および適用範囲>
- `before`: <任意: 変更前の管理された記述>
- `after`: <任意: 変更後の承認された記述>
- `basis`: <リスク、要求事項、複雑性、利用可能な能力および資源、ならびに関連規格>
- `candidate_evaluation`: <適用条件、専門知識・経験、ステークホルダーの期待・要求事項およびリスク許容度に照らした候補Skillまたはライフサイクルモデルの評価>
- `rationale`: <推奨: 判断根拠>
- `decision`: <管理判断、および該当する場合はその解決可能な参照>
- `affected_party_input`: <影響当事者および取得したInput、または該当者なしの明示>
- `controls_constraints`: <適用ControlおよびConstraint、または該当なしの明示>
- `assumptions_criteria`: <任意: 前提および判断基準>
- `performance_assessment`: <任意: Tailoring済み適用の監視・評価方法>
```

Conformanceを主張する場合だけConformanceブロックを用いる。

```markdown
## Conformance
- `kind`: conformance
- `subject`: <主張対象>
- `scope`: <主張範囲>
- `basis`: <Outcome、Taskまたは双方>
- `claim`: <FullまたはTailored>
- `tailoring_decision`: <Tailoring詳細を局所的に再掲しない場合の管理されたTailoring判断参照>
- `remaining_requirements`: <Tailored Conformanceの場合に範囲へ残るOutcomeおよびActivity・Taskに含まれる要求事項>
- `evidence`: <主張を支える証拠>
```

Tailored Conformanceでは、Conformanceブロックの`subject`、`scope`および`remaining_requirements`によって、TailoringしたSkillまたはProcess、主張範囲、ならびにその範囲に残るOutcomeおよびActivity・Taskに含まれる要求事項を識別する。さらに、局所的な`tailoring`ブロックまたは詳細を解決できる`tailoring_decision`参照のいずれかを記載する。`tailoring_decision`参照は、Conformanceブロックの`scope`または`remaining_requirements`を置き換えない。ALPSの主張では、証拠によってそれらの残存Outcomeおよび要求事項の充足を示す必要があるが、checkerが検査するのは`evidence`フィールドの存在だけである。

## 生成器および検査器

生成器はCommand Lineで明示した値だけを転記する。Skillを読み取ってPurpose、Outcome、Task、規範属性またはTailoringを推定しない。内容全体を準備してから出力先へ原子的に配置するため、置換に失敗しても既存記録を切り詰めない。

```bash
python3 ../../../scripts/process_instance_record.py --locale ja new \
  --title "契約確認" \
  --source "contract-review SKILL.md、管理版2026-08-15" \
  --context "契約Aを社内承認前に確認する" \
  --scope "契約本文および提供済み別紙" \
  --outcome "重要な契約上の問題が識別されている。" \
  --task "適用される契約条項を確認する必要がある。" \
  --output contract-review.md

python3 ../../../scripts/process_instance_record.py --locale ja check --at instantiation contract-review.md
python3 ../../../scripts/process_instance_record.py --locale ja check --at completion contract-review.md
```

Instance化時の検査は、`record_format: process-instance-record/1`を持つ一つだけの`application`ブロック、出典、文脈、適用範囲および一つ以上の意図するOutcomeまたは成功基準を要求する。完了時の検査は、各Outcome、記録対象に含めたTask、独立した成功基準、および`criterion`を宣言した他の各ブロックの結果および判定も要求する。検査器が証拠を必須とするのはConformance主張だけであり、`claim`には`Full`または`Tailored`だけを認める。Tailored主張では`scope`および`remaining_requirements`に加え、局所的なTailoringブロックまたは`tailoring_decision`参照を要求する。それ以外の条件付きブロックは、存在する場合だけ検査する。これらの検査は本Bindingへの適合だけを確認し、真実性、Outcome達成、Tailoringの妥当性またはALPS Conformanceを証明しない。

# ALPS準拠`SKILL.md`の代表テンプレート

この資料は、読みやすいSkill Descriptionを起草するための参考例であり、特定の見出し、並び順、箇条番号または識別子を要求しない。Process Framework、ALPSおよび適用される実行環境の規則を優先する。

## テンプレート

```markdown
---
name: <lowercase-hyphen-name>
description: "<Skillが行うこと、使用する状況、および必要なら適用しない状況を簡潔に記述する>ALPS準拠。"
---

# <短い名詞句のSkill Name>

## Purpose

<本Skillが存在する理由となる、まとまりをもつ一つまたは複数の上位目的を簡潔に記述する。>
<必要な場合は、Purposeの意味を変えない範囲説明、対象領域または厳密さの考え方を、参考情報として続ける。>

## Outcomes

- a) <肯定的、観察可能かつ評価可能な一結果が成立している。>
- b) <一つの独立した結果が成立している。>
- c) <Purposeの達成に必要な結果が成立している。>

## Activities & Tasks

以下の見出し、Activity、Taskおよび番号は、内容を読みやすく示すためのものであり、手順または実行順序を定めない。Entry Criteriaは発動前の判定条件、Exit Criteriaは完了宣言前の判定条件であり、ControlsおよびConstraintsは記載位置にかかわらず適用される。

### <Activityの短い名称>

1. <要求事項となる行為>する必要がある。
2. <推奨する行為>するのが望ましい。
3. <許容する行為>してよい。
4. 通常、<通常実施する行為>する。

## Inputs

- <Skillによって変換される情報項目または成果物>
- <他のSkillまたは外部情報源から受け取る項目>

## Outputs

- <成果物または情報項目。Outcomeそのものと混同しない。>
- <受領側のInputとして利用できる項目。>

## Entry Criteria

- <Skillを発動できる条件。>

## Exit Criteria

- <Outcomeの達成状況を判定できる条件。>
- <Outputを引き渡せる条件。>

## Controls

- <法令、方針、規格、合意その他の実行を方向付ける事項。>

## Constraints

- <外部環境または適用条件に由来する制限。>

## Enablers

- <必要な能力、Agent、ツール、技術または実行資源。>

## Conformance

- <Conformanceを主張する場合の対象、適用範囲および基準。>
- <OutcomeまたはTaskを基準とする場合の充足条件。>

## Interfaces & Traceability

- <Outcome、Activity、Taskおよび証拠の対応を識別できるのが望ましい。>
- <Outputと受領側Inputの名称、意味および適用範囲を整合させるのが望ましい。>

## Bundled Resources

- [<参照資料>](references/<reference>.md): <役割と、読む条件。>
- `scripts/<script>.*`: <役割、使用条件および限界。>
- `assets/<asset>.*`: <発見、提示またはOutput作成における役割。>

## Common Approach

この節は参考情報であり、規範上の強さを持たない。

- <適用方法の一例または実務上のヒント。>
```

## 利用上の注意

- Name、PurposeおよびOutcomeは必須要素として保持する。他の節は、Purposeと必要な詳細度に応じて含めるのが望ましい。
- Purposeの最初の文と、その後に置く参考説明とを区別する。参考説明でPurposeを追加または変更しない。
- OutcomeはOutputの作成ではなく、結果が成立している状態として記述する。
- Taskは、一つ以上のOutcomeの達成を支援する個別の行為を表すことを主たる機能とし、その行為の対象と動作が判別できるように記述する。
- Constraint、判定基準または品質条件をTaskへ含める場合、それらを行為の対象または行為を方向付ける条件として扱い、Taskの主たる機能を個別の行為として維持する。
- 主たる機能が個別の行為ではない記述は、その機能に対応する別の要素へ置く。
- Taskごとに、要求事項、禁止事項、推奨事項、許容または通常のいずれかを規範語で判別可能にする。すべての種類を含める必要はない。
- Agent、ツールまたは実行環境はInputに含めず、Enablerとして扱う。
- 必須参照は解決可能である必要がある。Packageには、Skillの理解・実行またはOutput作成を直接支援する付随資源だけを含めるのが望ましい。
- Decision GateはSkill Descriptionの構成要素にせず、Skillの適用を制御する別個の意思決定機構として扱う。

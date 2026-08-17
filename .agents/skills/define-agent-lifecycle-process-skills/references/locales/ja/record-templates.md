# 定義Processの記録テンプレート

必要な記録だけを選択し、適用状況とリスクに応じてTailoringする。空欄を推測で埋めず、`未確認`、`該当なし`または`保留`として扱う。

## 1. Skillニーズ記録

```markdown
# Skillニーズ記録

- 記録ID:
- 状態: 候補 / 選定 / 見送り / 再検討
- ニーズまたは問題:
- 想定利用者:
- ステークホルダーと期待:
- 想定利用文脈:
- 反復性または影響度:
- 既存Skillとの重複・隣接・隙間:
- 期待便益:
- リスク:
- 費用または制約:
- 決定:
- 根拠と証拠:
- 未解決事項:
```

## 2. 要素間トレーサビリティ

Outcome参照およびTask参照には、安定ID、短い名称、見出し、リスト位置または短い引用など、適用状況に合う参照方法を用いる。

| Outcome参照 | 寄与するActivity | 寄与するTask参照 | 関連Input/Output | 検証証拠 | 状態 |
|---|---|---|---|---|---|
| | | | | | 未評価 / 適合 / 欠陥 / 対象外 |

確認観点:

- Activityおよび分離されたSkillの集合で、すべてのOutcomeを網羅する必要がある。
- Outcome、ActivityおよびTaskの対応関係を識別できるのが望ましい。
- 外部授受では、提供側Outputと受領側Inputの名称、意味および範囲を整合させるのが望ましい。
- Outputの変更が他のSkillのInputに影響する場合、影響を受けるSkillおよび対応関係を識別し、必要な再評価を行うのが望ましい。

## 3. 検証記録

```markdown
# Skill検証記録

- 対象Skill・版:
- 検証範囲: Skill Description / Skill Package / 両方
- Conformance対象: 記述 / Reference Model / 実行
- Conformance形態（Reference Modelまたは実行の場合）: Full / Tailored
- Conformance基準:
  - 記述: 適用するALPS箇条
  - Full: Outcome / Task / 双方
  - Tailored: TailoringしたSkillまたはProcessおよびその適用範囲、残存Outcome、Activity・Taskに含まれる要求事項
- 適用規範・Control:
- レビュー基準:
- 独立した観点:
- 代表的利用文脈:
- 境界事例:

## 結果
| 検証項目 | 証拠 | 判定 | 欠陥ID |
|---|---|---|---|
| | | 適合 / 不適合 / 未評価 | |

## 欠陥処置
| 欠陥ID | 内容 | 影響 | 対応 | 完了条件 | 期限 | 状態 |
|---|---|---|---|---|---|---|
| | | | | | | |

## 制限・前提
-
```

## 4. 採用Decision Gate記録

```markdown
# 採用Decision Gate

- 対象Skill・版:
- Decision Criteria:
- 参照した証拠:
- 未解決欠陥と残留リスク:
- 決定: 採用 / 条件付き採用 / 保留 / 再設計 / 却下
- 根拠:
- 前提:
- 適用条件:
- 次の受領先:
```

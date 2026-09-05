# リポジトリ作業指示

[英語正本](../../../AGENTS.md)

本指示はリポジトリに適用する。ユーザーが許可した範囲に従い、無関係な作業とユーザー作成データを保全する。`localization.yaml`は英語を正本、日本語を対応言語と定める。

## 正本の位置付け

| 対象 | 正本 |
| --- | --- |
| プロセスの意味、境界、参照、変更、評価 | [プロセスフレームワーク](../../../spec/locales/ja/process-framework.md) |
| プロセス記述とAgent Skillの対応付け | フレームワークに従う[ALPS Specification](../../../spec/locales/ja/ALPS-SPEC.md) |
| 配布する設計プロセス | [design-process-description](../../../skills/design-process-description/references/locales/ja/SKILL.md) |
| リポジトリ作業と配布 | 本ファイル |
| 草案作成の補助 | [テンプレート](../../../skills/design-process-description/references/locales/ja/SKILL-template.md)と[具体例](../../../skills/design-process-description/references/locales/ja/examples.md)。いずれも参考情報。 |

テスト、テンプレート、Host別manifest、アイコン、その他の表示資源からプロセス要件を推定しない。選択したSkillを適用する前に、その`SKILL.md`全文を読む。

## 配置と配布

| パス | 役割 |
| --- | --- |
| `skills/design-process-description/` | 唯一の配布Skill。ルートの英語`SKILL.md`が正本。 |
| `.agents/skills/design-process-description` | リポジトリ内の発見用に`../../skills/design-process-description`を指す相対symlink。 |
| `.agents/skills/review-alps/` | リポジトリの意味と配布をレビューする実ディレクトリ。Plugin Skillではない。 |
| `.agents/skills/sync-locales/` | 日英レビューの実ディレクトリ。Plugin Skillではない。 |
| `spec/` | Pluginルートに含める共有の規範正本。 |
| `spec/locales/ja/`、`docs/locales/ja/`、配布Skillの`references/locales/ja/` | 対応する翻訳。第二の正本ではない。 |
| `plugin.json`、`.claude-plugin/`、`.cursor-plugin/`、`.codex-plugin/` | ルートPlugin形式と、それぞれのHostアダプター。 |
| `assets/`およびSkillの`agents/`と`assets/` | 表示資源。 |

`skills/`を配布の唯一の正本とする。Hostは各規約とmanifestにより発見する。`.agents/skills/`はリポジトリ内の統合ビューであり、普遍的なHost規約ではない。checkoutに開発用Skillを含めても、それをPlugin Skillとして公開することにはならない。`spec/`への必須リンクが利用できるようPluginルートの配置を保つ。開発用Skillを`skills/`へコピーしない。

## 変更とレビュー

- 編集前に現在のファイルと作業対象の差分を確認する。無関係な作業を保全する。
- 仕様、Skill内容、リポジトリ案内、テスト、配布、表示が意味や境界に影響する変更では`review-alps`を使用する。
- 影響する日英の各ペアに`sync-locales`を使用する。開発用Skillには日本語のPlugin対応ファイルはない。
- プロセス記述の作成・レビューには`design-process-description`を用いる。
- 各Hostアダプターを、そのHost固有の形式と上記の配布配置に整合させる。
- 貢献とライセンスの要件には[CONTRIBUTING](CONTRIBUTING.md)を、リリース方針には[版管理](versioning.md)を適用する。

## 検証と提供

次の三種類の証拠を分ける。

1. 適用形式に照らしたAgent SkillとPluginの形式検証。
2. 必須ファイル、版、相対リンク、symlink、Host資源、配布境界のリポジトリ整合性検証。
3. 目的と成果の十分性、必要な詳細と義務、参照、評価の限界、日英の意味と規範強度の意味レビュー。

`.github/workflows/validate.yml`の検証のうち環境で可能なものを実行する。最低限、`python3 -m unittest discover -s tests -v`、`git diff --check`、変更したリンクの検査、新規ファイルを含む作業対象差分全体のレビューを行う。機械検証の成功は意味の妥当性やプロセス実行の成功を証明しない。

指摘、完了した検証、失敗または未実行の検証、限界を報告する。

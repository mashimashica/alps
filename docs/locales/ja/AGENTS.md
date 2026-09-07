# リポジトリ作業指示

[英語版](../../../AGENTS.md)

本指示はリポジトリに適用する。ユーザーが許可した範囲に従い、無関係な作業とユーザー作成データを保全する。`localization.yaml`は英語を基準言語、日本語を対応言語と定める。

## 参照する文書

| 対象 | 参照する文書 |
| --- | --- |
| プロセスの意味、境界、参照、変更、評価 | [プロセスフレームワーク](../../../spec/locales/ja/process-framework.md) |
| エージェント・ツール・情報・環境の設計 | [エージェント作業システムの設計原則](../../../spec/locales/ja/agent-work-system-design.md) |
| 二つの基盤のAgent Skillでの統合 | それぞれの対象について各参照元に従う[ALPS Specification](../../../spec/locales/ja/ALPS-SPEC.md) |
| 配布する設計プロセス | [design-process-description](../../../skills/design-process-description/references/locales/ja/SKILL.md)と[design-agent-work-system](../../../skills/design-agent-work-system/references/locales/ja/SKILL.md) |
| リポジトリ作業と配布 | 本ファイル |
| 草案作成の補助 | [テンプレート](../../../skills/design-process-description/references/locales/ja/SKILL-template.md)と[具体例](../../../skills/design-process-description/references/locales/ja/examples.md)。いずれも参考情報。 |

テスト、テンプレート、Host別manifest、アイコン、その他の表示資源からプロセス要件を推定しない。選択したSkillを適用する前に、その`SKILL.md`全文を読む。

## 配置と配布

| パス | 役割 |
| --- | --- |
| `skills/design-process-description/`、`skills/design-agent-work-system/` | 配布Skill。各ルートの英語`SKILL.md`を、そのプロセスの基準とする。 |
| `.agents/skills/<distributed-skill>` | リポジトリ内の発見用に`../../skills/<distributed-skill>`を指す相対symlink。 |
| `.agents/skills/review-alps/` | リポジトリの意味と配布をレビューする実ディレクトリ。Plugin Skillではない。 |
| `.agents/skills/sync-locales/` | 日英レビューの実ディレクトリ。Plugin Skillではない。 |
| `spec/` | Pluginルートに含める共有の規範文書。 |
| `spec/locales/ja/`、`docs/locales/ja/`、各Skillの`references/locales/ja/` | 対応する英語版の翻訳。 |
| `examples/` | 実働する対象Skillを含む、同梱する参照資料。Plugin Skillの発見対象外。ガイドの翻訳は`examples/locales/ja/`、対象Skillの翻訳はその`references/locales/ja/`に置く。 |
| `plugin.json`、`.claude-plugin/`、`.cursor-plugin/`、`.codex-plugin/` | ルートPlugin形式と、それぞれのHostアダプター。 |
| `assets/`およびSkillの`agents/`と`assets/` | 表示資源。 |

`skills/`をPlugin Skillの配布元とする。Hostは各規約とmanifestにより発見する。`.agents/skills/`はリポジトリ内の統合ビューであり、普遍的なHost規約ではない。checkoutに開発用Skillを含めても、それをPlugin Skillとして公開することにはならない。`spec/`と`examples/`へのリンクが利用できるようPluginルートの配置を保つ。開発用Skillと例のSkillは`skills/`の外に置く。

## 変更とレビュー

- 編集前に現在のファイルと作業対象の差分を確認する。無関係な作業を保全する。
- 仕様、Skill内容、リポジトリ案内、テスト、配布、表示が意味や境界に影響する変更では`review-alps`を使用する。
- 影響する日英の各ペアに`sync-locales`を使用する。開発用Skillには日本語のPlugin対応ファイルはない。
- プロセス記述の作成・レビューには`design-process-description`を用いる。
- 実現を支える構成、実装、有効性の設計・レビューには`design-agent-work-system`を用いる。共有する仕事の意味を維持し、統合規則はALPS-SPECに置く。二つの基盤仕様は、それぞれ独立して利用できる。
- 各Hostアダプターを、そのHost固有の形式と上記の配布配置に整合させる。
- 貢献とライセンスの要件には[CONTRIBUTING](CONTRIBUTING.md)を、リリース方針には[版管理](versioning.md)を適用する。

## 検証と提供

次の証拠を区別する。

1. 適用形式に照らしたAgent SkillとPluginの形式検証。
2. 必須ファイル、版、相対リンク、symlink、Host資源、配布境界のリポジトリ整合性検証。
3. 目的と成果の十分性、必要な詳細と義務、参照、評価の限界、日英の意味と規範強度の意味レビュー。
4. 失敗と不完全な結果を含め、定められた動作に照らしたツールと接続の検証。
5. エージェント・情報・ツール・環境を用いた代表的な仕事を通じ、仕事の成果と条件に照らした作業システムの有効性の評価。

`.github/workflows/validate.yml`の検証のうち環境で可能なものを実行する。最低限、`python3 -m unittest discover -s tests -v`、`git diff --check`、変更したリンクの検査、新規ファイルを含む作業対象差分全体のレビューを行う。機械検証の成功は意味の妥当性やプロセス実行の成功を証明しない。

指摘、完了した検証、失敗または未実行の検証、限界を報告する。

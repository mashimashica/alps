# ChatGPT Web・モバイルでALPSを使う

ChatGPTはアップロードしたAgent Skillをインストールできますが、Personal SkillはデスクトップとWeb／モバイルで別々に管理されます。そのためALPSでは、リポジトリ内の正本となるSkill Packageを変更せずに、三つの参照Skillを単体で利用できる形へ出力する手段を提供します。

> 利用可否はChatGPTのプランとワークスペース設定に依存します。管理されたワークスペースで利用する場合は、OpenAIの最新のSkillsドキュメントも確認してください。

## Skillを出力する

リポジトリのルートで次を実行します。

```console
python3 scripts/export_agent_skills.py --target chatgpt
```

`dist/chatgpt/`以下に、自己完結した三つのSkillディレクトリが生成されます。

```text
dist/chatgpt/
├── define-alps/
├── apply-alps/
└── manage-alps/
```

各ディレクトリには、ルートの`SKILL.md`、既存の同梱リソース、および`references/alps/spec/`以下へコピーされたALPSの共有規範文書が含まれます。通常はリポジトリ直下の`.alps/spec`を参照するリンクも、生成物の中だけで書き換えられるため、単体でアップロードした後も参照できます。

特定のSkillだけを出力する場合は、必要に応じて`--skill`を指定します。

```console
python3 scripts/export_agent_skills.py --target chatgpt --skill apply-alps
```

`dist/`以下は破棄可能な生成物であり、正本として保守する資産ではありません。

## Web／モバイル向けにインストールする

1. Web版ChatGPTで**Plugins**を開き、**Skills**を選択します。
2. **Create**から**Upload from your computer**を選択します。
3. 利用したい出力済みAgent Skillをそれぞれアップロードします。
4. 表示される案内に従い、Web／モバイル向けにSkillをインストールします。
5. モバイル版ChatGPTを開き、特定のALPS Processを明示したい場合は、たとえば`Use apply-alps to ...`のようにSkill名を指定します。

OpenAIの現行ドキュメントでは、Personal SkillはデスクトップとWeb／モバイルで別インストールとされています。デスクトップ側だけに追加したSkillは、モバイルへ自動同期されません。

## `skills/`をそのままコピーしない理由

ALPSの正本となるSkill Descriptionは、`.alps/spec`にあるリポジトリ共通の規範文書を意図的に共有しています。そのため、`skills/apply-alps`、`skills/define-alps`、`skills/manage-alps`だけをリポジトリ外へコピーすると、その参照が解決できません。exporterは、保守対象となるソース構造を維持したまま、アップロード向けクライアントで利用できる自己完結した搬送用コピーを生成します。

## 検証

exporterのテストは次で実行できます。

```console
python3 -m unittest tests/test_export_agent_skills.py
```

exporter自身も、各生成Skillについて、ルート`SKILL.md`、同梱された規範文書、およびリポジトリ外へ抜ける`.alps/spec`参照が残っていないことを検証します。

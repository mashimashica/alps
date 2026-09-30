# ALPS — エージェントライフサイクルプロセススキル

[![Validate](https://github.com/mashimashica/alps/actions/workflows/validate.yml/badge.svg)](https://github.com/mashimashica/alps/actions/workflows/validate.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](../../../LICENSE)

[English](../../../README.md)

<p align="center">
  <img src="../../../assets/icon.svg" alt="ALPS icon" width="160">
</p>

ALPSは、仕事の意味と、それを実現するエージェント作業システムを設計するための体系です。なぜ行うのか、どの観察可能な状態を成功とするのか、どの境界と詳細が必要なのかを記述します。必要に応じて、その仕事を有効に遂行するエージェント・ツール・情報資源・環境を設計します。

一度限りの依頼の明確化、既存Skillの改善、人やAgentが共同で行う作業の記述に使えます。**名称、目的、成果**から始め、理解・適用・評価に影響する場合に詳細を加えます。

## 導入

ALPSはClaude CodeとCodexのアダプターを持つ[Agent Plugins](https://agent-plugins.org/)パッケージです。対応クライアントからPlugin全体を導入します。[`plugins` CLI](https://www.npmjs.com/package/plugins)では次を使用できます。

```console
npx plugins add mashimashica/alps
```

Claude Codeでは、このリポジトリをPluginマーケットプレイスとして追加し、そこから導入することもできます。

```text
/plugin marketplace add mashimashica/alps
/plugin install alps@alps
```

導入後は対象クライアントを再読込みしてください。各Skillは単体で機能します。組み合わせる場合は、仕事の記述を一方から他方へ受け渡します。Pluginは、二つの設計Skillとその参照資源を、参照資料である`examples/`とともに配布し、あわせて[ハーネス](#ハーネス)とその`run-process` Skillを配布します。導入先で`design-process-description`と`design-agent-work-system`が表示され、それぞれの参照リンクを開けることを確認してください。ハーネスには[Bun](#必要なもの)が必要です。

## Skillの使い方

| Skill | 設計・評価の対象 |
| --- | --- |
| [design-process-description](../../../skills/design-process-description/references/locales/ja/SKILL.ja.md) | プロセス記述の意味、関係、適用条件。 |
| [design-agent-work-system](../../../skills/design-agent-work-system/references/locales/ja/SKILL.ja.md) | エージェント・ツール・情報資源・実行環境の構成と相互作用。依頼範囲で実装・検証も含む。 |

両Skillは作成・改訂・レビューを支援し、それぞれ単体で機能します。設計の基礎となる情報が十分であれば、どちらからでも使えます。組み合わせる場合は、仕事の記述を受け渡します。プロセス記述をシステム設計の出発点にでき、システム設計はその記述の中で再検討が必要な前提を報告できます。仕事の記述には必要な方法や順序も含められます。自然言語で依頼するか、Hostの仕様に応じてSkill名を明示します。

```text
design-process-descriptionを使い、この一度限りの作業を、目的、観察可能な成功条件、必要な境界によって記述してください。

このプロセス記述をレビューしてください。不明確な成果、不必要な手段の固定、不足する参照、限界を識別し、書き換えずに指摘を返してください。

design-agent-work-systemを使い、この仕事に必要な能力とインターフェースを設計してください。適切なツールを再利用し、不足する処理を実装し、代表例で構成を検証してください。

このエージェント作業システムをレビューしてください。判断と処理の配分、情報供給、ツールのインターフェース、有効性の証拠を評価し、変更せずに指摘を返してください。
```

[最小テンプレート](../../../skills/design-process-description/references/locales/ja/SKILL-template.md)は、通常のAgent Skill frontmatterと、プロセスの三つの必須要素から始めます。[具体例](../../../skills/design-process-description/references/locales/ja/examples.md)では、最小の作業、一度限りの作業、固定成果物のない作業、必要な承認と順序、共有情報、ビュー、参照不足、成果を満たさない出力を扱います。

[実働例](../../../examples/locales/ja/README.md)では、一つのサービス評価Skillに対する二つの設計責務を示します。スクリプトが測定を検証して比較を計算し、エージェントが文脈を評価して証拠を解釈します。[システム設計の具体例](../../../skills/design-agent-work-system/references/locales/ja/examples.md)では、既存ツール、状態を変更する操作、能力変化への適応も扱います。

## ハーネス

ハーネスは、プロセスモデルを具体的な仕事に適用します。具体的な入力に対してプロセスをインスタンス化し、エージェントで実行し、その実行と、各出力をどの実行が作ったかを記録し、各成果の評価をその根拠とともに記録します。プロセスモデルとSkillは読むだけで、変更しません。人はWebUIでプロセスのネットワーク、ダッシュボード、インスタンスを見て、エージェントはMCPサーバーを使います。ダッシュボードは、判断された成果、実行、所要時間、費用を数え、判断した実行の後に入力か`SKILL.md`が変わった評価を示します。実行が終わったこと、出力があること、エージェントが報告したことは、どれも成果の達成として数えません。成果は、人か明示されたエージェントが根拠とともに判断します。`run-process` Skillは、セッション自身が実行を行う場合（エージェント`self`）の手順を示します。

### 必要なもの

ハーネスは[Bun](https://bun.sh/) 1.3.11以上で動きます。Bunは、ハーネスを起動するクライアントの`PATH`になければなりません。

```console
curl -fsSL https://bun.sh/install | bash
```

macOSとLinuxに対応します。Windowsは試験的な対応です。CIでハーネスのテストを走らせますが合格を必須とせず、エージェントのプロセスツリー全体の停止は未検証です。

### Pluginから使う

- **Claude Code**は、`.mcp.json`から`harness` MCPサーバーを登録し、各セッションでプロジェクトのディレクトリに対して起動します。マーケットプレイスからPluginを取得する際、Claude Codeは根の`bun.lock`からハーネスの実行時の依存を導入します。ネットワークに接続できないなどでこの導入を実行できなかった場合は、Pluginのディレクトリで`bun install`を実行してください。ツールは`mcp__plugin_alps_harness__<ツール名>`として現れ、`/alps:harness [network|dashboard|instances]`はWebUIを開いてそのURLを示します。
- **Codex**は、根の`plugin.json`を読みます。これはMCPサーバーを登録しません。Agent Pluginsはサーバーの設定を既定の場所、つまりPluginの根の`mcp.json`で見つけます。`mcp.json`は同じサーバーを`${PLUGIN_ROOT}`で登録し、`.codex-plugin/plugin.json`もこれを指します。Agent Pluginsは依存の導入を定めていないため、Pluginのディレクトリで`bun install`を実行してください。また、Agent Pluginsはサーバーにプロジェクトのディレクトリを渡しません。ハーネスはワークスペースをそこから探しますが、Codexがサーバーをプロジェクトのディレクトリで起動するかはまだ検証していません。
- **Cursor**は、Agent Plugins形式を通じてSkillを読み込みますが、ハーネスは読み込みません。`mcp.json`の`${PLUGIN_ROOT}`を展開しないため、MCPサーバーが起動しません。

ワークスペースごとに一つのハーネスサーバー（デーモン）が記録を持ち、WebUIを配信します。MCPサーバーはそれに中継し、動いていなければ起動します。このため、WebUIと実行中のエージェントはセッションが終わっても止まりません。デーモンは、接続も実行中の実行もない状態が30分続くと終了します。ただし、スケジュールを設定している間は終了しません。

### 単体で使う

リポジトリをcloneし、実行時の依存を導入して、[例のワークスペース](../../../examples/locales/ja/README.md#ハーネスのワークスペース)などのワークスペースを配信します。

```console
git clone https://github.com/mashimashica/alps.git
cd alps
bun install
bun harness/src/cli.ts serve examples/service-change --open
```

| コマンド | 効果 |
| --- | --- |
| `serve [workspace] [--daemon] [--port <port>] [--open] [--dev]` | ハーネスサーバーを起動し、WebUIのURLを表示する。URLの`#`の後ろは合い言葉である。`--daemon`は切り離して起動し、`--open`はブラウザを開く。 |
| `stop [workspace]` | ハーネスサーバーと、それが動かしているエージェントを止める。 |
| `wake [workspace] [--agent claude-code\|codex]` | スケジュールと同じようにエージェントを目覚めさせる。launchd、cron、CIなどの外部のスケジューラから使う。 |
| `assess [workspace] [--format markdown\|json]` | 統計、所見、各インスタンスの事実を出力する。 |
| `mcp` | `ALPS_WORKSPACE`か現在のディレクトリのワークスペースについて、stdioでMCPを提供する。 |

`bun harness/src/cli.ts --help`が各オプションを説明します。`--dev`は、WebUIの開発のために、要求のたびにWebUIを束ね、変更を即座に反映します。このときのページとアセットには、サーバーのHost検査もセキュリティヘッダーも掛かりません。

### ワークスペース

ワークスペースは、与えられたディレクトリ（Pluginからはプロジェクトのディレクトリ、または`ALPS_WORKSPACE`）から上へたどって、最初に`alps-harness.yaml`か`process-model.yaml`があるディレクトリです。

| ファイル | 内容 |
| --- | --- |
| `process-model.yaml` | 仕事の意味。プロセスとその目的と成果、プロセスが読み書きするアーティファクトの型。 |
| `alps-harness.yaml` | ワークスペースがモデルをどう実現するか。キーは下の表のとおり。 |
| `skills/<name>/SKILL.md` | 各プロセスのSkill。name、ディレクトリ名、見出しによって見つける。 |
| `.alps-harness/` | ハーネスの記録。`state.json`、`runs/`、サーバーが動いている間の`server.json`。版管理の対象から外す。 |

| `alps-harness.yaml`のキー | 意味 |
| --- | --- |
| `model` | プロセスモデルのファイル。既定は`process-model.yaml`。 |
| `artifacts` | 各アーティファクトの型の`kind`（`information`、`product`、`service`）と置き場所の`paths`。`*`は一つの階層の中で、`**`は複数の階層にわたって一致し、末尾の`/`はディレクトリを一つのアーティファクトにする。 |
| `skills` | nameで見つからないプロセスのSkillの場所。 |
| `skillRoots` | Skillを探す場所。既定は`skills`、`.claude/skills`、`.agents/skills`、`.codex/skills`。 |
| `agents` | 各エージェントの起動の仕方。`command`、`args`（`{prompt}`を置き換える）、`env`、`stdin`、`format`（`claude`、`codex`、`demo`、`text`）。`false`はエージェントを外し、`self: false`はselfの実行を禁じる。 |
| `prompt` | 実行のプロンプトの差し替え。`{process}`、`{skill}`、`{inputs}`、`{controls}`、`{outputs}`、`{criteria}`、`{notes}`を使える。 |
| `language` | `en`（既定）か`ja`。プロンプトとMCPの応答の言語。WebUIはブラウザの言語に従い、独自の切り替えを持つ。 |
| `server` | `port`（既定は4830）と`idleMinutes`（30）。 |
| `guidance` | 目覚めたエージェントが読むMarkdownのファイル。何を先にするか、何を優先するか、どんなときにプロセスを走らせないかを文章で書く。ハーネスはそれを解釈しない。 |
| `schedules` | デーモンがエージェントを目覚めさせる時刻。`cron`（五つの欄、現地時刻）と`agent`（`claude-code`か`codex`）。目覚めたエージェントはモデル、案内、現状を読み、どのプロセスを走らせるかを判断する。 |

[例のワークスペース](../../../examples/locales/ja/service-change/alps-harness.yaml)は、各キーをコメントで説明しています。

### MCPツール

| ツール | すること |
| --- | --- |
| `get_model` | プロセスとその成果とSkillの場所、アーティファクトの型、使えるエージェントを返す。 |
| `list_artifacts` | 型の置き場所にあるアーティファクトを、それぞれを最後に作った実行とともに一覧する。 |
| `list_instances` | インスタンスを、最新の実行、判断、根拠が古いかという事実とともに一覧する。 |
| `instantiate` | インスタンスを作る。具体的な入力のパス、出力の置き場所、この適用での各成果の意味を持つ。 |
| `run` | `claude-code`、`codex`、`demo`、`self`のいずれかで実行を開始する。成功が意味するのは開始したことだけである。 |
| `get_run` | 実行の記録と末尾のイベントを返す。`wait`で終了まで待つ。 |
| `cancel_run` | 実行と、そのエージェントのプロセスグループを止める。 |
| `finish_run` | selfの実行を報告とともに終える。または、目覚めたエージェントの報告を受け取る。 |
| `evaluate` | 成果ごとに一つの判断（`achieved`、`not-achieved`、`unverified`）を、空にできない根拠とともに記録する。 |
| `get_assessment` | 統計と所見を、JSONかMarkdownで返す。 |
| `wake` | どのプロセスを走らせるかを判断するエージェントを目覚めさせる。 |
| `open_ui` | WebUIのURLを返す。`open: true`のときはブラウザで開く。 |

リソースは`alps://model`、`alps://process/<id>`、`alps://instance/<id>`、`alps://run/<id>/log`、`alps://assessment`です。ファイルの中身を読むツールはありません。エージェントは、Skillとアーティファクトを自分のツールで読みます。

### 安全策

- サーバーは127.0.0.1だけで待ち受け、`Host`ヘッダーがサーバー自身を指さない要求を拒否します。
- 起動ごとに合い言葉が変わります。合い言葉はURLのfragment（`#token=…`）で渡り、サーバーには届きません。ページはそれを一度だけ読み、sessionStorageに保持します。合い言葉を示すのは、`.alps-harness/server.json`（権限0600）と、サーバーを起動した端末だけです。`--open`と`open_ui`は、`.alps-harness/`にある権限0600のページを通じてブラウザを開くため、合い言葉がコマンドラインに現れることはありません。
- APIは、cross-siteとsame-siteの要求（`Sec-Fetch-Site`）と、JSONでない要求本文を拒否します。ほかのオリジンは応答を読み込めません（`Cross-Origin-Resource-Policy: same-origin`）。ページはフレームに埋め込めず（`X-Frame-Options: DENY`と`frame-ancestors 'none'`）、Content Security Policyはサーバー自身の資源だけを許し（`default-src 'self'`）、表示するMarkdownは無害化します。
- インスタンスの入力と出力は、ワークスペースの中で、かつ`.alps-harness/`の外になければなりません。
- エージェントは、ワークスペースで、そのコマンドラインが与える権限で動きます。Claude Codeは`--permission-mode acceptEdits`、Codexは`--sandbox workspace-write`です。目覚めたエージェントには、ハーネスのMCPツールも許可します。プロンプトは、入力アーティファクトの内容を指示ではなくデータとして扱うようエージェントに伝えます。既定は`agents`で変えられます。

ハーネスの開発については[harness/README.md](../../../harness/README.md)（英語）を参照してください。

## 設計思想

ALPSは、**システムズ／ソフトウェア工学に由来するプロセス記述**と、**小さく明確な道具を組み合わせるUnix哲学**をつなぎます。仕事の目的・成果・必要な作業や条件はプロセス記述で示し、確立した処理は道具として組み合わせられるようにします。

<p align="center">
  <img src="../../../assets/alps-agent-onion.svg" alt="Why / Whatが仕事の意味、Howが利用可能な手段、その間の判断をAgentが担う" width="900">
</p>

仕事の意味（**Why / What**）と手段（**How**）を区別し、その間をエージェントの判断でつなぎます。確立した処理はツールに任せ、エージェントは目的と状況に応じて手段を選び、組み合わせ、必要に応じて方法を調整します。

仕事に必要な方法や順序は明示し、状況に依存する判断には裁量を残します。

## 資源

| 資源 | 英語 | 日本語 |
| --- | --- | --- |
| プロセス記述の意味 | [Process Framework](../../../skills/design-process-description/references/process-framework.md) | [プロセスフレームワーク](../../../skills/design-process-description/references/locales/ja/process-framework.md) |
| 作業システムの設計 | [Design principles](../../../skills/design-agent-work-system/references/agent-work-system-design.md) | [エージェント作業システムの設計原則](../../../skills/design-agent-work-system/references/locales/ja/agent-work-system-design.md) |
| プロセス記述の設計 | [Skill](../../../skills/design-process-description/SKILL.md) | [Skill](../../../skills/design-process-description/references/locales/ja/SKILL.ja.md) |
| エージェント作業システムの設計 | [Skill](../../../skills/design-agent-work-system/SKILL.md) | [Skill](../../../skills/design-agent-work-system/references/locales/ja/SKILL.ja.md) |
| セッション自身によるハーネスの実行 | [Skill](../../../skills/run-process/SKILL.md) | [Skill](../../../skills/run-process/references/locales/ja/SKILL.ja.md) |
| ハーネスの開発 | [harness/README.md](../../../harness/README.md) | — |
| 貢献とリポジトリ作業 | [CONTRIBUTING](../../../CONTRIBUTING.md)、[AGENTS](../../../AGENTS.md) | [CONTRIBUTING](CONTRIBUTING.md)、[AGENTS](AGENTS.md) |
| 版管理方針とリリースノート | [Versioning](../../../docs/versioning.md)、[0.9.0](../../../docs/releases/0.9.0.md) | [版管理](versioning.md)、[0.9.0](releases/0.9.0.md) |

## 版とライセンス

リポジトリ全体を一つの単位として版管理します。リリースの範囲と互換性については、上記の版管理方針とリリースノートを参照してください。

明示された第三者資料を除き、本リポジトリは[Apache License 2.0](../../../LICENSE)で提供します。[NOTICE](../../../NOTICE)も参照してください。

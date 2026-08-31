# ALPS — Agent Lifecycle Process Skills

<p align="right">
  <a href="../../../README.md">英語</a> | <strong>日本語</strong>
</p>

<p align="center">
  <img src="../../../assets/icon.svg" alt="ALPSアイコン" width="160">
</p>

ALPSは、反復されるエージェント作業を明確で再利用可能なプロセススキルにするプロジェクト名および方法名です。「Lifecycle」は、スキルを繰り返し利用し、その利用から得た知見で再設計する意図を表します。ALPSがライフサイクル状態機械や統制システムを提供するという意味ではありません。

このパッケージが配布するスキルは[`design-process-description`](../../../skills/design-process-description/references/locales/ja/SKILL.md)一つだけです。反復作業の正本となるプロセス記述を作成、改訂または簡素化します。記述は、一つの目的、観察可能な成果、再利用可能な境界、および正確性、安全性、意味、組合せ可能性または評価可能性に必要な詳細だけを中心にします。

ALPSは、対象プロセスの実行、リポジトリやリリースの管理、形式的な適合主張または認証を行いません。対象プロセススキルの成果を達成するには、そのスキルを直接適用してください。

## インストール

ALPSは[Agent Plugins](https://agent-plugins.org/) v1パッケージとして配布します。Node.js 18以降の環境で実行します。

```console
npx plugins add mashimashica/alps
```

インストール済みスキルの再読込みが必要なクライアントを再起動してください。

## 利用方法

通常は、ルートの[`SKILL.md`](../../../skills/design-process-description/SKILL.md)だけを読みます。特定の設計判断に詳しい情報が必要な場合だけ、そこから三つの焦点を絞った参考資料の一つへ進みます。

依頼例:

```text
この反復的なインシデント要約作業を、一つの目的と観察可能な成果を持つ再利用可能なプロセス記述にしてください。

このプロセススキルから案件固有のツール、ファイルパス、固定順序および正しい利用に不要な詳細を取り除いて簡素化してください。

添付した利用結果、失敗、繰り返された確認および未解決の仮定を用いて、このプロセス記述を改訂してください。
```

このスキルは、設計または改訂したプロセス記述を提示し、不明点を推測せず明示します。

## リポジトリ

英語版スキルを正本とし、保守対象の[日本語版](../../../skills/design-process-description/references/locales/ja/SKILL.md)を収録します。ホストアダプターは同じ単一スキルを公開し、追加の振る舞いを定義しません。

ALPSの現在の版は**0.6.0**です。[バージョン管理](versioning.md)、[変更履歴](../../../CHANGELOG.md)、[貢献ガイド](CONTRIBUTING.md)および[リポジトリ作業指示](AGENTS.md)を参照してください。

明示した第三者資料を除き、本リポジトリには[Apache License 2.0](../../../LICENSE)を適用します。[NOTICE](../../../NOTICE)も参照してください。

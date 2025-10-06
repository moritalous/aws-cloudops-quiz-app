# AWS CloudOps試験問題生成ツール

AWS Document MCPサーバーとStrands Agentsを使用して、一度に10問の高品質なAWS CloudOps試験問題を生成するシンプルなコマンドラインツールです。

## 特徴

- **シンプル**: main.py一つで完結する約100行の実装
- **高品質**: AWS公式ドキュメントを参照した正確な問題生成
- **構造化**: Pydanticベースの型安全な出力
- **日本語対応**: 日本語での問題文と解説
- **試験準拠**: AWS CloudOps認定試験の5つのドメインに対応

## 前提条件

- Python 3.13以上
- uv (Python パッケージマネージャー)
- AWS認証情報の設定
- インターネット接続 (AWS Document MCPサーバー用)

## インストールと実行

```bash
# プロジェクトディレクトリに移動
cd aws-question-tool

# 依存関係をインストール
uv sync

# ツールを実行
uv run python main.py
```

## 出力

実行すると、以下の形式でファイルが生成されます：

- ファイル名: `questions_YYYYMMDD_HHMMSS.json`
- 内容: 10問の試験問題（JSON形式）
- メタデータ: 生成日時、ドメイン配分、難易度配分

## 生成される問題の特徴

### ドメイン配分
- Content Domain 1: 監視、ログ記録、分析、修復、パフォーマンス最適化 (22%)
- Content Domain 2: 信頼性とビジネス継続性 (22%)
- Content Domain 3: デプロイメント、プロビジョニング、自動化 (22%)
- Content Domain 4: セキュリティとコンプライアンス (16%)
- Content Domain 5: ネットワーキングとコンテンツ配信 (18%)

### 問題タイプ
- 単一選択問題
- 複数選択問題

### 難易度レベル
- Easy: 基本的な概念と操作
- Medium: 実践的なシナリオ
- Hard: 複雑な問題解決

## トラブルシューティング

### よくあるエラー

1. **MCP接続エラー**
   - uvがインストールされているか確認
   - インターネット接続を確認

2. **AWS認証エラー**
   - AWS認証情報が設定されているか確認
   - `aws configure` または環境変数で設定

3. **依存関係エラー**
   - `uv sync` で依存関係を再インストール

## 技術仕様

- **フレームワーク**: Strands Agents
- **モデル**: Claude Sonnet 4.5 (東京リージョン)
- **MCP**: AWS Documentation MCP Server
- **出力形式**: JSON (UTF-8エンコーディング)
- **ID形式**: `q{YYYYMMDD}_{HHMMSS}_{001-010}`

## ライセンス

このツールは内部使用を目的としています。
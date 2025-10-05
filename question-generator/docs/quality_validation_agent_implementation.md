# Quality Validation Agent Implementation

## 概要

Quality Validation Agent は、AWS CloudOps試験問題の品質を包括的に検証するAI駆動システムです。Strands Agents フレームワークと Amazon Bedrock OpenAI モデルを使用して、技術的正確性、明確性、適切な難易度、日本語品質などを自動評価します。

## 主要機能

### 1. 個別問題検証 (Single Question Validation)

各問題に対して以下の項目を詳細に検証：

- **技術的正確性**: AWS公式ドキュメントとの整合性確認
- **明確性**: 問題文の理解しやすさと曖昧さの排除
- **難易度適切性**: 指定された難易度レベルとの一致
- **誤答選択肢品質**: もっともらしさと学習効果の評価
- **解説包括性**: 正解理由と学習ポイントの完全性
- **学習リソース有効性**: URLの有効性と関連性
- **日本語品質**: 自然な表現と技術用語の適切性
- **試験関連性**: AWS CloudOps試験範囲との適合性

### 2. バッチ検証 (Batch Validation)

10問単位のバッチに対する包括的検証：

- **個別問題検証**: 各問題の詳細評価
- **ドメイン配分確認**: 試験ドメインの適切な配分
- **難易度バランス**: easy/medium/hard の適切な比率
- **問題タイプバランス**: 単一選択/複数選択の比率
- **重複検出**: 類似コンテンツの自動識別
- **カバレッジ分析**: トピックとAWSサービスの網羅性

### 3. 重複検出 (Duplicate Detection)

新しい問題と既存問題の類似性分析：

- **テキスト類似性**: 問題文の類似度計算
- **サービス重複**: 同一AWSサービスと同一ドメインの組み合わせ検出
- **セマンティック分析**: 意味的な類似性の評価
- **推奨事項**: 重複回避のための具体的提案

### 4. 品質レポート生成 (Quality Report Generation)

複数バッチの総合的な品質分析：

- **全体統計**: 承認率、平均スコア、技術的正確性率
- **バッチ詳細**: 各バッチの品質メトリクス
- **品質分布**: 高品質/中品質/低品質バッチの分類
- **改善推奨**: データ駆動型の品質向上提案

## アーキテクチャ

### コンポーネント構成

```
QualityValidationAgent
├── AgentFactory (Strands Agents管理)
├── Bedrock OpenAI Model (gpt-oss-120b)
├── AWS Knowledge MCP Server (事実確認)
└── Validation Models (Pydantic構造化出力)
```

### データフロー

1. **問題入力**: Question/QuestionBatch オブジェクト
2. **AWS文書検索**: 関連するAWS公式ドキュメントの取得
3. **AI検証実行**: 構造化出力による詳細評価
4. **結果構造化**: QuestionValidation/BatchValidation モデル
5. **レポート生成**: 包括的な品質分析レポート

## 使用方法

### 基本的な使用例

```python
from config import AgentConfig
from core.quality_validation_agent import QualityValidationAgent
from models.question_models import Question

# 設定とエージェントの初期化
config = AgentConfig()
validator = QualityValidationAgent(config)

# 単一問題の検証
question = Question(...)  # 問題オブジェクト
validation_result = validator.validate_question(question)

print(f"Overall Score: {validation_result.overall_score}/100")
print(f"Approved: {validation_result.approved}")
```

### バッチ検証

```python
from models.question_models import QuestionBatch

# バッチ検証
batch = QuestionBatch(
    batch_number=1,
    questions=[...]  # 10問のリスト
)

batch_validation = validator.validate_batch(batch)
print(f"Batch Quality Score: {batch_validation.batch_quality_score}/100")
print(f"Approved Questions: {sum(1 for qv in batch_validation.question_validations if qv.approved)}/10")
```

### 重複検出

```python
# 既存問題との重複チェック
existing_questions = [...]  # 既存問題のリスト
new_question = Question(...)

duplicate_result = validator.validate_question_against_existing(
    new_question, existing_questions
)

if duplicate_result['has_duplicates']:
    print("⚠️ Duplicate content detected!")
    for similar in duplicate_result['similar_questions']:
        print(f"Similar to {similar['id']}: {similar['reason']}")
```

### 品質レポート生成

```python
# 複数バッチの品質レポート
batch_validations = [...]  # BatchValidation のリスト

quality_report = validator.generate_quality_report(batch_validations)
print(f"Overall Approval Rate: {quality_report['summary']['approval_rate']:.1%}")
```

## 検証基準

### スコアリングシステム

各問題は以下の重み付けでスコア計算：

- **技術的正確性スコア**: 25% (1-10点)
- **明確性スコア**: 15% (1-10点)
- **誤答選択肢品質**: 15% (1-10点)
- **解説スコア**: 15% (1-10点)
- **日本語品質**: 10% (1-10点)
- **試験関連性**: 20% (1-10点)

### ペナルティシステム

以下の条件でペナルティが適用：

- 技術的不正確性: -20点
- 難易度不適切: -10点
- 解説不完全: -10点
- リソース無効: -5点
- AWSサービス不正確: -15点

### 承認基準

- **個別問題**: 総合スコア70点以上 + 技術的正確性必須
- **バッチ承認**: 8/10問以上承認 + バッチスコア75点以上

## 設定オプション

### AgentConfig での設定

```python
config = AgentConfig(
    bedrock=BedrockConfig(
        model_id="openai.gpt-oss-120b-1:0",
        temperature=0.3,  # 一貫性のため低温度
        max_tokens=4000
    ),
    mcp=MCPConfig(
        server_name="aws-docs",
        command="uvx",
        args=["awslabs.aws-documentation-mcp-server@latest"]
    )
)
```

### システムプロンプトのカスタマイズ

```python
config.system_prompt_template = """
あなたは{role}の専門家です。

{context}

以下の要件に従って作業してください：
{requirements}
"""
```

## エラーハンドリング

### 再試行機能

```python
@retry_with_backoff(max_retries=3, base_delay=2.0)
def validate_question(self, question: Question) -> QuestionValidation:
    # 自動再試行付きの検証実行
```

### エラータイプ

- **ValidationError**: 検証プロセスの失敗
- **BedrockConnectionError**: Bedrockモデル接続エラー
- **MCPConnectionError**: AWS Knowledge MCP接続エラー

## パフォーマンス最適化

### バッチ処理

- 10問単位での効率的な処理
- MCP接続の再利用
- プロンプトキャッシングの活用

### 並列処理

```python
# 複数問題の並列検証（将来実装）
async def validate_questions_parallel(self, questions: List[Question]):
    tasks = [self.validate_question(q) for q in questions]
    return await asyncio.gather(*tasks)
```

## 品質メトリクス

### 主要指標

- **承認率**: 承認された問題の割合
- **平均品質スコア**: 全問題の平均スコア
- **技術的正確性率**: 技術的に正確な問題の割合
- **日本語品質平均**: 日本語表現の平均品質

### 品質分類

- **高品質**: スコア85点以上
- **中品質**: スコア70-84点
- **低品質**: スコア70点未満

## テスト

### 単体テスト

```bash
# 品質検証エージェントのテスト実行
python test_quality_validation_agent.py
```

### 実行例

```bash
# 使用例の実行
python examples/quality_validation_agent_example.py
```

## 出力ファイル

### 検証結果

- `output/quality_validation_examples/single_question_validation.json`
- `output/quality_validation_examples/batch_validation.json`
- `output/quality_validation_examples/duplicate_detection.json`
- `output/quality_validation_examples/quality_report.json`

### ログファイル

- `logs/quality_validation_agent.log`
- 詳細な検証プロセスとエラー情報

## 今後の拡張

### 予定機能

1. **セマンティック類似性**: より高度な重複検出
2. **学習リソース自動検証**: URLの有効性確認
3. **品質予測**: 機械学習による品質予測
4. **A/Bテスト**: 異なる検証手法の比較

### カスタマイズ

- 検証基準の調整
- スコアリング重みの変更
- 新しい検証項目の追加
- 他の試験形式への対応

## トラブルシューティング

### よくある問題

1. **Bedrock接続エラー**
   - AWS認証情報の確認
   - リージョン設定の確認
   - モデルアクセス権限の確認

2. **MCP接続エラー**
   - uvx のインストール確認
   - aws-docs MCPサーバーの起動確認
   - ネットワーク接続の確認

3. **検証スコアが低い**
   - AWS公式ドキュメントとの整合性確認
   - 問題文の明確性改善
   - 日本語表現の自然さ向上

### デバッグ

```python
# デバッグモードでの実行
config = AgentConfig(log_level="DEBUG")
validator = QualityValidationAgent(config)
```

## まとめ

Quality Validation Agent は、AI駆動の包括的な品質検証システムとして、AWS CloudOps試験問題の品質向上に重要な役割を果たします。構造化出力、自動事実確認、詳細な品質メトリクスにより、高品質な問題データベースの構築を支援します。
#!/usr/bin/env python3
"""
AWS CloudOps試験問題生成ツール

AWS Document MCPサーバーとStrands Agentsを使用して、
一度に10問の高品質な試験問題を生成するシンプルなコマンドラインツール。
"""

import json
import sys
import uuid
from datetime import datetime
from typing import List, Dict, Any

from pydantic import BaseModel, Field
from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp import MCPClient
from strands import Agent
from strands.models import BedrockModel


# Pydanticモデル定義
class Choice(BaseModel):
    id: str
    text: str
    is_correct: bool


class Question(BaseModel):
    id: str  # 形式: "q{YYYYMMDD}_{HHMMSS}_{001-010}"
    question_text: str
    choices: List[Choice]
    question_type: str  # "single_choice" or "multiple_choice"
    correct_answers: List[str]
    explanation: str
    learning_resources: List[str]
    domain: str  # 5つのドメインのいずれか
    difficulty: str  # "easy", "medium", "hard"
    aws_services: List[str]


class QuestionSet(BaseModel):
    questions: List[Question]
    generation_timestamp: str = Field(description="問題生成日時 (ISO 8601形式)")
    total_questions: int = Field(default=10, description="生成された問題の総数")
    domains: Dict[str, Any] = Field(description="ドメイン配分情報 (ドメイン名: 問題数)")
    difficulty_distribution: Dict[str, int] = Field(description="難易度配分情報 (難易度: 問題数)")
    mcp_server_info: Dict[str, str] = Field(default={}, description="使用したAWS Document MCPサーバーの情報")
    strands_agent_config: Dict[str, str] = Field(default={}, description="使用したStrands Agentsの設定情報")


def generate_question_id(timestamp: str, question_number: int) -> str:
    """
    タイムスタンプベースの一意のID生成
    要件15.1, 15.2, 15.3, 15.4に従う
    """
    try:
        # 要件15.2: ID形式 "q{YYYYMMDD}_{HHMMSS}_{001-010}"
        return f"q{timestamp}_{question_number:03d}"
    except Exception:
        # 要件15.4: エラー時はUUIDベースの代替ID生成
        return f"q_uuid_{str(uuid.uuid4())[:8]}_{question_number:03d}"


def create_natural_language_prompt() -> str:
    """
    自然言語での問題生成用プロンプトを作成
    タスク5: AWS CloudOps試験ガイドの内容を直接含めて問題を生成
    """
    return """AWS CloudOps Engineer Associate試験の問題を10問、日本語で生成してください。

【AWS CloudOps Engineer Associate試験ガイド】
以下は公式試験ガイドの内容です：

## 試験概要
- 試験時間: 130分
- 問題数: 65問
- 合格点: 720点（1000点満点）
- 問題形式: 単一選択、複数選択

## Content Domains（出題範囲）

### Content Domain 1: Monitoring, Logging, Analysis, Remediation, and Performance Optimization (22%)
**Task Statement 1.1:** CloudWatchを使用してメトリクスとログを監視する
- CloudWatch Metrics、Logs、Alarms、Dashboards
- CloudWatch Agent、Custom Metrics
- CloudWatch Insights、Log Groups

**Task Statement 1.2:** パフォーマンスの問題を特定し、修復する
- X-Ray、Performance Insights
- リソース使用率の分析
- ボトルネックの特定と解決

**Task Statement 1.3:** ログ分析とトラブルシューティング
- CloudTrail、VPC Flow Logs
- ログの集約と分析
- 問題の根本原因分析

### Content Domain 2: Reliability and Business Continuity (22%)
**Task Statement 2.1:** 高可用性とフォルトトレラント設計を実装する
- Multi-AZ、Auto Scaling
- Load Balancing、Health Checks
- 障害復旧戦略

**Task Statement 2.2:** バックアップと復旧戦略を実装する
- AWS Backup、スナップショット
- クロスリージョンレプリケーション
- RTO/RPO要件の実現

**Task Statement 2.3:** 災害復旧計画を策定・実行する
- Pilot Light、Warm Standby、Multi-Site
- 災害復旧テスト
- ビジネス継続性計画

### Content Domain 3: Deployment, Provisioning, and Automation (22%)
**Task Statement 3.1:** Infrastructure as Code（IaC）を使用する
- CloudFormation、CDK
- テンプレートの管理とベストプラクティス
- Change Sets、Stack管理

**Task Statement 3.2:** 自動化とオーケストレーションを実装する
- Systems Manager、Lambda
- EventBridge、Step Functions
- CI/CDパイプライン

**Task Statement 3.3:** 設定管理とパッチ管理を自動化する
- Systems Manager Patch Manager
- Configuration Management
- Compliance管理

### Content Domain 4: Security and Compliance (16%)
**Task Statement 4.1:** セキュリティ監視とコンプライアンスを実装する
- AWS Config、Security Hub
- GuardDuty、Inspector
- コンプライアンスレポート

**Task Statement 4.2:** アクセス制御とアイデンティティ管理
- IAM、Organizations
- Resource-based policies
- 最小権限の原則

**Task Statement 4.3:** データ保護と暗号化
- KMS、暗号化
- データ分類とDLP
- セキュアな通信

### Content Domain 5: Networking and Content Delivery (18%)
**Task Statement 5.1:** ネットワーク設計と最適化
- VPC、Subnets、Route Tables
- NAT Gateway、Internet Gateway
- ネットワークセキュリティ

**Task Statement 5.2:** コンテンツ配信とパフォーマンス最適化
- CloudFront、Global Accelerator
- Route 53、DNS管理
- エッジロケーション活用

## 主要AWSサービス
- Amazon EC2、Auto Scaling
- Amazon RDS、DynamoDB
- Amazon S3、EBS、EFS
- Amazon VPC、Route 53、CloudFront
- AWS CloudFormation、Systems Manager
- Amazon CloudWatch、CloudTrail、X-Ray
- AWS Config、Security Hub、GuardDuty
- AWS Backup、Lambda、EventBridge
- Application Load Balancer、Network Load Balancer

【問題生成要件】
1. 実際の運用シナリオに基づいた実践的な問題
2. 各Content Domainから適切に配分（Domain 1-3: 各22%, Domain 4: 16%, Domain 5: 18%）
3. 難易度: easy（基本概念）、medium（実践応用）、hard（複雑な運用シナリオ）を適切に配分
4. 単一選択問題と複数選択問題を混在
5. 各問題に4つの選択肢を提供
6. 詳細な解説とAWSベストプラクティスに基づく説明

【出力形式】
各問題について以下の情報を含めて自然言語で出力してください：

問題1:
問題文: [実際の運用シナリオに基づいた問題文]
選択肢A: [選択肢1]
選択肢B: [選択肢2] 
選択肢C: [選択肢3]
選択肢D: [選択肢4]
正解: [A/B/C/D または複数選択の場合はA,C等]
解説: [詳細な解説とAWSベストプラクティスに基づく説明]
学習リソース: [関連するAWS公式ドキュメントURL]
ドメイン: [該当するContent Domain]
難易度: [easy/medium/hard]
関連AWSサービス: [関連するAWSサービス名]

（問題2〜10も同様の形式で）

上記の試験ガイドに基づいて、技術的に正確で実践的な問題を生成してください。"""


def create_prompt() -> str:
    """
    問題生成用の詳細なプロンプトを作成
    """
    return """AWS CloudOps試験の問題を10問、日本語で生成してください。

【重要指示】問題生成前に必ず以下の手順を実行してください：
1. AWS Document MCPサーバーのsearch_documentation機能を使用して「AWS CloudOps」「CloudOps Engineer Associate」で検索し、試験ガイドの最新情報を取得
2. 各Content Domainに関連するAWSサービスの公式ドキュメントをread_documentation機能で詳細に参照
3. recommend機能を使用して関連する学習リソースを発見
4. 取得した公式ドキュメントの情報に基づいて技術的に正確な問題を作成

【ドメイン配分】以下の5つのContent Domainから適切に配分してください：
- Content Domain 1: Monitoring, Logging, Analysis, Remediation, and Performance Optimization (22%)
  - 運用監視、ログ分析、パフォーマンス最適化の実践的シナリオ
- Content Domain 2: Reliability and Business Continuity (22%)  
  - 高可用性、障害復旧、ビジネス継続性の運用課題
- Content Domain 3: Deployment, Provisioning, and Automation (22%)
  - インフラ自動化、デプロイメント管理の実務シナリオ
- Content Domain 4: Security and Compliance (16%)
  - セキュリティ運用、コンプライアンス管理の実践課題
- Content Domain 5: Networking and Content Delivery (18%)
  - ネットワーク運用、コンテンツ配信の技術課題

【対象候補者レベル】
- 1年以上のAWS運用経験を持つシステム管理者レベル
- 監視、ログ記録、トラブルシューティング技術の実務経験
- AWS CloudOps試験ガイドで推奨されるAWSサービスの知識範囲内
- 実際の運用課題を解決できる実践的スキル

【問題形式】
- 単一選択問題（Single Choice）と複数選択問題（Multiple Choice）を適切に混在
- 難易度：easy（基本概念）、medium（実践応用）、hard（複雑な運用シナリオ）を適切に配分
- 各問題に4つの選択肢を提供
- 実際の運用シナリオに基づいた実践的な問題

【除外事項】以下の内容は試験範囲外のため含めないでください：
- 分散アーキテクチャの設計（アプリケーション設計）
- CI/CDパイプラインの設計（開発プロセス設計）
- ソフトウェア開発に関する問題（コーディング、プログラミング）
- コスト分析や請求管理に関する問題（FinOps領域）
- 高レベルなアーキテクチャ設計判断

【出力要件】
- 各問題に一意のIDを付与（後でタイムスタンプベースのIDに置換されます）
- 詳細な解説を日本語で提供（AWS公式ドキュメントの情報に基づく）
- 学習リソースとして取得した公式AWSドキュメントのURLを含める
- 関連するAWSサービス名をリストアップ
- 適切なドメインと難易度を設定

【品質要件】
- AWS Document MCPサーバーから取得した最新情報に基づく技術的正確性
- AWS CloudOps試験ガイドの出題傾向との整合性
- 実際の運用現場で遭遇する実践的な課題
- 明確で理解しやすい日本語表現

必ずAWS Document MCPサーバーの全ての機能（search_documentation、read_documentation、recommend）を活用して、最新かつ正確な公式情報に基づいた高品質な問題を生成してください。"""


def main():
    """メイン実行関数"""
    print("AWS CloudOps試験問題生成ツールを開始します...")
    
    try:
        # Claude Sonnet 4.5をクロスリージョン推論で使用 (要件3.1, デザイン仕様)
        print("🔧 Strands Agentを初期化中...")
        bedrock_model = BedrockModel(
            model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
            region_name="ap-northeast-1"  # 東京リージョン
        )
        print("✅ BedrockModel初期化完了 (Claude Sonnet 4.5, クロスリージョン推論)")
        
        # MCP接続設定 (要件11.1, 11.2, 11.3)
        print("🔗 AWS Document MCPサーバーに接続中...")
        mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uvx",  # 要件11.2
                args=["awslabs.aws-documentation-mcp-server@latest"],  # 要件11.2
                env={
                    "FASTMCP_LOG_LEVEL": "ERROR",  # 要件11.3
                    "AWS_DOCUMENTATION_PARTITION": "aws"  # 要件11.3
                }
            )
        ))
        
        # MCPクライアントのwith文内でAgentを使用 (Strands Agents要件)
        with mcp_client:
            # MCPツールを取得 (要件3.3)
            tools = mcp_client.list_tools_sync()
            print(f"✅ MCPツール取得完了: {len(tools)}個のツールが利用可能")
            
            # Agentを初期化 (要件3.1, 3.2) - modelとtoolsパラメータを正しく渡す
            agent = Agent(model=bedrock_model, tools=tools)
            print("✅ Strands Agent初期化完了")
            
            print("🤖 問題生成を開始します...")
            print("📋 AWS Document MCPサーバーの検索機能を活用した構造化出力を実行中...")
            
            # 2段階アプローチ (タスク5: 試験ガイド含有 + MCPサーバー使用 + 構造化出力分離)
            # 第1段階: 試験ガイドを含むプロンプトでMCPサーバーを使って自然言語で問題を生成
            print("🔍 第1段階: 試験ガイド + MCPサーバーを使って問題内容を生成中...")
            natural_language_prompt = create_natural_language_prompt()
            
            # 自然言語での問題生成（MCPサーバー使用）
            natural_result = agent(natural_language_prompt)
            print("✅ 第1段階完了: 自然言語での問題内容が生成されました")
            
        # 第2段階: MCPクライアントを再初期化して構造化出力で整理
        print("🔍 第2段階: 生成された問題を構造化出力で整理中...")
        print("🔧 構造化出力用のMCPクライアントを再初期化中...")
        
        # 構造化出力用に新しいMCPクライアントとAgentを初期化
        structure_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uvx",
                args=["awslabs.aws-documentation-mcp-server@latest"],
                env={
                    "FASTMCP_LOG_LEVEL": "ERROR",
                    "AWS_DOCUMENTATION_PARTITION": "aws"
                }
            )
        ))
        
        with structure_mcp_client:
            # 構造化出力用のツールを取得
            structure_tools = structure_mcp_client.list_tools_sync()
            print(f"✅ 構造化出力用MCPツール取得完了: {len(structure_tools)}個のツールが利用可能")
            
            # 構造化出力用のAgentを初期化
            structure_agent = Agent(model=bedrock_model, tools=structure_tools)
            print("✅ 構造化出力用Agent初期化完了")
            
            structure_prompt = f"""
以下の生成された問題内容を、指定されたJSON形式に構造化してください：

{natural_result}

各問題について以下の形式で整理してください：
- 問題文
- 選択肢（4つ）
- 正解
- 解説
- 学習リソース
- ドメイン
- 難易度
- 関連AWSサービス
"""
            
            # 構造化出力（再初期化されたAgent使用）
            result = structure_agent.structured_output(QuestionSet, structure_prompt)
            print("✅ 第2段階完了: 構造化出力が完了しました")
            
            # タイムスタンプベースのファイル名とID生成
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            iso_timestamp = now.isoformat()
            
            # 各問題に一意のIDを付与 (要件15.1, 15.2, 15.3)
            for i, question in enumerate(result.questions, 1):
                question.id = generate_question_id(timestamp, i)
            
            # メタデータ情報を設定 (要件17.1, 17.2, 17.3, 17.4)
            result.generation_timestamp = iso_timestamp
            result.mcp_server_info = {
                "server_name": "awslabs.aws-documentation-mcp-server",
                "version": "latest",
                "partition": "aws"
            }
            result.strands_agent_config = {
                "model_id": "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "region": "ap-northeast-1",
                "tools_count": str(len(structure_tools))
            }
            
            # ファイル名: questions_{YYYYMMDD}_{HHMMSS}.json
            filename = f"questions_{timestamp}.json"
            
            # JSON出力
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
            
            print(f"✅ 生成完了: {filename} (10問)")
            print(f"📊 ドメイン配分: {result.domains}")
            print(f"📈 難易度配分: {result.difficulty_distribution}")
            
            # 生成された問題の品質確認ログ (要件18.4)
            print("\n📋 生成された問題の概要:")
            for i, question in enumerate(result.questions, 1):
                print(f"  {i:2d}. [{question.domain}] [{question.difficulty}] {question.question_type}")
                print(f"      ID: {question.id}")
                print(f"      AWSサービス: {', '.join(question.aws_services[:3])}{'...' if len(question.aws_services) > 3 else ''}")
                print(f"      学習リソース: {len(question.learning_resources)}個のリソース")
            
            print(f"\n🎯 品質メトリクス:")
            print(f"   - 総問題数: {len(result.questions)}")
            print(f"   - ドメインカバレッジ: {len(result.domains)}個のドメイン")
            print(f"   - 難易度バランス: {len(result.difficulty_distribution)}レベル")
            print(f"   - 生成時刻: {result.generation_timestamp}")
            print(f"   - 出力ファイル: {filename}")
            
    except Exception as e:
        error_msg = str(e).lower()
        print(f"❌ エラーが発生しました: {e}")
        
        # MCP接続エラーの詳細診断 (要件11.4)
        if "uvx" in error_msg or "command not found" in error_msg:
            print("💡 uvがインストールされていません。以下のコマンドでインストールしてください:")
            print("   pip install uv")
        elif "aws-documentation-mcp-server" in error_msg:
            print("💡 AWS Document MCPサーバーに接続できません:")
            print("   - uvがインストールされているか確認してください")
            print("   - インターネット接続を確認してください")
        elif "bedrock" in error_msg or "credentials" in error_msg:
            print("💡 AWS認証情報が設定されているか確認してください:")
            print("   - AWS CLI設定: aws configure")
            print("   - 環境変数: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        else:
            print("💡 一般的な解決方法:")
            print("   - uvがインストールされているか確認: uv --version")
            print("   - AWS認証情報が設定されているか確認: aws sts get-caller-identity")
        
        sys.exit(1)


if __name__ == "__main__":
    main()

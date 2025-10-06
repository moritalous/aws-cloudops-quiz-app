#!/usr/bin/env python3
"""
AWS CloudOps試験問題生成ツール

AWS Document MCPサーバーとStrands Agentsを使用して、
一度に10問の高品質な試験問題を生成するシンプルなコマンドラインツール。
"""

import json
import sys
from datetime import datetime
from typing import List

from pydantic import BaseModel
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
    generation_timestamp: str
    total_questions: int = 10
    domains: dict  # ドメイン配分情報
    difficulty_distribution: dict  # 難易度配分情報


def create_prompt() -> str:
    """問題生成用の詳細なプロンプトを作成"""
    return """
AWS CloudOps試験の問題を10問、日本語で生成してください。

【ドメイン配分】以下の5つのドメインから適切に配分：
- Content Domain 1: 監視、ログ記録、分析、修復、パフォーマンス最適化 (22%)
- Content Domain 2: 信頼性とビジネス継続性 (22%)  
- Content Domain 3: デプロイメント、プロビジョニング、自動化 (22%)
- Content Domain 4: セキュリティとコンプライアンス (16%)
- Content Domain 5: ネットワーキングとコンテンツ配信 (18%)

【対象レベル】1年のAWS運用経験、システム管理者レベル
【問題タイプ】単一選択と複数選択を混在
【難易度】easy、medium、hardを適切に配分
【除外事項】分散アーキテクチャ設計、CI/CD設計、ソフトウェア開発、コスト分析は含めない

各問題にはタイムスタンプベースの一意のID（q{YYYYMMDD}_{HHMMSS}_{001-010}形式）を付与し、
AWS公式ドキュメントを参照して正確な情報を使用してください。

generation_timestampには現在の日時を、domainsには実際の配分を、
difficulty_distributionには難易度の配分を記録してください。
"""


def main():
    """メイン実行関数"""
    print("AWS CloudOps試験問題生成ツールを開始します...")
    
    try:
        # Claude Sonnet 4.5を東京リージョンで使用
        bedrock_model = BedrockModel(
            model_id="anthropic.claude-sonnet-4-5-20250929-v1:0",
            region_name="ap-northeast-1"  # 東京リージョン
        )
        
        # MCP接続設定
        mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uvx",
                args=["awslabs.aws-documentation-mcp-server@latest"],
                env={
                    "FASTMCP_LOG_LEVEL": "ERROR",
                    "AWS_DOCUMENTATION_PARTITION": "aws"
                }
            )
        ))
        
        print("AWS Document MCPサーバーに接続中...")
        
        with mcp_client:
            # MCPツールを取得
            tools = mcp_client.list_tools_sync()
            print(f"MCPツール取得完了: {len(tools)}個のツールが利用可能")
            
            # Agentを初期化
            agent = Agent(model=bedrock_model, tools=tools)
            
            print("問題生成を開始します...")
            
            # 構造化出力で10問生成
            prompt = create_prompt()
            result = agent.structured_output(QuestionSet, prompt)
            
            # タイムスタンプベースのファイル名とID生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 各問題に一意のIDを付与
            for i, question in enumerate(result.questions, 1):
                question.id = f"q{timestamp}_{i:03d}"
            
            # ファイル名: questions_{YYYYMMDD}_{HHMMSS}.json
            filename = f"questions_{timestamp}.json"
            
            # JSON出力
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
            
            print(f"✅ 生成完了: {filename} (10問)")
            print(f"📊 ドメイン配分: {result.domains}")
            print(f"📈 難易度配分: {result.difficulty_distribution}")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        print("💡 uvがインストールされているか確認してください")
        print("💡 AWS認証情報が設定されているか確認してください")
        sys.exit(1)


if __name__ == "__main__":
    main()

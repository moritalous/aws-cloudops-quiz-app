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


def create_prompt() -> str:
    """問題生成用の詳細なプロンプトを作成"""
    return """AWS CloudOps試験の問題を10問、日本語で生成してください。

ドメイン配分：
1. 監視・ログ記録 (22%)
2. 信頼性・継続性 (22%)  
3. デプロイメント・自動化 (22%)
4. セキュリティ (16%)
5. ネットワーキング (18%)

対象：1年のAWS運用経験レベル
形式：単一選択・複数選択混在、easy/medium/hard配分
AWS公式ドキュメントを参照して正確な情報を使用してください。"""


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
        
        with mcp_client:
            # MCPツールを取得 (要件3.3)
            tools = mcp_client.list_tools_sync()
            print(f"✅ MCPツール取得完了: {len(tools)}個のツールが利用可能")
            
            # Agentを初期化 (要件3.1, 3.2)
            agent = Agent(model=bedrock_model, tools=tools)
            print("✅ Strands Agent初期化完了")
            
            print("🤖 問題生成を開始します...")
            
            # 構造化出力で10問生成 (要件3.2, 3.4)
            prompt = create_prompt()
            result = agent.structured_output(QuestionSet, prompt)
            
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
                "tools_count": str(len(tools))
            }
            
            # ファイル名: questions_{YYYYMMDD}_{HHMMSS}.json
            filename = f"questions_{timestamp}.json"
            
            # JSON出力
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
            
            print(f"✅ 生成完了: {filename} (10問)")
            print(f"📊 ドメイン配分: {result.domains}")
            print(f"📈 難易度配分: {result.difficulty_distribution}")
            
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

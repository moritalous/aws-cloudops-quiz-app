"""
Factory for creating and configuring Strands Agents with Bedrock and MCP integration.

This module provides centralized creation and configuration of AI agents
for the question generation system, including Bedrock model setup,
MCP server integration, and error handling.
"""

import boto3
from typing import Optional, List, Dict, Any
import logging
from pathlib import Path

# Strands Agents imports
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

# Local imports
from config import AgentConfig, BedrockConfig, MCPConfig
from core.error_handling import BedrockConnectionError, MCPConnectionError, retry_with_backoff

logger = logging.getLogger(__name__)


def create_bedrock_model(config: BedrockConfig, boto_session: Optional[boto3.Session] = None) -> BedrockModel:
    """
    Create and configure a Bedrock model for Strands Agents.
    
    Args:
        config: Bedrock configuration
        boto_session: Optional boto3 session (will create default if None)
    
    Returns:
        Configured BedrockModel instance
    
    Raises:
        BedrockConnectionError: If model creation or connection fails
    """
    try:
        logger.info(f"Creating Bedrock model: {config.model_id}")
        
        # Create boto3 session if not provided
        if boto_session is None:
            boto_session = boto3.Session(region_name=config.region_name)
        
        # Create BedrockModel with configuration
        # Note: Don't pass region_name if boto_session is provided
        bedrock_kwargs = {
            "model_id": config.model_id,
            "streaming": config.streaming,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
            "stop_sequences": config.stop_sequences,
            "cache_prompt": config.cache_prompt,
            "cache_tools": config.cache_tools,
            "guardrail_id": config.guardrail_id,
            "guardrail_version": config.guardrail_version,
            "guardrail_trace": config.guardrail_trace,
        }
        
        if boto_session is not None:
            bedrock_kwargs["boto_session"] = boto_session
        else:
            bedrock_kwargs["region_name"] = config.region_name
        
        bedrock_model = BedrockModel(**bedrock_kwargs)
        
        logger.info(f"Successfully created Bedrock model: {config.model_id}")
        return bedrock_model
        
    except Exception as e:
        error_msg = f"Failed to create Bedrock model {config.model_id}: {str(e)}"
        logger.error(error_msg)
        raise BedrockConnectionError(error_msg) from e


def create_mcp_client(config: MCPConfig) -> MCPClient:
    """
    Create and configure an MCP client for aws-docs integration.
    
    Args:
        config: MCP configuration
    
    Returns:
        Configured MCPClient instance
    
    Raises:
        MCPConnectionError: If MCP client creation fails
    """
    try:
        logger.info(f"Creating MCP client for server: {config.server_name}")
        
        # Create stdio parameters for the MCP server
        stdio_params = config.get_stdio_parameters()
        
        # Create MCP client with stdio transport
        mcp_client = MCPClient(
            lambda: stdio_client(stdio_params)
        )
        
        logger.info(f"Successfully created MCP client for: {config.server_name}")
        return mcp_client
        
    except Exception as e:
        error_msg = f"Failed to create MCP client for {config.server_name}: {str(e)}"
        logger.error(error_msg)
        raise MCPConnectionError(error_msg) from e


class AgentFactory:
    """Factory class for creating specialized AI agents."""
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the agent factory.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.bedrock_model: Optional[BedrockModel] = None
        self.mcp_client: Optional[MCPClient] = None
        self.mcp_tools: List[Any] = []
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger.info("AgentFactory initialized")
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def _initialize_bedrock(self) -> BedrockModel:
        """Initialize Bedrock model with retry logic."""
        if self.bedrock_model is None:
            # Create boto3 session with configuration
            session_kwargs = self.config.get_boto_session_kwargs()
            boto_session = boto3.Session(**session_kwargs) if session_kwargs else None
            
            self.bedrock_model = create_bedrock_model(self.config.bedrock, boto_session)
        
        return self.bedrock_model
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def _initialize_mcp(self) -> MCPClient:
        """Initialize MCP client with retry logic."""
        if self.mcp_client is None:
            self.mcp_client = create_mcp_client(self.config.mcp)
        
        return self.mcp_client
    
    def _get_mcp_tools(self) -> List[Any]:
        """Get MCP tools from the client."""
        if not self.mcp_tools and self.mcp_client:
            try:
                with self.mcp_client:
                    self.mcp_tools = self.mcp_client.list_tools_sync()
                    logger.info(f"Retrieved {len(self.mcp_tools)} MCP tools")
            except Exception as e:
                logger.warning(f"Failed to retrieve MCP tools: {e}")
                self.mcp_tools = []
        
        return self.mcp_tools
    
    def create_exam_guide_analyzer(self) -> Agent:
        """
        Create an agent specialized for exam guide analysis.
        
        Returns:
            Configured Agent for exam guide analysis
        """
        bedrock_model = self._initialize_bedrock()
        
        system_prompt = self.config.system_prompt_template.format(
            role="AWS認定試験ガイド分析",
            context="""AWS Certified CloudOps Engineer - Associate (SOA-C03) 試験ガイドの専門分析を行います。
試験ガイドから以下の情報を構造化して抽出します：
- 各ドメインの詳細分析
- タスクとスキルの階層構造
- 重み付けと目標問題数の計算
- 関連AWSサービスの特定""",
            requirements="""1. 構造化出力を使用してPydanticモデルに準拠した結果を提供
2. 各ドメインの重み付けを正確に計算
3. タスクとスキルを階層的に整理
4. 200問の配分を適切に計算
5. 技術的に正確な情報のみを抽出"""
        )
        
        agent = Agent(
            model=bedrock_model,
            system_prompt=system_prompt
        )
        
        logger.info("Created exam guide analyzer agent")
        return agent
    
    def create_batch_manager(self) -> Agent:
        """
        Create an agent specialized for batch management and planning.
        
        Returns:
            Configured Agent for batch management
        """
        bedrock_model = self._initialize_bedrock()
        
        system_prompt = self.config.system_prompt_template.format(
            role="AI問題生成バッチ管理",
            context="""10問単位でのバッチ処理による効率的な問題生成を管理します。
現在の進捗状況を分析し、次のバッチの最適な計画を立案します。
ドメイン配分、難易度バランス、トピック重複回避を考慮します。""",
            requirements="""1. 現在のデータベース状態を正確に分析
2. 目標配分に向けた最適なバッチ計画を作成
3. 重複トピックを回避する戦略的計画
4. 品質要件を満たす実行可能な計画
5. 進捗追跡と報告機能"""
        )
        
        agent = Agent(
            model=bedrock_model,
            system_prompt=system_prompt
        )
        
        logger.info("Created batch manager agent")
        return agent
    
    def create_document_researcher(self) -> Agent:
        """
        Create an agent specialized for AWS documentation research using MCP.
        
        Returns:
            Configured Agent with MCP tools for documentation research
        """
        bedrock_model = self._initialize_bedrock()
        mcp_client = self._initialize_mcp()
        mcp_tools = self._get_mcp_tools()
        
        system_prompt = self.config.system_prompt_template.format(
            role="AWSドキュメント検索・研究",
            context="""aws-docs MCPツールを使用してAWS公式ドキュメントから最新の技術情報を収集します。
問題生成に必要な正確な技術仕様、ベストプラクティス、設定例を取得します。
収集した情報を構造化して問題生成に活用できる形式で提供します。""",
            requirements="""1. aws-docs MCPツールを効果的に活用
2. 技術的に正確で最新の情報のみを収集
3. 問題生成に適した形式で情報を整理
4. 公式ドキュメントのURLと引用を含める
5. ベストプラクティスと実装例を重視"""
        )
        
        # Note: MCP tools must be used within the MCP client context
        agent = Agent(
            model=bedrock_model,
            tools=mcp_tools,
            system_prompt=system_prompt
        )
        
        logger.info("Created document researcher agent with MCP tools")
        return agent
    
    def create_aws_knowledge_agent(self):
        """
        Create an AWS Knowledge MCP integration agent.
        
        Returns:
            AWSKnowledgeAgent instance for comprehensive AWS knowledge retrieval
        """
        from core.aws_knowledge_agent import AWSKnowledgeAgent
        
        aws_knowledge_agent = AWSKnowledgeAgent(self.config)
        logger.info("Created AWS Knowledge MCP integration agent")
        return aws_knowledge_agent
    
    def create_question_generator(self) -> Agent:
        """
        Create an agent specialized for question generation.
        
        Returns:
            Configured Agent for question generation
        """
        bedrock_model = self._initialize_bedrock()
        
        system_prompt = self.config.system_prompt_template.format(
            role="AWS CloudOps試験問題生成",
            context="""AWS Certified CloudOps Engineer - Associate認定試験の高品質な問題を生成します。
実際の試験形式に準拠し、実世界のCloudOpsエンジニアリング状況を反映した問題を作成します。
技術的正確性、適切な難易度、自然な日本語表現を重視します。""",
            requirements="""1. 公式AWS認定試験の形式とスタイルに従う
2. 実世界のCloudOpsシナリオを反映
3. 技術的に正確で最新の情報を使用
4. もっともらしい誤答選択肢を作成
5. 包括的な日本語解説を提供
6. 関連する学習リソースを含める
7. 構造化出力でPydanticモデルに準拠"""
        )
        
        agent = Agent(
            model=bedrock_model,
            system_prompt=system_prompt
        )
        
        logger.info("Created question generator agent")
        return agent
    
    def create_quality_validator(self) -> Agent:
        """
        Create an agent specialized for quality validation.
        
        Returns:
            Configured Agent for quality validation
        """
        bedrock_model = self._initialize_bedrock()
        mcp_client = self._initialize_mcp()
        mcp_tools = self._get_mcp_tools()
        
        system_prompt = self.config.system_prompt_template.format(
            role="AI問題品質検証",
            context="""生成された試験問題の品質を包括的に検証します。
技術的正確性、明確性、適切な難易度、日本語品質を評価します。
aws-docs MCPツールを使用して事実確認を行います。""",
            requirements="""1. 技術的正確性をAWSドキュメントと照合
2. 問題の明確性と曖昧さの排除
3. 適切な難易度レベルの確認
4. 誤答選択肢の妥当性評価
5. 日本語表現の自然さと正確性
6. 学習リソースの有効性確認
7. 構造化された検証結果の提供"""
        )
        
        agent = Agent(
            model=bedrock_model,
            tools=mcp_tools,
            system_prompt=system_prompt
        )
        
        logger.info("Created quality validator agent")
        return agent
    
    def create_japanese_optimizer(self) -> Agent:
        """
        Create an agent specialized for Japanese language optimization.
        
        Returns:
            Configured Agent for Japanese optimization
        """
        bedrock_model = self._initialize_bedrock()
        
        system_prompt = self.config.system_prompt_template.format(
            role="日本語技術文書最適化",
            context="""AWS試験問題の日本語表現を自然で理解しやすい形に最適化します。
技術用語の適切な日本語表記、文法と可読性の向上、文化的コンテキストの考慮を行います。
専門用語の一貫性を確保し、学習者にとって分かりやすい表現に調整します。""",
            requirements="""1. 技術用語の適切な日本語表記
2. 文法と可読性の向上
3. 文化的コンテキストの考慮
4. 専門用語の一貫性確保
5. 学習者にとって分かりやすい表現
6. 原文の技術的意味を保持
7. 自然な日本語への調整"""
        )
        
        agent = Agent(
            model=bedrock_model,
            system_prompt=system_prompt
        )
        
        logger.info("Created Japanese optimizer agent")
        return agent
    
    def create_database_integrator(self) -> Agent:
        """
        Create an agent specialized for database integration.
        
        Returns:
            Configured Agent for database integration
        """
        bedrock_model = self._initialize_bedrock()
        
        system_prompt = self.config.system_prompt_template.format(
            role="データベース統合管理",
            context="""生成された問題バッチを既存のquestions.jsonデータベースに安全に統合します。
ID連続性の確保、メタデータの更新、JSON構造の整合性維持を行います。
バックアップとロールバック機能を提供し、データの整合性を保証します。""",
            requirements="""1. 既存問題の完全保持
2. ID連続性の確保（q001, q002, ...）
3. メタデータの正確な更新
4. JSON構造の整合性維持
5. バックアップの作成
6. 統合後の検証実行
7. 構造化された統合結果の報告"""
        )
        
        agent = Agent(
            model=bedrock_model,
            system_prompt=system_prompt
        )
        
        logger.info("Created database integrator agent")
        return agent
    
    def create_overall_quality_checker(self) -> Agent:
        """
        Create an agent specialized for overall quality assessment.
        
        Returns:
            Configured Agent for overall quality checking
        """
        bedrock_model = self._initialize_bedrock()
        mcp_client = self._initialize_mcp()
        mcp_tools = self._get_mcp_tools()
        
        system_prompt = self.config.system_prompt_template.format(
            role="全体品質確認・最終検証",
            context="""200問全体の技術的正確性と品質を一括検証します。
ドメイン配分、難易度分布、学習リソースの有効性を最終確認します。
aws-docs MCPツールを使用して包括的な品質レポートを生成します。""",
            requirements="""1. 200問全体の技術的正確性検証
2. ドメイン配分と難易度分布の確認
3. 学習リソースリンクの有効性確認
4. 重複コンテンツの最終チェック
5. 品質メトリクスの計算
6. 包括的な品質レポート生成
7. 改善提案の提供"""
        )
        
        agent = Agent(
            model=bedrock_model,
            tools=mcp_tools,
            system_prompt=system_prompt
        )
        
        logger.info("Created overall quality checker agent")
        return agent
    
    def get_mcp_context_manager(self):
        """
        Get the MCP client context manager for use with MCP-enabled agents.
        
        Returns:
            MCP client context manager
        """
        if self.mcp_client is None:
            self._initialize_mcp()
        
        return self.mcp_client
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up AgentFactory resources")
        # Note: MCP client cleanup is handled by context manager
        self.mcp_client = None
        self.mcp_tools = []
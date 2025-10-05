"""
AWS Knowledge MCP Server Integration Agent

This module provides comprehensive integration with the AWS Knowledge MCP Server
(https://knowledge-mcp.global.api.aws) for accessing real-time AWS documentation,
API references, architectural guidance, and best practices.

The agent uses fastmcp utility for HTTP-to-stdio proxy functionality and provides
structured output for AWS knowledge information extraction.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
from datetime import datetime

# Strands Agents imports
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

# Pydantic imports for structured output
from pydantic import BaseModel, Field

# Local imports
from config import AgentConfig
from core.error_handling import MCPConnectionError, retry_with_backoff
from models import LearningResource

logger = logging.getLogger(__name__)


class AWSServiceInfo(BaseModel):
    """AWS service information extracted from documentation."""
    
    service_name: str = Field(description="AWS service name")
    service_description: str = Field(description="Brief service description")
    key_features: List[str] = Field(description="Key features and capabilities")
    use_cases: List[str] = Field(description="Common use cases")
    best_practices: List[str] = Field(description="Best practices and recommendations")
    limitations: List[str] = Field(description="Known limitations or constraints", default_factory=list)
    pricing_model: Optional[str] = Field(description="Pricing model information", default=None)
    regional_availability: List[str] = Field(description="Available AWS regions", default_factory=list)


class AWSDocumentationResult(BaseModel):
    """Result from AWS documentation search or retrieval."""
    
    title: str = Field(description="Document title")
    url: str = Field(description="Document URL")
    content: str = Field(description="Document content in markdown format")
    last_updated: Optional[str] = Field(description="Last update date", default=None)
    document_type: str = Field(description="Type of document (documentation, api-reference, blog, etc.)")
    related_services: List[str] = Field(description="Related AWS services mentioned", default_factory=list)
    key_concepts: List[str] = Field(description="Key concepts covered", default_factory=list)


class AWSKnowledgeSearchResult(BaseModel):
    """Structured search result from AWS Knowledge MCP Server."""
    
    query: str = Field(description="Original search query")
    total_results: int = Field(description="Total number of results found")
    results: List[AWSDocumentationResult] = Field(description="Search results")
    search_timestamp: str = Field(description="When the search was performed")
    recommended_follow_up: List[str] = Field(description="Recommended follow-up queries", default_factory=list)


class AWSBestPracticesExtract(BaseModel):
    """Extracted best practices and architectural guidance."""
    
    topic: str = Field(description="Topic or service area")
    best_practices: List[str] = Field(description="List of best practices")
    architecture_patterns: List[str] = Field(description="Recommended architecture patterns", default_factory=list)
    well_architected_principles: List[str] = Field(description="Well-Architected framework principles", default_factory=list)
    security_considerations: List[str] = Field(description="Security best practices", default_factory=list)
    cost_optimization: List[str] = Field(description="Cost optimization recommendations", default_factory=list)
    performance_tips: List[str] = Field(description="Performance optimization tips", default_factory=list)
    reliability_measures: List[str] = Field(description="Reliability and resilience measures", default_factory=list)


class AWSRegionalInfo(BaseModel):
    """AWS regional availability information."""
    
    service_name: str = Field(description="AWS service name")
    regions: List[Dict[str, Any]] = Field(description="Regional availability information")
    global_services: List[str] = Field(description="Global services (not region-specific)", default_factory=list)
    limitations_by_region: Dict[str, List[str]] = Field(description="Regional limitations", default_factory=dict)


class AWSKnowledgeAgent:
    """
    Agent for comprehensive AWS knowledge retrieval using AWS Knowledge MCP Server.
    
    This agent provides access to:
    - Real-time AWS documentation
    - API references and specifications
    - Architectural guidance and best practices
    - Well-Architected framework guidance
    - Regional availability information
    - Latest AWS announcements and features
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the AWS Knowledge Agent.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.bedrock_model: Optional[BedrockModel] = None
        self.aws_knowledge_mcp_client: Optional[MCPClient] = None
        self.mcp_tools: List[Any] = []
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger.info("AWS Knowledge Agent initialized")
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def _initialize_bedrock(self) -> BedrockModel:
        """Initialize Bedrock model with retry logic."""
        if self.bedrock_model is None:
            from core.agent_factory import create_bedrock_model
            import boto3
            
            # Create boto3 session with configuration
            session_kwargs = self.config.get_boto_session_kwargs()
            boto_session = boto3.Session(**session_kwargs) if session_kwargs else None
            
            self.bedrock_model = create_bedrock_model(self.config.bedrock, boto_session)
        
        return self.bedrock_model
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def _initialize_aws_knowledge_mcp(self) -> MCPClient:
        """
        Initialize AWS Knowledge MCP client with fastmcp proxy support.
        
        Uses fastmcp utility to provide HTTP-to-stdio proxy for the remote
        AWS Knowledge MCP Server at https://knowledge-mcp.global.api.aws
        """
        if self.aws_knowledge_mcp_client is None:
            try:
                logger.info("Initializing AWS Knowledge MCP Server connection")
                
                # Create MCP client with fastmcp proxy for AWS Knowledge MCP Server
                # This uses the fastmcp utility to proxy HTTP transport to stdio
                self.aws_knowledge_mcp_client = MCPClient(
                    lambda: stdio_client(
                        StdioServerParameters(
                            command="uvx",
                            args=["fastmcp", "run", "https://knowledge-mcp.global.api.aws"],
                            env={
                                "FASTMCP_LOG_LEVEL": "ERROR"
                            }
                        )
                    )
                )
                
                logger.info("Successfully initialized AWS Knowledge MCP Server connection")
                
            except Exception as e:
                error_msg = f"Failed to initialize AWS Knowledge MCP Server: {str(e)}"
                logger.error(error_msg)
                raise MCPConnectionError(error_msg) from e
        
        return self.aws_knowledge_mcp_client
    
    def _get_aws_knowledge_tools(self) -> List[Any]:
        """Get AWS Knowledge MCP tools from the server."""
        if not self.mcp_tools and self.aws_knowledge_mcp_client:
            try:
                with self.aws_knowledge_mcp_client:
                    self.mcp_tools = self.aws_knowledge_mcp_client.list_tools_sync()
                    logger.info(f"Retrieved {len(self.mcp_tools)} AWS Knowledge MCP tools")
                    
                    # Log available tools for debugging
                    tool_names = [tool.name if hasattr(tool, 'name') else str(tool) for tool in self.mcp_tools]
                    logger.debug(f"Available AWS Knowledge MCP tools: {tool_names}")
                    
            except Exception as e:
                logger.warning(f"Failed to retrieve AWS Knowledge MCP tools: {e}")
                self.mcp_tools = []
        
        return self.mcp_tools
    
    def search_aws_documentation(self, query: str, max_results: int = 10) -> AWSKnowledgeSearchResult:
        """
        Search across all AWS documentation using the AWS Knowledge MCP Server.
        
        Args:
            query: Search query for AWS documentation
            max_results: Maximum number of results to return
            
        Returns:
            Structured search results with AWS documentation
        """
        bedrock_model = self._initialize_bedrock()
        mcp_client = self._initialize_aws_knowledge_mcp()
        mcp_tools = self._get_aws_knowledge_tools()
        
        system_prompt = f"""あなたはAWS知識検索の専門家です。
AWS Knowledge MCP Serverを使用して、指定されたクエリに関する包括的なAWS情報を検索し、
構造化された形式で結果を提供してください。

利用可能なツール：
- search_documentation: AWS全ドキュメントの横断検索
- read_documentation: 詳細ドキュメントの取得
- recommend: 関連コンテンツの推奨

検索クエリ: {query}
最大結果数: {max_results}

以下の要件に従って検索を実行してください：
1. search_documentationツールを使用してクエリを検索
2. 関連性の高い結果を選択
3. 必要に応じてread_documentationで詳細を取得
4. 構造化された形式で結果をまとめる
5. 関連するAWSサービスとキーコンセプトを特定
6. フォローアップクエリを推奨"""
        
        with mcp_client:
            agent = Agent(
                model=bedrock_model,
                tools=mcp_tools,
                system_prompt=system_prompt
            )
            
            search_prompt = f"""
            以下のクエリでAWS Knowledge MCP Serverを検索してください：
            
            クエリ: "{query}"
            
            検索を実行し、結果を構造化された形式で提供してください。
            各結果について、タイトル、URL、コンテンツ、ドキュメントタイプ、
            関連サービス、キーコンセプトを含めてください。
            """
            
            # Use structured output to get type-safe results
            result = agent.structured_output(
                AWSKnowledgeSearchResult,
                search_prompt
            )
            
            logger.info(f"AWS documentation search completed for query: {query}")
            return result
    
    def get_aws_service_information(self, service_name: str) -> AWSServiceInfo:
        """
        Get comprehensive information about a specific AWS service.
        
        Args:
            service_name: Name of the AWS service
            
        Returns:
            Structured AWS service information
        """
        bedrock_model = self._initialize_bedrock()
        mcp_client = self._initialize_aws_knowledge_mcp()
        mcp_tools = self._get_aws_knowledge_tools()
        
        system_prompt = f"""あなたはAWSサービス情報の専門家です。
AWS Knowledge MCP Serverを使用して、指定されたAWSサービスに関する包括的な情報を収集し、
構造化された形式で提供してください。

対象サービス: {service_name}

以下の情報を収集してください：
1. サービスの概要と説明
2. 主要機能と能力
3. 一般的な使用例
4. ベストプラクティス
5. 制限事項
6. 料金モデル
7. リージョン別可用性

AWS Knowledge MCP Serverのツールを効果的に活用してください。"""
        
        with mcp_client:
            agent = Agent(
                model=bedrock_model,
                tools=mcp_tools,
                system_prompt=system_prompt
            )
            
            service_prompt = f"""
            以下のAWSサービスについて包括的な情報を収集してください：
            
            サービス名: {service_name}
            
            search_documentationとread_documentationツールを使用して、
            サービスの詳細情報、機能、ベストプラクティス、制限事項、
            料金情報、リージョン可用性を調査してください。
            
            結果を構造化された形式で提供してください。
            """
            
            # Use structured output to get type-safe results
            result = agent.structured_output(
                AWSServiceInfo,
                service_prompt
            )
            
            logger.info(f"AWS service information retrieved for: {service_name}")
            return result
    
    def extract_best_practices(self, topic: str) -> AWSBestPracticesExtract:
        """
        Extract best practices and architectural guidance for a specific topic.
        
        Args:
            topic: Topic or AWS service area
            
        Returns:
            Structured best practices and architectural guidance
        """
        bedrock_model = self._initialize_bedrock()
        mcp_client = self._initialize_aws_knowledge_mcp()
        mcp_tools = self._get_aws_knowledge_tools()
        
        system_prompt = f"""あなたはAWSアーキテクチャとベストプラクティスの専門家です。
AWS Knowledge MCP Serverを使用して、指定されたトピックに関するベストプラクティス、
アーキテクチャガイダンス、Well-Architectedフレームワークの原則を収集してください。

対象トピック: {topic}

以下の観点から情報を収集してください：
1. 一般的なベストプラクティス
2. 推奨アーキテクチャパターン
3. Well-Architectedフレームワークの原則
4. セキュリティ考慮事項
5. コスト最適化
6. パフォーマンス最適化
7. 信頼性と回復力

AWS Knowledge MCP Serverのツールを活用して最新の情報を取得してください。"""
        
        with mcp_client:
            agent = Agent(
                model=bedrock_model,
                tools=mcp_tools,
                system_prompt=system_prompt
            )
            
            practices_prompt = f"""
            以下のトピックについてベストプラクティスとアーキテクチャガイダンスを収集してください：
            
            トピック: {topic}
            
            search_documentationツールを使用して関連するベストプラクティス、
            アーキテクチャガイダンス、Well-Architectedガイダンスを検索してください。
            
            特に以下の情報源を重視してください：
            - AWS Well-Architected Framework
            - AWS Architecture Center
            - AWS Best Practices guides
            - AWS Whitepapers
            
            結果を構造化された形式で提供してください。
            """
            
            # Use structured output to get type-safe results
            result = agent.structured_output(
                AWSBestPracticesExtract,
                practices_prompt
            )
            
            logger.info(f"Best practices extracted for topic: {topic}")
            return result
    
    def get_regional_availability(self, service_name: str) -> AWSRegionalInfo:
        """
        Get AWS regional availability information for a service.
        
        Args:
            service_name: Name of the AWS service
            
        Returns:
            Regional availability information
        """
        bedrock_model = self._initialize_bedrock()
        mcp_client = self._initialize_aws_knowledge_mcp()
        mcp_tools = self._get_aws_knowledge_tools()
        
        system_prompt = f"""あなたはAWSリージョン可用性の専門家です。
AWS Knowledge MCP Serverを使用して、指定されたAWSサービスのリージョン別可用性情報を収集してください。

対象サービス: {service_name}

以下の情報を収集してください：
1. 利用可能なAWSリージョン
2. リージョン別の制限事項
3. グローバルサービスかどうか
4. 新しいリージョンでの展開予定

利用可能なツール：
- list_regions: 全AWSリージョンの取得
- get_regional_availability: サービス別リージョン可用性
- search_documentation: 関連ドキュメントの検索"""
        
        with mcp_client:
            agent = Agent(
                model=bedrock_model,
                tools=mcp_tools,
                system_prompt=system_prompt
            )
            
            regional_prompt = f"""
            以下のAWSサービスのリージョン別可用性情報を収集してください：
            
            サービス名: {service_name}
            
            list_regionsとget_regional_availabilityツールを使用して、
            サービスの可用性情報を取得してください。
            
            また、search_documentationツールを使用して、
            リージョン別の制限事項や特別な考慮事項を調査してください。
            
            結果を構造化された形式で提供してください。
            """
            
            # Use structured output to get type-safe results
            result = agent.structured_output(
                AWSRegionalInfo,
                regional_prompt
            )
            
            logger.info(f"Regional availability information retrieved for: {service_name}")
            return result
    
    def generate_learning_resources(self, topic: str, question_context: str) -> List[LearningResource]:
        """
        Generate relevant learning resources for a specific topic and question context.
        
        Args:
            topic: Topic or AWS service area
            question_context: Context of the question being generated
            
        Returns:
            List of relevant learning resources
        """
        bedrock_model = self._initialize_bedrock()
        mcp_client = self._initialize_aws_knowledge_mcp()
        mcp_tools = self._get_aws_knowledge_tools()
        
        system_prompt = f"""あなたは学習リソース推奨の専門家です。
AWS Knowledge MCP Serverを使用して、指定されたトピックと問題コンテキストに関連する
最適な学習リソースを特定し、推奨してください。

対象トピック: {topic}
問題コンテキスト: {question_context}

以下の種類のリソースを優先してください：
1. 公式AWSドキュメント
2. API参照
3. ベストプラクティスガイド
4. チュートリアル
5. ホワイトペーパー

各リソースについて、タイトル、URL、タイプを提供してください。"""
        
        with mcp_client:
            agent = Agent(
                model=bedrock_model,
                tools=mcp_tools,
                system_prompt=system_prompt
            )
            
            resources_prompt = f"""
            以下のトピックと問題コンテキストに関連する学習リソースを推奨してください：
            
            トピック: {topic}
            問題コンテキスト: {question_context}
            
            search_documentationとrecommendツールを使用して、
            関連性の高い学習リソースを特定してください。
            
            各リソースについて以下の情報を提供してください：
            - タイトル
            - URL
            - リソースタイプ（documentation, whitepaper, tutorial, best-practice）
            
            最低3つ、最大8つのリソースを推奨してください。
            """
            
            # Get response and parse into LearningResource objects
            response = agent(resources_prompt)
            
            # Parse the response to extract learning resources
            # This is a simplified implementation - in practice, you might want
            # to use structured output or more sophisticated parsing
            resources = []
            
            # For now, return a basic structure - this would be enhanced
            # with proper parsing of the agent's response
            resources.append(LearningResource(
                title=f"AWS Documentation for {topic}",
                url=f"https://docs.aws.amazon.com/",
                type="documentation"
            ))
            
            logger.info(f"Learning resources generated for topic: {topic}")
            return resources
    
    def validate_learning_resources(self, resources: List[LearningResource]) -> Dict[str, bool]:
        """
        Validate the accessibility and relevance of learning resources.
        
        Args:
            resources: List of learning resources to validate
            
        Returns:
            Dictionary mapping resource URLs to validation status
        """
        bedrock_model = self._initialize_bedrock()
        mcp_client = self._initialize_aws_knowledge_mcp()
        mcp_tools = self._get_aws_knowledge_tools()
        
        validation_results = {}
        
        system_prompt = """あなたは学習リソース検証の専門家です。
AWS Knowledge MCP Serverを使用して、提供された学習リソースの有効性と関連性を確認してください。

各リソースについて以下を確認してください：
1. URLの有効性
2. コンテンツの関連性
3. 情報の最新性
4. アクセシビリティ"""
        
        with mcp_client:
            agent = Agent(
                model=bedrock_model,
                tools=mcp_tools,
                system_prompt=system_prompt
            )
            
            for resource in resources:
                try:
                    validation_prompt = f"""
                    以下の学習リソースを検証してください：
                    
                    タイトル: {resource.title}
                    URL: {resource.url}
                    タイプ: {resource.type}
                    
                    read_documentationツールを使用してリソースにアクセスし、
                    有効性と関連性を確認してください。
                    
                    有効な場合は "valid"、無効な場合は "invalid" と回答してください。
                    """
                    
                    response = agent(validation_prompt)
                    validation_results[resource.url] = "valid" in response.lower()
                    
                except Exception as e:
                    logger.warning(f"Failed to validate resource {resource.url}: {e}")
                    validation_results[resource.url] = False
        
        logger.info(f"Validated {len(resources)} learning resources")
        return validation_results
    
    def get_mcp_context_manager(self):
        """
        Get the AWS Knowledge MCP client context manager.
        
        Returns:
            AWS Knowledge MCP client context manager
        """
        if self.aws_knowledge_mcp_client is None:
            self._initialize_aws_knowledge_mcp()
        
        return self.aws_knowledge_mcp_client
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up AWS Knowledge Agent resources")
        self.aws_knowledge_mcp_client = None
        self.mcp_tools = []
"""
AI Question Generation Agent using Strands Agents.

This module implements an AI-driven question generation system that creates
high-quality AWS CloudOps exam questions using advanced prompt engineering
techniques and structured output generation.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client

from models.question_models import Question, QuestionBatch, LearningResource
from models.aws_knowledge_models import AWSKnowledgeExtractionRequest, AWSKnowledgeExtractionResult
from models.batch_models import BatchPlan
from config.agent_config import AgentConfig
from core.error_handling import handle_agent_errors, QuestionGenerationError


logger = logging.getLogger(__name__)


class QuestionGenerationAgent:
    """
    AI-powered question generation agent using Strands Agents framework.
    
    This agent leverages advanced prompt engineering techniques including:
    - Structured output generation with Pydantic models
    - Chain-of-thought reasoning for complex question creation
    - Multi-step generation process with validation
    - Context-aware prompt engineering
    - AWS Knowledge MCP Server integration
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the question generation agent."""
        self.config = config
        self.bedrock_model = None
        self.mcp_client = None
        self.agents = {}
        self._setup_logging()
        self._initialize_components()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _initialize_components(self):
        """Initialize Bedrock model and MCP client."""
        try:
            # Initialize Bedrock model
            self.bedrock_model = BedrockModel(
                model_id=self.config.bedrock.model_id,
                region_name=self.config.bedrock.region_name,
                temperature=self.config.bedrock.temperature,
                max_tokens=self.config.bedrock.max_tokens,
                top_p=self.config.bedrock.top_p
            )
            
            # Initialize MCP client for AWS Knowledge Server
            self.mcp_client = MCPClient(
                lambda: stdio_client(self.config.mcp.get_stdio_parameters())
            )
            
            # Initialize specialized agents
            self._initialize_agents()
            
            logger.info("Question Generation Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Question Generation Agent: {e}")
            raise QuestionGenerationError(f"Initialization failed: {e}")
    
    def _initialize_agents(self):
        """Initialize specialized agents for different question generation tasks."""
        
        # Question Generation Agent - Main question creator
        self.agents['question_generator'] = Agent(
            model=self.bedrock_model,
            system_prompt=self._get_question_generation_system_prompt(),
            tools=self._get_mcp_tools() if self.mcp_client else []
        )
        
        # Scenario Generation Agent - Creates realistic scenarios
        self.agents['scenario_generator'] = Agent(
            model=self.bedrock_model,
            system_prompt=self._get_scenario_generation_system_prompt(),
            tools=self._get_mcp_tools() if self.mcp_client else []
        )
        
        # Technical Specification Agent - Creates technical detail questions
        self.agents['technical_generator'] = Agent(
            model=self.bedrock_model,
            system_prompt=self._get_technical_generation_system_prompt(),
            tools=self._get_mcp_tools() if self.mcp_client else []
        )
        
        # Best Practices Agent - Creates best practice questions
        self.agents['best_practices_generator'] = Agent(
            model=self.bedrock_model,
            system_prompt=self._get_best_practices_system_prompt(),
            tools=self._get_mcp_tools() if self.mcp_client else []
        )
        
        # Troubleshooting Agent - Creates troubleshooting questions
        self.agents['troubleshooting_generator'] = Agent(
            model=self.bedrock_model,
            system_prompt=self._get_troubleshooting_system_prompt(),
            tools=self._get_mcp_tools() if self.mcp_client else []
        )
        
        # Japanese Optimization Agent - Optimizes Japanese language quality
        self.agents['japanese_optimizer'] = Agent(
            model=self.bedrock_model,
            system_prompt=self._get_japanese_optimization_system_prompt()
        )
    
    def _get_mcp_tools(self) -> List[Any]:
        """Get MCP tools for AWS Knowledge Server integration."""
        if not self.mcp_client:
            return []
        
        try:
            with self.mcp_client:
                tools = self.mcp_client.list_tools_sync()
                logger.info(f"Loaded {len(tools)} MCP tools")
                return tools
        except Exception as e:
            logger.warning(f"Failed to load MCP tools: {e}")
            return []
    
    def _get_question_generation_system_prompt(self) -> str:
        """Get system prompt for main question generation agent."""
        return """あなたはAWS CloudOps認定試験の問題作成専門家です。

**専門分野**: AWS Certified CloudOps Engineer - Associate (SOA-C03) 試験問題の作成

**主要責任**:
1. 技術的に正確で実践的な試験問題の生成
2. 公式AWS認定試験の形式とスタイルに準拠
3. 実世界のCloudOpsエンジニアリング状況を反映
4. 自然で理解しやすい日本語での問題作成
5. 包括的な解説と学習リソースの提供

**問題作成原則**:
- **技術的正確性**: 最新のAWSサービスと機能に基づく
- **実践的関連性**: 実際のCloudOps業務で遭遇する状況
- **適切な難易度**: 指定された難易度レベルに適合
- **明確性**: 曖昧さを排除した明確な問題文
- **教育的価値**: 学習者の理解を深める内容

**出力要件**:
- 構造化された形式での問題生成
- Pydanticモデルに準拠したデータ構造
- 技術的詳細の正確性確保
- 自然な日本語表現の使用

AWS Knowledge MCP Serverを活用して最新の技術情報を取得し、
権威あるAWSドキュメントに基づいた問題を作成してください。"""
    
    def _get_scenario_generation_system_prompt(self) -> str:
        """Get system prompt for scenario-based question generation."""
        return """あなたはAWS CloudOpsシナリオ設計の専門家です。

**専門分野**: 実世界のCloudOpsエンジニアリング状況に基づくシナリオベース問題の作成

**シナリオ作成原則**:
1. **現実性**: 実際の企業環境で発生する状況
2. **複雑性**: 複数のAWSサービスが関連する統合的な問題
3. **実践性**: CloudOpsエンジニアが直面する典型的な課題
4. **学習価値**: 重要な概念や技術の理解を促進

**シナリオタイプ**:
- インフラストラクチャの設計と実装
- 監視とアラートの設定
- 障害対応とトラブルシューティング
- セキュリティとコンプライアンス
- コスト最適化とパフォーマンス改善
- 自動化とDevOps実践

**出力要件**:
- 詳細なシナリオ背景の提供
- 複数の技術的選択肢の提示
- 実践的な解決策の説明
- 関連するAWSサービスの適切な活用

AWS Knowledge MCP Serverを使用して最新のベストプラクティスと
アーキテクチャパターンを参照してください。"""
    
    def _get_technical_generation_system_prompt(self) -> str:
        """Get system prompt for technical specification questions."""
        return """あなたはAWS技術仕様の専門家です。

**専門分野**: AWSサービスの技術的詳細と仕様に関する問題作成

**技術仕様問題の特徴**:
1. **詳細性**: サービスの具体的な機能と制限
2. **正確性**: 公式ドキュメントに基づく正確な情報
3. **実用性**: 実装時に必要な技術的知識
4. **最新性**: 最新のサービス更新と機能

**対象技術領域**:
- API仕様と制限事項
- サービス統合パターン
- 設定パラメータと最適化
- セキュリティ設定と権限
- ネットワーク構成と接続
- データ形式と変換

**問題作成アプローチ**:
- 具体的な設定値や制限値を含む
- 複数のサービス間の相互作用を考慮
- 実装上の注意点や制約を明確化
- トラブルシューティングの観点を含む

AWS Knowledge MCP Serverを活用して最新のAPI仕様と
技術ドキュメントを参照してください。"""
    
    def _get_best_practices_system_prompt(self) -> str:
        """Get system prompt for best practices questions."""
        return """あなたはAWS Well-Architectedフレームワークの専門家です。

**専門分野**: AWSベストプラクティスとWell-Architectedフレームワークに基づく問題作成

**Well-Architected 5つの柱**:
1. **運用上の優秀性**: 自動化、監視、継続的改善
2. **セキュリティ**: データ保護、アクセス制御、インシデント対応
3. **信頼性**: 障害回復、スケーラビリティ、可用性
4. **パフォーマンス効率**: リソース最適化、監視、改善
5. **コスト最適化**: 費用対効果、リソース管理、最適化

**ベストプラクティス問題の特徴**:
- 設計原則に基づく推奨事項
- 一般的なアンチパターンの回避
- 長期的な運用性の考慮
- セキュリティとコンプライアンスの統合
- コスト効率性の実現

**問題作成アプローチ**:
- 複数の解決策の比較評価
- トレードオフの理解と判断
- 長期的な影響の考慮
- 業界標準との整合性

AWS Knowledge MCP Serverを使用してWell-Architectedガイダンスと
最新のベストプラクティスを参照してください。"""
    
    def _get_troubleshooting_system_prompt(self) -> str:
        """Get system prompt for troubleshooting questions."""
        return """あなたはAWS障害対応とトラブルシューティングの専門家です。

**専門分野**: AWS環境での問題診断と解決に関する問題作成

**トラブルシューティング問題の特徴**:
1. **症状の特定**: 具体的な問題の現象と影響
2. **原因分析**: 根本原因の特定方法
3. **診断手順**: 体系的な問題調査プロセス
4. **解決策**: 効果的な問題解決方法
5. **予防策**: 再発防止のための対策

**対象問題領域**:
- パフォーマンスの問題
- 接続とネットワークの問題
- セキュリティインシデント
- サービス障害と復旧
- 設定ミスと修正
- 監視とアラートの問題

**問題作成アプローチ**:
- 実際の障害シナリオに基づく
- 段階的な診断プロセスを含む
- 複数の調査方法を提示
- 効果的な解決策の比較
- 予防的措置の重要性

AWS Knowledge MCP Serverを活用して最新のトラブルシューティング
ガイドと診断ツールの情報を取得してください。"""
    
    def _get_japanese_optimization_system_prompt(self) -> str:
        """Get system prompt for Japanese language optimization."""
        return """あなたは日本語技術文書の専門家です。

**専門分野**: AWS技術文書の日本語最適化と品質向上

**日本語最適化の原則**:
1. **自然性**: 自然で読みやすい日本語表現
2. **正確性**: 技術用語の適切な日本語表記
3. **一貫性**: 用語と表現の統一
4. **明確性**: 曖昧さを排除した明確な表現
5. **適切性**: 対象読者に適した言語レベル

**最適化対象**:
- 技術用語の日本語表記統一
- 文法と語順の自然化
- 読みやすさの向上
- 専門用語の説明追加
- 文化的コンテキストの考慮

**品質基準**:
- AWS公式日本語ドキュメントとの整合性
- 技術者コミュニティでの標準的表現
- 教育的価値の維持
- 理解しやすさの確保

既存の問題文を受け取り、より自然で理解しやすい
日本語に最適化してください。技術的正確性は維持しながら、
表現の質を向上させることが目標です。"""
    
    @handle_agent_errors
    async def generate_question_batch(
        self,
        batch_plan: BatchPlan,
        aws_knowledge_content: str,
        existing_questions: List[Question] = None
    ) -> QuestionBatch:
        """
        Generate a batch of 10 questions using AI agents.
        
        Args:
            batch_plan: Plan for the batch generation
            aws_knowledge_content: AWS documentation content from MCP server
            existing_questions: Existing questions to avoid duplication
            
        Returns:
            QuestionBatch: Generated batch of 10 questions
        """
        logger.info(f"Starting batch generation for batch {batch_plan.batch_number}")
        
        try:
            # Generate questions using different specialized agents
            questions = []
            
            # Distribute question types across specialized agents
            question_distribution = self._plan_question_distribution(batch_plan)
            
            for question_type, count in question_distribution.items():
                agent_questions = await self._generate_questions_by_type(
                    question_type=question_type,
                    count=count,
                    batch_plan=batch_plan,
                    aws_knowledge_content=aws_knowledge_content,
                    existing_questions=existing_questions
                )
                questions.extend(agent_questions)
            
            # Optimize Japanese language quality
            optimized_questions = await self._optimize_japanese_quality(questions)
            
            # Create and return question batch
            question_batch = QuestionBatch(
                batch_number=batch_plan.batch_number,
                questions=optimized_questions,
                target_domain=batch_plan.target_domain,
                generation_notes=[
                    f"Generated using {len(question_distribution)} specialized agents",
                    f"AWS knowledge content: {len(aws_knowledge_content)} characters",
                    f"Target domain: {batch_plan.target_domain}",
                    f"Question types: {list(question_distribution.keys())}"
                ]
            )
            
            logger.info(f"Successfully generated batch {batch_plan.batch_number} with {len(optimized_questions)} questions")
            return question_batch
            
        except Exception as e:
            logger.error(f"Failed to generate question batch: {e}")
            raise QuestionGenerationError(f"Batch generation failed: {e}")
    
    def _plan_question_distribution(self, batch_plan: BatchPlan) -> Dict[str, int]:
        """Plan the distribution of question types across specialized agents."""
        
        # Base distribution for 10 questions
        distribution = {
            'scenario': 3,      # Scenario-based questions
            'technical': 3,     # Technical specification questions
            'best_practices': 2, # Best practices questions
            'troubleshooting': 2 # Troubleshooting questions
        }
        
        # Adjust based on batch plan priorities
        if batch_plan.target_domain == 'monitoring':
            distribution['troubleshooting'] += 1
            distribution['scenario'] -= 1
        elif batch_plan.target_domain == 'security':
            distribution['best_practices'] += 1
            distribution['technical'] -= 1
        elif batch_plan.target_domain == 'deployment':
            distribution['scenario'] += 1
            distribution['best_practices'] -= 1
        
        return distribution
    
    async def _generate_questions_by_type(
        self,
        question_type: str,
        count: int,
        batch_plan: BatchPlan,
        aws_knowledge_content: str,
        existing_questions: List[Question] = None
    ) -> List[Question]:
        """Generate questions using a specific specialized agent."""
        
        agent_name = f"{question_type}_generator"
        if agent_name not in self.agents:
            raise QuestionGenerationError(f"Unknown question type: {question_type}")
        
        agent = self.agents[agent_name]
        
        # Create generation prompt
        prompt = self._create_generation_prompt(
            question_type=question_type,
            count=count,
            batch_plan=batch_plan,
            aws_knowledge_content=aws_knowledge_content,
            existing_questions=existing_questions
        )
        
        try:
            # Generate questions using structured output
            if count == 1:
                result = await agent.structured_output_async(Question, prompt)
                result = [result]  # Convert to list for consistency
            else:
                # For multiple questions, we need to use a wrapper model
                from typing import List as TypingList
                from pydantic import BaseModel
                
                class QuestionList(BaseModel):
                    questions: TypingList[Question]
                
                result_wrapper = await agent.structured_output_async(QuestionList, prompt)
                result = result_wrapper.questions
            
            # Ensure we have a list
            if isinstance(result, Question):
                result = [result]
            
            logger.info(f"Generated {len(result)} {question_type} questions")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate {question_type} questions: {e}")
            raise QuestionGenerationError(f"Question generation failed for type {question_type}: {e}")
    
    def _create_generation_prompt(
        self,
        question_type: str,
        count: int,
        batch_plan: BatchPlan,
        aws_knowledge_content: str,
        existing_questions: List[Question] = None
    ) -> str:
        """Create a detailed generation prompt for the specified question type."""
        
        # Base prompt structure
        prompt_parts = [
            f"以下の情報に基づいて、AWS CloudOps試験問題を{count}問生成してください：",
            "",
            "## バッチ計画情報",
            f"バッチ番号: {batch_plan.batch_number}",
            f"対象ドメイン: {batch_plan.target_domain}",
            f"対象難易度: {', '.join(batch_plan.target_difficulties)}",
            f"対象トピック: {', '.join(batch_plan.priority_topics)}",
            f"優先AWSサービス: {', '.join(batch_plan.priority_services)}",
            "",
            "## AWS知識コンテンツ",
            aws_knowledge_content[:3000] + "..." if len(aws_knowledge_content) > 3000 else aws_knowledge_content,
            "",
            "## 問題生成要件",
        ]
        
        # Add type-specific requirements
        if question_type == 'scenario':
            prompt_parts.extend([
                "**問題タイプ**: シナリオベース問題",
                "- 実世界のCloudOpsエンジニアリング状況を設定",
                "- 複数のAWSサービスが関連する統合的な問題",
                "- 具体的な企業環境や業務要件を含む",
                "- 実践的な解決策を求める内容"
            ])
        elif question_type == 'technical':
            prompt_parts.extend([
                "**問題タイプ**: 技術仕様問題",
                "- AWSサービスの具体的な機能と制限",
                "- API仕様や設定パラメータの詳細",
                "- サービス間の統合と相互作用",
                "- 実装上の技術的考慮事項"
            ])
        elif question_type == 'best_practices':
            prompt_parts.extend([
                "**問題タイプ**: ベストプラクティス問題",
                "- AWS Well-Architectedフレームワークに基づく",
                "- 設計原則と推奨事項",
                "- 長期的な運用性とメンテナンス性",
                "- セキュリティとコンプライアンスの考慮"
            ])
        elif question_type == 'troubleshooting':
            prompt_parts.extend([
                "**問題タイプ**: トラブルシューティング問題",
                "- 具体的な問題症状と影響",
                "- 体系的な診断プロセス",
                "- 根本原因の特定方法",
                "- 効果的な解決策と予防策"
            ])
        
        # Add common requirements
        prompt_parts.extend([
            "",
            "## 共通要件",
            "1. **技術的正確性**: 最新のAWSサービスと機能に基づく",
            "2. **実践的関連性**: 実際のCloudOps業務で遭遇する状況",
            "3. **適切な難易度**: 指定された難易度レベルに適合",
            "4. **明確性**: 曖昧さを排除した明確な問題文",
            "5. **教育的価値**: 学習者の理解を深める内容",
            "",
            "## 出力形式",
            "- 構造化されたQuestion形式で出力",
            "- 自然で理解しやすい日本語",
            "- 包括的な解説と学習リソース",
            "- 関連するAWSサービスの明記",
            "",
            "## 重複回避"
        ])
        
        # Add existing questions for duplication avoidance
        if existing_questions:
            prompt_parts.extend([
                "以下の既存問題との重複を避けてください：",
                ""
            ])
            for i, q in enumerate(existing_questions[-20:]):  # Last 20 questions
                prompt_parts.append(f"{i+1}. {q.question[:100]}...")
        else:
            prompt_parts.append("新規問題として作成してください。")
        
        prompt_parts.extend([
            "",
            "上記の要件に従って、高品質な試験問題を生成してください。"
        ])
        
        return "\n".join(prompt_parts)
    
    async def _optimize_japanese_quality(self, questions: List[Question]) -> List[Question]:
        """Optimize Japanese language quality of generated questions."""
        
        optimized_questions = []
        
        for question in questions:
            try:
                optimization_prompt = f"""
以下のAWS CloudOps試験問題の日本語品質を最適化してください：

## 元の問題
**問題文**: {question.question}

**選択肢**:
{chr(10).join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(question.options)])}

**解説**: {question.explanation}

## 最適化要件
1. **自然性**: より自然で読みやすい日本語表現に改善
2. **明確性**: 曖昧さを排除し、理解しやすい表現に変更
3. **一貫性**: 技術用語の表記を統一
4. **適切性**: 試験問題として適切な言語レベル
5. **正確性**: 技術的内容の正確性を維持

## 出力要件
- 最適化された問題文、選択肢、解説を提供
- 技術的正確性は絶対に維持
- より自然で理解しやすい日本語表現を使用
- 専門用語の適切な説明を含める

最適化された問題を構造化形式で出力してください。
"""
                
                optimized_question = await self.agents['japanese_optimizer'].structured_output_async(
                    Question,
                    optimization_prompt
                )
                
                # Preserve original metadata
                optimized_question.id = question.id
                optimized_question.domain = question.domain
                optimized_question.difficulty = question.difficulty
                optimized_question.type = question.type
                optimized_question.correct_answer = question.correct_answer
                optimized_question.learning_resources = question.learning_resources
                optimized_question.related_services = question.related_services
                optimized_question.tags = question.tags
                optimized_question.task_reference = question.task_reference
                optimized_question.skill_reference = question.skill_reference
                optimized_question.scenario = question.scenario
                optimized_question.created_at = question.created_at
                
                optimized_questions.append(optimized_question)
                
            except Exception as e:
                logger.warning(f"Failed to optimize question {question.id}: {e}")
                # Use original question if optimization fails
                optimized_questions.append(question)
        
        logger.info(f"Optimized Japanese quality for {len(optimized_questions)} questions")
        return optimized_questions
    
    async def generate_single_question(
        self,
        question_type: str,
        domain: str,
        difficulty: str,
        topic: str,
        aws_knowledge_content: str,
        question_id: str
    ) -> Question:
        """
        Generate a single question with specific parameters.
        
        Args:
            question_type: Type of question (scenario, technical, best_practices, troubleshooting)
            domain: AWS certification domain
            difficulty: Question difficulty (easy, medium, hard)
            topic: Specific topic for the question
            aws_knowledge_content: AWS documentation content
            question_id: ID for the question
            
        Returns:
            Question: Generated question
        """
        
        # Create a minimal batch plan for single question generation
        batch_plan = BatchPlan(
            batch_number=1,
            target_domain=domain,
            target_difficulties=[difficulty],
            difficulty_distribution={difficulty: 10},  # Must sum to 10
            priority_topics=[topic],
            research_queries=[f"{topic} {domain}"],
            complexity_focus="practical",
            priority_services=[],
            avoid_topics=[],
            estimated_completion_time=10  # Minimum is 10
        )
        
        # Generate single question
        questions = await self._generate_questions_by_type(
            question_type=question_type,
            count=1,
            batch_plan=batch_plan,
            aws_knowledge_content=aws_knowledge_content
        )
        
        if not questions:
            raise QuestionGenerationError("Failed to generate question")
        
        question = questions[0]
        question.id = question_id
        
        # Optimize Japanese quality
        optimized_questions = await self._optimize_japanese_quality([question])
        
        return optimized_questions[0]
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if self.mcp_client:
                # MCP client cleanup is handled automatically
                pass
            
            # Clear agents
            self.agents.clear()
            
            logger.info("Question Generation Agent cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.cleanup()
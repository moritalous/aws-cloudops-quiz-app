"""
Tests for Question Generation Agent.

This module contains comprehensive tests for the AI-driven question generation
system, including unit tests, integration tests, and quality validation tests.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from core.question_generation_agent import QuestionGenerationAgent
from models.question_models import Question, QuestionBatch, LearningResource
from models.batch_models import BatchPlan
from config.agent_config import AgentConfig, BedrockConfig, MCPConfig
from core.error_handling import QuestionGenerationError


class TestQuestionGenerationAgent:
    """Test cases for QuestionGenerationAgent."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return AgentConfig(
            bedrock=BedrockConfig(
                model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
                region_name="us-west-2",
                temperature=0.3,
                max_tokens=4000
            ),
            mcp=MCPConfig(
                server_name="aws-docs-test",
                connection_timeout=10
            ),
            debug_mode=True
        )
    
    @pytest.fixture
    def sample_batch_plan(self):
        """Create sample batch plan for testing."""
        return BatchPlan(
            batch_number=1,
            target_domain="monitoring",
            target_difficulties=["medium"],
            target_topics=["CloudWatch monitoring", "CloudWatch alarms"],
            research_queries=["CloudWatch best practices"],
            question_types={"scenario": 2, "technical": 2, "best_practices": 1, "troubleshooting": 1},
            priority_services=["CloudWatch", "SNS"],
            avoid_topics=["Basic monitoring"],
            estimated_completion_time=10
        )
    
    @pytest.fixture
    def sample_aws_content(self):
        """Create sample AWS knowledge content."""
        return """
# Amazon CloudWatch Best Practices

## Monitoring Strategy
- Use custom metrics for application-specific monitoring
- Set up appropriate alarm thresholds based on historical data
- Implement composite alarms for complex scenarios

## Cost Optimization
- Use metric filters to reduce log ingestion costs
- Set appropriate retention periods for logs

## Security Considerations
- Use IAM roles for CloudWatch access
- Enable CloudTrail for API logging
"""
    
    @pytest.fixture
    def sample_question(self):
        """Create sample question for testing."""
        return Question(
            id="q001",
            domain="monitoring",
            difficulty="medium",
            type="single",
            question="CloudWatchでカスタムメトリクスを効率的に監視するための最適な方法は何ですか？",
            options=[
                "すべてのメトリクスを1分間隔で収集する",
                "アプリケーション固有のメトリクスを定義し、適切な間隔で収集する",
                "デフォルトメトリクスのみを使用する",
                "すべてのメトリクスを詳細監視で設定する"
            ],
            correct_answer="B",
            explanation="アプリケーション固有のカスタムメトリクスを定義し、適切な収集間隔を設定することで、効率的で費用対効果の高い監視が実現できます。",
            learning_resources=[
                LearningResource(
                    title="CloudWatch Custom Metrics",
                    url="https://docs.aws.amazon.com/cloudwatch/latest/monitoring/publishingMetrics.html",
                    type="documentation"
                )
            ],
            related_services=["CloudWatch", "EC2"],
            tags=["monitoring", "custom-metrics"]
        )
    
    def test_initialization(self, config):
        """Test agent initialization."""
        with patch('core.question_generation_agent.BedrockModel') as mock_bedrock:
            with patch('core.question_generation_agent.MCPClient') as mock_mcp:
                agent = QuestionGenerationAgent(config)
                
                assert agent.config == config
                assert mock_bedrock.called
                assert mock_mcp.called
                assert len(agent.agents) == 6  # 5 generators + 1 optimizer
    
    def test_agent_types_initialization(self, config):
        """Test that all required agent types are initialized."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                agent = QuestionGenerationAgent(config)
                
                expected_agents = [
                    'question_generator',
                    'scenario_generator',
                    'technical_generator',
                    'best_practices_generator',
                    'troubleshooting_generator',
                    'japanese_optimizer'
                ]
                
                for agent_name in expected_agents:
                    assert agent_name in agent.agents
    
    def test_question_distribution_planning(self, config, sample_batch_plan):
        """Test question distribution planning logic."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                agent = QuestionGenerationAgent(config)
                
                distribution = agent._plan_question_distribution(sample_batch_plan)
                
                # Check total questions is 10
                assert sum(distribution.values()) == 10
                
                # Check all question types are present
                expected_types = ['scenario', 'technical', 'best_practices', 'troubleshooting']
                for q_type in expected_types:
                    assert q_type in distribution
                    assert distribution[q_type] > 0
    
    def test_domain_specific_distribution(self, config):
        """Test domain-specific question distribution adjustments."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                agent = QuestionGenerationAgent(config)
                
                # Test monitoring domain
                monitoring_plan = BatchPlan(
                    batch_number=1,
                    target_domain="monitoring",
                    target_difficulties=["medium"],
                    target_topics=["CloudWatch"],
                    research_queries=["CloudWatch"],
                    question_types={"scenario": 3, "technical": 3, "best_practices": 2, "troubleshooting": 2},
                    priority_services=["CloudWatch"],
                    avoid_topics=[],
                    estimated_completion_time=10
                )
                
                distribution = agent._plan_question_distribution(monitoring_plan)
                
                # Monitoring should have more troubleshooting questions
                assert distribution['troubleshooting'] >= 2
                assert sum(distribution.values()) == 10
    
    def test_generation_prompt_creation(self, config, sample_batch_plan, sample_aws_content):
        """Test generation prompt creation."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                agent = QuestionGenerationAgent(config)
                
                prompt = agent._create_generation_prompt(
                    question_type="scenario",
                    count=2,
                    batch_plan=sample_batch_plan,
                    aws_knowledge_content=sample_aws_content
                )
                
                # Check prompt contains required elements
                assert "シナリオベース問題" in prompt
                assert "バッチ番号: 1" in prompt
                assert "対象ドメイン: monitoring" in prompt
                assert "CloudWatch monitoring" in prompt
                assert "実世界のCloudOpsエンジニアリング状況" in prompt
    
    def test_prompt_type_specific_requirements(self, config, sample_batch_plan, sample_aws_content):
        """Test that different question types have specific requirements in prompts."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                agent = QuestionGenerationAgent(config)
                
                # Test scenario prompt
                scenario_prompt = agent._create_generation_prompt(
                    "scenario", 1, sample_batch_plan, sample_aws_content
                )
                assert "実世界のCloudOpsエンジニアリング状況" in scenario_prompt
                
                # Test technical prompt
                technical_prompt = agent._create_generation_prompt(
                    "technical", 1, sample_batch_plan, sample_aws_content
                )
                assert "API仕様や設定パラメータ" in technical_prompt
                
                # Test best practices prompt
                bp_prompt = agent._create_generation_prompt(
                    "best_practices", 1, sample_batch_plan, sample_aws_content
                )
                assert "Well-Architectedフレームワーク" in bp_prompt
                
                # Test troubleshooting prompt
                ts_prompt = agent._create_generation_prompt(
                    "troubleshooting", 1, sample_batch_plan, sample_aws_content
                )
                assert "体系的な診断プロセス" in ts_prompt
    
    @pytest.mark.asyncio
    async def test_single_question_generation_mock(self, config, sample_aws_content):
        """Test single question generation with mocked agent."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                agent = QuestionGenerationAgent(config)
                
                # Mock the agent's structured_output_async method
                mock_question = Question(
                    id="q_test_001",
                    domain="security",
                    difficulty="medium",
                    type="single",
                    question="Test question",
                    options=["A", "B", "C", "D"],
                    correct_answer="A",
                    explanation="Test explanation",
                    learning_resources=[
                        LearningResource(
                            title="Test Resource",
                            url="https://example.com",
                            type="documentation"
                        )
                    ],
                    related_services=["S3"],
                    tags=["security"]
                )
                
                # Mock the agents
                for agent_name in agent.agents:
                    agent.agents[agent_name].structured_output_async = AsyncMock(return_value=mock_question)
                
                result = await agent.generate_single_question(
                    question_type="best_practices",
                    domain="security",
                    difficulty="medium",
                    topic="S3 security",
                    aws_knowledge_content=sample_aws_content,
                    question_id="q_test_001"
                )
                
                assert isinstance(result, Question)
                assert result.id == "q_test_001"
                assert result.domain == "security"
                assert result.difficulty == "medium"
    
    @pytest.mark.asyncio
    async def test_batch_generation_mock(self, config, sample_batch_plan, sample_aws_content):
        """Test batch generation with mocked agents."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                agent = QuestionGenerationAgent(config)
                
                # Create mock questions
                mock_questions = []
                for i in range(10):
                    mock_question = Question(
                        id=f"q{i+1:03d}",
                        domain="monitoring",
                        difficulty="medium",
                        type="single",
                        question=f"Test question {i+1}",
                        options=["A", "B", "C", "D"],
                        correct_answer="A",
                        explanation=f"Test explanation {i+1}",
                        learning_resources=[
                            LearningResource(
                                title="Test Resource",
                                url="https://example.com",
                                type="documentation"
                            )
                        ],
                        related_services=["CloudWatch"],
                        tags=["monitoring"]
                    )
                    mock_questions.append(mock_question)
                
                # Mock the _generate_questions_by_type method
                async def mock_generate_by_type(question_type, count, batch_plan, aws_knowledge_content, existing_questions=None):
                    return mock_questions[:count]
                
                agent._generate_questions_by_type = mock_generate_by_type
                
                # Mock Japanese optimization
                async def mock_optimize_japanese(questions):
                    return questions
                
                agent._optimize_japanese_quality = mock_optimize_japanese
                
                result = await agent.generate_question_batch(
                    batch_plan=sample_batch_plan,
                    aws_knowledge_content=sample_aws_content
                )
                
                assert isinstance(result, QuestionBatch)
                assert result.batch_number == 1
                assert len(result.questions) == 10
                assert result.target_domain == "monitoring"
    
    def test_system_prompts_content(self, config):
        """Test that system prompts contain required content."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                agent = QuestionGenerationAgent(config)
                
                # Test main question generation prompt
                main_prompt = agent._get_question_generation_system_prompt()
                assert "AWS CloudOps認定試験の問題作成専門家" in main_prompt
                assert "技術的正確性" in main_prompt
                assert "構造化された形式" in main_prompt
                
                # Test scenario generation prompt
                scenario_prompt = agent._get_scenario_generation_system_prompt()
                assert "シナリオベース問題" in scenario_prompt
                assert "実世界のCloudOpsエンジニアリング状況" in scenario_prompt
                
                # Test Japanese optimization prompt
                japanese_prompt = agent._get_japanese_optimization_system_prompt()
                assert "日本語技術文書の専門家" in japanese_prompt
                assert "自然性" in japanese_prompt
                assert "技術用語の適切な日本語表記" in japanese_prompt
    
    def test_cleanup(self, config):
        """Test agent cleanup."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                agent = QuestionGenerationAgent(config)
                
                # Ensure agents are initialized
                assert len(agent.agents) > 0
                
                # Test cleanup
                agent.cleanup()
                
                # Agents should be cleared
                assert len(agent.agents) == 0
    
    def test_context_manager(self, config):
        """Test context manager functionality."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                with QuestionGenerationAgent(config) as agent:
                    assert isinstance(agent, QuestionGenerationAgent)
                    assert len(agent.agents) > 0
                
                # After context exit, agents should be cleaned up
                assert len(agent.agents) == 0
    
    def test_error_handling_initialization(self):
        """Test error handling during initialization."""
        config = AgentConfig()
        
        with patch('core.question_generation_agent.BedrockModel', side_effect=Exception("Bedrock error")):
            with pytest.raises(QuestionGenerationError):
                QuestionGenerationAgent(config)
    
    @pytest.mark.asyncio
    async def test_error_handling_generation(self, config, sample_batch_plan, sample_aws_content):
        """Test error handling during question generation."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                agent = QuestionGenerationAgent(config)
                
                # Mock agent to raise exception
                async def mock_generate_error(*args, **kwargs):
                    raise Exception("Generation error")
                
                agent._generate_questions_by_type = mock_generate_error
                
                with pytest.raises(QuestionGenerationError):
                    await agent.generate_question_batch(
                        batch_plan=sample_batch_plan,
                        aws_knowledge_content=sample_aws_content
                    )


class TestQuestionGenerationIntegration:
    """Integration tests for question generation."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_generation_flow(self):
        """Test full question generation flow (requires actual AWS credentials)."""
        # This test would require actual AWS credentials and MCP server
        # Skip in normal test runs
        pytest.skip("Integration test requires AWS credentials and MCP server")
    
    @pytest.mark.integration
    def test_mcp_server_connection(self):
        """Test MCP server connection (requires MCP server running)."""
        # This test would require actual MCP server
        pytest.skip("Integration test requires running MCP server")


class TestPromptEngineering:
    """Tests for prompt engineering techniques."""
    
    def test_prompt_structure(self, config, sample_batch_plan, sample_aws_content):
        """Test prompt structure and content."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                agent = QuestionGenerationAgent(config)
                
                prompt = agent._create_generation_prompt(
                    question_type="scenario",
                    count=3,
                    batch_plan=sample_batch_plan,
                    aws_knowledge_content=sample_aws_content
                )
                
                # Check prompt structure
                assert "## バッチ計画情報" in prompt
                assert "## AWS知識コンテンツ" in prompt
                assert "## 問題生成要件" in prompt
                assert "## 共通要件" in prompt
                assert "## 出力形式" in prompt
                assert "## 重複回避" in prompt
    
    def test_prompt_content_truncation(self, config, sample_batch_plan):
        """Test that long AWS content is properly truncated."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                agent = QuestionGenerationAgent(config)
                
                # Create very long content
                long_content = "A" * 5000
                
                prompt = agent._create_generation_prompt(
                    question_type="technical",
                    count=1,
                    batch_plan=sample_batch_plan,
                    aws_knowledge_content=long_content
                )
                
                # Content should be truncated
                assert "..." in prompt
                assert len(prompt) < len(long_content) + 2000  # Reasonable prompt size
    
    def test_existing_questions_in_prompt(self, config, sample_batch_plan, sample_aws_content, sample_question):
        """Test that existing questions are included in prompt for duplication avoidance."""
        with patch('core.question_generation_agent.BedrockModel'):
            with patch('core.question_generation_agent.MCPClient'):
                agent = QuestionGenerationAgent(config)
                
                existing_questions = [sample_question]
                
                prompt = agent._create_generation_prompt(
                    question_type="scenario",
                    count=1,
                    batch_plan=sample_batch_plan,
                    aws_knowledge_content=sample_aws_content,
                    existing_questions=existing_questions
                )
                
                # Should contain reference to existing questions
                assert "既存問題との重複を避けてください" in prompt
                assert sample_question.question[:50] in prompt


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
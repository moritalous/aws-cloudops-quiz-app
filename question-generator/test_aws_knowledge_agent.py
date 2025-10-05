"""
Tests for AWS Knowledge MCP Server Integration Agent.

This module provides comprehensive tests for the AWSKnowledgeAgent,
including unit tests, integration tests, and mock tests for development.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

from config import AgentConfig
from core.aws_knowledge_agent import AWSKnowledgeAgent
from models.aws_knowledge_models import (
    AWSKnowledgeSearchResult, AWSServiceInfo, AWSBestPracticesExtract,
    AWSRegionalAvailability, AWSKnowledgeExtractionRequest, DocumentType
)
from models import LearningResource


class TestAWSKnowledgeAgent:
    """Test suite for AWS Knowledge Agent."""
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return AgentConfig(
            log_level="DEBUG",
            debug_mode=True
        )
    
    @pytest.fixture
    def aws_agent(self, config):
        """Create AWS Knowledge Agent instance."""
        return AWSKnowledgeAgent(config)
    
    @pytest.fixture
    def mock_mcp_client(self):
        """Create mock MCP client."""
        mock_client = Mock()
        mock_client.list_tools_sync.return_value = [
            Mock(name="search_documentation"),
            Mock(name="read_documentation"),
            Mock(name="recommend"),
            Mock(name="list_regions"),
            Mock(name="get_regional_availability")
        ]
        return mock_client
    
    @pytest.fixture
    def mock_bedrock_model(self):
        """Create mock Bedrock model."""
        return Mock()
    
    def test_agent_initialization(self, config):
        """Test AWS Knowledge Agent initialization."""
        agent = AWSKnowledgeAgent(config)
        
        assert agent.config == config
        assert agent.bedrock_model is None
        assert agent.aws_knowledge_mcp_client is None
        assert agent.mcp_tools == []
    
    @patch('core.aws_knowledge_agent.MCPClient')
    @patch('core.aws_knowledge_agent.stdio_client')
    def test_mcp_client_initialization(self, mock_stdio_client, mock_mcp_client_class, aws_agent):
        """Test MCP client initialization with fastmcp proxy."""
        mock_mcp_client = Mock()
        mock_mcp_client_class.return_value = mock_mcp_client
        
        # Test initialization
        result = aws_agent._initialize_aws_knowledge_mcp()
        
        # Verify MCP client was created with correct parameters
        mock_mcp_client_class.assert_called_once()
        assert result == mock_mcp_client
        assert aws_agent.aws_knowledge_mcp_client == mock_mcp_client
    
    @patch('core.aws_knowledge_agent.create_bedrock_model')
    @patch('boto3.Session')
    def test_bedrock_initialization(self, mock_session, mock_create_bedrock, aws_agent):
        """Test Bedrock model initialization."""
        mock_bedrock = Mock()
        mock_create_bedrock.return_value = mock_bedrock
        
        # Test initialization
        result = aws_agent._initialize_bedrock()
        
        # Verify Bedrock model was created
        mock_create_bedrock.assert_called_once()
        assert result == mock_bedrock
        assert aws_agent.bedrock_model == mock_bedrock
    
    def test_get_mcp_tools(self, aws_agent, mock_mcp_client):
        """Test MCP tools retrieval."""
        aws_agent.aws_knowledge_mcp_client = mock_mcp_client
        
        # Test tools retrieval
        with patch.object(aws_agent, 'aws_knowledge_mcp_client', mock_mcp_client):
            tools = aws_agent._get_aws_knowledge_tools()
        
        # Verify tools were retrieved
        assert len(tools) == 5
        assert tools == mock_mcp_client.list_tools_sync.return_value
    
    @patch('core.aws_knowledge_agent.Agent')
    def test_search_aws_documentation(self, mock_agent_class, aws_agent, mock_bedrock_model, mock_mcp_client):
        """Test AWS documentation search functionality."""
        # Setup mocks
        aws_agent.bedrock_model = mock_bedrock_model
        aws_agent.aws_knowledge_mcp_client = mock_mcp_client
        aws_agent.mcp_tools = [Mock(name="search_documentation")]
        
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        # Create expected result
        expected_result = AWSKnowledgeSearchResult(
            query="CloudWatch monitoring",
            total_results=5,
            results=[],
            recommended_follow_up=["CloudWatch Logs", "CloudWatch Alarms"]
        )
        mock_agent.structured_output.return_value = expected_result
        
        # Test search
        with patch.object(aws_agent, '_initialize_bedrock', return_value=mock_bedrock_model), \
             patch.object(aws_agent, '_initialize_aws_knowledge_mcp', return_value=mock_mcp_client), \
             patch.object(aws_agent, '_get_aws_knowledge_tools', return_value=aws_agent.mcp_tools):
            
            result = aws_agent.search_aws_documentation("CloudWatch monitoring", max_results=5)
        
        # Verify result
        assert isinstance(result, AWSKnowledgeSearchResult)
        assert result.query == "CloudWatch monitoring"
        assert result.total_results == 5
        mock_agent.structured_output.assert_called_once()
    
    @patch('core.aws_knowledge_agent.Agent')
    def test_get_aws_service_information(self, mock_agent_class, aws_agent, mock_bedrock_model, mock_mcp_client):
        """Test AWS service information retrieval."""
        # Setup mocks
        aws_agent.bedrock_model = mock_bedrock_model
        aws_agent.aws_knowledge_mcp_client = mock_mcp_client
        aws_agent.mcp_tools = [Mock(name="search_documentation")]
        
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        # Create expected result
        expected_result = AWSServiceInfo(
            service_name="Amazon CloudWatch",
            service_code="cloudwatch",
            category="Management & Governance",
            description="Monitoring and observability service",
            key_features=["Real-time monitoring", "Custom metrics"],
            use_cases=["Application monitoring", "Infrastructure monitoring"]
        )
        mock_agent.structured_output.return_value = expected_result
        
        # Test service info retrieval
        with patch.object(aws_agent, '_initialize_bedrock', return_value=mock_bedrock_model), \
             patch.object(aws_agent, '_initialize_aws_knowledge_mcp', return_value=mock_mcp_client), \
             patch.object(aws_agent, '_get_aws_knowledge_tools', return_value=aws_agent.mcp_tools):
            
            result = aws_agent.get_aws_service_information("Amazon CloudWatch")
        
        # Verify result
        assert isinstance(result, AWSServiceInfo)
        assert result.service_name == "Amazon CloudWatch"
        assert result.service_code == "cloudwatch"
        assert len(result.key_features) == 2
        mock_agent.structured_output.assert_called_once()
    
    @patch('core.aws_knowledge_agent.Agent')
    def test_extract_best_practices(self, mock_agent_class, aws_agent, mock_bedrock_model, mock_mcp_client):
        """Test best practices extraction."""
        # Setup mocks
        aws_agent.bedrock_model = mock_bedrock_model
        aws_agent.aws_knowledge_mcp_client = mock_mcp_client
        aws_agent.mcp_tools = [Mock(name="search_documentation")]
        
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        # Create expected result
        expected_result = AWSBestPracticesExtract(
            topic="CloudWatch monitoring",
            general_best_practices=["Monitor key metrics", "Set appropriate thresholds"],
            security_considerations=["Use IAM roles", "Enable CloudTrail"],
            cost_optimization=["Use metric filters", "Set retention periods"]
        )
        mock_agent.structured_output.return_value = expected_result
        
        # Test best practices extraction
        with patch.object(aws_agent, '_initialize_bedrock', return_value=mock_bedrock_model), \
             patch.object(aws_agent, '_initialize_aws_knowledge_mcp', return_value=mock_mcp_client), \
             patch.object(aws_agent, '_get_aws_knowledge_tools', return_value=aws_agent.mcp_tools):
            
            result = aws_agent.extract_best_practices("CloudWatch monitoring")
        
        # Verify result
        assert isinstance(result, AWSBestPracticesExtract)
        assert result.topic == "CloudWatch monitoring"
        assert len(result.general_best_practices) == 2
        assert len(result.security_considerations) == 2
        mock_agent.structured_output.assert_called_once()
    
    @patch('core.aws_knowledge_agent.Agent')
    def test_get_regional_availability(self, mock_agent_class, aws_agent, mock_bedrock_model, mock_mcp_client):
        """Test regional availability information retrieval."""
        # Setup mocks
        aws_agent.bedrock_model = mock_bedrock_model
        aws_agent.aws_knowledge_mcp_client = mock_mcp_client
        aws_agent.mcp_tools = [Mock(name="list_regions"), Mock(name="get_regional_availability")]
        
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        # Create expected result
        expected_result = AWSRegionalAvailability(
            service_name="AWS Lambda",
            available_regions=[],
            unavailable_regions=[],
            global_service=False,
            regional_service=True
        )
        mock_agent.structured_output.return_value = expected_result
        
        # Test regional availability
        with patch.object(aws_agent, '_initialize_bedrock', return_value=mock_bedrock_model), \
             patch.object(aws_agent, '_initialize_aws_knowledge_mcp', return_value=mock_mcp_client), \
             patch.object(aws_agent, '_get_aws_knowledge_tools', return_value=aws_agent.mcp_tools):
            
            result = aws_agent.get_regional_availability("AWS Lambda")
        
        # Verify result
        assert isinstance(result, AWSRegionalAvailability)
        assert result.service_name == "AWS Lambda"
        assert result.global_service is False
        assert result.regional_service is True
        mock_agent.structured_output.assert_called_once()
    
    @patch('core.aws_knowledge_agent.Agent')
    def test_generate_learning_resources(self, mock_agent_class, aws_agent, mock_bedrock_model, mock_mcp_client):
        """Test learning resources generation."""
        # Setup mocks
        aws_agent.bedrock_model = mock_bedrock_model
        aws_agent.aws_knowledge_mcp_client = mock_mcp_client
        aws_agent.mcp_tools = [Mock(name="search_documentation"), Mock(name="recommend")]
        
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        mock_agent.return_value = "Generated learning resources response"
        
        # Test learning resources generation
        with patch.object(aws_agent, '_initialize_bedrock', return_value=mock_bedrock_model), \
             patch.object(aws_agent, '_initialize_aws_knowledge_mcp', return_value=mock_mcp_client), \
             patch.object(aws_agent, '_get_aws_knowledge_tools', return_value=aws_agent.mcp_tools):
            
            result = aws_agent.generate_learning_resources("CloudWatch", "Monitoring question context")
        
        # Verify result
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], LearningResource)
        mock_agent.assert_called_once()
    
    @patch('core.aws_knowledge_agent.Agent')
    def test_validate_learning_resources(self, mock_agent_class, aws_agent, mock_bedrock_model, mock_mcp_client):
        """Test learning resources validation."""
        # Setup mocks
        aws_agent.bedrock_model = mock_bedrock_model
        aws_agent.aws_knowledge_mcp_client = mock_mcp_client
        aws_agent.mcp_tools = [Mock(name="read_documentation")]
        
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        mock_agent.return_value = "valid resource"
        
        # Create test resources
        resources = [
            LearningResource(
                title="CloudWatch Documentation",
                url="https://docs.aws.amazon.com/cloudwatch/",
                type="documentation"
            ),
            LearningResource(
                title="CloudWatch Best Practices",
                url="https://aws.amazon.com/cloudwatch/best-practices/",
                type="best-practice"
            )
        ]
        
        # Test validation
        with patch.object(aws_agent, '_initialize_bedrock', return_value=mock_bedrock_model), \
             patch.object(aws_agent, '_initialize_aws_knowledge_mcp', return_value=mock_mcp_client), \
             patch.object(aws_agent, '_get_aws_knowledge_tools', return_value=aws_agent.mcp_tools):
            
            result = aws_agent.validate_learning_resources(resources)
        
        # Verify result
        assert isinstance(result, dict)
        assert len(result) == 2
        for url, is_valid in result.items():
            assert isinstance(is_valid, bool)
            assert url in [r.url for r in resources]
    
    def test_get_mcp_context_manager(self, aws_agent, mock_mcp_client):
        """Test MCP context manager retrieval."""
        aws_agent.aws_knowledge_mcp_client = mock_mcp_client
        
        # Test context manager retrieval
        context_manager = aws_agent.get_mcp_context_manager()
        
        assert context_manager == mock_mcp_client
    
    def test_cleanup(self, aws_agent):
        """Test resource cleanup."""
        # Set some resources
        aws_agent.aws_knowledge_mcp_client = Mock()
        aws_agent.mcp_tools = [Mock(), Mock()]
        
        # Test cleanup
        aws_agent.cleanup()
        
        # Verify cleanup
        assert aws_agent.aws_knowledge_mcp_client is None
        assert aws_agent.mcp_tools == []


class TestAWSKnowledgeModels:
    """Test suite for AWS Knowledge models."""
    
    def test_aws_knowledge_search_result_validation(self):
        """Test AWSKnowledgeSearchResult validation."""
        # Valid data
        valid_data = {
            "query": "CloudWatch monitoring",
            "total_results": 2,
            "results": [
                {
                    "title": "CloudWatch Documentation",
                    "url": "https://docs.aws.amazon.com/cloudwatch/",
                    "content": "# CloudWatch\n\nMonitoring service...",
                    "document_type": "documentation",
                    "related_services": ["CloudWatch", "EC2"],
                    "key_concepts": ["Metrics", "Alarms"]
                },
                {
                    "title": "CloudWatch Best Practices",
                    "url": "https://aws.amazon.com/cloudwatch/best-practices/",
                    "content": "# Best Practices\n\nFollow these practices...",
                    "document_type": "best-practice",
                    "related_services": ["CloudWatch"],
                    "key_concepts": ["Best Practices"]
                }
            ]
        }
        
        # Test valid data
        result = AWSKnowledgeSearchResult(**valid_data)
        assert result.query == "CloudWatch monitoring"
        assert result.total_results == 2
        assert len(result.results) == 2
        assert result.results[0].document_type == DocumentType.DOCUMENTATION
        assert result.results[1].document_type == DocumentType.BEST_PRACTICE
    
    def test_aws_service_info_validation(self):
        """Test AWSServiceInfo validation."""
        valid_data = {
            "service_name": "Amazon CloudWatch",
            "service_code": "cloudwatch",
            "category": "Management & Governance",
            "description": "Monitoring and observability service",
            "key_features": ["Real-time monitoring", "Custom metrics"],
            "use_cases": ["Application monitoring", "Infrastructure monitoring"],
            "regional_availability": ["us-east-1", "us-west-2", "eu-west-1"]
        }
        
        service_info = AWSServiceInfo(**valid_data)
        assert service_info.service_name == "Amazon CloudWatch"
        assert service_info.service_code == "cloudwatch"
        assert len(service_info.key_features) == 2
        assert len(service_info.regional_availability) == 3
        assert service_info.global_service is False  # default value
    
    def test_aws_best_practices_extract_validation(self):
        """Test AWSBestPracticesExtract validation."""
        valid_data = {
            "topic": "CloudWatch monitoring",
            "general_best_practices": ["Monitor key metrics", "Set appropriate thresholds"],
            "security_considerations": ["Use IAM roles", "Enable CloudTrail"],
            "cost_optimization": ["Use metric filters", "Set retention periods"],
            "well_architected_principles": ["Operational Excellence", "Reliability"]
        }
        
        best_practices = AWSBestPracticesExtract(**valid_data)
        assert best_practices.topic == "CloudWatch monitoring"
        assert len(best_practices.general_best_practices) == 2
        assert len(best_practices.security_considerations) == 2
        assert len(best_practices.cost_optimization) == 2
        assert len(best_practices.well_architected_principles) == 2
    
    def test_aws_knowledge_extraction_request_validation(self):
        """Test AWSKnowledgeExtractionRequest validation."""
        valid_data = {
            "topic": "Amazon S3 security",
            "extraction_type": "best_practices",
            "max_results": 5,
            "target_audience": "intermediate",
            "question_context": "Security configuration for S3 buckets",
            "domain": "security",
            "difficulty_level": "medium"
        }
        
        request = AWSKnowledgeExtractionRequest(**valid_data)
        assert request.topic == "Amazon S3 security"
        assert request.extraction_type == "best_practices"
        assert request.max_results == 5
        assert request.target_audience == "intermediate"
        assert request.domain == "security"
        assert request.difficulty_level == "medium"


@pytest.mark.integration
class TestAWSKnowledgeAgentIntegration:
    """Integration tests for AWS Knowledge Agent (requires actual MCP server)."""
    
    @pytest.fixture
    def real_config(self):
        """Create real configuration for integration tests."""
        return AgentConfig.from_env()
    
    @pytest.fixture
    def real_aws_agent(self, real_config):
        """Create real AWS Knowledge Agent for integration tests."""
        return AWSKnowledgeAgent(real_config)
    
    @pytest.mark.skip(reason="Requires actual AWS Knowledge MCP Server connection")
    def test_real_documentation_search(self, real_aws_agent):
        """Test real documentation search (requires MCP server)."""
        try:
            result = real_aws_agent.search_aws_documentation("CloudWatch monitoring", max_results=3)
            
            assert isinstance(result, AWSKnowledgeSearchResult)
            assert result.total_results > 0
            assert len(result.results) > 0
            assert result.query == "CloudWatch monitoring"
            
        except Exception as e:
            pytest.skip(f"MCP server not available: {e}")
        finally:
            real_aws_agent.cleanup()
    
    @pytest.mark.skip(reason="Requires actual AWS Knowledge MCP Server connection")
    def test_real_service_information(self, real_aws_agent):
        """Test real service information retrieval (requires MCP server)."""
        try:
            result = real_aws_agent.get_aws_service_information("Amazon CloudWatch")
            
            assert isinstance(result, AWSServiceInfo)
            assert result.service_name
            assert len(result.key_features) > 0
            assert len(result.use_cases) > 0
            
        except Exception as e:
            pytest.skip(f"MCP server not available: {e}")
        finally:
            real_aws_agent.cleanup()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
#!/usr/bin/env python3
"""
Test script to verify Strands Agents and Bedrock setup.

This script tests the basic functionality of the question generation system
including Bedrock model creation, MCP client setup, and agent initialization.
"""

import sys
import logging
from pathlib import Path

# Add the question-generator directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_settings, AgentConfig
from core import AgentFactory, create_bedrock_model, create_mcp_client
from models import ExamGuideAnalysis, Question, QuestionBatch

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_configuration():
    """Test configuration loading."""
    logger.info("Testing configuration loading...")
    
    try:
        # Test settings loading
        settings = get_settings()
        logger.info(f"Settings loaded: {settings.app_name} v{settings.app_version}")
        
        # Test agent config
        agent_config = AgentConfig.from_env()
        logger.info(f"Agent config loaded with model: {agent_config.bedrock.model_id}")
        
        return True
    except Exception as e:
        logger.error(f"Configuration test failed: {e}")
        return False


def test_pydantic_models():
    """Test Pydantic model creation."""
    logger.info("Testing Pydantic models...")
    
    try:
        # Test basic model creation
        from models.exam_guide_models import Skill, Task, DomainAnalysis
        
        skill = Skill(
            skill_id="test-skill-1",
            description="Test skill description",
            aws_services=["EC2", "CloudWatch"],
            difficulty="medium",
            keywords=["monitoring", "metrics"]
        )
        
        task = Task(
            task_id="test-task-1",
            description="Test task description",
            skills=[skill],
            estimated_questions=5
        )
        
        domain = DomainAnalysis(
            domain="monitoring",
            domain_name="Monitoring, Logging, and Remediation",
            weight=22.0,
            target_questions=44,
            tasks=[task],
            complexity_level="intermediate"
        )
        
        logger.info(f"Created domain analysis: {domain.domain} with {len(domain.tasks)} tasks")
        return True
        
    except Exception as e:
        logger.error(f"Pydantic models test failed: {e}")
        return False


def test_bedrock_model_creation():
    """Test Bedrock model creation (without actual AWS call)."""
    logger.info("Testing Bedrock model creation...")
    
    try:
        from config.agent_config import BedrockConfig
        
        # Create a test configuration
        bedrock_config = BedrockConfig(
            model_id="openai.gpt-oss-120b-1:0",
            region_name="us-west-2",
            temperature=0.3,
            max_tokens=4000
        )
        
        logger.info(f"Bedrock config created: {bedrock_config.model_id}")
        
        # Note: We don't actually create the Bedrock model here to avoid AWS calls
        # In a real test, you would uncomment the following:
        # bedrock_model = create_bedrock_model(bedrock_config)
        # logger.info(f"Bedrock model created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Bedrock model creation test failed: {e}")
        return False


def test_mcp_client_creation():
    """Test MCP client creation (without actual connection)."""
    logger.info("Testing MCP client creation...")
    
    try:
        from config.agent_config import MCPConfig
        
        # Create a test configuration
        mcp_config = MCPConfig(
            server_name="aws-docs",
            server_command="uv",
            server_args=["tool", "run", "awslabs.aws-documentation-mcp-server@latest"]
        )
        
        logger.info(f"MCP config created: {mcp_config.server_name}")
        
        # Note: We don't actually create the MCP client here to avoid external dependencies
        # In a real test, you would uncomment the following:
        # mcp_client = create_mcp_client(mcp_config)
        # logger.info(f"MCP client created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"MCP client creation test failed: {e}")
        return False


def test_agent_factory():
    """Test AgentFactory initialization."""
    logger.info("Testing AgentFactory...")
    
    try:
        agent_config = AgentConfig()
        factory = AgentFactory(agent_config)
        
        logger.info("AgentFactory created successfully")
        
        # Test that we can create agent configurations (without actual agents)
        logger.info("Testing agent creation methods exist...")
        
        # Check that all required methods exist
        required_methods = [
            'create_exam_guide_analyzer',
            'create_batch_manager', 
            'create_document_researcher',
            'create_question_generator',
            'create_quality_validator',
            'create_japanese_optimizer',
            'create_database_integrator',
            'create_overall_quality_checker'
        ]
        
        for method_name in required_methods:
            if not hasattr(factory, method_name):
                raise AttributeError(f"AgentFactory missing method: {method_name}")
            logger.info(f"✓ Method {method_name} exists")
        
        factory.cleanup()
        return True
        
    except Exception as e:
        logger.error(f"AgentFactory test failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("Starting Strands Agents setup verification...")
    
    tests = [
        ("Configuration Loading", test_configuration),
        ("Pydantic Models", test_pydantic_models),
        ("Bedrock Model Creation", test_bedrock_model_creation),
        ("MCP Client Creation", test_mcp_client_creation),
        ("Agent Factory", test_agent_factory),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Strands Agents setup is ready.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
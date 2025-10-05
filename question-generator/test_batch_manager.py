"""
Test script for the BatchManagerAgent implementation.

This script tests the AI-driven batch management functionality including
state analysis, batch planning, progress reporting, and checkpoint management.
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime

from core.batch_manager import BatchManagerAgent
from core.agent_factory import AgentFactory
from models.batch_models import DatabaseState, BatchPlan, ProgressReport
from models.exam_guide_models import ExamGuideAnalysis
from config.settings import get_settings
from config.agent_config import AgentConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def create_mock_questions_file() -> Path:
    """Create a mock questions.json file for testing."""
    mock_questions = {
        "metadata": {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "total_questions": 11,
            "domains": {
                "monitoring": 3,
                "reliability": 2,
                "deployment": 2,
                "security": 2,
                "networking": 2
            },
            "difficulty": {
                "easy": 4,
                "medium": 5,
                "hard": 2
            },
            "question_types": {
                "single": 9,
                "multiple": 2
            }
        },
        "questions": [
            {
                "id": f"q{i:03d}",
                "domain": ["monitoring", "reliability", "deployment", "security", "networking"][i % 5],
                "difficulty": ["easy", "medium", "hard"][i % 3],
                "type": "single" if i % 5 != 0 else "multiple",
                "question": f"Test question {i}",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A" if i % 5 != 0 else ["A", "B"],
                "explanation": f"Test explanation {i}",
                "learning_resources": [
                    {
                        "title": f"Test Resource {i}",
                        "url": f"https://docs.aws.amazon.com/test{i}",
                        "type": "documentation"
                    }
                ],
                "related_services": ["EC2", "CloudWatch"],
                "tags": ["test"]
            }
            for i in range(1, 12)
        ]
    }
    
    mock_file = Path("test_questions.json")
    with open(mock_file, 'w', encoding='utf-8') as f:
        json.dump(mock_questions, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Created mock questions file: {mock_file}")
    return mock_file


async def create_mock_exam_guide_analysis() -> ExamGuideAnalysis:
    """Create a mock exam guide analysis for testing."""
    from models.exam_guide_models import DomainAnalysis, Task, Skill
    
    # Create mock skills
    skills = [
        Skill(
            skill_id="monitoring-1.1",
            description="Monitor AWS resources using CloudWatch",
            aws_services=["CloudWatch", "EC2", "RDS"],
            difficulty="medium",
            keywords=["metrics", "alarms", "dashboards"]
        )
    ]
    
    # Create mock tasks
    tasks = [
        Task(
            task_id="domain1-task1",
            description="Implement monitoring and alerting",
            weight_percentage=50.0,
            skills=skills,
            estimated_questions=22
        )
    ]
    
    # Create mock domains
    domains = [
        DomainAnalysis(
            domain="monitoring",
            domain_name="Monitoring, Logging, and Remediation",
            weight=22.0,
            target_questions=44,
            tasks=tasks,
            key_services=["CloudWatch", "CloudTrail", "Config"],
            complexity_level="intermediate"
        ),
        DomainAnalysis(
            domain="reliability",
            domain_name="Reliability and Business Continuity",
            weight=22.0,
            target_questions=44,
            tasks=tasks,
            key_services=["Auto Scaling", "ELB", "Route 53"],
            complexity_level="intermediate"
        ),
        DomainAnalysis(
            domain="deployment",
            domain_name="Deployment, Provisioning, and Automation",
            weight=22.0,
            target_questions=44,
            tasks=tasks,
            key_services=["CloudFormation", "CodeDeploy", "Systems Manager"],
            complexity_level="intermediate"
        ),
        DomainAnalysis(
            domain="security",
            domain_name="Security and Compliance",
            weight=16.0,
            target_questions=32,
            tasks=tasks,
            key_services=["IAM", "KMS", "Security Hub"],
            complexity_level="advanced"
        ),
        DomainAnalysis(
            domain="networking",
            domain_name="Networking and Content Delivery",
            weight=18.0,
            target_questions=36,
            tasks=tasks,
            key_services=["VPC", "CloudFront", "Route 53"],
            complexity_level="intermediate"
        )
    ]
    
    return ExamGuideAnalysis(
        total_questions=200,
        exam_code="SOA-C03",
        exam_title="AWS Certified CloudOps Engineer - Associate",
        domains=domains,
        exam_info={"duration": 180, "passing_score": 720}
    )


async def test_database_state_analysis():
    """Test database state analysis functionality."""
    logger.info("Testing database state analysis...")
    
    try:
        # Create mock questions file
        mock_file = await create_mock_questions_file()
        
        # Create agent factory and batch manager
        config = AgentConfig()
        agent_factory = AgentFactory(config)
        batch_manager = BatchManagerAgent(agent_factory)
        
        # Test state analysis
        logger.info("Analyzing database state...")
        database_state = await batch_manager.analyze_current_state(mock_file)
        
        # Verify results
        assert isinstance(database_state, DatabaseState)
        assert database_state.total_questions == 11
        assert database_state.completion_percentage > 0
        
        logger.info(f"✓ Database state analysis successful:")
        logger.info(f"  - Total questions: {database_state.total_questions}")
        logger.info(f"  - Completion: {database_state.completion_percentage:.1f}%")
        logger.info(f"  - Domain distribution: {database_state.domain_distribution}")
        
        # Cleanup
        mock_file.unlink()
        
        return database_state
        
    except Exception as e:
        logger.error(f"✗ Database state analysis failed: {e}")
        raise


async def test_batch_planning():
    """Test batch planning functionality."""
    logger.info("Testing batch planning...")
    
    try:
        # Create mock data
        mock_file = await create_mock_questions_file()
        exam_guide_analysis = await create_mock_exam_guide_analysis()
        
        # Create agent factory and batch manager
        config = AgentConfig()
        agent_factory = AgentFactory(config)
        batch_manager = BatchManagerAgent(agent_factory)
        
        # Analyze current state first
        database_state = await batch_manager.analyze_current_state(mock_file)
        
        # Test batch planning
        logger.info("Planning next batch...")
        batch_plan = await batch_manager.plan_next_batch(database_state, exam_guide_analysis)
        
        # Verify results
        assert isinstance(batch_plan, BatchPlan)
        assert batch_plan.batch_number > 0
        assert batch_plan.target_domain in ["monitoring", "reliability", "deployment", "security", "networking"]
        assert len(batch_plan.target_difficulties) > 0
        
        logger.info(f"✓ Batch planning successful:")
        logger.info(f"  - Batch number: {batch_plan.batch_number}")
        logger.info(f"  - Target domain: {batch_plan.target_domain}")
        logger.info(f"  - Difficulties: {batch_plan.target_difficulties}")
        logger.info(f"  - Estimated time: {batch_plan.estimated_completion_time} minutes")
        
        # Cleanup
        mock_file.unlink()
        
        return batch_plan
        
    except Exception as e:
        logger.error(f"✗ Batch planning failed: {e}")
        raise


async def test_progress_reporting():
    """Test progress reporting functionality."""
    logger.info("Testing progress reporting...")
    
    try:
        # Create mock data
        mock_file = await create_mock_questions_file()
        
        # Create agent factory and batch manager
        config = AgentConfig()
        agent_factory = AgentFactory(config)
        batch_manager = BatchManagerAgent(agent_factory)
        
        # Analyze current state first
        database_state = await batch_manager.analyze_current_state(mock_file)
        
        # Test progress reporting
        logger.info("Generating progress report...")
        progress_report = await batch_manager.generate_progress_report(database_state)
        
        # Verify results
        assert isinstance(progress_report, ProgressReport)
        assert 0 <= progress_report.current_progress <= 100
        assert progress_report.questions_completed >= 0
        assert progress_report.questions_remaining >= 0
        
        logger.info(f"✓ Progress reporting successful:")
        logger.info(f"  - Current progress: {progress_report.current_progress:.1f}%")
        logger.info(f"  - Questions completed: {progress_report.questions_completed}")
        logger.info(f"  - Questions remaining: {progress_report.questions_remaining}")
        logger.info(f"  - Estimated remaining time: {progress_report.estimated_remaining_time} minutes")
        
        # Cleanup
        mock_file.unlink()
        
        return progress_report
        
    except Exception as e:
        logger.error(f"✗ Progress reporting failed: {e}")
        raise


async def test_checkpoint_management():
    """Test checkpoint save/load functionality."""
    logger.info("Testing checkpoint management...")
    
    try:
        # Create mock data
        mock_file = await create_mock_questions_file()
        
        # Create agent factory and batch manager
        config = AgentConfig()
        agent_factory = AgentFactory(config)
        batch_manager = BatchManagerAgent(agent_factory)
        
        # Set up some state
        database_state = await batch_manager.analyze_current_state(mock_file)
        progress_report = await batch_manager.generate_progress_report(database_state)
        
        # Test checkpoint saving
        logger.info("Saving checkpoint...")
        checkpoint_path = await batch_manager.save_checkpoint("test_checkpoint")
        
        assert checkpoint_path.exists()
        logger.info(f"✓ Checkpoint saved: {checkpoint_path}")
        
        # Create new batch manager and test loading
        batch_manager2 = BatchManagerAgent(agent_factory)
        
        logger.info("Loading checkpoint...")
        success = await batch_manager2.load_checkpoint(checkpoint_path)
        
        assert success
        assert batch_manager2.current_state is not None
        assert len(batch_manager2.progress_history) > 0
        
        logger.info("✓ Checkpoint loaded successfully")
        
        # Test resumption capability
        can_resume = await batch_manager2.can_resume()
        logger.info(f"✓ Can resume: {can_resume}")
        
        # Cleanup
        mock_file.unlink()
        checkpoint_path.unlink()
        
    except Exception as e:
        logger.error(f"✗ Checkpoint management failed: {e}")
        raise


async def run_all_tests():
    """Run all batch manager tests."""
    logger.info("Starting BatchManagerAgent tests...")
    
    try:
        # Test individual components
        await test_database_state_analysis()
        await test_batch_planning()
        await test_progress_reporting()
        await test_checkpoint_management()
        
        logger.info("✓ All BatchManagerAgent tests passed!")
        
    except Exception as e:
        logger.error(f"✗ Tests failed: {e}")
        raise


if __name__ == "__main__":
    # Run tests
    asyncio.run(run_all_tests())
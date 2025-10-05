"""
Example usage of the BatchManagerAgent for AI-driven question generation.

This example demonstrates how to use the batch management agent to:
1. Analyze current database state
2. Plan optimal batches
3. Track progress
4. Handle interruption and resumption
"""

import asyncio
import logging
from pathlib import Path

from core.batch_manager import BatchManagerAgent
from core.agent_factory import AgentFactory
from config.agent_config import AgentConfig
from config.settings import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main example workflow."""
    logger.info("Starting BatchManagerAgent example...")
    
    try:
        # Initialize configuration and agent factory
        config = AgentConfig()
        agent_factory = AgentFactory(config)
        batch_manager = BatchManagerAgent(agent_factory)
        
        # Check if we can resume from previous session
        if await batch_manager.can_resume():
            logger.info("Previous session found, resuming...")
            await batch_manager.resume_generation()
        else:
            logger.info("Starting fresh generation process...")
        
        # Analyze current database state
        logger.info("Analyzing current database state...")
        current_state = await batch_manager.analyze_current_state()
        
        logger.info(f"Current state:")
        logger.info(f"  - Total questions: {current_state.total_questions}")
        logger.info(f"  - Completion: {current_state.completion_percentage:.1f}%")
        logger.info(f"  - Domain distribution: {current_state.domain_distribution}")
        logger.info(f"  - Remaining by domain: {current_state.domain_remaining}")
        
        # Generate progress report
        logger.info("Generating progress report...")
        progress_report = await batch_manager.generate_progress_report(current_state)
        
        logger.info(f"Progress report:")
        logger.info(f"  - Current progress: {progress_report.current_progress:.1f}%")
        logger.info(f"  - Questions remaining: {progress_report.questions_remaining}")
        logger.info(f"  - Estimated remaining time: {progress_report.estimated_remaining_time} minutes")
        logger.info(f"  - Recommendations: {progress_report.recommendations}")
        
        # Plan next batch if not complete
        if current_state.total_questions < 200:
            logger.info("Planning next batch...")
            batch_plan = await batch_manager.plan_next_batch(current_state)
            
            logger.info(f"Next batch plan:")
            logger.info(f"  - Batch number: {batch_plan.batch_number}")
            logger.info(f"  - Target domain: {batch_plan.target_domain}")
            logger.info(f"  - Difficulties: {batch_plan.target_difficulties}")
            logger.info(f"  - Priority topics: {batch_plan.priority_topics}")
            logger.info(f"  - Research queries: {batch_plan.research_queries}")
            logger.info(f"  - Estimated time: {batch_plan.estimated_completion_time} minutes")
            logger.info(f"  - Strategic notes: {batch_plan.strategic_notes}")
            
            # Save checkpoint before proceeding
            checkpoint_path = await batch_manager.save_checkpoint()
            logger.info(f"Checkpoint saved: {checkpoint_path}")
            
            # Here you would integrate with other agents:
            # 1. Document research agent using batch_plan.research_queries
            # 2. Question generation agent using batch_plan specifications
            # 3. Quality validation agent for generated questions
            # 4. Database integration agent to add questions
            
            logger.info("Next steps would be:")
            logger.info("1. Use document research agent with research queries")
            logger.info("2. Generate questions using question generation agent")
            logger.info("3. Validate questions using quality validation agent")
            logger.info("4. Integrate questions using database integration agent")
            logger.info("5. Update progress and plan next batch")
            
        else:
            logger.info("All questions generated! Process complete.")
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        raise


async def demonstrate_checkpoint_workflow():
    """Demonstrate checkpoint save/load workflow."""
    logger.info("Demonstrating checkpoint workflow...")
    
    try:
        # Create first batch manager instance
        config = AgentConfig()
        agent_factory = AgentFactory(config)
        batch_manager1 = BatchManagerAgent(agent_factory)
        
        # Analyze state and create checkpoint
        current_state = await batch_manager1.analyze_current_state()
        progress_report = await batch_manager1.generate_progress_report(current_state)
        
        checkpoint_path = await batch_manager1.save_checkpoint("demo_checkpoint")
        logger.info(f"Checkpoint saved: {checkpoint_path}")
        
        # Create second batch manager instance and load checkpoint
        batch_manager2 = BatchManagerAgent(agent_factory)
        success = await batch_manager2.load_checkpoint(checkpoint_path)
        
        if success:
            logger.info("Checkpoint loaded successfully!")
            logger.info(f"Restored state: {batch_manager2.current_state.total_questions} questions")
            logger.info(f"Progress history: {len(batch_manager2.progress_history)} reports")
        else:
            logger.error("Failed to load checkpoint")
        
        # Test resumption capability
        can_resume = await batch_manager2.can_resume()
        logger.info(f"Can resume from saved state: {can_resume}")
        
        if can_resume:
            await batch_manager2.resume_generation()
            logger.info("Generation process resumed successfully!")
        
        # Cleanup
        checkpoint_path.unlink()
        
    except Exception as e:
        logger.error(f"Checkpoint workflow demonstration failed: {e}")
        raise


if __name__ == "__main__":
    # Run main example
    asyncio.run(main())
    
    print("\n" + "="*50 + "\n")
    
    # Run checkpoint demonstration
    asyncio.run(demonstrate_checkpoint_workflow())
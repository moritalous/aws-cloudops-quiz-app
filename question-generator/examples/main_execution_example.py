"""
Example usage of the Main Execution Flow.

This script demonstrates how to use the complete AI automation flow
for generating AWS CloudOps exam questions with full orchestration,
monitoring, and error recovery capabilities.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Local imports
from config import AgentConfig
from core import MainExecutionFlow, ConfigurationManager, QuestionGenerationError


async def demonstrate_full_automation():
    """Demonstrate complete AI automation flow."""
    
    print("🤖 AWS CloudOps Question Generation - Main Execution Flow Demo")
    print("=" * 70)
    
    try:
        # Initialize configuration manager
        print("\n⚙️ Initializing configuration...")
        config_manager = ConfigurationManager("config/execution_config.yaml")
        
        # Show configuration summary
        summary = config_manager.get_configuration_summary()
        print(f"✅ Configuration loaded: {summary['configuration_file']}")
        print(f"   📊 Batch size: {summary['batch_configuration']['batch_size']}")
        print(f"   🎯 Total batches: {summary['batch_configuration']['total_batches']}")
        print(f"   ⚙️  Execution mode: {summary['execution_mode']}")
        print(f"   📝 Log level: {summary['log_level']}")
        
        # Validate configuration
        is_valid, issues = config_manager.validate_configuration()
        if not is_valid:
            print("❌ Configuration validation failed:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        
        print("✅ Configuration validation passed")
        
        # Create agent configuration
        base_config = AgentConfig()
        agent_config = config_manager.create_agent_config(base_config)
        
        # Initialize main execution flow
        print("\n🚀 Initializing main execution flow...")
        execution_flow = MainExecutionFlow(
            config=agent_config,
            database_path=config_manager.database_config.database_path,
            backup_dir=config_manager.database_config.backup_directory,
            log_level=config_manager.monitoring_config.log_level.value
        )
        
        print("✅ Main execution flow initialized")
        
        # Show initial status
        print("\n📊 Initial Status:")
        status = execution_flow.get_real_time_status()
        print(f"   Status: {status['status']}")
        print(f"   System Health: {status['system_health']}")
        
        # Demonstrate configuration adjustments
        print("\n⚙️ Demonstrating dynamic configuration adjustments...")
        
        # Adjust batch size for demo (smaller batches)
        config_manager.adjust_batch_size(5)
        print(f"   📦 Batch size adjusted to: {config_manager.batch_config.batch_size}")
        print(f"   📊 Total batches recalculated to: {config_manager.batch_config.total_batches}")
        
        # Enable debug mode for detailed logging
        config_manager.enable_debug_mode()
        print(f"   🐛 Debug mode enabled")
        print(f"   📝 Log level: {config_manager.monitoring_config.log_level.value}")
        
        # Adjust quality thresholds
        config_manager.adjust_quality_thresholds(
            min_technical_accuracy=8.5,
            min_clarity_score=8.0
        )
        print(f"   🎯 Quality thresholds adjusted")
        
        # Show updated runtime parameters
        runtime_params = config_manager.get_runtime_parameters()
        print(f"\n📋 Runtime Parameters:")
        print(f"   Batch size: {runtime_params['batch_size']}")
        print(f"   Total batches: {runtime_params['total_batches']}")
        print(f"   Execution mode: {runtime_params['execution_mode']}")
        print(f"   Quality thresholds: {runtime_params['quality_thresholds']}")
        
        # Demonstrate state management
        print("\n💾 Demonstrating state management...")
        
        # Simulate some progress
        execution_flow.progress.completed_batches = 3
        execution_flow.progress.total_questions_generated = 15
        execution_flow.progress.overall_validation_score = 8.2
        
        # Save state
        execution_flow.save_state()
        print("✅ Execution state saved")
        
        # Load state in new instance
        new_flow = MainExecutionFlow(
            config=agent_config,
            database_path=config_manager.database_config.database_path,
            backup_dir=config_manager.database_config.backup_directory,
            state_file=execution_flow.state_file
        )
        
        loaded = new_flow.load_state()
        print(f"✅ State loaded successfully: {loaded}")
        print(f"   📊 Completed batches: {new_flow.progress.completed_batches}")
        print(f"   🎯 Questions generated: {new_flow.progress.total_questions_generated}")
        print(f"   ⭐ Validation score: {new_flow.progress.overall_validation_score}")
        
        # Demonstrate progress reporting
        print("\n📈 Progress Reporting:")
        progress_report = new_flow.get_progress_report()
        
        print(f"   Overall Status: {progress_report['overall_status']}")
        print(f"   Progress: {progress_report['overall_progress_percentage']:.1f}%")
        print(f"   Batches Completed: {progress_report['batches_completed']}")
        print(f"   Questions Generated: {progress_report['total_questions_generated']}")
        print(f"   Validation Score: {progress_report['overall_validation_score']}")
        
        # Show batch details
        print(f"\n📋 Batch Details (first 5):")
        for batch in progress_report['batch_details'][:5]:
            status_icon = "✅" if batch['status'] == 'completed' else "⏳"
            print(f"   {status_icon} Batch {batch['batch_number']:2d}: {batch['status']:12s} | "
                  f"Questions: {batch['questions_generated']:2d} | Score: {batch['validation_score']:4.1f}")
        
        # Demonstrate pause/resume functionality
        print("\n⏸️ Demonstrating pause/resume functionality...")
        
        execution_flow.pause_flow()
        print(f"   Pause requested: {execution_flow.progress.pause_requested}")
        
        execution_flow.resume_flow()
        print(f"   Flow resumed: {not execution_flow.progress.pause_requested}")
        
        # Demonstrate agent lazy initialization
        print("\n🤖 Demonstrating agent lazy initialization...")
        
        # Check initial state (no agents initialized)
        status = execution_flow.get_real_time_status()
        agents_status = status['system_health']['agents_initialized']
        print(f"   Initial agent status: {agents_status}")
        
        # Access an agent to trigger initialization (mock)
        print(f"   Accessing exam analyzer...")
        try:
            # This would normally initialize the agent
            # For demo, we'll just show the concept
            print(f"   ✅ Exam analyzer would be initialized on first access")
        except Exception as e:
            print(f"   ⚠️  Agent initialization would happen here: {e}")
        
        # Demonstrate configuration export/import
        print("\n📤 Demonstrating configuration export/import...")
        
        export_path = "examples/exported_config.yaml"
        config_manager.export_configuration(export_path)
        print(f"   ✅ Configuration exported to: {export_path}")
        
        # Create new config manager and import
        new_config_manager = ConfigurationManager("examples/temp_config.yaml")
        new_config_manager.import_configuration(export_path)
        print(f"   ✅ Configuration imported successfully")
        
        # Verify imported settings
        imported_summary = new_config_manager.get_configuration_summary()
        print(f"   📊 Imported batch size: {imported_summary['batch_configuration']['batch_size']}")
        
        print("\n🎉 Main Execution Flow demonstration completed successfully!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        return False


async def demonstrate_mock_execution():
    """Demonstrate a mock execution flow (without real AI agents)."""
    
    print("\n🎭 Mock Execution Flow Demo")
    print("-" * 40)
    
    try:
        # Create a simple configuration for mock execution
        config_manager = ConfigurationManager()
        config_manager.adjust_batch_size(3)  # Small batches for demo
        
        base_config = AgentConfig()
        agent_config = config_manager.create_agent_config(base_config)
        
        # Initialize execution flow
        execution_flow = MainExecutionFlow(
            config=agent_config,
            database_path="examples/mock_questions.json",
            backup_dir="examples/mock_backups",
            log_level="INFO"
        )
        
        print("✅ Mock execution flow initialized")
        
        # Simulate initialization
        print("\n📋 Simulating flow initialization...")
        execution_flow.progress.status = execution_flow.progress.status.__class__.INITIALIZING
        execution_flow.progress.start_time = datetime.now()
        
        # Simulate batch processing
        print("\n🔄 Simulating batch processing...")
        
        for batch_num in range(1, 4):  # Process 3 batches
            print(f"\n   Processing batch {batch_num}...")
            
            batch_progress = execution_flow.progress.batch_progress[batch_num]
            batch_progress.status = batch_progress.status.__class__.ANALYZING
            batch_progress.start_time = datetime.now()
            batch_progress.current_step = "Analyzing current state"
            
            # Simulate steps
            steps = [
                "Analyzing current state",
                "Planning batch",
                "Researching AWS knowledge", 
                "Generating questions",
                "Validating quality",
                "Optimizing Japanese",
                "Integrating database"
            ]
            
            for i, step in enumerate(steps):
                batch_progress.current_step = step
                batch_progress.steps_completed = i + 1
                print(f"      {step}...")
                
                # Simulate some processing time
                await asyncio.sleep(0.1)
            
            # Complete batch
            batch_progress.status = batch_progress.status.__class__.COMPLETED
            batch_progress.end_time = datetime.now()
            batch_progress.questions_generated = 3  # Mock 3 questions per batch
            batch_progress.validation_score = 8.0 + (batch_num * 0.2)
            
            # Update overall progress
            execution_flow.progress.completed_batches += 1
            execution_flow.progress.total_questions_generated += 3
            
            print(f"   ✅ Batch {batch_num} completed")
            
            # Show progress
            progress_report = execution_flow.get_progress_report()
            print(f"      Progress: {progress_report['overall_progress_percentage']:.1f}%")
        
        # Complete flow
        execution_flow.progress.status = execution_flow.progress.status.__class__.COMPLETED
        execution_flow.progress.end_time = datetime.now()
        
        # Calculate overall validation score
        total_score = sum(
            bp.validation_score * bp.questions_generated 
            for bp in execution_flow.progress.batch_progress.values() 
            if bp.questions_generated > 0
        )
        total_questions = execution_flow.progress.total_questions_generated
        execution_flow.progress.overall_validation_score = total_score / total_questions if total_questions > 0 else 0
        
        # Final report
        final_report = execution_flow.get_progress_report()
        print(f"\n🎉 Mock execution completed!")
        print(f"   📊 Total questions generated: {final_report['total_questions_generated']}")
        print(f"   ⭐ Overall validation score: {final_report['overall_validation_score']:.2f}")
        print(f"   ✅ Batches completed: {final_report['batches_completed']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Mock execution failed: {e}")
        return False


async def main():
    """Main demonstration function."""
    
    print("🚀 Starting Main Execution Flow Examples")
    print("=" * 50)
    
    # Run configuration and flow management demo
    success1 = await demonstrate_full_automation()
    
    # Run mock execution demo
    success2 = await demonstrate_mock_execution()
    
    if success1 and success2:
        print("\n🎉 All demonstrations completed successfully!")
        return 0
    else:
        print("\n❌ Some demonstrations failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
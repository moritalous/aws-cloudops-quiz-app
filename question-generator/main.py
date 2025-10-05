#!/usr/bin/env python3
"""
Main execution script for AWS CloudOps Question Generation System.

This script provides the entry point for running the complete AI automation
flow with configurable parameters, monitoring, and error recovery.
"""

import asyncio
import argparse
import sys
import signal
from pathlib import Path
from datetime import datetime
import logging

# Local imports
from config import AgentConfig
from core import (
    MainExecutionFlow, ConfigurationManager, 
    QuestionGenerationError
)


class QuestionGenerationRunner:
    """Main runner for the question generation system."""
    
    def __init__(self, config_file: str = None):
        """
        Initialize the runner.
        
        Args:
            config_file: Path to configuration file
        """
        # Initialize configuration manager
        self.config_manager = ConfigurationManager(
            config_file or "config/execution_config.yaml"
        )
        
        # Validate configuration
        is_valid, issues = self.config_manager.validate_configuration()
        if not is_valid:
            print("❌ Configuration validation failed:")
            for issue in issues:
                print(f"   - {issue}")
            sys.exit(1)
        
        # Create agent configuration
        base_agent_config = AgentConfig()
        self.agent_config = self.config_manager.create_agent_config(base_agent_config)
        
        # Initialize main execution flow
        self.execution_flow = MainExecutionFlow(
            config=self.agent_config,
            database_path=self.config_manager.database_config.database_path,
            backup_dir=self.config_manager.database_config.backup_directory,
            log_level=self.config_manager.monitoring_config.log_level.value
        )
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        print("🤖 AWS CloudOps Question Generation System")
        print("=" * 50)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, requesting graceful shutdown...")
        self.execution_flow.pause_flow()
    
    async def run_full_generation(self) -> bool:
        """
        Run the complete question generation flow.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print("🚀 Starting complete AI automation flow...")
            print(f"📊 Configuration: {self.config_manager.batch_config.total_batches} batches of {self.config_manager.batch_config.batch_size} questions")
            print(f"🎯 Target: 200 total questions (189 new + 11 existing)")
            print(f"⚙️  Mode: {self.config_manager.execution_config.mode.value}")
            print()
            
            # Run the complete flow
            final_database = await self.execution_flow.run_complete_flow()
            
            if final_database:
                print("🎉 Question generation completed successfully!")
                print(f"📊 Final database: {final_database.total_questions} questions")
                print(f"✅ Quality score: {self.execution_flow.progress.overall_validation_score:.2f}/10")
                return True
            else:
                print("⏸️ Execution paused or interrupted")
                return False
        
        except QuestionGenerationError as e:
            print(f"❌ Question generation failed: {e}")
            return False
        except Exception as e:
            print(f"💥 Unexpected error: {e}")
            return False
    
    async def resume_generation(self) -> bool:
        """
        Resume a paused generation flow.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print("▶️ Resuming question generation flow...")
            
            # Load previous state
            if not self.execution_flow.load_state():
                print("❌ No previous execution state found")
                return False
            
            # Resume execution
            self.execution_flow.resume_flow()
            final_database = await self.execution_flow.run_complete_flow()
            
            if final_database:
                print("🎉 Question generation resumed and completed successfully!")
                return True
            else:
                print("⏸️ Execution paused again")
                return False
        
        except Exception as e:
            print(f"❌ Failed to resume generation: {e}")
            return False
    
    def show_status(self) -> None:
        """Show current execution status."""
        try:
            # Load state if available
            self.execution_flow.load_state()
            
            # Get status
            status = self.execution_flow.get_real_time_status()
            progress = status['progress']
            
            print("📊 Current Status")
            print("-" * 30)
            print(f"Status: {status['status']}")
            print(f"Overall Progress: {progress['overall_progress_percentage']:.1f}%")
            print(f"Batches Completed: {progress['batches_completed']}/{progress['batches_remaining'] + progress['batches_completed']}")
            print(f"Questions Generated: {progress['total_questions_generated']}")
            print(f"Validation Score: {progress['overall_validation_score']:.2f}/10")
            
            if progress['current_batch']:
                current = progress['current_batch']
                print(f"Current Batch: {current['batch_number']} ({current['status']})")
                print(f"Current Step: {current['current_step']}")
            
            if progress['estimated_completion_time']:
                print(f"Estimated Completion: {progress['estimated_completion_time']}")
            
            # Show batch details
            print("\n📋 Batch Details:")
            for batch in progress['batch_details'][:10]:  # Show first 10 batches
                status_icon = "✅" if batch['status'] == 'completed' else "❌" if batch['status'] == 'failed' else "⏳"
                print(f"  {status_icon} Batch {batch['batch_number']:2d}: {batch['status']:12s} | Questions: {batch['questions_generated']:2d} | Score: {batch['validation_score']:4.1f}")
        
        except Exception as e:
            print(f"❌ Failed to get status: {e}")
    
    def show_configuration(self) -> None:
        """Show current configuration summary."""
        try:
            summary = self.config_manager.get_configuration_summary()
            
            print("⚙️ Configuration Summary")
            print("-" * 30)
            print(f"Configuration File: {summary['configuration_file']}")
            print(f"Valid: {'✅' if summary['is_valid'] else '❌'}")
            
            if summary['validation_issues']:
                print("Issues:")
                for issue in summary['validation_issues']:
                    print(f"  - {issue}")
            
            print(f"Execution Mode: {summary['execution_mode']}")
            print(f"Log Level: {summary['log_level']}")
            
            batch_config = summary['batch_configuration']
            print(f"Batch Size: {batch_config['batch_size']}")
            print(f"Total Batches: {batch_config['total_batches']}")
            print(f"Strategy: {batch_config['strategy']}")
            
            print("\n📊 Domain Distribution:")
            for domain, config in summary['domain_summary'].items():
                enabled_icon = "✅" if config['enabled'] else "❌"
                print(f"  {enabled_icon} {domain:12s}: {config['target_questions']:3d} questions ({config['weight_percentage']:4.1f}%)")
            
            print("\n🤖 Agent Configuration:")
            for agent, config in summary['agent_summary'].items():
                enabled_icon = "✅" if config['enabled'] else "❌"
                print(f"  {enabled_icon} {agent:20s}: temp={config['temperature']:.1f}, tokens={config['max_tokens']}")
        
        except Exception as e:
            print(f"❌ Failed to show configuration: {e}")
    
    def validate_setup(self) -> bool:
        """
        Validate the complete setup before execution.
        
        Returns:
            True if setup is valid, False otherwise
        """
        print("🔍 Validating setup...")
        
        issues = []
        
        # Check configuration
        is_valid, config_issues = self.config_manager.validate_configuration()
        if not is_valid:
            issues.extend([f"Config: {issue}" for issue in config_issues])
        
        # Check required directories
        database_dir = Path(self.config_manager.database_config.database_path).parent
        if not database_dir.exists():
            try:
                database_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created database directory: {database_dir}")
            except Exception as e:
                issues.append(f"Cannot create database directory: {e}")
        
        backup_dir = Path(self.config_manager.database_config.backup_directory)
        if not backup_dir.exists():
            try:
                backup_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created backup directory: {backup_dir}")
            except Exception as e:
                issues.append(f"Cannot create backup directory: {e}")
        
        logs_dir = Path("logs")
        if not logs_dir.exists():
            try:
                logs_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created logs directory: {logs_dir}")
            except Exception as e:
                issues.append(f"Cannot create logs directory: {e}")
        
        # Check exam guide
        exam_guide = Path("docs/AWS_Certified_CloudOps_Engineer_Associate_Exam_Guide.md")
        if not exam_guide.exists():
            issues.append(f"Exam guide not found: {exam_guide}")
        
        # Report results
        if issues:
            print("❌ Setup validation failed:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Setup validation passed")
            return True


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AWS CloudOps Question Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py run                    # Run complete generation
  python main.py resume                 # Resume paused generation
  python main.py status                 # Show current status
  python main.py config                 # Show configuration
  python main.py validate               # Validate setup
  python main.py run --config custom.yaml  # Use custom config
        """
    )
    
    parser.add_argument(
        "command",
        choices=["run", "resume", "status", "config", "validate"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        help="Override batch size"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize runner
        runner = QuestionGenerationRunner(args.config)
        
        # Apply command line overrides
        if args.debug:
            runner.config_manager.enable_debug_mode()
            print("🐛 Debug mode enabled")
        
        if args.batch_size:
            runner.config_manager.adjust_batch_size(args.batch_size)
            print(f"📦 Batch size set to {args.batch_size}")
        
        # Execute command
        if args.command == "run":
            if not runner.validate_setup():
                sys.exit(1)
            
            success = await runner.run_full_generation()
            sys.exit(0 if success else 1)
        
        elif args.command == "resume":
            success = await runner.resume_generation()
            sys.exit(0 if success else 1)
        
        elif args.command == "status":
            runner.show_status()
        
        elif args.command == "config":
            runner.show_configuration()
        
        elif args.command == "validate":
            success = runner.validate_setup()
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
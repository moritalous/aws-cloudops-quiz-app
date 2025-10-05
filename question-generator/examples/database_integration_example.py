"""
Example usage of the Database Integration Agent.

This script demonstrates how to use the AI-powered Database Integration Agent
to safely integrate question batches into the questions.json database with
structured output, backup functionality, and comprehensive validation.
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime

# Local imports
from config import AgentConfig
from core import AgentFactory, DatabaseIntegrationAgent
from models import (
    QuestionBatch, Question, LearningResource, 
    IntegrationResult, DatabaseBackup
)


async def main():
    """Demonstrate Database Integration Agent usage."""
    
    print("🤖 Database Integration Agent Example")
    print("=" * 50)
    
    # Initialize configuration
    config = AgentConfig()
    
    # Create agent factory
    factory = AgentFactory(config)
    
    # Setup paths
    example_dir = Path("examples/data")
    example_dir.mkdir(exist_ok=True)
    
    database_path = example_dir / "questions.json"
    backup_dir = example_dir / "backups"
    
    # Create Database Integration Agent
    print("\n📊 Creating Database Integration Agent...")
    db_agent = factory.create_database_integration_agent(
        database_path=str(database_path),
        backup_dir=str(backup_dir)
    )
    
    # Create initial database if it doesn't exist
    if not database_path.exists():
        print("📝 Creating initial database...")
        initial_data = {
            "version": "2.0.0",
            "generated_at": datetime.now().isoformat(),
            "generation_method": "AI-Strands-Agents-Bedrock",
            "total_questions": 0,
            "domains": {
                "monitoring": 0,
                "reliability": 0,
                "deployment": 0,
                "security": 0,
                "networking": 0
            },
            "difficulty": {
                "easy": 0,
                "medium": 0,
                "hard": 0
            },
            "question_types": {
                "single": 0,
                "multiple": 0
            },
            "questions": []
        }
        
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Initial database created at: {database_path}")
    
    # Create sample question batch
    print("\n🔨 Creating sample question batch...")
    
    learning_resource = LearningResource(
        title="Amazon CloudWatch User Guide",
        url="https://docs.aws.amazon.com/cloudwatch/latest/monitoring/",
        type="documentation"
    )
    
    sample_questions = []
    for i in range(1, 6):  # Create 5 sample questions
        question = Question(
            id=f"q{i:03d}",  # Will be reassigned during integration
            domain="monitoring",
            difficulty="medium",
            type="single",
            question=f"Sample CloudWatch monitoring question {i} with sufficient length to meet validation requirements for the question field",
            options=[
                "A. Option A - Incorrect monitoring approach",
                "B. Option B - Correct CloudWatch configuration", 
                "C. Option C - Alternative but suboptimal method",
                "D. Option D - Completely incorrect approach"
            ],
            correct_answer="B",
            explanation=f"Sample explanation {i} that provides comprehensive details about why option B is correct and explains the CloudWatch monitoring concepts involved. This explanation meets the minimum character requirements for validation and provides educational value to learners preparing for the AWS CloudOps certification exam.",
            learning_resources=[learning_resource],
            related_services=["CloudWatch", "EC2", "Lambda"],
            tags=["monitoring", "cloudwatch", "metrics"]
        )
        sample_questions.append(question)
    
    question_batch = QuestionBatch(
        batch_number=1,
        questions=sample_questions,
        batch_metadata={
            "generated_at": datetime.now().isoformat(),
            "domain_focus": "monitoring",
            "total_questions": len(sample_questions)
        }
    )
    
    print(f"✅ Created batch with {len(sample_questions)} questions")
    
    # Demonstrate backup functionality
    print("\n💾 Testing backup functionality...")
    
    try:
        backup_info = db_agent.create_backup(batch_number=1)
        print(f"✅ Backup created: {backup_info.backup_id}")
        print(f"   📁 Backup path: {backup_info.backup_file_path}")
        print(f"   📊 Questions backed up: {backup_info.questions_count}")
        print(f"   🔒 Checksum: {backup_info.checksum[:16]}...")
    except Exception as e:
        print(f"❌ Backup creation failed: {e}")
    
    # Demonstrate JSON structure validation
    print("\n🔍 Testing JSON structure validation...")
    
    # Load current database for validation
    with open(database_path, 'r', encoding='utf-8') as f:
        current_data = json.load(f)
    
    is_valid, issues = db_agent.validate_json_structure(current_data)
    print(f"✅ JSON structure valid: {is_valid}")
    if issues:
        print(f"⚠️  Issues found: {issues}")
    
    # Demonstrate ID continuity validation
    print("\n🔢 Testing ID continuity validation...")
    
    questions = current_data.get('questions', [])
    id_valid, id_issues = db_agent.validate_id_continuity(questions)
    print(f"✅ ID continuity valid: {id_valid}")
    if id_issues:
        print(f"⚠️  ID issues found: {id_issues}")
    
    # Demonstrate batch integration with structured output
    print("\n🔄 Testing batch integration with AI structured output...")
    
    try:
        # Note: This will use a mock agent in the example since we don't have real Bedrock access
        print("⚠️  Note: Using mock AI agent for demonstration")
        
        integration_result = db_agent.integrate_batch_with_structured_output(
            question_batch=question_batch,
            create_backup=True
        )
        
        print(f"✅ Integration completed successfully!")
        print(f"   📊 Questions added: {integration_result.questions_added}")
        print(f"   📈 New total: {integration_result.new_total_questions}")
        print(f"   ✅ Validation passed: {integration_result.validation_passed}")
        print(f"   💾 Backup created: {integration_result.backup_created}")
        print(f"   ⏱️  Integration time: {integration_result.integration_time_seconds:.2f}s")
        
        if integration_result.issues:
            print(f"   ⚠️  Issues: {integration_result.issues}")
        
        # Show added question IDs
        if integration_result.added_question_ids:
            print(f"   🆔 Added IDs: {', '.join(integration_result.added_question_ids)}")
        
    except Exception as e:
        print(f"❌ Integration failed: {e}")
    
    # Demonstrate backup listing
    print("\n📋 Listing available backups...")
    
    try:
        backups = db_agent.list_backups()
        print(f"✅ Found {len(backups)} backup(s)")
        
        for backup in backups[:3]:  # Show first 3 backups
            print(f"   📁 {backup.backup_id}")
            print(f"      📊 Questions: {backup.questions_count}")
            print(f"      📅 Created: {backup.created_at}")
            print(f"      💾 Size: {backup.backup_size_bytes} bytes")
    
    except Exception as e:
        print(f"❌ Failed to list backups: {e}")
    
    # Demonstrate database integrity validation
    print("\n🔍 Testing comprehensive database integrity validation...")
    
    try:
        is_valid, issues, report = db_agent.validate_database_integrity()
        
        print(f"✅ Database integrity valid: {is_valid}")
        print(f"   📁 File exists: {report['file_exists']}")
        print(f"   📄 JSON valid: {report['json_valid']}")
        print(f"   🏗️  Structure valid: {report['structure_valid']}")
        print(f"   🔢 ID continuity valid: {report['id_continuity_valid']}")
        print(f"   📊 Question count: {report['question_count']}")
        print(f"   💾 File size: {report['file_size_bytes']} bytes")
        
        if issues:
            print(f"   ⚠️  Issues found:")
            for issue in issues[:5]:  # Show first 5 issues
                print(f"      - {issue}")
    
    except Exception as e:
        print(f"❌ Integrity validation failed: {e}")
    
    # Show final database state
    print("\n📊 Final database state:")
    
    try:
        with open(database_path, 'r', encoding='utf-8') as f:
            final_data = json.load(f)
        
        print(f"   📈 Total questions: {final_data.get('total_questions', 0)}")
        print(f"   📅 Last updated: {final_data.get('generated_at', 'Unknown')}")
        print(f"   🏷️  Version: {final_data.get('version', 'Unknown')}")
        
        # Show domain distribution
        domains = final_data.get('domains', {})
        print(f"   🏗️  Domain distribution:")
        for domain, count in domains.items():
            print(f"      - {domain}: {count}")
    
    except Exception as e:
        print(f"❌ Failed to read final database state: {e}")
    
    print("\n🎉 Database Integration Agent example completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
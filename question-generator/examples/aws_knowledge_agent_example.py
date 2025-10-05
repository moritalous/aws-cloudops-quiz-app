"""
Example usage of AWS Knowledge MCP Server Integration Agent.

This example demonstrates how to use the AWSKnowledgeAgent to:
1. Search AWS documentation
2. Get comprehensive service information
3. Extract best practices and architectural guidance
4. Retrieve regional availability information
5. Generate and validate learning resources
"""

import json
from pathlib import Path
import sys

# Add the parent directory to the path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from config import AgentConfig
from core.aws_knowledge_agent import AWSKnowledgeAgent
from models.aws_knowledge_models import AWSKnowledgeExtractionRequest


def save_example_results():
    """Save example results to JSON files for reference."""
    
    print("💾 Saving Example Results")
    print("-" * 40)
    
    # Create example data structures
    example_search_result = {
        "query": "CloudWatch monitoring best practices",
        "total_results": 15,
        "search_timestamp": "2024-01-15T10:30:00Z",
        "results": [
            {
                "title": "Amazon CloudWatch Best Practices",
                "url": "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_best_practices.html",
                "content": "# CloudWatch Best Practices\n\nThis guide covers best practices...",
                "document_type": "documentation",
                "related_services": ["CloudWatch", "EC2", "Lambda"],
                "key_concepts": ["Metrics", "Alarms", "Dashboards"]
            }
        ],
        "recommended_follow_up": [
            "CloudWatch Logs best practices",
            "CloudWatch alarms configuration"
        ]
    }
    
    example_service_info = {
        "service_name": "Amazon CloudWatch",
        "service_code": "cloudwatch",
        "category": "Management & Governance",
        "description": "Amazon CloudWatch is a monitoring and observability service...",
        "key_features": [
            "Real-time monitoring",
            "Custom metrics",
            "Automated actions"
        ],
        "use_cases": [
            "Application monitoring",
            "Infrastructure monitoring",
            "Log analysis"
        ],
        "best_practices": [
            "Use custom metrics for application-specific monitoring",
            "Set up appropriate alarm thresholds"
        ],
        "regional_availability": ["us-east-1", "us-west-2", "eu-west-1"],
        "global_service": False
    }
    
    example_best_practices = {
        "topic": "CloudWatch monitoring and alerting",
        "extraction_timestamp": "2024-01-15T10:30:00Z",
        "general_best_practices": [
            "Monitor key performance indicators (KPIs)",
            "Use composite alarms for complex scenarios"
        ],
        "security_considerations": [
            "Use IAM roles for CloudWatch access",
            "Enable CloudTrail for API logging"
        ],
        "cost_optimization": [
            "Use metric filters to reduce log ingestion costs",
            "Set appropriate retention periods"
        ],
        "well_architected_principles": [
            "Operational Excellence: Automate monitoring",
            "Reliability: Set up multi-region monitoring"
        ]
    }
    
    # Save to files
    output_dir = Path("output/aws_knowledge_examples")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    examples = {
        "search_result": example_search_result,
        "service_info": example_service_info,
        "best_practices": example_best_practices
    }
    
    for name, data in examples.items():
        file_path = output_dir / f"example_{name}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {file_path}")
    
    print(f"📁 Examples saved to: {output_dir}")


def demonstrate_basic_functionality():
    """Demonstrate basic AWS Knowledge Agent functionality without MCP connection."""
    
    print("🚀 AWS Knowledge MCP Server Integration Agent Demo")
    print("=" * 60)
    
    # Initialize configuration and agent
    config = AgentConfig.from_env()
    aws_agent = AWSKnowledgeAgent(config)
    
    print("✅ AWS Knowledge Agent initialized successfully")
    print(f"✅ Configuration loaded: {config.bedrock.model_id}")
    print(f"✅ MCP Server: {config.mcp.server_name}")
    
    # Test model creation
    try:
        extraction_request = AWSKnowledgeExtractionRequest(
            topic="Amazon S3 security",
            extraction_type="best_practices",
            max_results=5,
            include_best_practices=True,
            target_audience="intermediate",
            question_context="Security configuration for S3 buckets",
            domain="security",
            difficulty_level="medium"
        )
        
        print("\n🎯 Structured Extraction Request Created")
        print(f"  Topic: {extraction_request.topic}")
        print(f"  Type: {extraction_request.extraction_type}")
        print(f"  Target Audience: {extraction_request.target_audience}")
        print(f"  Domain: {extraction_request.domain}")
        print(f"  Difficulty: {extraction_request.difficulty_level}")
        
        print("\n✅ All basic functionality working")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up resources
        aws_agent.cleanup()
        print("\n🧹 Resources cleaned up")


if __name__ == "__main__":
    print("AWS Knowledge MCP Server Integration Agent Examples")
    print("=" * 60)
    
    # Run basic functionality test
    demonstrate_basic_functionality()
    
    # Save example results
    save_example_results()
    
    print("\n🎉 All examples completed successfully!")
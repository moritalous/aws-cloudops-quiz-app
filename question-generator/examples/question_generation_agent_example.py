"""
Example usage of Question Generation Agent.

This example demonstrates how to use the QuestionGenerationAgent to:
1. Generate batches of AWS CloudOps exam questions
2. Create different types of questions (scenario, technical, best practices, troubleshooting)
3. Optimize Japanese language quality
4. Integrate with AWS Knowledge MCP Server
5. Use advanced prompt engineering techniques
"""

import json
import asyncio
from pathlib import Path
import sys

# Add the parent directory to the path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from config import AgentConfig
from core.question_generation_agent import QuestionGenerationAgent
from models.question_models import Question, QuestionBatch
from models.batch_models import BatchPlan


async def demonstrate_question_generation():
    """Demonstrate question generation functionality."""
    
    print("🚀 Question Generation Agent Demo")
    print("=" * 60)
    
    # Initialize configuration and agent
    config = AgentConfig.from_env()
    
    async with QuestionGenerationAgent(config) as question_agent:
        print("✅ Question Generation Agent initialized successfully")
        print(f"✅ Configuration loaded: {config.bedrock.model_id}")
        print(f"✅ MCP Server: {config.mcp.server_name}")
        
        # Create example batch plan
        batch_plan = BatchPlan(
            batch_number=1,
            target_domain="monitoring",
            target_difficulties=["medium", "hard"],
            difficulty_distribution={"medium": 6, "hard": 4},
            priority_topics=[
                "CloudWatch monitoring",
                "CloudWatch alarms",
                "CloudWatch Logs",
                "X-Ray tracing"
            ],
            research_queries=[
                "CloudWatch monitoring best practices",
                "CloudWatch alarms configuration",
                "CloudWatch Logs analysis",
                "X-Ray distributed tracing"
            ],
            complexity_focus="practical",
            priority_services=[
                "CloudWatch",
                "CloudWatch Logs",
                "X-Ray",
                "SNS",
                "Lambda"
            ],
            avoid_topics=[
                "Basic EC2 monitoring",
                "Simple metric collection"
            ],
            estimated_completion_time=15
        )
        
        # Example AWS knowledge content (in real usage, this would come from MCP server)
        aws_knowledge_content = """
# Amazon CloudWatch Best Practices

## Monitoring Strategy
- Use custom metrics for application-specific monitoring
- Set up appropriate alarm thresholds based on historical data
- Implement composite alarms for complex scenarios
- Use CloudWatch Insights for log analysis

## Cost Optimization
- Use metric filters to reduce log ingestion costs
- Set appropriate retention periods for logs
- Leverage CloudWatch agent for efficient metric collection

## Security Considerations
- Use IAM roles for CloudWatch access
- Enable CloudTrail for API logging
- Implement least privilege access principles

## Operational Excellence
- Automate monitoring setup using Infrastructure as Code
- Create standardized dashboards for different services
- Implement automated remediation using CloudWatch Events
"""
        
        print("\n🎯 Generating Question Batch")
        print("-" * 40)
        
        try:
            # Generate a batch of questions
            question_batch = await question_agent.generate_question_batch(
                batch_plan=batch_plan,
                aws_knowledge_content=aws_knowledge_content
            )
            
            print(f"✅ Generated batch {question_batch.batch_number}")
            print(f"✅ Questions created: {len(question_batch.questions)}")
            print(f"✅ Target domain: {question_batch.target_domain}")
            
            # Display batch metadata
            metadata = question_batch.batch_metadata
            print(f"\n📊 Batch Metadata:")
            print(f"  Domain distribution: {metadata.get('domain_distribution', {})}")
            print(f"  Difficulty distribution: {metadata.get('difficulty_distribution', {})}")
            print(f"  Question types: {metadata.get('question_types', {})}")
            print(f"  AWS services covered: {len(metadata.get('aws_services_covered', []))}")
            
            # Save example batch
            output_dir = Path("output/question_generation_examples")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            batch_file = output_dir / f"example_batch_{question_batch.batch_number}.json"
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump(question_batch.model_dump(), f, indent=2, ensure_ascii=False)
            
            print(f"💾 Batch saved to: {batch_file}")
            
            # Display first question as example
            if question_batch.questions:
                first_question = question_batch.questions[0]
                print(f"\n📝 Example Question ({first_question.id}):")
                print(f"  Domain: {first_question.domain}")
                print(f"  Difficulty: {first_question.difficulty}")
                print(f"  Type: {first_question.type}")
                print(f"  Question: {first_question.question[:100]}...")
                print(f"  Options: {len(first_question.options)} choices")
                print(f"  Correct Answer: {first_question.correct_answer}")
                print(f"  Learning Resources: {len(first_question.learning_resources)}")
                print(f"  Related Services: {', '.join(first_question.related_services[:3])}")
            
        except Exception as e:
            print(f"❌ Error during batch generation: {e}")
            import traceback
            traceback.print_exc()


async def demonstrate_single_question_generation():
    """Demonstrate single question generation."""
    
    print("\n🎯 Single Question Generation Demo")
    print("-" * 40)
    
    config = AgentConfig.from_env()
    
    async with QuestionGenerationAgent(config) as question_agent:
        
        # Example AWS knowledge content
        aws_knowledge_content = """
# Amazon S3 Security Best Practices

## Access Control
- Use IAM policies for fine-grained access control
- Implement bucket policies for resource-based permissions
- Enable MFA Delete for critical buckets
- Use S3 Access Points for simplified access management

## Encryption
- Enable default encryption for all buckets
- Use AWS KMS for server-side encryption
- Implement client-side encryption for sensitive data
- Rotate encryption keys regularly

## Monitoring and Logging
- Enable CloudTrail for API logging
- Use S3 access logging for detailed access records
- Implement CloudWatch metrics and alarms
- Monitor for unusual access patterns
"""
        
        try:
            # Generate a single technical question about S3 security
            question = await question_agent.generate_single_question(
                question_type="best_practices",
                domain="security",
                difficulty="medium",
                topic="S3 security configuration",
                aws_knowledge_content=aws_knowledge_content,
                question_id="q_example_001"
            )
            
            print("✅ Single question generated successfully")
            print(f"\n📝 Generated Question:")
            print(f"  ID: {question.id}")
            print(f"  Domain: {question.domain}")
            print(f"  Difficulty: {question.difficulty}")
            print(f"  Type: {question.type}")
            print(f"  Question: {question.question}")
            print(f"\n  Options:")
            for i, option in enumerate(question.options):
                print(f"    {chr(65+i)}. {option}")
            print(f"\n  Correct Answer: {question.correct_answer}")
            print(f"  Explanation: {question.explanation[:200]}...")
            print(f"  Learning Resources: {len(question.learning_resources)}")
            
            # Save single question example
            output_dir = Path("output/question_generation_examples")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            question_file = output_dir / f"example_single_question.json"
            with open(question_file, 'w', encoding='utf-8') as f:
                json.dump(question.model_dump(), f, indent=2, ensure_ascii=False)
            
            print(f"💾 Question saved to: {question_file}")
            
        except Exception as e:
            print(f"❌ Error during single question generation: {e}")
            import traceback
            traceback.print_exc()


def save_example_prompts():
    """Save example prompts for reference."""
    
    print("\n💾 Saving Example Prompts")
    print("-" * 40)
    
    # Example prompts for different question types
    example_prompts = {
        "scenario_prompt": """
以下の情報に基づいて、AWS CloudOps試験問題を3問生成してください：

## バッチ計画情報
バッチ番号: 1
対象ドメイン: monitoring
対象難易度: medium, hard
対象トピック: CloudWatch monitoring, CloudWatch alarms
優先AWSサービス: CloudWatch, SNS, Lambda

## AWS知識コンテンツ
[AWS CloudWatch documentation content...]

## 問題生成要件
**問題タイプ**: シナリオベース問題
- 実世界のCloudOpsエンジニアリング状況を設定
- 複数のAWSサービスが関連する統合的な問題
- 具体的な企業環境や業務要件を含む
- 実践的な解決策を求める内容

## 共通要件
1. **技術的正確性**: 最新のAWSサービスと機能に基づく
2. **実践的関連性**: 実際のCloudOps業務で遭遇する状況
3. **適切な難易度**: 指定された難易度レベルに適合
4. **明確性**: 曖昧さを排除した明確な問題文
5. **教育的価値**: 学習者の理解を深める内容

上記の要件に従って、高品質な試験問題を生成してください。
""",
        
        "technical_prompt": """
以下の情報に基づいて、AWS CloudOps試験問題を3問生成してください：

## 問題生成要件
**問題タイプ**: 技術仕様問題
- AWSサービスの具体的な機能と制限
- API仕様や設定パラメータの詳細
- サービス間の統合と相互作用
- 実装上の技術的考慮事項

技術的に正確で詳細な問題を作成してください。
""",
        
        "best_practices_prompt": """
以下の情報に基づいて、AWS CloudOps試験問題を2問生成してください：

## 問題生成要件
**問題タイプ**: ベストプラクティス問題
- AWS Well-Architectedフレームワークに基づく
- 設計原則と推奨事項
- 長期的な運用性とメンテナンス性
- セキュリティとコンプライアンスの考慮

Well-Architectedの原則に基づいた問題を作成してください。
""",
        
        "troubleshooting_prompt": """
以下の情報に基づいて、AWS CloudOps試験問題を2問生成してください：

## 問題生成要件
**問題タイプ**: トラブルシューティング問題
- 具体的な問題症状と影響
- 体系的な診断プロセス
- 根本原因の特定方法
- 効果的な解決策と予防策

実践的なトラブルシューティングスキルを評価する問題を作成してください。
""",
        
        "japanese_optimization_prompt": """
以下のAWS CloudOps試験問題の日本語品質を最適化してください：

## 元の問題
**問題文**: [Original question text]
**選択肢**: [Original options]
**解説**: [Original explanation]

## 最適化要件
1. **自然性**: より自然で読みやすい日本語表現に改善
2. **明確性**: 曖昧さを排除し、理解しやすい表現に変更
3. **一貫性**: 技術用語の表記を統一
4. **適切性**: 試験問題として適切な言語レベル
5. **正確性**: 技術的内容の正確性を維持

最適化された問題を構造化形式で出力してください。
"""
    }
    
    # Save prompts to files
    output_dir = Path("output/question_generation_examples")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for prompt_name, prompt_content in example_prompts.items():
        prompt_file = output_dir / f"{prompt_name}.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt_content)
        print(f"✅ Saved {prompt_file}")
    
    print(f"📁 Prompts saved to: {output_dir}")


async def main():
    """Main example execution."""
    print("Question Generation Agent Examples")
    print("=" * 60)
    
    # Run batch generation demo
    await demonstrate_question_generation()
    
    # Run single question generation demo
    await demonstrate_single_question_generation()
    
    # Save example prompts
    save_example_prompts()
    
    print("\n🎉 All examples completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
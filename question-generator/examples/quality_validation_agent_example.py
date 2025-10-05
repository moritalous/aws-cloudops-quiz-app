#!/usr/bin/env python3
"""
Example usage of the Quality Validation Agent.

This example demonstrates how to use the AI-driven quality validation
system for AWS CloudOps exam questions.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List

# Local imports
from config import AgentConfig
from core.quality_validation_agent import QualityValidationAgent
from models.question_models import Question, QuestionBatch, LearningResource
from models.validation_models import QuestionValidation, BatchValidation

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_sample_questions() -> List[Question]:
    """Load sample questions for validation."""
    return [
        Question(
            id="q001",
            domain="monitoring",
            difficulty="medium",
            type="single",
            question="""
EC2インスタンス上で動作するWebアプリケーションで、突然レスポンス時間が遅くなりました。
CloudWatchメトリクスを確認したところ、CPU使用率は正常ですが、ディスクI/O待機時間が高くなっています。

この問題を解決するために最も効果的な対策はどれですか？
            """.strip(),
            options=[
                "EBSボリュームをgp2からgp3に変更し、IOPSを増加させる",
                "インスタンスタイプをより大きなものに変更する",
                "Auto Scalingグループの最小インスタンス数を増やす",
                "CloudFrontディストリビューションを設定する"
            ],
            correct_answer="A",
            explanation="""
正解はA「EBSボリュームをgp2からgp3に変更し、IOPSを増加させる」です。

**正解の理由:**
ディスクI/O待機時間が高い場合、ストレージのパフォーマンスがボトルネックになっています。
gp3ボリュームはgp2よりも高いIOPSとスループットを提供でき、パフォーマンス問題を解決できます。

**他の選択肢が不適切な理由:**
- B: CPU使用率が正常なため、インスタンスサイズの変更は効果的ではない
- C: Auto Scalingはトラフィック増加に対する対策で、I/O問題の根本解決にならない
- D: CloudFrontは静的コンテンツの配信に有効だが、サーバーサイドのI/O問題は解決しない
            """.strip(),
            learning_resources=[
                LearningResource(
                    title="Amazon EBS ボリュームタイプ",
                    url="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-volume-types.html",
                    type="documentation"
                )
            ],
            related_services=["EC2", "EBS", "CloudWatch"],
            tags=["performance", "storage", "troubleshooting"]
        ),
        Question(
            id="q002",
            domain="reliability",
            difficulty="hard",
            type="multiple",
            question="""
マルチAZ構成のRDSデータベースで、プライマリインスタンスに障害が発生した場合の
自動フェイルオーバーを最適化したいと考えています。

フェイルオーバー時間を最小化し、アプリケーションの可用性を向上させるために
実装すべき対策はどれですか？（2つ選択してください）
            """.strip(),
            options=[
                "RDS Proxyを使用してコネクションプールを管理する",
                "Read Replicaを複数のAZに配置する",
                "アプリケーションでコネクション再試行ロジックを実装する",
                "データベースのバックアップ頻度を増やす",
                "RDSインスタンスのサイズを大きくする"
            ],
            correct_answer=["A", "C"],
            explanation="""
正解はAとCです。

**A. RDS Proxyを使用してコネクションプールを管理する**
- フェイルオーバー時のコネクション管理を最適化
- アプリケーションからの接続を効率的に処理
- フェイルオーバー時間の短縮に直接貢献

**C. アプリケーションでコネクション再試行ロジックを実装する**
- フェイルオーバー中の一時的な接続エラーに対応
- 自動的な接続復旧により可用性向上
- アプリケーションレベルでの耐障害性強化

**他の選択肢について:**
- B: Read Replicaは読み取り専用で、フェイルオーバーには直接関与しない
- D: バックアップ頻度はフェイルオーバー時間に影響しない
- E: インスタンスサイズはフェイルオーバー速度に影響しない
            """.strip(),
            learning_resources=[
                LearningResource(
                    title="Amazon RDS Multi-AZ 配置",
                    url="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html",
                    type="documentation"
                ),
                LearningResource(
                    title="RDS Proxy の使用",
                    url="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html",
                    type="documentation"
                )
            ],
            related_services=["RDS", "RDS Proxy"],
            tags=["high-availability", "failover", "database"]
        )
    ]


async def example_single_question_validation():
    """Example: Validate a single question."""
    logger.info("Example: Single Question Validation")
    logger.info("-" * 40)
    
    # Create configuration
    config = AgentConfig()
    
    # Create quality validation agent
    validator = QualityValidationAgent(config)
    
    # Load sample question
    questions = load_sample_questions()
    question = questions[0]
    
    logger.info(f"Validating question: {question.id}")
    logger.info(f"Domain: {question.domain}, Difficulty: {question.difficulty}")
    
    try:
        # Validate the question
        validation_result = validator.validate_question(question)
        
        # Display results
        print(f"\n📊 Validation Results for {question.id}")
        print(f"Overall Score: {validation_result.overall_score}/100")
        print(f"Technical Accuracy: {'✅' if validation_result.technical_accuracy else '❌'}")
        print(f"Clarity Score: {validation_result.clarity_score}/10")
        print(f"Difficulty Appropriate: {'✅' if validation_result.difficulty_appropriate else '❌'}")
        print(f"Japanese Quality: {validation_result.japanese_quality}/10")
        print(f"Approved: {'✅' if validation_result.approved else '❌'}")
        
        if validation_result.issues:
            print(f"\n⚠️  Issues Identified:")
            for issue in validation_result.issues:
                print(f"  • {issue}")
        
        if validation_result.suggestions:
            print(f"\n💡 Suggestions:")
            for suggestion in validation_result.suggestions:
                print(f"  • {suggestion}")
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return None


async def example_batch_validation():
    """Example: Validate a batch of questions."""
    logger.info("\nExample: Batch Validation")
    logger.info("-" * 40)
    
    # Create configuration
    config = AgentConfig()
    
    # Create quality validation agent
    validator = QualityValidationAgent(config)
    
    # Create a batch from sample questions
    questions = load_sample_questions()
    
    # Extend to 10 questions by duplicating and modifying
    extended_questions = []
    for i in range(10):
        base_question = questions[i % len(questions)]
        question = Question(**base_question.model_dump())
        question.id = f"q{i+1:03d}"
        
        # Vary domains and difficulties
        domains = ["monitoring", "reliability", "deployment", "security", "networking"]
        difficulties = ["easy", "medium", "hard"]
        question.domain = domains[i % len(domains)]
        question.difficulty = difficulties[i % len(difficulties)]
        
        extended_questions.append(question)
    
    batch = QuestionBatch(
        batch_number=1,
        questions=extended_questions,
        target_domain="monitoring"
    )
    
    logger.info(f"Validating batch {batch.batch_number} with {len(batch.questions)} questions")
    
    try:
        # Validate the batch
        batch_validation = validator.validate_batch(batch)
        
        # Display results
        print(f"\n📊 Batch Validation Results")
        print(f"Batch Number: {batch_validation.batch_number}")
        print(f"Batch Quality Score: {batch_validation.batch_quality_score}/100")
        print(f"Approved Questions: {sum(1 for qv in batch_validation.question_validations if qv.approved)}/10")
        print(f"Batch Approved: {'✅' if batch_validation.batch_approved else '❌'}")
        
        # Show individual question scores
        print(f"\n📝 Individual Question Scores:")
        for qv in batch_validation.question_validations:
            status = "✅" if qv.approved else "❌"
            print(f"  {qv.question_id}: {qv.overall_score}/100 {status}")
        
        # Show validation summary
        if batch_validation.validation_summary:
            summary = batch_validation.validation_summary
            print(f"\n📈 Validation Summary:")
            print(f"  Technical Accuracy Rate: {summary.get('technical_accuracy_rate', 0):.1%}")
            print(f"  Explanation Completeness Rate: {summary.get('explanation_completeness_rate', 0):.1%}")
            print(f"  Average Japanese Quality: {summary.get('average_japanese_quality', 0):.1f}/10")
            print(f"  Issues Identified: {summary.get('issues_identified', 0)}")
        
        if batch_validation.required_fixes:
            print(f"\n🔧 Required Fixes:")
            for fix in batch_validation.required_fixes:
                print(f"  • {fix}")
        
        if batch_validation.recommendations:
            print(f"\n💡 Recommendations:")
            for rec in batch_validation.recommendations:
                print(f"  • {rec}")
        
        return batch_validation
        
    except Exception as e:
        logger.error(f"Batch validation failed: {e}")
        return None


async def example_duplicate_detection():
    """Example: Detect duplicate questions."""
    logger.info("\nExample: Duplicate Detection")
    logger.info("-" * 40)
    
    # Create configuration
    config = AgentConfig()
    
    # Create quality validation agent
    validator = QualityValidationAgent(config)
    
    # Load existing questions
    existing_questions = load_sample_questions()
    
    # Create a new question that's similar to an existing one
    similar_question = Question(
        id="q003",
        domain="monitoring",
        difficulty="medium",
        type="single",
        question="""
EC2インスタンス上のWebアプリケーションで、レスポンス時間が突然遅くなりました。
CloudWatchメトリクスを確認すると、CPU使用率は正常ですが、ディスクI/O待機時間が高い状態です。

この問題を解決するために最も効果的な対策はどれですか？
        """.strip(),
        options=[
            "EBSボリュームをgp2からgp3に変更し、IOPSを増加させる",
            "インスタンスタイプをより大きなものに変更する",
            "Auto Scalingグループの最小インスタンス数を増やす",
            "CloudFrontディストリビューションを設定する"
        ],
        correct_answer="A",
        explanation="Similar explanation...",
        learning_resources=[
            LearningResource(
                title="Amazon EBS ボリュームタイプ",
                url="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-volume-types.html",
                type="documentation"
            )
        ],
        related_services=["EC2", "EBS", "CloudWatch"],
        tags=["performance", "storage", "troubleshooting"]
    )
    
    # Create a completely different question
    different_question = Question(
        id="q004",
        domain="security",
        difficulty="hard",
        type="single",
        question="IAMロールとIAMユーザーの主な違いは何ですか？",
        options=[
            "IAMロールは一時的な認証情報を提供する",
            "IAMユーザーは永続的なアクセスキーを持つ",
            "IAMロールはAWSサービス専用である",
            "IAMユーザーはプログラマティックアクセスのみ可能"
        ],
        correct_answer="A",
        explanation="IAMロールとユーザーの違いについての説明...",
        learning_resources=[
            LearningResource(
                title="IAM ユーザーガイド",
                url="https://docs.aws.amazon.com/iam/",
                type="documentation"
            )
        ],
        related_services=["IAM"],
        tags=["security", "identity", "access-management"]
    )
    
    logger.info("Testing duplicate detection...")
    
    try:
        # Test similar question
        similar_result = validator.validate_question_against_existing(
            similar_question, existing_questions
        )
        
        # Test different question
        different_result = validator.validate_question_against_existing(
            different_question, existing_questions
        )
        
        # Display results
        print(f"\n🔍 Duplicate Detection Results")
        
        print(f"\n📝 Similar Question ({similar_question.id}):")
        print(f"  Has Duplicates: {'⚠️  Yes' if similar_result['has_duplicates'] else '✅ No'}")
        print(f"  Recommendation: {similar_result['recommendation']}")
        if similar_result['similar_questions']:
            print(f"  Similar to:")
            for sim in similar_result['similar_questions']:
                print(f"    • {sim['id']} (similarity: {sim['similarity']:.2f}) - {sim['reason']}")
        
        print(f"\n📝 Different Question ({different_question.id}):")
        print(f"  Has Duplicates: {'⚠️  Yes' if different_result['has_duplicates'] else '✅ No'}")
        print(f"  Recommendation: {different_result['recommendation']}")
        if different_result['similar_questions']:
            print(f"  Similar to:")
            for sim in different_result['similar_questions']:
                print(f"    • {sim['id']} (similarity: {sim['similarity']:.2f}) - {sim['reason']}")
        
        return similar_result, different_result
        
    except Exception as e:
        logger.error(f"Duplicate detection failed: {e}")
        return None, None


async def example_quality_report():
    """Example: Generate a comprehensive quality report."""
    logger.info("\nExample: Quality Report Generation")
    logger.info("-" * 40)
    
    # Create configuration
    config = AgentConfig()
    
    # Create quality validation agent
    validator = QualityValidationAgent(config)
    
    # Create multiple batches for the report
    batch_validations = []
    
    logger.info("Creating sample batch validations...")
    
    # Create 3 sample batches with different quality levels
    for batch_num in range(1, 4):
        questions = load_sample_questions()
        
        # Extend to 10 questions
        extended_questions = []
        for i in range(10):
            base_question = questions[i % len(questions)]
            question = Question(**base_question.model_dump())
            question.id = f"q{(batch_num-1)*10 + i + 1:03d}"
            extended_questions.append(question)
        
        batch = QuestionBatch(
            batch_number=batch_num,
            questions=extended_questions
        )
        
        # Validate batch
        batch_validation = validator.validate_batch(batch)
        batch_validations.append(batch_validation)
    
    logger.info(f"Generating quality report for {len(batch_validations)} batches...")
    
    try:
        # Generate comprehensive quality report
        quality_report = validator.generate_quality_report(batch_validations)
        
        # Display report summary
        print(f"\n📊 Quality Report Summary")
        print(f"Report Generated: {quality_report['report_generated_at']}")
        
        summary = quality_report['summary']
        print(f"\n📈 Overall Statistics:")
        print(f"  Total Batches: {summary['total_batches']}")
        print(f"  Total Questions: {summary['total_questions']}")
        print(f"  Approved Questions: {summary['approved_questions']}")
        print(f"  Approval Rate: {summary['approval_rate']:.1%}")
        print(f"  Average Overall Score: {summary['average_overall_score']:.1f}/100")
        print(f"  Technical Accuracy Rate: {summary['technical_accuracy_rate']:.1%}")
        print(f"  Average Japanese Quality: {summary['average_japanese_quality']:.1f}/10")
        
        # Show batch details
        print(f"\n📝 Batch Details:")
        for batch_detail in quality_report['batch_details']:
            status = "✅" if batch_detail['approved'] else "❌"
            print(f"  Batch {batch_detail['batch_number']}: {batch_detail['batch_score']}/100 "
                  f"({batch_detail['approved_questions']}/10 approved) {status}")
        
        # Show quality metrics
        metrics = quality_report['quality_metrics']
        print(f"\n🎯 Quality Metrics:")
        print(f"  High Quality Batches (≥85): {metrics['high_quality_batches']}")
        print(f"  Medium Quality Batches (70-84): {metrics['medium_quality_batches']}")
        print(f"  Low Quality Batches (<70): {metrics['low_quality_batches']}")
        print(f"  Batches Needing Revision: {metrics['batches_needing_revision']}")
        
        # Show recommendations
        if quality_report['recommendations']:
            print(f"\n💡 Overall Recommendations:")
            for rec in quality_report['recommendations']:
                print(f"  • {rec}")
        
        # Save report to file
        output_dir = Path("output/quality_validation_examples")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "example_quality_report.json", "w", encoding="utf-8") as f:
            json.dump(quality_report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Quality report saved to {output_dir / 'example_quality_report.json'}")
        
        return quality_report
        
    except Exception as e:
        logger.error(f"Quality report generation failed: {e}")
        return None


async def main():
    """Run all quality validation examples."""
    print("🚀 Quality Validation Agent Examples")
    print("=" * 50)
    
    try:
        # Example 1: Single question validation
        await example_single_question_validation()
        
        # Example 2: Batch validation
        await example_batch_validation()
        
        # Example 3: Duplicate detection
        await example_duplicate_detection()
        
        # Example 4: Quality report generation
        await example_quality_report()
        
        print(f"\n✅ All examples completed successfully!")
        print(f"Check the 'output/quality_validation_examples/' directory for detailed results.")
        
    except Exception as e:
        logger.error(f"Examples failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
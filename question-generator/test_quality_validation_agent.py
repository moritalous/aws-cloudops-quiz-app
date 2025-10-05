#!/usr/bin/env python3
"""
Test script for the Quality Validation Agent.

This script tests the AI-driven quality validation functionality
for AWS CloudOps exam questions using Strands Agents.
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


def create_sample_question() -> Question:
    """Create a sample question for testing."""
    return Question(
        id="q001",
        domain="monitoring",
        difficulty="medium",
        type="single",
        question="""
あなたの会社では、EC2インスタンス上で動作するWebアプリケーションのパフォーマンス監視を強化したいと考えています。
アプリケーションのレスポンス時間、エラー率、スループットを詳細に監視し、問題が発生した際に自動的にアラートを送信する仕組みを構築する必要があります。

この要件を満たすために最も適切なAWSサービスの組み合わせはどれですか？
        """.strip(),
        options=[
            "Amazon CloudWatch + Amazon SNS + AWS X-Ray",
            "AWS CloudTrail + Amazon SES + Amazon Inspector",
            "Amazon GuardDuty + AWS Config + Amazon SQS",
            "AWS Systems Manager + Amazon EventBridge + AWS Lambda"
        ],
        correct_answer="A",
        explanation="""
正解はA「Amazon CloudWatch + Amazon SNS + AWS X-Ray」です。

**正解の理由:**
- **Amazon CloudWatch**: EC2インスタンスとアプリケーションのメトリクス（CPU使用率、メモリ使用率、カスタムメトリクス）を収集・監視
- **Amazon SNS**: CloudWatchアラームがトリガーされた際に、メール、SMS、その他の通知方法でアラートを送信
- **AWS X-Ray**: アプリケーションのレスポンス時間、エラー率、スループットを詳細に分析し、パフォーマンスのボトルネックを特定

**他の選択肢が不適切な理由:**
- **B**: CloudTrailはAPI呼び出しの監査ログ、SESはメール送信サービス、InspectorはセキュリティアセスメントでありWebアプリケーションのパフォーマンス監視には適さない
- **C**: GuardDutyは脅威検出、AWS Configは設定変更の追跡、SQSはメッセージキューイングサービスでパフォーマンス監視の要件を満たさない
- **D**: Systems Managerは主にインスタンス管理、EventBridgeはイベントルーティング、Lambdaは関数実行サービスで、包括的なアプリケーション監視には不十分

**ベストプラクティス:**
- CloudWatchカスタムメトリクスを使用してアプリケーション固有のメトリクスを収集
- X-Rayトレーシングを有効にしてリクエストの詳細な分析を実行
- CloudWatchアラームの閾値を適切に設定し、誤検知を避ける
        """.strip(),
        learning_resources=[
            LearningResource(
                title="Amazon CloudWatch ユーザーガイド",
                url="https://docs.aws.amazon.com/cloudwatch/",
                type="documentation"
            ),
            LearningResource(
                title="AWS X-Ray 開発者ガイド",
                url="https://docs.aws.amazon.com/xray/",
                type="documentation"
            )
        ],
        related_services=["CloudWatch", "SNS", "X-Ray", "EC2"],
        tags=["monitoring", "alerting", "performance", "troubleshooting"],
        task_reference="1.1",
        skill_reference="1.1.1"
    )


def create_sample_batch() -> QuestionBatch:
    """Create a sample batch of questions for testing."""
    questions = []
    
    # Create 10 sample questions with variations
    for i in range(10):
        question = create_sample_question()
        question.id = f"q{i+1:03d}"
        
        # Vary domains
        domains = ["monitoring", "reliability", "deployment", "security", "networking"]
        question.domain = domains[i % len(domains)]
        
        # Vary difficulties
        difficulties = ["easy", "medium", "hard"]
        question.difficulty = difficulties[i % len(difficulties)]
        
        # Vary types
        question.type = "multiple" if i % 5 == 0 else "single"
        if question.type == "multiple":
            question.correct_answer = ["A", "C"]
        
        questions.append(question)
    
    return QuestionBatch(
        batch_number=1,
        questions=questions,
        target_domain="monitoring"
    )


async def test_single_question_validation():
    """Test validation of a single question."""
    logger.info("Testing single question validation...")
    
    try:
        # Create configuration
        config = AgentConfig()
        
        # Create quality validation agent
        validator = QualityValidationAgent(config)
        
        # Create sample question
        question = create_sample_question()
        
        # Validate question
        logger.info(f"Validating question: {question.id}")
        validation_result = validator.validate_question(question)
        
        # Display results
        logger.info(f"Validation completed for {question.id}")
        logger.info(f"Overall Score: {validation_result.overall_score}")
        logger.info(f"Technical Accuracy: {validation_result.technical_accuracy}")
        logger.info(f"Approved: {validation_result.approved}")
        
        if validation_result.issues:
            logger.info(f"Issues found: {validation_result.issues}")
        
        if validation_result.suggestions:
            logger.info(f"Suggestions: {validation_result.suggestions}")
        
        # Save result to file
        output_dir = Path("output/quality_validation_examples")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "single_question_validation.json", "w", encoding="utf-8") as f:
            json.dump(validation_result.model_dump(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"Validation result saved to {output_dir / 'single_question_validation.json'}")
        
        return validation_result
        
    except Exception as e:
        logger.error(f"Single question validation test failed: {e}")
        raise


async def test_batch_validation():
    """Test validation of a question batch."""
    logger.info("Testing batch validation...")
    
    try:
        # Create configuration
        config = AgentConfig()
        
        # Create quality validation agent
        validator = QualityValidationAgent(config)
        
        # Create sample batch
        batch = create_sample_batch()
        
        # Validate batch
        logger.info(f"Validating batch {batch.batch_number} with {len(batch.questions)} questions")
        batch_validation = validator.validate_batch(batch)
        
        # Display results
        logger.info(f"Batch validation completed for batch {batch.batch_number}")
        logger.info(f"Batch Quality Score: {batch_validation.batch_quality_score}")
        logger.info(f"Batch Approved: {batch_validation.batch_approved}")
        logger.info(f"Approved Questions: {sum(1 for qv in batch_validation.question_validations if qv.approved)}/10")
        
        if batch_validation.required_fixes:
            logger.info(f"Required Fixes: {batch_validation.required_fixes}")
        
        if batch_validation.recommendations:
            logger.info(f"Recommendations: {batch_validation.recommendations}")
        
        # Save result to file
        output_dir = Path("output/quality_validation_examples")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "batch_validation.json", "w", encoding="utf-8") as f:
            json.dump(batch_validation.model_dump(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"Batch validation result saved to {output_dir / 'batch_validation.json'}")
        
        return batch_validation
        
    except Exception as e:
        logger.error(f"Batch validation test failed: {e}")
        raise


async def test_duplicate_detection():
    """Test duplicate detection functionality."""
    logger.info("Testing duplicate detection...")
    
    try:
        # Create configuration
        config = AgentConfig()
        
        # Create quality validation agent
        validator = QualityValidationAgent(config)
        
        # Create original question
        original_question = create_sample_question()
        
        # Create similar question
        similar_question = create_sample_question()
        similar_question.id = "q002"
        similar_question.question = original_question.question.replace("Webアプリケーション", "ウェブアプリケーション")
        
        # Create different question
        different_question = Question(
            id="q003",
            domain="security",
            difficulty="hard",
            type="multiple",
            question="IAMポリシーでS3バケットへのアクセスを制限する最適な方法は？",
            options=["Option A", "Option B", "Option C", "Option D"],
            correct_answer=["A", "B"],
            explanation="セキュリティに関する説明...",
            learning_resources=[
                LearningResource(title="IAM Guide", url="https://docs.aws.amazon.com/iam/", type="documentation")
            ],
            related_services=["IAM", "S3"],
            tags=["security", "access-control"]
        )
        
        existing_questions = [original_question, different_question]
        
        # Test duplicate detection
        logger.info("Testing similar question detection...")
        similar_result = validator.validate_question_against_existing(similar_question, existing_questions)
        
        logger.info("Testing different question detection...")
        different_result = validator.validate_question_against_existing(different_question, existing_questions)
        
        # Display results
        logger.info(f"Similar question has duplicates: {similar_result['has_duplicates']}")
        logger.info(f"Different question has duplicates: {different_result['has_duplicates']}")
        
        # Save results
        output_dir = Path("output/quality_validation_examples")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "duplicate_detection.json", "w", encoding="utf-8") as f:
            json.dump({
                "similar_question_result": similar_result,
                "different_question_result": different_result
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Duplicate detection results saved to {output_dir / 'duplicate_detection.json'}")
        
        return similar_result, different_result
        
    except Exception as e:
        logger.error(f"Duplicate detection test failed: {e}")
        raise


async def test_quality_report_generation():
    """Test quality report generation."""
    logger.info("Testing quality report generation...")
    
    try:
        # Create configuration
        config = AgentConfig()
        
        # Create quality validation agent
        validator = QualityValidationAgent(config)
        
        # Create multiple batch validations
        batch_validations = []
        
        for batch_num in range(1, 4):  # Create 3 batches
            batch = create_sample_batch()
            batch.batch_number = batch_num
            
            # Validate batch
            batch_validation = validator.validate_batch(batch)
            batch_validations.append(batch_validation)
        
        # Generate quality report
        logger.info("Generating comprehensive quality report...")
        quality_report = validator.generate_quality_report(batch_validations)
        
        # Display summary
        logger.info(f"Quality Report Summary:")
        logger.info(f"Total Batches: {quality_report['summary']['total_batches']}")
        logger.info(f"Total Questions: {quality_report['summary']['total_questions']}")
        logger.info(f"Approval Rate: {quality_report['summary']['approval_rate']:.2%}")
        logger.info(f"Average Score: {quality_report['summary']['average_overall_score']}")
        
        # Save report
        output_dir = Path("output/quality_validation_examples")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "quality_report.json", "w", encoding="utf-8") as f:
            json.dump(quality_report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Quality report saved to {output_dir / 'quality_report.json'}")
        
        return quality_report
        
    except Exception as e:
        logger.error(f"Quality report generation test failed: {e}")
        raise


async def main():
    """Run all quality validation tests."""
    logger.info("Starting Quality Validation Agent tests...")
    
    try:
        # Test 1: Single question validation
        logger.info("\n" + "="*50)
        logger.info("TEST 1: Single Question Validation")
        logger.info("="*50)
        await test_single_question_validation()
        
        # Test 2: Batch validation
        logger.info("\n" + "="*50)
        logger.info("TEST 2: Batch Validation")
        logger.info("="*50)
        await test_batch_validation()
        
        # Test 3: Duplicate detection
        logger.info("\n" + "="*50)
        logger.info("TEST 3: Duplicate Detection")
        logger.info("="*50)
        await test_duplicate_detection()
        
        # Test 4: Quality report generation
        logger.info("\n" + "="*50)
        logger.info("TEST 4: Quality Report Generation")
        logger.info("="*50)
        await test_quality_report_generation()
        
        logger.info("\n" + "="*50)
        logger.info("All Quality Validation Agent tests completed successfully!")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"Quality validation tests failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
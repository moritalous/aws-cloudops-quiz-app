"""
AI-driven quality validation agent for generated AWS CloudOps exam questions.

This module implements comprehensive quality validation using Strands Agents
with Amazon Bedrock OpenAI models and AWS Knowledge MCP Server integration.
It validates technical accuracy, clarity, difficulty appropriateness, and
overall question quality.
"""

import logging
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# Strands Agents imports
from strands import Agent

# Local imports
from models.question_models import Question, QuestionBatch
from models.validation_models import QuestionValidation, BatchValidation
from core.agent_factory import AgentFactory
from core.error_handling import ValidationError, retry_with_backoff
from config import AgentConfig

logger = logging.getLogger(__name__)


class QualityValidationAgent:
    """
    AI-driven quality validation agent for AWS CloudOps exam questions.
    
    Uses Strands Agents with structured output to perform comprehensive
    quality assessment including technical accuracy, clarity, difficulty
    appropriateness, and Japanese language quality.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Initialize the quality validation agent.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.agent_factory = AgentFactory(config)
        self.validator_agent: Optional[Agent] = None
        self.aws_knowledge_agent = None
        
        logger.info("QualityValidationAgent initialized")
    
    def _get_validator_agent(self) -> Agent:
        """Get or create the quality validator agent."""
        if self.validator_agent is None:
            self.validator_agent = self.agent_factory.create_quality_validator()
        return self.validator_agent
    
    def _get_aws_knowledge_agent(self):
        """Get or create the AWS knowledge agent for fact-checking."""
        if self.aws_knowledge_agent is None:
            self.aws_knowledge_agent = self.agent_factory.create_aws_knowledge_agent()
        return self.aws_knowledge_agent
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def validate_question(
        self, 
        question: Question,
        aws_docs_context: Optional[str] = None
    ) -> QuestionValidation:
        """
        Validate a single question using AI-driven analysis.
        
        Args:
            question: Question to validate
            aws_docs_context: Optional AWS documentation context for fact-checking
        
        Returns:
            QuestionValidation result with detailed assessment
        
        Raises:
            ValidationError: If validation fails
        """
        try:
            logger.info(f"Validating question: {question.id}")
            
            # Get AWS documentation context if not provided
            if aws_docs_context is None:
                aws_docs_context = self._get_aws_context_for_question(question)
            
            # Create validation prompt
            validation_prompt = self._create_question_validation_prompt(
                question, aws_docs_context
            )
            
            # Get validator agent
            validator_agent = self._get_validator_agent()
            
            # Use MCP context manager for AWS docs access
            mcp_context = self.agent_factory.get_mcp_context_manager()
            
            with mcp_context:
                # Perform structured validation
                validation_result = validator_agent.structured_output(
                    QuestionValidation,
                    validation_prompt
                )
            
            logger.info(
                f"Question {question.id} validated - Score: {validation_result.overall_score}, "
                f"Approved: {validation_result.approved}"
            )
            
            return validation_result
            
        except Exception as e:
            error_msg = f"Failed to validate question {question.id}: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg) from e
    
    def _get_aws_context_for_question(self, question: Question) -> str:
        """
        Get relevant AWS documentation context for a question.
        
        Args:
            question: Question to get context for
        
        Returns:
            AWS documentation context string
        """
        try:
            aws_knowledge_agent = self._get_aws_knowledge_agent()
            
            # Create search queries based on question content
            search_queries = []
            
            # Add related services as search terms
            for service in question.related_services:
                search_queries.append(f"AWS {service}")
            
            # Add domain-specific search terms
            domain_terms = {
                'monitoring': ['CloudWatch', 'monitoring', 'logging', 'metrics'],
                'reliability': ['backup', 'disaster recovery', 'high availability'],
                'deployment': ['CloudFormation', 'deployment', 'provisioning'],
                'security': ['IAM', 'security', 'compliance', 'encryption'],
                'networking': ['VPC', 'networking', 'content delivery']
            }
            
            if question.domain in domain_terms:
                search_queries.extend(domain_terms[question.domain])
            
            # Search for relevant documentation
            context_parts = []
            for query in search_queries[:3]:  # Limit to avoid too many API calls
                try:
                    search_results = aws_knowledge_agent.search_comprehensive_knowledge(
                        query, max_results=2
                    )
                    for result in search_results:
                        context_parts.append(f"## {result.get('title', 'AWS Documentation')}\n{result.get('content', '')}")
                except Exception as e:
                    logger.warning(f"Failed to search AWS docs for '{query}': {e}")
            
            return "\n\n".join(context_parts) if context_parts else "No specific AWS documentation context available."
            
        except Exception as e:
            logger.warning(f"Failed to get AWS context for question {question.id}: {e}")
            return "AWS documentation context unavailable."
    
    def _create_question_validation_prompt(
        self, 
        question: Question, 
        aws_docs_context: str
    ) -> str:
        """
        Create a comprehensive validation prompt for a question.
        
        Args:
            question: Question to validate
            aws_docs_context: AWS documentation context
        
        Returns:
            Validation prompt string
        """
        return f"""
以下のAWS CloudOps試験問題を包括的に検証してください。

## 検証対象問題

**問題ID**: {question.id}
**ドメイン**: {question.domain}
**難易度**: {question.difficulty}
**問題タイプ**: {question.type}

**問題文**:
{question.question}

**選択肢**:
{chr(10).join([f"{chr(65+i)}. {option}" for i, option in enumerate(question.options)])}

**正解**: {question.correct_answer}

**解説**:
{question.explanation}

**学習リソース**:
{chr(10).join([f"- {resource.title} ({resource.type}): {resource.url}" for resource in question.learning_resources])}

**関連AWSサービス**: {', '.join(question.related_services)}

## AWS公式ドキュメント参照

{aws_docs_context}

## 検証項目

以下の項目について詳細に検証し、構造化された結果を提供してください：

### 1. 技術的正確性 (Technical Accuracy)
- AWS公式ドキュメントとの整合性
- サービス仕様の正確性
- 設定や手順の妥当性
- 最新情報との一致

### 2. 問題の明確性 (Clarity)
- 問題文の明確さと理解しやすさ
- 曖昧な表現の有無
- 必要な情報の完全性
- 誤解を招く表現の有無

### 3. 難易度の適切性 (Difficulty Appropriateness)
- 指定された難易度レベルとの一致
- AWS CloudOps試験レベルとの適合性
- 必要な知識レベルの妥当性

### 4. 誤答選択肢の品質 (Distractor Quality)
- もっともらしさの評価
- 明らかに間違いとわかる選択肢の回避
- 学習効果のある誤答選択肢

### 5. 解説の包括性 (Explanation Completeness)
- 正解の理由の明確な説明
- 誤答選択肢が間違いである理由
- 追加の学習ポイント
- 実践的な応用例

### 6. 学習リソースの有効性 (Resource Validity)
- URLの有効性（可能な範囲で）
- リソースの関連性
- 公式ドキュメントの優先
- 学習価値の評価

### 7. 日本語品質 (Japanese Quality)
- 自然な日本語表現
- 技術用語の適切な使用
- 文法と表記の正確性
- 読みやすさ

### 8. AWS試験関連性 (Exam Relevance)
- AWS CloudOps試験範囲との適合性
- 実際の試験問題との類似性
- 実務的な価値

## 出力要件

構造化された検証結果を以下の形式で提供してください：
- 各項目の詳細な評価
- 具体的な問題点の指摘
- 改善提案
- 総合評価スコア
- 承認可否の判定

検証は厳格に行い、技術的正確性を最優先してください。
疑わしい点があれば、AWS公式ドキュメントとの照合を重視してください。
"""
    
    @retry_with_backoff(max_retries=3, base_delay=3.0)
    def validate_batch(
        self, 
        question_batch: QuestionBatch,
        aws_docs_context: Optional[str] = None
    ) -> BatchValidation:
        """
        Validate a complete batch of questions.
        
        Args:
            question_batch: Batch of questions to validate
            aws_docs_context: Optional AWS documentation context
        
        Returns:
            BatchValidation result with batch-level assessment
        
        Raises:
            ValidationError: If batch validation fails
        """
        try:
            logger.info(f"Validating batch {question_batch.batch_number} with {len(question_batch.questions)} questions")
            
            # Validate individual questions
            question_validations = []
            for question in question_batch.questions:
                validation = self.validate_question(question, aws_docs_context)
                question_validations.append(validation)
            
            # Perform batch-level validation
            batch_validation = self._validate_batch_level_requirements(
                question_batch, question_validations
            )
            
            logger.info(
                f"Batch {question_batch.batch_number} validated - "
                f"Score: {batch_validation.batch_quality_score}, "
                f"Approved: {batch_validation.batch_approved}"
            )
            
            return batch_validation
            
        except Exception as e:
            error_msg = f"Failed to validate batch {question_batch.batch_number}: {str(e)}"
            logger.error(error_msg)
            raise ValidationError(error_msg) from e
    
    def _validate_batch_level_requirements(
        self,
        question_batch: QuestionBatch,
        question_validations: List[QuestionValidation]
    ) -> BatchValidation:
        """
        Validate batch-level requirements and create BatchValidation.
        
        Args:
            question_batch: Original question batch
            question_validations: Individual question validation results
        
        Returns:
            BatchValidation with batch-level assessment
        """
        # Analyze domain distribution
        domain_counts = {}
        for question in question_batch.questions:
            domain_counts[question.domain] = domain_counts.get(question.domain, 0) + 1
        
        # Analyze difficulty distribution
        difficulty_counts = {}
        for question in question_batch.questions:
            difficulty_counts[question.difficulty] = difficulty_counts.get(question.difficulty, 0) + 1
        
        # Analyze question type distribution
        type_counts = {}
        for question in question_batch.questions:
            type_counts[question.type] = type_counts.get(question.type, 0) + 1
        
        # Check for duplicates (simplified - could be enhanced with semantic similarity)
        duplicate_check = self._check_for_duplicates(question_batch.questions)
        
        # Create batch validation
        batch_validation = BatchValidation(
            batch_number=question_batch.batch_number,
            question_validations=question_validations,
            batch_quality_score=0,  # Will be calculated in model_post_init
            domain_distribution_check=True,  # Could add specific logic
            difficulty_balance_check=self._check_difficulty_balance(difficulty_counts),
            question_type_balance_check=self._check_type_balance(type_counts),
            duplicate_check=duplicate_check,
            duplicate_details=[],
            coverage_analysis={
                "domains": domain_counts,
                "difficulties": difficulty_counts,
                "question_types": type_counts
            },
            batch_approved=False,  # Will be calculated in model_post_init
            required_fixes=[],
            recommendations=self._generate_batch_recommendations(
                question_batch, question_validations
            )
        )
        
        return batch_validation
    
    def _check_difficulty_balance(self, difficulty_counts: Dict[str, int]) -> bool:
        """
        Check if difficulty distribution is reasonable for a batch.
        
        Args:
            difficulty_counts: Count of questions by difficulty
        
        Returns:
            True if balance is acceptable
        """
        total = sum(difficulty_counts.values())
        if total == 0:
            return False
        
        # For a 10-question batch, allow some flexibility
        # Target: ~30% easy, ~50% medium, ~20% hard
        easy_ratio = difficulty_counts.get('easy', 0) / total
        medium_ratio = difficulty_counts.get('medium', 0) / total
        hard_ratio = difficulty_counts.get('hard', 0) / total
        
        # Allow reasonable deviation for small batches
        return (
            0.1 <= easy_ratio <= 0.5 and
            0.3 <= medium_ratio <= 0.7 and
            0.0 <= hard_ratio <= 0.4
        )
    
    def _check_type_balance(self, type_counts: Dict[str, int]) -> bool:
        """
        Check if question type distribution is reasonable.
        
        Args:
            type_counts: Count of questions by type
        
        Returns:
            True if balance is acceptable
        """
        total = sum(type_counts.values())
        if total == 0:
            return False
        
        # Target: ~80% single, ~20% multiple
        single_ratio = type_counts.get('single', 0) / total
        multiple_ratio = type_counts.get('multiple', 0) / total
        
        # Allow flexibility for small batches
        return (
            0.6 <= single_ratio <= 1.0 and
            0.0 <= multiple_ratio <= 0.4
        )
    
    def _check_for_duplicates(self, questions: List[Question]) -> bool:
        """
        Check for duplicate content in questions.
        
        Args:
            questions: List of questions to check
        
        Returns:
            True if no duplicates found
        """
        # Simple duplicate check - could be enhanced with semantic similarity
        question_texts = [q.question.lower().strip() for q in questions]
        return len(question_texts) == len(set(question_texts))
    
    def _generate_batch_recommendations(
        self,
        question_batch: QuestionBatch,
        question_validations: List[QuestionValidation]
    ) -> List[str]:
        """
        Generate recommendations for batch improvement.
        
        Args:
            question_batch: Original question batch
            question_validations: Individual validation results
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Analyze common issues
        low_score_count = sum(1 for v in question_validations if v.overall_score < 70)
        if low_score_count > 2:
            recommendations.append(f"{low_score_count}問の品質スコアが低いため、全体的な品質向上が必要")
        
        # Check technical accuracy
        inaccurate_count = sum(1 for v in question_validations if not v.technical_accuracy)
        if inaccurate_count > 0:
            recommendations.append(f"{inaccurate_count}問で技術的不正確性が検出されました - AWS公式ドキュメントとの再確認が必要")
        
        # Check explanation quality
        poor_explanation_count = sum(1 for v in question_validations if not v.explanation_completeness)
        if poor_explanation_count > 1:
            recommendations.append("解説の包括性を向上させ、より詳細な説明を追加してください")
        
        # Check Japanese quality
        avg_japanese_score = sum(v.japanese_quality for v in question_validations) / len(question_validations)
        if avg_japanese_score < 7:
            recommendations.append("日本語表現の自然さと読みやすさの改善が推奨されます")
        
        # Check resource validity
        invalid_resource_count = sum(1 for v in question_validations if not v.resource_validity)
        if invalid_resource_count > 0:
            recommendations.append("学習リソースの有効性と関連性を確認してください")
        
        return recommendations
    
    def validate_question_against_existing(
        self,
        new_question: Question,
        existing_questions: List[Question]
    ) -> Dict[str, Any]:
        """
        Validate a new question against existing questions for duplicates.
        
        Args:
            new_question: New question to validate
            existing_questions: List of existing questions
        
        Returns:
            Dictionary with duplicate analysis results
        """
        try:
            logger.info(f"Checking question {new_question.id} against {len(existing_questions)} existing questions")
            
            # Simple text similarity check
            similar_questions = []
            for existing in existing_questions:
                # Check question text similarity (simplified)
                if self._calculate_text_similarity(new_question.question, existing.question) > 0.8:
                    similar_questions.append({
                        'id': existing.id,
                        'similarity': self._calculate_text_similarity(new_question.question, existing.question),
                        'reason': 'Similar question text'
                    })
                
                # Check if same AWS services and domain
                if (new_question.domain == existing.domain and 
                    set(new_question.related_services) == set(existing.related_services) and
                    len(new_question.related_services) > 0):
                    similar_questions.append({
                        'id': existing.id,
                        'similarity': 0.7,
                        'reason': 'Same domain and AWS services'
                    })
            
            return {
                'has_duplicates': len(similar_questions) > 0,
                'similar_questions': similar_questions,
                'recommendation': 'Modify question to avoid duplication' if similar_questions else 'No duplicates detected'
            }
            
        except Exception as e:
            logger.error(f"Failed to check duplicates for question {new_question.id}: {e}")
            return {
                'has_duplicates': False,
                'similar_questions': [],
                'recommendation': 'Duplicate check failed - manual review recommended'
            }
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity between two strings.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score between 0 and 1
        """
        # Simple word-based similarity (could be enhanced with more sophisticated methods)
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def generate_quality_report(
        self,
        batch_validations: List[BatchValidation]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive quality report from multiple batch validations.
        
        Args:
            batch_validations: List of batch validation results
        
        Returns:
            Comprehensive quality report
        """
        try:
            logger.info(f"Generating quality report for {len(batch_validations)} batches")
            
            # Aggregate statistics
            total_questions = sum(len(bv.question_validations) for bv in batch_validations)
            total_approved = sum(
                sum(1 for qv in bv.question_validations if qv.approved) 
                for bv in batch_validations
            )
            
            # Calculate average scores
            all_question_validations = []
            for bv in batch_validations:
                all_question_validations.extend(bv.question_validations)
            
            avg_overall_score = sum(qv.overall_score for qv in all_question_validations) / len(all_question_validations)
            avg_technical_accuracy = sum(1 for qv in all_question_validations if qv.technical_accuracy) / len(all_question_validations)
            avg_japanese_quality = sum(qv.japanese_quality for qv in all_question_validations) / len(all_question_validations)
            
            # Domain distribution
            domain_counts = {}
            for qv in all_question_validations:
                # Note: This would need actual question data to get domain
                pass  # Simplified for now
            
            # Generate report
            quality_report = {
                'report_generated_at': datetime.now().isoformat(),
                'summary': {
                    'total_batches': len(batch_validations),
                    'total_questions': total_questions,
                    'approved_questions': total_approved,
                    'approval_rate': total_approved / total_questions if total_questions > 0 else 0,
                    'average_overall_score': round(avg_overall_score, 2),
                    'technical_accuracy_rate': round(avg_technical_accuracy, 2),
                    'average_japanese_quality': round(avg_japanese_quality, 2)
                },
                'batch_details': [
                    {
                        'batch_number': bv.batch_number,
                        'batch_score': bv.batch_quality_score,
                        'approved': bv.batch_approved,
                        'approved_questions': sum(1 for qv in bv.question_validations if qv.approved),
                        'issues_count': sum(len(qv.issues) for qv in bv.question_validations)
                    }
                    for bv in batch_validations
                ],
                'recommendations': self._generate_overall_recommendations(batch_validations),
                'quality_metrics': {
                    'high_quality_batches': sum(1 for bv in batch_validations if bv.batch_quality_score >= 85),
                    'medium_quality_batches': sum(1 for bv in batch_validations if 70 <= bv.batch_quality_score < 85),
                    'low_quality_batches': sum(1 for bv in batch_validations if bv.batch_quality_score < 70),
                    'batches_needing_revision': sum(1 for bv in batch_validations if not bv.batch_approved)
                }
            }
            
            logger.info(f"Quality report generated - Approval rate: {quality_report['summary']['approval_rate']:.2%}")
            return quality_report
            
        except Exception as e:
            logger.error(f"Failed to generate quality report: {e}")
            raise ValidationError(f"Quality report generation failed: {str(e)}") from e
    
    def _generate_overall_recommendations(
        self,
        batch_validations: List[BatchValidation]
    ) -> List[str]:
        """
        Generate overall recommendations based on all batch validations.
        
        Args:
            batch_validations: List of batch validation results
        
        Returns:
            List of overall recommendations
        """
        recommendations = []
        
        # Check overall approval rate
        total_batches = len(batch_validations)
        approved_batches = sum(1 for bv in batch_validations if bv.batch_approved)
        approval_rate = approved_batches / total_batches if total_batches > 0 else 0
        
        if approval_rate < 0.8:
            recommendations.append(f"バッチ承認率が{approval_rate:.1%}と低いため、品質向上プロセスの見直しが必要")
        
        # Check for common issues across batches
        common_issues = {}
        for bv in batch_validations:
            for fix in bv.required_fixes:
                common_issues[fix] = common_issues.get(fix, 0) + 1
        
        for issue, count in common_issues.items():
            if count > total_batches * 0.3:  # If issue appears in >30% of batches
                recommendations.append(f"共通課題: {issue} ({count}バッチで発生)")
        
        # Check quality trends
        avg_scores = [bv.batch_quality_score for bv in batch_validations]
        if len(avg_scores) > 1:
            if avg_scores[-1] < avg_scores[0]:  # Quality declining
                recommendations.append("品質スコアの低下傾向が見られます - プロセス改善を検討してください")
        
        return recommendations
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up QualityValidationAgent resources")
        if self.agent_factory:
            self.agent_factory.cleanup()
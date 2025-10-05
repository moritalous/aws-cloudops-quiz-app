"""
Pydantic models for AI-driven quality validation of generated questions.

These models define the structure for comprehensive quality assessment,
including technical accuracy, clarity, difficulty appropriateness, and
overall question quality metrics.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime


class QuestionValidation(BaseModel):
    """Validation result for an individual question."""
    
    question_id: str = Field(
        description="ID of the validated question"
    )
    technical_accuracy: bool = Field(
        description="Whether the question is technically accurate"
    )
    technical_accuracy_score: int = Field(
        description="Technical accuracy score (1-10)",
        ge=1,
        le=10
    )
    clarity_score: int = Field(
        description="Question clarity and readability score (1-10)",
        ge=1,
        le=10
    )
    difficulty_appropriate: bool = Field(
        description="Whether the assigned difficulty level is appropriate"
    )
    difficulty_justification: str = Field(
        description="Explanation for the difficulty level assessment"
    )
    distractor_quality: int = Field(
        description="Quality of incorrect answer options score (1-10)",
        ge=1,
        le=10
    )
    explanation_completeness: bool = Field(
        description="Whether the explanation is comprehensive and helpful"
    )
    explanation_score: int = Field(
        description="Explanation quality score (1-10)",
        ge=1,
        le=10
    )
    resource_validity: bool = Field(
        description="Whether learning resources are valid and relevant"
    )
    resource_accessibility: bool = Field(
        description="Whether learning resource URLs are accessible",
        default=True
    )
    japanese_quality: int = Field(
        description="Japanese language quality score (1-10)",
        ge=1,
        le=10
    )
    aws_service_accuracy: bool = Field(
        description="Whether AWS service references are accurate and current"
    )
    exam_relevance: int = Field(
        description="Relevance to actual AWS CloudOps exam (1-10)",
        ge=1,
        le=10
    )
    issues: List[str] = Field(
        description="List of identified issues or problems",
        default_factory=list
    )
    suggestions: List[str] = Field(
        description="List of improvement suggestions",
        default_factory=list
    )
    overall_score: int = Field(
        description="Overall quality score (1-100)",
        ge=1,
        le=100
    )
    approved: bool = Field(
        description="Whether the question is approved for inclusion"
    )
    validation_notes: Optional[str] = Field(
        description="Additional validation notes",
        default=None
    )
    validated_at: str = Field(
        description="Validation timestamp",
        default_factory=lambda: datetime.now().isoformat()
    )
    
    def model_post_init(self, __context) -> None:
        """Calculate overall score based on individual metrics."""
        # Weighted scoring system
        weights = {
            'technical_accuracy_score': 0.25,
            'clarity_score': 0.15,
            'distractor_quality': 0.15,
            'explanation_score': 0.15,
            'japanese_quality': 0.10,
            'exam_relevance': 0.20
        }
        
        weighted_score = sum(
            getattr(self, metric) * weight 
            for metric, weight in weights.items()
        )
        
        # Apply boolean penalties
        penalties = 0
        if not self.technical_accuracy:
            penalties += 20
        if not self.difficulty_appropriate:
            penalties += 10
        if not self.explanation_completeness:
            penalties += 10
        if not self.resource_validity:
            penalties += 5
        if not self.aws_service_accuracy:
            penalties += 15
        
        self.overall_score = max(1, min(100, int(weighted_score * 10 - penalties)))
        self.approved = self.overall_score >= 70 and self.technical_accuracy


class BatchValidation(BaseModel):
    """Validation result for a complete batch of questions."""
    
    batch_number: int = Field(
        description="Batch number being validated",
        ge=1,
        le=19
    )
    question_validations: List[QuestionValidation] = Field(
        description="Individual validation results for each question"
    )
    batch_quality_score: int = Field(
        description="Overall batch quality score (1-100)",
        ge=1,
        le=100
    )
    domain_distribution_check: bool = Field(
        description="Whether domain distribution meets requirements"
    )
    difficulty_balance_check: bool = Field(
        description="Whether difficulty balance is appropriate"
    )
    question_type_balance_check: bool = Field(
        description="Whether single/multiple choice balance is appropriate"
    )
    duplicate_check: bool = Field(
        description="Whether duplicate content was detected"
    )
    duplicate_details: List[str] = Field(
        description="Details about any duplicates found",
        default_factory=list
    )
    coverage_analysis: Dict[str, int] = Field(
        description="Analysis of topic and service coverage",
        default_factory=dict
    )
    batch_approved: bool = Field(
        description="Whether the entire batch is approved"
    )
    required_fixes: List[str] = Field(
        description="List of issues that must be fixed",
        default_factory=list
    )
    recommendations: List[str] = Field(
        description="Recommendations for improvement",
        default_factory=list
    )
    validation_summary: Dict[str, any] = Field(
        description="Summary statistics for the batch",
        default_factory=dict
    )
    validated_at: str = Field(
        description="Batch validation timestamp",
        default_factory=lambda: datetime.now().isoformat()
    )
    
    @validator('question_validations')
    def validate_question_count(cls, v):
        """Ensure exactly 10 questions are validated."""
        if len(v) != 10:
            raise ValueError('Batch must contain exactly 10 question validations')
        return v
    
    def model_post_init(self, __context) -> None:
        """Calculate batch-level metrics and approval status."""
        if not self.question_validations:
            return
            
        # Calculate batch quality score
        individual_scores = [q.overall_score for q in self.question_validations]
        self.batch_quality_score = int(sum(individual_scores) / len(individual_scores))
        
        # Count approvals
        approved_count = sum(1 for q in self.question_validations if q.approved)
        
        # Analyze distributions
        domains = [q.question_id for q in self.question_validations]  # This would need actual question data
        
        # Determine batch approval
        self.batch_approved = (
            approved_count >= 8 and  # At least 8/10 questions approved
            self.batch_quality_score >= 75 and
            self.domain_distribution_check and
            self.difficulty_balance_check and
            self.duplicate_check
        )
        
        # Generate validation summary
        self.validation_summary = {
            "total_questions": len(self.question_validations),
            "approved_questions": approved_count,
            "average_score": self.batch_quality_score,
            "technical_accuracy_rate": sum(1 for q in self.question_validations if q.technical_accuracy) / len(self.question_validations),
            "explanation_completeness_rate": sum(1 for q in self.question_validations if q.explanation_completeness) / len(self.question_validations),
            "resource_validity_rate": sum(1 for q in self.question_validations if q.resource_validity) / len(self.question_validations),
            "average_japanese_quality": sum(q.japanese_quality for q in self.question_validations) / len(self.question_validations),
            "issues_identified": sum(len(q.issues) for q in self.question_validations),
            "suggestions_provided": sum(len(q.suggestions) for q in self.question_validations)
        }
        
        # Generate required fixes if not approved
        if not self.batch_approved:
            if approved_count < 8:
                self.required_fixes.append(f"Only {approved_count}/10 questions approved - need at least 8")
            if self.batch_quality_score < 75:
                self.required_fixes.append(f"Batch quality score {self.batch_quality_score} below minimum 75")
            if not self.domain_distribution_check:
                self.required_fixes.append("Domain distribution does not meet requirements")
            if not self.difficulty_balance_check:
                self.required_fixes.append("Difficulty balance needs adjustment")
            if not self.duplicate_check:
                self.required_fixes.append("Duplicate content detected and must be resolved")
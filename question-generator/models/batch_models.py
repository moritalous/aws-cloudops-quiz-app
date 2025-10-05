"""
Pydantic models for AI-driven batch management and progress tracking.

These models define the structure for intelligent batch planning, database
state analysis, and progress reporting throughout the question generation process.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Literal
from datetime import datetime


class DatabaseState(BaseModel):
    """Current state of the question database."""
    
    total_questions: int = Field(
        description="Current total number of questions in database",
        ge=0,
        le=200
    )
    existing_questions: int = Field(
        description="Number of existing questions (should be 11 initially)",
        ge=0
    )
    generated_questions: int = Field(
        description="Number of newly generated questions",
        ge=0
    )
    domain_distribution: Dict[str, int] = Field(
        description="Current distribution of questions by domain",
        default_factory=dict
    )
    domain_targets: Dict[str, int] = Field(
        description="Target distribution of questions by domain",
        default_factory=lambda: {
            "monitoring": 44,
            "reliability": 44, 
            "deployment": 44,
            "security": 32,
            "networking": 36
        }
    )
    domain_remaining: Dict[str, int] = Field(
        description="Remaining questions needed per domain",
        default_factory=dict
    )
    difficulty_distribution: Dict[str, int] = Field(
        description="Current distribution by difficulty level",
        default_factory=dict
    )
    difficulty_targets: Dict[str, int] = Field(
        description="Target distribution by difficulty level",
        default_factory=lambda: {
            "easy": 60,    # 30%
            "medium": 100, # 50%
            "hard": 40     # 20%
        }
    )
    difficulty_remaining: Dict[str, int] = Field(
        description="Remaining questions needed per difficulty",
        default_factory=dict
    )
    question_type_distribution: Dict[str, int] = Field(
        description="Current distribution by question type",
        default_factory=dict
    )
    question_type_targets: Dict[str, int] = Field(
        description="Target distribution by question type",
        default_factory=lambda: {
            "single": 160,   # 80%
            "multiple": 40   # 20%
        }
    )
    covered_topics: List[str] = Field(
        description="List of topics already covered",
        default_factory=list
    )
    covered_services: List[str] = Field(
        description="List of AWS services already covered",
        default_factory=list
    )
    last_updated: str = Field(
        description="Timestamp of last database update",
        default_factory=lambda: datetime.now().isoformat()
    )
    completion_percentage: float = Field(
        description="Overall completion percentage (0-100)",
        ge=0,
        le=100,
        default=0.0
    )
    
    def model_post_init(self, __context) -> None:
        """Calculate remaining targets and completion percentage."""
        # Calculate domain remaining
        for domain, target in self.domain_targets.items():
            current = self.domain_distribution.get(domain, 0)
            self.domain_remaining[domain] = max(0, target - current)
        
        # Calculate difficulty remaining
        for difficulty, target in self.difficulty_targets.items():
            current = self.difficulty_distribution.get(difficulty, 0)
            self.difficulty_remaining[difficulty] = max(0, target - current)
        
        # Calculate completion percentage
        self.completion_percentage = (self.total_questions / 200.0) * 100.0


class BatchPlan(BaseModel):
    """Intelligent plan for the next batch of questions to generate."""
    
    batch_number: int = Field(
        description="Batch number (1-19)",
        ge=1,
        le=19
    )
    target_domain: str = Field(
        description="Primary target domain for this batch"
    )
    secondary_domains: List[str] = Field(
        description="Secondary domains to include if needed",
        default_factory=list
    )
    target_difficulties: List[str] = Field(
        description="Target difficulty levels for this batch"
    )
    difficulty_distribution: Dict[str, int] = Field(
        description="Specific difficulty distribution for this batch",
        default_factory=dict
    )
    target_question_types: Dict[str, int] = Field(
        description="Distribution of single vs multiple choice",
        default_factory=lambda: {"single": 8, "multiple": 2}
    )
    priority_topics: List[str] = Field(
        description="High-priority topics to cover in this batch",
        default_factory=list
    )
    priority_services: List[str] = Field(
        description="AWS services to prioritize in this batch",
        default_factory=list
    )
    avoid_topics: List[str] = Field(
        description="Topics to avoid due to recent coverage",
        default_factory=list
    )
    avoid_services: List[str] = Field(
        description="Services to avoid due to recent coverage",
        default_factory=list
    )
    research_queries: List[str] = Field(
        description="Specific AWS docs search queries for this batch",
        default_factory=list
    )
    complexity_focus: Literal['conceptual', 'practical', 'troubleshooting', 'best-practices'] = Field(
        description="Primary complexity focus for this batch"
    )
    scenario_requirements: Optional[str] = Field(
        description="Specific scenario requirements for this batch",
        default=None
    )
    estimated_completion_time: int = Field(
        description="Estimated completion time in minutes",
        ge=10,
        le=120,
        default=45
    )
    strategic_notes: List[str] = Field(
        description="Strategic notes for question generation",
        default_factory=list
    )
    quality_requirements: Dict[str, any] = Field(
        description="Specific quality requirements for this batch",
        default_factory=lambda: {
            "min_technical_accuracy": 8,
            "min_clarity_score": 7,
            "min_explanation_score": 8,
            "min_japanese_quality": 8,
            "require_official_docs": True,
            "max_similar_topics": 2
        }
    )
    created_at: str = Field(
        description="Plan creation timestamp",
        default_factory=lambda: datetime.now().isoformat()
    )
    
    @validator('target_difficulties')
    def validate_difficulties(cls, v):
        """Ensure valid difficulty levels."""
        valid_difficulties = {'easy', 'medium', 'hard'}
        for difficulty in v:
            if difficulty not in valid_difficulties:
                raise ValueError(f'Invalid difficulty: {difficulty}')
        return v
    
    @validator('difficulty_distribution')
    def validate_difficulty_sum(cls, v):
        """Ensure difficulty distribution sums to 10."""
        if sum(v.values()) != 10:
            raise ValueError('Difficulty distribution must sum to 10 questions')
        return v


class ProgressReport(BaseModel):
    """Comprehensive progress report for the question generation process."""
    
    current_progress: float = Field(
        description="Overall progress percentage (0-100)",
        ge=0,
        le=100
    )
    questions_completed: int = Field(
        description="Total questions completed so far",
        ge=0,
        le=200
    )
    questions_remaining: int = Field(
        description="Questions still needed",
        ge=0,
        le=200
    )
    batches_completed: int = Field(
        description="Number of batches completed",
        ge=0,
        le=19
    )
    remaining_batches: int = Field(
        description="Number of batches remaining",
        ge=0,
        le=19
    )
    domain_progress: Dict[str, float] = Field(
        description="Progress percentage by domain",
        default_factory=dict
    )
    difficulty_progress: Dict[str, float] = Field(
        description="Progress percentage by difficulty level",
        default_factory=dict
    )
    quality_metrics: Dict[str, float] = Field(
        description="Quality metrics across completed questions",
        default_factory=dict
    )
    performance_metrics: Dict[str, any] = Field(
        description="Performance and efficiency metrics",
        default_factory=dict
    )
    estimated_total_time: int = Field(
        description="Estimated total completion time in minutes",
        ge=0
    )
    estimated_remaining_time: int = Field(
        description="Estimated remaining time in minutes",
        ge=0
    )
    current_velocity: float = Field(
        description="Questions per hour completion rate",
        ge=0,
        default=0.0
    )
    bottlenecks_identified: List[str] = Field(
        description="Identified bottlenecks or issues",
        default_factory=list
    )
    recommendations: List[str] = Field(
        description="Recommendations for optimization",
        default_factory=list
    )
    next_batch_preview: Optional[str] = Field(
        description="Preview of next batch focus",
        default=None
    )
    milestone_status: Dict[str, bool] = Field(
        description="Status of key milestones",
        default_factory=lambda: {
            "25_percent_complete": False,
            "50_percent_complete": False,
            "75_percent_complete": False,
            "domain_balance_achieved": False,
            "quality_targets_met": False
        }
    )
    risk_assessment: Dict[str, str] = Field(
        description="Risk assessment for completion",
        default_factory=lambda: {
            "schedule_risk": "low",
            "quality_risk": "low", 
            "resource_risk": "low",
            "technical_risk": "low"
        }
    )
    generated_at: str = Field(
        description="Report generation timestamp",
        default_factory=lambda: datetime.now().isoformat()
    )
    
    def model_post_init(self, __context) -> None:
        """Calculate derived metrics and update milestone status."""
        # Update milestone status
        if self.current_progress >= 25:
            self.milestone_status["25_percent_complete"] = True
        if self.current_progress >= 50:
            self.milestone_status["50_percent_complete"] = True
        if self.current_progress >= 75:
            self.milestone_status["75_percent_complete"] = True
        
        # Calculate velocity if we have performance data
        if "total_time_spent" in self.performance_metrics and self.performance_metrics["total_time_spent"] > 0:
            hours_spent = self.performance_metrics["total_time_spent"] / 60.0
            self.current_velocity = self.questions_completed / hours_spent if hours_spent > 0 else 0.0
        
        # Update remaining time estimate based on velocity
        if self.current_velocity > 0:
            self.estimated_remaining_time = int((self.questions_remaining / self.current_velocity) * 60)
        
        # Assess risks based on progress and metrics
        if self.current_progress < 10 and self.batches_completed >= 3:
            self.risk_assessment["schedule_risk"] = "high"
        elif self.current_progress < 25 and self.batches_completed >= 6:
            self.risk_assessment["schedule_risk"] = "medium"
        
        if "average_quality_score" in self.quality_metrics and self.quality_metrics["average_quality_score"] < 75:
            self.risk_assessment["quality_risk"] = "high"
        elif "average_quality_score" in self.quality_metrics and self.quality_metrics["average_quality_score"] < 85:
            self.risk_assessment["quality_risk"] = "medium"
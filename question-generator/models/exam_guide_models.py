"""
Pydantic models for AWS CloudOps exam guide analysis.

These models define the structure for AI-driven analysis of the AWS Certified 
CloudOps Engineer - Associate exam guide, enabling structured extraction of 
domains, tasks, skills, and requirements.
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class Skill(BaseModel):
    """Individual skill detailed information within a task."""
    
    skill_id: str = Field(
        description="Unique identifier for the skill (e.g., 'monitoring-1.1')"
    )
    description: str = Field(
        description="Detailed description of the skill requirement"
    )
    aws_services: List[str] = Field(
        description="List of related AWS services for this skill",
        default_factory=list
    )
    difficulty: Literal['easy', 'medium', 'hard'] = Field(
        description="Estimated difficulty level for this skill"
    )
    keywords: List[str] = Field(
        description="Key technical terms and concepts for this skill",
        default_factory=list
    )


class Task(BaseModel):
    """Task information within a domain."""
    
    task_id: str = Field(
        description="Unique identifier for the task (e.g., 'domain1-task1')"
    )
    description: str = Field(
        description="Detailed description of the task"
    )
    weight_percentage: Optional[float] = Field(
        description="Percentage weight of this task within the domain",
        default=None,
        ge=0,
        le=100
    )
    skills: List[Skill] = Field(
        description="List of skills included in this task"
    )
    estimated_questions: int = Field(
        description="Estimated number of questions for this task",
        ge=0
    )


class DomainAnalysis(BaseModel):
    """Complete analysis result for a single exam domain."""
    
    domain: Literal[
        'monitoring', 
        'reliability', 
        'deployment', 
        'security', 
        'networking'
    ] = Field(
        description="Domain identifier"
    )
    domain_name: str = Field(
        description="Full domain name from the exam guide"
    )
    weight: float = Field(
        description="Exam weight percentage for this domain",
        ge=0,
        le=100
    )
    target_questions: int = Field(
        description="Target number of questions for this domain (out of 200)",
        ge=0,
        le=200
    )
    tasks: List[Task] = Field(
        description="List of tasks included in this domain"
    )
    key_services: List[str] = Field(
        description="Primary AWS services covered in this domain",
        default_factory=list
    )
    complexity_level: Literal['beginner', 'intermediate', 'advanced'] = Field(
        description="Overall complexity level of this domain"
    )


class ExamGuideAnalysis(BaseModel):
    """Complete analysis result of the AWS CloudOps exam guide."""
    
    total_questions: int = Field(
        description="Total target questions to generate",
        default=200
    )
    exam_code: str = Field(
        description="AWS exam code (e.g., 'SOA-C03')",
        default="SOA-C03"
    )
    exam_title: str = Field(
        description="Full exam title",
        default="AWS Certified CloudOps Engineer - Associate"
    )
    domains: List[DomainAnalysis] = Field(
        description="Analysis results for all exam domains"
    )
    exam_info: dict = Field(
        description="Additional exam metadata and information",
        default_factory=dict
    )
    analysis_metadata: dict = Field(
        description="Metadata about the analysis process",
        default_factory=lambda: {
            "analysis_version": "1.0",
            "total_skills_identified": 0,
            "total_tasks_identified": 0,
            "coverage_completeness": 0.0
        }
    )
    
    def model_post_init(self, __context) -> None:
        """Post-initialization to calculate metadata."""
        total_skills = sum(len(task.skills) for domain in self.domains for task in domain.tasks)
        total_tasks = sum(len(domain.tasks) for domain in self.domains)
        
        self.analysis_metadata.update({
            "total_skills_identified": total_skills,
            "total_tasks_identified": total_tasks,
            "coverage_completeness": min(100.0, (total_skills / 50.0) * 100)  # Assuming ~50 skills target
        })
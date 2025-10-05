"""
Pydantic models for AWS CloudOps question generation.

These models define the structure for AI-generated exam questions, including
question content, metadata, learning resources, and batch organization.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Union, Literal, Optional
from datetime import datetime


class LearningResource(BaseModel):
    """Learning resource information for question explanations."""
    
    title: str = Field(
        description="Title of the learning resource"
    )
    url: str = Field(
        description="URL of the learning resource"
    )
    type: Literal[
        'documentation', 
        'whitepaper', 
        'tutorial', 
        'best-practice',
        'faq',
        'video'
    ] = Field(
        description="Type of learning resource"
    )
    description: Optional[str] = Field(
        description="Brief description of the resource content",
        default=None
    )
    
    @validator('url')
    def validate_url(cls, v):
        """Ensure URL is properly formatted."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class Question(BaseModel):
    """Complete AWS CloudOps exam question structure."""
    
    id: str = Field(
        description="Question ID in format 'q001' to 'q200'"
    )
    domain: Literal[
        'monitoring', 
        'reliability', 
        'deployment', 
        'security', 
        'networking'
    ] = Field(
        description="Question domain"
    )
    difficulty: Literal['easy', 'medium', 'hard'] = Field(
        description="Question difficulty level"
    )
    type: Literal['single', 'multiple'] = Field(
        description="Question type - single or multiple choice"
    )
    question: str = Field(
        description="Question text in Japanese",
        min_length=50
    )
    options: List[str] = Field(
        description="List of answer options (A, B, C, D, E, F)",
        min_items=4,
        max_items=6
    )
    correct_answer: Union[str, List[str]] = Field(
        description="Correct answer(s) - single: 'A', multiple: ['A', 'C']"
    )
    explanation: str = Field(
        description="Detailed explanation in Japanese",
        min_length=100
    )
    learning_resources: List[LearningResource] = Field(
        description="List of learning resources",
        min_items=1
    )
    related_services: List[str] = Field(
        description="List of related AWS services mentioned in question/answer",
        default_factory=list
    )
    tags: List[str] = Field(
        description="Classification tags for the question",
        default_factory=list
    )
    task_reference: Optional[str] = Field(
        description="Reference to exam guide task",
        default=None
    )
    skill_reference: Optional[str] = Field(
        description="Reference to exam guide skill",
        default=None
    )
    scenario: Optional[str] = Field(
        description="Scenario context for scenario-based questions",
        default=None
    )
    created_at: str = Field(
        description="Question creation timestamp",
        default_factory=lambda: datetime.now().isoformat()
    )
    
    @validator('id')
    def validate_id_format(cls, v):
        """Validate question ID format."""
        if not v.startswith('q') or not v[1:].isdigit():
            raise ValueError('Question ID must be in format q001, q002, etc.')
        question_num = int(v[1:])
        if not 1 <= question_num <= 200:
            raise ValueError('Question number must be between 1 and 200')
        return v
    
    @validator('correct_answer')
    def validate_correct_answer(cls, v, values):
        """Validate correct answer format based on question type."""
        question_type = values.get('type')
        options = values.get('options', [])
        
        if question_type == 'single':
            if not isinstance(v, str) or len(v) != 1:
                raise ValueError('Single choice questions must have exactly one correct answer')
            if v not in ['A', 'B', 'C', 'D', 'E', 'F'][:len(options)]:
                raise ValueError(f'Correct answer must be one of the available options')
        elif question_type == 'multiple':
            if not isinstance(v, list) or len(v) < 2:
                raise ValueError('Multiple choice questions must have at least 2 correct answers')
            for answer in v:
                if answer not in ['A', 'B', 'C', 'D', 'E', 'F'][:len(options)]:
                    raise ValueError(f'All correct answers must be valid options')
        
        return v
    
    @validator('options')
    def validate_options_format(cls, v):
        """Validate options are properly formatted."""
        if len(v) < 4:
            raise ValueError('Questions must have at least 4 options')
        
        # Check that options don't start with A), B), etc. - they should be plain text
        for i, option in enumerate(v):
            if option.strip().startswith(f'{chr(65+i)})'):
                raise ValueError('Options should not include letter prefixes (A), B), etc.)')
        
        return v


class QuestionBatch(BaseModel):
    """Batch of 10 questions for processing."""
    
    batch_number: int = Field(
        description="Batch number (1-19 for 190 new questions)",
        ge=1,
        le=19
    )
    questions: List[Question] = Field(
        description="Exactly 10 questions in this batch",
        min_items=10,
        max_items=10
    )
    batch_metadata: dict = Field(
        description="Metadata about this batch",
        default_factory=lambda: {
            "created_at": datetime.now().isoformat(),
            "domain_distribution": {},
            "difficulty_distribution": {},
            "question_types": {},
            "total_learning_resources": 0,
            "aws_services_covered": []
        }
    )
    target_domain: Optional[str] = Field(
        description="Primary target domain for this batch",
        default=None
    )
    generation_notes: List[str] = Field(
        description="Notes about the generation process for this batch",
        default_factory=list
    )
    
    def model_post_init(self, __context) -> None:
        """Post-initialization to calculate batch metadata."""
        domain_count = {}
        difficulty_count = {}
        type_count = {}
        all_services = set()
        total_resources = 0
        
        for question in self.questions:
            # Count domains
            domain_count[question.domain] = domain_count.get(question.domain, 0) + 1
            
            # Count difficulties
            difficulty_count[question.difficulty] = difficulty_count.get(question.difficulty, 0) + 1
            
            # Count question types
            type_count[question.type] = type_count.get(question.type, 0) + 1
            
            # Collect AWS services
            all_services.update(question.related_services)
            
            # Count learning resources
            total_resources += len(question.learning_resources)
        
        self.batch_metadata.update({
            "domain_distribution": domain_count,
            "difficulty_distribution": difficulty_count,
            "question_types": type_count,
            "total_learning_resources": total_resources,
            "aws_services_covered": sorted(list(all_services))
        })
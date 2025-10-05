"""
Pydantic models for database integration and final question database structure.

These models define the structure for integrating generated questions into
the final questions.json database and managing the complete question collection.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from .question_models import Question


class IntegrationResult(BaseModel):
    """Result of integrating a batch of questions into the database."""
    
    success: bool = Field(
        description="Whether the integration was successful"
    )
    batch_number: int = Field(
        description="Batch number that was integrated",
        ge=1,
        le=19
    )
    questions_added: int = Field(
        description="Number of questions successfully added",
        ge=0,
        le=10
    )
    new_total_questions: int = Field(
        description="Total questions after integration",
        ge=0,
        le=200
    )
    added_question_ids: List[str] = Field(
        description="List of question IDs that were added",
        default_factory=list
    )
    updated_metadata: Dict[str, Any] = Field(
        description="Updated database metadata after integration",
        default_factory=dict
    )
    validation_passed: bool = Field(
        description="Whether post-integration validation passed"
    )
    schema_compliance: bool = Field(
        description="Whether the result complies with existing schema",
        default=True
    )
    id_sequence_valid: bool = Field(
        description="Whether question ID sequence is valid",
        default=True
    )
    backup_created: bool = Field(
        description="Whether a backup was created before integration"
    )
    backup_path: Optional[str] = Field(
        description="Path to the backup file if created",
        default=None
    )
    integration_time_seconds: float = Field(
        description="Time taken for integration in seconds",
        ge=0,
        default=0.0
    )
    issues: List[str] = Field(
        description="List of issues encountered during integration",
        default_factory=list
    )
    warnings: List[str] = Field(
        description="List of warnings generated during integration",
        default_factory=list
    )
    rollback_available: bool = Field(
        description="Whether rollback is possible",
        default=False
    )
    rollback_instructions: Optional[str] = Field(
        description="Instructions for rollback if needed",
        default=None
    )
    integrated_at: str = Field(
        description="Integration timestamp",
        default_factory=lambda: datetime.now().isoformat()
    )
    
    @validator('added_question_ids')
    def validate_question_ids(cls, v, values):
        """Validate that added question IDs match the count."""
        questions_added = values.get('questions_added', 0)
        if len(v) != questions_added:
            raise ValueError('Number of question IDs must match questions_added count')
        return v


class QuestionDatabase(BaseModel):
    """Complete structure of the final questions.json database."""
    
    version: str = Field(
        description="Database version identifier",
        default="2.0.0"
    )
    generated_at: str = Field(
        description="Database generation timestamp",
        default_factory=lambda: datetime.now().isoformat()
    )
    generation_method: str = Field(
        description="Method used to generate questions",
        default="AI-Strands-Agents-Bedrock"
    )
    exam_info: Dict[str, Any] = Field(
        description="Information about the target exam",
        default_factory=lambda: {
            "exam_code": "SOA-C03",
            "exam_title": "AWS Certified CloudOps Engineer - Associate",
            "exam_domains": [
                "Monitoring, Logging, and Remediation",
                "Reliability and Business Continuity", 
                "Deployment, Provisioning, and Automation",
                "Security and Compliance",
                "Networking and Content Delivery"
            ]
        }
    )
    total_questions: int = Field(
        description="Total number of questions in database",
        default=200
    )
    original_questions: int = Field(
        description="Number of original questions preserved",
        default=11
    )
    generated_questions: int = Field(
        description="Number of AI-generated questions",
        default=189
    )
    domains: Dict[str, int] = Field(
        description="Distribution of questions by domain",
        default_factory=lambda: {
            "monitoring": 44,    # 22%
            "reliability": 44,   # 22%
            "deployment": 44,    # 22%
            "security": 32,      # 16%
            "networking": 36     # 18%
        }
    )
    difficulty: Dict[str, int] = Field(
        description="Distribution of questions by difficulty",
        default_factory=lambda: {
            "easy": 60,      # 30%
            "medium": 100,   # 50%
            "hard": 40       # 20%
        }
    )
    question_types: Dict[str, int] = Field(
        description="Distribution of question types",
        default_factory=lambda: {
            "single": 160,   # 80%
            "multiple": 40   # 20%
        }
    )
    aws_services_covered: List[str] = Field(
        description="List of all AWS services covered in questions",
        default_factory=list
    )
    topics_covered: List[str] = Field(
        description="List of all topics covered in questions",
        default_factory=list
    )
    quality_metrics: Dict[str, float] = Field(
        description="Overall quality metrics for the database",
        default_factory=lambda: {
            "average_technical_accuracy": 0.0,
            "average_clarity_score": 0.0,
            "average_explanation_score": 0.0,
            "average_japanese_quality": 0.0,
            "resource_validity_rate": 0.0,
            "overall_quality_score": 0.0
        }
    )
    generation_statistics: Dict[str, Any] = Field(
        description="Statistics about the generation process",
        default_factory=lambda: {
            "total_batches_processed": 0,
            "total_generation_time_minutes": 0,
            "average_batch_time_minutes": 0,
            "questions_regenerated": 0,
            "validation_failures": 0,
            "ai_model_used": "gpt-oss-120b",
            "mcp_tools_used": ["aws-docs"],
            "strands_agents_version": "latest"
        }
    )
    compatibility: Dict[str, Any] = Field(
        description="Compatibility information with existing application",
        default_factory=lambda: {
            "schema_version": "1.0",
            "backward_compatible": True,
            "required_app_version": ">=1.0.0",
            "breaking_changes": []
        }
    )
    questions: List[Question] = Field(
        description="Complete list of all questions",
        min_items=200,
        max_items=200
    )
    
    @validator('questions')
    def validate_question_count_and_ids(cls, v):
        """Validate question count and ID sequence."""
        if len(v) != 200:
            raise ValueError('Database must contain exactly 200 questions')
        
        # Check ID sequence
        expected_ids = [f'q{i:03d}' for i in range(1, 201)]
        actual_ids = [q.id for q in v]
        
        if actual_ids != expected_ids:
            raise ValueError('Question IDs must be sequential from q001 to q200')
        
        return v
    
    def model_post_init(self, __context) -> None:
        """Calculate derived statistics and validate distributions."""
        if not self.questions:
            return
        
        # Calculate actual distributions
        domain_count = {}
        difficulty_count = {}
        type_count = {}
        all_services = set()
        all_topics = set()
        
        # Quality metrics accumulation
        total_questions = len(self.questions)
        quality_scores = {
            'technical_accuracy': 0,
            'clarity': 0,
            'explanation': 0,
            'japanese': 0,
            'resource_validity': 0
        }
        
        for question in self.questions:
            # Count distributions
            domain_count[question.domain] = domain_count.get(question.domain, 0) + 1
            difficulty_count[question.difficulty] = difficulty_count.get(question.difficulty, 0) + 1
            type_count[question.type] = type_count.get(question.type, 0) + 1
            
            # Collect services and topics
            all_services.update(question.related_services)
            all_topics.update(question.tags)
            
            # Note: In a real implementation, we would need access to validation scores
            # For now, we'll set placeholder values
        
        # Update calculated fields
        self.aws_services_covered = sorted(list(all_services))
        self.topics_covered = sorted(list(all_topics))
        
        # Verify distributions match targets (within tolerance)
        tolerance = 2  # Allow ±2 questions difference
        
        for domain, expected in self.domains.items():
            actual = domain_count.get(domain, 0)
            if abs(actual - expected) > tolerance:
                raise ValueError(f'Domain {domain}: expected ~{expected}, got {actual}')
        
        for difficulty, expected in self.difficulty.items():
            actual = difficulty_count.get(difficulty, 0)
            if abs(actual - expected) > tolerance:
                raise ValueError(f'Difficulty {difficulty}: expected ~{expected}, got {actual}')
        
        for qtype, expected in self.question_types.items():
            actual = type_count.get(qtype, 0)
            if abs(actual - expected) > tolerance:
                raise ValueError(f'Question type {qtype}: expected ~{expected}, got {actual}')


class DatabaseBackup(BaseModel):
    """Backup information for the question database."""
    
    backup_id: str = Field(
        description="Unique backup identifier"
    )
    original_file_path: str = Field(
        description="Path to the original questions.json file"
    )
    backup_file_path: str = Field(
        description="Path to the backup file"
    )
    backup_size_bytes: int = Field(
        description="Size of the backup file in bytes",
        ge=0
    )
    questions_count: int = Field(
        description="Number of questions in the backup",
        ge=0
    )
    created_at: str = Field(
        description="Backup creation timestamp",
        default_factory=lambda: datetime.now().isoformat()
    )
    created_before_batch: Optional[int] = Field(
        description="Batch number this backup was created before",
        default=None
    )
    checksum: Optional[str] = Field(
        description="Checksum of the backup file for integrity verification",
        default=None
    )
    restoration_tested: bool = Field(
        description="Whether restoration from this backup has been tested",
        default=False
    )
    retention_until: Optional[str] = Field(
        description="Backup retention expiry date",
        default=None
    )
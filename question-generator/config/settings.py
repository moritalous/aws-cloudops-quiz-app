"""
Global settings and configuration management for the question generation system.

This module provides centralized settings management with support for
environment variables, configuration files, and runtime overrides.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path
import json
import os
from .agent_config import AgentConfig


class Settings(BaseSettings):
    """Global application settings."""
    
    # Application metadata
    app_name: str = Field(
        description="Application name",
        default="AWS CloudOps Question Generator"
    )
    
    app_version: str = Field(
        description="Application version",
        default="1.0.0"
    )
    
    # Environment settings
    environment: str = Field(
        description="Runtime environment",
        default="development"
    )
    
    # Configuration file paths
    config_file: Optional[Path] = Field(
        description="Path to configuration file",
        default=None
    )
    
    # Agent configuration
    agent_config: AgentConfig = Field(
        description="Agent configuration",
        default_factory=AgentConfig
    )
    
    # Question generation settings
    target_questions: int = Field(
        description="Target number of questions to generate",
        default=200,
        ge=1,
        le=1000
    )
    
    existing_questions: int = Field(
        description="Number of existing questions to preserve",
        default=11,
        ge=0
    )
    
    questions_file_path: Path = Field(
        description="Path to the questions.json file",
        default_factory=lambda: Path("../vite-project/app/data/questions.json")
    )
    
    exam_guide_path: Path = Field(
        description="Path to the exam guide file",
        default_factory=lambda: Path("../Exam-Guide/AWS-Certified-CloudOps-Engineer-Associate_Exam-Guide.md")
    )
    
    # Processing settings
    enable_parallel_processing: bool = Field(
        description="Enable parallel batch processing",
        default=True
    )
    
    max_parallel_batches: int = Field(
        description="Maximum number of parallel batches",
        default=2,
        ge=1,
        le=5
    )
    
    enable_auto_backup: bool = Field(
        description="Enable automatic backups",
        default=True
    )
    
    backup_retention_days: int = Field(
        description="Number of days to retain backups",
        default=30,
        ge=1,
        le=365
    )
    
    # Quality control settings
    enable_quality_validation: bool = Field(
        description="Enable quality validation",
        default=True
    )
    
    enable_duplicate_detection: bool = Field(
        description="Enable duplicate detection",
        default=True
    )
    
    enable_japanese_validation: bool = Field(
        description="Enable Japanese language quality validation",
        default=True
    )
    
    # Progress tracking
    enable_progress_reporting: bool = Field(
        description="Enable progress reporting",
        default=True
    )
    
    progress_report_interval: int = Field(
        description="Progress report interval in batches",
        default=1,
        ge=1,
        le=10
    )
    
    # Error handling
    max_retry_attempts: int = Field(
        description="Maximum retry attempts for failed operations",
        default=3,
        ge=1,
        le=10
    )
    
    enable_graceful_degradation: bool = Field(
        description="Enable graceful degradation on errors",
        default=True
    )
    
    # Development and testing
    dry_run_mode: bool = Field(
        description="Enable dry run mode (no actual file modifications)",
        default=False
    )
    
    enable_mock_mode: bool = Field(
        description="Enable mock mode for testing",
        default=False
    )
    
    class Config:
        env_prefix = "QUESTION_GEN_"
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def load_from_file(self, config_path: Path) -> None:
        """Load configuration from a JSON file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Update settings with file data
        for key, value in config_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def save_to_file(self, config_path: Path) -> None:
        """Save current configuration to a JSON file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.dict(), f, indent=2, ensure_ascii=False, default=str)
    
    def validate_paths(self) -> None:
        """Validate that required paths exist."""
        if not self.exam_guide_path.exists():
            raise FileNotFoundError(f"Exam guide not found: {self.exam_guide_path}")
        
        # Create parent directory for questions file if it doesn't exist
        self.questions_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def get_calculated_questions(self) -> int:
        """Get the number of questions to generate (target - existing)."""
        return max(0, self.target_questions - self.existing_questions)
    
    def get_batch_count(self) -> int:
        """Get the number of batches needed."""
        questions_to_generate = self.get_calculated_questions()
        batch_size = self.agent_config.batch_size
        return (questions_to_generate + batch_size - 1) // batch_size  # Ceiling division


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance."""
    global _settings
    
    if _settings is None:
        # Try to load from environment first
        _settings = Settings()
        
        # Try to load from config file if specified
        config_file = os.getenv("QUESTION_GEN_CONFIG_FILE")
        if config_file:
            config_path = Path(config_file)
            if config_path.exists():
                _settings.load_from_file(config_path)
        
        # Load agent config from environment
        _settings.agent_config = AgentConfig.from_env()
        
        # Validate paths
        try:
            _settings.validate_paths()
        except FileNotFoundError as e:
            print(f"Warning: {e}")
    
    return _settings


def update_settings(**kwargs) -> Settings:
    """Update global settings with new values."""
    global _settings
    settings = get_settings()
    
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
        else:
            raise ValueError(f"Unknown setting: {key}")
    
    return settings


def reset_settings() -> None:
    """Reset global settings to None (will be reloaded on next access)."""
    global _settings
    _settings = None
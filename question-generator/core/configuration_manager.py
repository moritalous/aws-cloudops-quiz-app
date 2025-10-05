"""
Configuration Management System for AWS CloudOps Question Generation.

This module provides comprehensive configuration management for AI agents,
batch processing parameters, execution settings, and dynamic adjustments
during runtime.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging
from enum import Enum

# Pydantic imports
from pydantic import BaseModel, Field, validator

# Local imports
from config import AgentConfig, BedrockConfig, MCPConfig


class LogLevel(Enum):
    """Available logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ExecutionMode(Enum):
    """Execution modes for the question generation system."""
    FULL_AUTO = "full_auto"          # Complete automation
    SEMI_AUTO = "semi_auto"          # Manual approval at key points
    MANUAL = "manual"                # Manual control of each step
    DEBUG = "debug"                  # Debug mode with detailed logging
    RECOVERY = "recovery"            # Recovery from failed state


class BatchStrategy(Enum):
    """Batch processing strategies."""
    SEQUENTIAL = "sequential"        # Process batches one by one
    PARALLEL = "parallel"           # Process multiple batches in parallel
    ADAPTIVE = "adaptive"           # Adapt based on system resources
    PRIORITY = "priority"           # Process high-priority batches first


@dataclass
class DomainConfiguration:
    """Configuration for individual exam domains."""
    name: str
    target_questions: int
    weight_percentage: float
    priority: int = 1
    difficulty_distribution: Dict[str, float] = field(default_factory=lambda: {
        "easy": 0.3, "medium": 0.5, "hard": 0.2
    })
    question_types: Dict[str, float] = field(default_factory=lambda: {
        "single": 0.8, "multiple": 0.2
    })
    focus_topics: List[str] = field(default_factory=list)
    aws_services: List[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class BatchConfiguration:
    """Configuration for batch processing."""
    batch_size: int = 10
    total_batches: int = 19
    strategy: BatchStrategy = BatchStrategy.SEQUENTIAL
    max_parallel_batches: int = 3
    retry_attempts: int = 3
    retry_delay_seconds: float = 5.0
    timeout_minutes: int = 30
    validation_threshold: float = 7.0
    auto_recovery: bool = True
    checkpoint_frequency: int = 1  # Save state every N batches


@dataclass
class AgentConfiguration:
    """Configuration for individual AI agents."""
    enabled: bool = True
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout_seconds: int = 120
    retry_attempts: int = 3
    custom_system_prompt: Optional[str] = None
    model_overrides: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityConfiguration:
    """Configuration for quality validation."""
    min_technical_accuracy: float = 8.0
    min_clarity_score: float = 7.5
    min_explanation_score: float = 8.0
    min_japanese_quality: float = 7.0
    enable_duplicate_detection: bool = True
    similarity_threshold: float = 0.85
    require_learning_resources: bool = True
    validate_aws_services: bool = True


@dataclass
class DatabaseConfiguration:
    """Configuration for database operations."""
    database_path: str = "output/questions.json"
    backup_directory: str = "backups"
    auto_backup: bool = True
    backup_retention_days: int = 30
    validate_schema: bool = True
    enable_rollback: bool = True
    compression_enabled: bool = False


@dataclass
class MonitoringConfiguration:
    """Configuration for monitoring and logging."""
    log_level: LogLevel = LogLevel.INFO
    log_file: str = "logs/question_generation.log"
    enable_real_time_monitoring: bool = True
    progress_update_interval: int = 30  # seconds
    enable_metrics_collection: bool = True
    metrics_file: str = "logs/metrics.json"
    enable_performance_profiling: bool = False


@dataclass
class ExecutionConfiguration:
    """Main execution configuration."""
    mode: ExecutionMode = ExecutionMode.FULL_AUTO
    enable_pause_resume: bool = True
    state_file: str = "execution_state.json"
    max_execution_time_hours: int = 24
    resource_limits: Dict[str, Any] = field(default_factory=lambda: {
        "max_memory_mb": 4096,
        "max_cpu_percent": 80,
        "max_concurrent_agents": 5
    })
    notification_settings: Dict[str, Any] = field(default_factory=lambda: {
        "enable_notifications": False,
        "email_on_completion": False,
        "email_on_error": True,
        "webhook_url": None
    })


class ConfigurationManager:
    """
    Comprehensive configuration management system.
    
    This class handles loading, validation, updating, and persistence of
    all configuration settings for the question generation system.
    """
    
    def __init__(self, config_file: str = "config/execution_config.yaml"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the main configuration file
        """
        self.config_file = Path(config_file)
        self.config_dir = self.config_file.parent
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize configurations
        self.domains: Dict[str, DomainConfiguration] = {}
        self.batch_config = BatchConfiguration()
        self.agents: Dict[str, AgentConfiguration] = {}
        self.quality_config = QualityConfiguration()
        self.database_config = DatabaseConfiguration()
        self.monitoring_config = MonitoringConfiguration()
        self.execution_config = ExecutionConfiguration()
        
        # Load configuration
        self.load_configuration()
        
        self.logger.info("ConfigurationManager initialized")
    
    def load_configuration(self) -> None:
        """Load configuration from file or create default configuration."""
        try:
            if self.config_file.exists():
                self.logger.info(f"Loading configuration from {self.config_file}")
                
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    if self.config_file.suffix.lower() == '.yaml':
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                self._parse_configuration(config_data)
                self.logger.info("Configuration loaded successfully")
            else:
                self.logger.info("No configuration file found, creating default configuration")
                self._create_default_configuration()
                self.save_configuration()
        
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self.logger.info("Using default configuration")
            self._create_default_configuration()
    
    def _create_default_configuration(self) -> None:
        """Create default configuration settings."""
        # Default domain configurations based on SOA-C03 exam guide
        self.domains = {
            "monitoring": DomainConfiguration(
                name="Monitoring, Logging, and Remediation",
                target_questions=44,  # 22% of 200
                weight_percentage=22.0,
                priority=1,
                focus_topics=["CloudWatch", "CloudTrail", "AWS Config", "Systems Manager"],
                aws_services=["CloudWatch", "CloudTrail", "Config", "Systems Manager", "X-Ray"]
            ),
            "reliability": DomainConfiguration(
                name="Reliability and Business Continuity",
                target_questions=44,  # 22% of 200
                weight_percentage=22.0,
                priority=1,
                focus_topics=["Backup", "Disaster Recovery", "High Availability", "Auto Scaling"],
                aws_services=["Backup", "RDS", "EC2", "ELB", "Auto Scaling", "Route 53"]
            ),
            "deployment": DomainConfiguration(
                name="Deployment, Provisioning, and Automation",
                target_questions=44,  # 22% of 200
                weight_percentage=22.0,
                priority=1,
                focus_topics=["CloudFormation", "CodeDeploy", "Systems Manager", "Elastic Beanstalk"],
                aws_services=["CloudFormation", "CodeDeploy", "CodePipeline", "Elastic Beanstalk", "Systems Manager"]
            ),
            "security": DomainConfiguration(
                name="Security and Compliance",
                target_questions=32,  # 16% of 200
                weight_percentage=16.0,
                priority=2,
                focus_topics=["IAM", "Security Groups", "KMS", "CloudTrail", "Config"],
                aws_services=["IAM", "KMS", "CloudTrail", "Config", "Security Hub", "GuardDuty"]
            ),
            "networking": DomainConfiguration(
                name="Networking and Content Delivery",
                target_questions=36,  # 18% of 200
                weight_percentage=18.0,
                priority=2,
                focus_topics=["VPC", "CloudFront", "Route 53", "ELB", "Direct Connect"],
                aws_services=["VPC", "CloudFront", "Route 53", "ELB", "Direct Connect", "API Gateway"]
            )
        }
        
        # Default agent configurations
        self.agents = {
            "exam_analyzer": AgentConfiguration(
                temperature=0.3,  # Lower temperature for analysis
                max_tokens=3000,
                timeout_seconds=180
            ),
            "batch_manager": AgentConfiguration(
                temperature=0.5,
                max_tokens=2000,
                timeout_seconds=120
            ),
            "aws_knowledge_agent": AgentConfiguration(
                temperature=0.4,
                max_tokens=4000,
                timeout_seconds=300  # Longer timeout for research
            ),
            "question_generator": AgentConfiguration(
                temperature=0.7,  # Higher temperature for creativity
                max_tokens=4000,
                timeout_seconds=240
            ),
            "quality_validator": AgentConfiguration(
                temperature=0.2,  # Very low temperature for validation
                max_tokens=3000,
                timeout_seconds=180
            ),
            "japanese_optimizer": AgentConfiguration(
                temperature=0.6,
                max_tokens=3000,
                timeout_seconds=150
            ),
            "database_integrator": AgentConfiguration(
                temperature=0.1,  # Minimal temperature for integration
                max_tokens=2000,
                timeout_seconds=120
            )
        }
    
    def _parse_configuration(self, config_data: Dict[str, Any]) -> None:
        """Parse configuration data from loaded file."""
        # Parse domain configurations
        if "domains" in config_data:
            self.domains = {}
            for domain_name, domain_data in config_data["domains"].items():
                self.domains[domain_name] = DomainConfiguration(**domain_data)
        
        # Parse batch configuration
        if "batch" in config_data:
            self.batch_config = BatchConfiguration(**config_data["batch"])
        
        # Parse agent configurations
        if "agents" in config_data:
            self.agents = {}
            for agent_name, agent_data in config_data["agents"].items():
                self.agents[agent_name] = AgentConfiguration(**agent_data)
        
        # Parse quality configuration
        if "quality" in config_data:
            self.quality_config = QualityConfiguration(**config_data["quality"])
        
        # Parse database configuration
        if "database" in config_data:
            self.database_config = DatabaseConfiguration(**config_data["database"])
        
        # Parse monitoring configuration
        if "monitoring" in config_data:
            monitoring_data = config_data["monitoring"].copy()
            if "log_level" in monitoring_data:
                monitoring_data["log_level"] = LogLevel(monitoring_data["log_level"])
            self.monitoring_config = MonitoringConfiguration(**monitoring_data)
        
        # Parse execution configuration
        if "execution" in config_data:
            execution_data = config_data["execution"].copy()
            if "mode" in execution_data:
                execution_data["mode"] = ExecutionMode(execution_data["mode"])
            self.execution_config = ExecutionConfiguration(**execution_data)
    
    def save_configuration(self) -> None:
        """Save current configuration to file."""
        try:
            config_data = {
                "domains": {
                    name: asdict(config) for name, config in self.domains.items()
                },
                "batch": asdict(self.batch_config),
                "agents": {
                    name: asdict(config) for name, config in self.agents.items()
                },
                "quality": asdict(self.quality_config),
                "database": asdict(self.database_config),
                "monitoring": {
                    **asdict(self.monitoring_config),
                    "log_level": self.monitoring_config.log_level.value
                },
                "execution": {
                    **asdict(self.execution_config),
                    "mode": self.execution_config.mode.value
                },
                "saved_at": datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                if self.config_file.suffix.lower() == '.yaml':
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Configuration saved to {self.config_file}")
        
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def get_domain_config(self, domain_name: str) -> Optional[DomainConfiguration]:
        """Get configuration for a specific domain."""
        return self.domains.get(domain_name)
    
    def update_domain_config(self, domain_name: str, **kwargs) -> None:
        """Update configuration for a specific domain."""
        if domain_name in self.domains:
            for key, value in kwargs.items():
                if hasattr(self.domains[domain_name], key):
                    setattr(self.domains[domain_name], key, value)
            self.logger.info(f"Updated domain configuration for {domain_name}")
        else:
            self.logger.warning(f"Domain {domain_name} not found in configuration")
    
    def get_agent_config(self, agent_name: str) -> Optional[AgentConfiguration]:
        """Get configuration for a specific agent."""
        return self.agents.get(agent_name)
    
    def update_agent_config(self, agent_name: str, **kwargs) -> None:
        """Update configuration for a specific agent."""
        if agent_name in self.agents:
            for key, value in kwargs.items():
                if hasattr(self.agents[agent_name], key):
                    setattr(self.agents[agent_name], key, value)
            self.logger.info(f"Updated agent configuration for {agent_name}")
        else:
            self.logger.warning(f"Agent {agent_name} not found in configuration")
    
    def adjust_batch_size(self, new_size: int) -> None:
        """Dynamically adjust batch size."""
        if 1 <= new_size <= 20:
            old_size = self.batch_config.batch_size
            self.batch_config.batch_size = new_size
            # Recalculate total batches
            total_questions = 189  # 200 - 11 existing
            self.batch_config.total_batches = (total_questions + new_size - 1) // new_size
            self.logger.info(f"Batch size adjusted from {old_size} to {new_size}")
            self.logger.info(f"Total batches recalculated to {self.batch_config.total_batches}")
        else:
            self.logger.warning(f"Invalid batch size: {new_size}. Must be between 1 and 20")
    
    def set_execution_mode(self, mode: ExecutionMode) -> None:
        """Set execution mode."""
        self.execution_config.mode = mode
        self.logger.info(f"Execution mode set to {mode.value}")
    
    def enable_debug_mode(self) -> None:
        """Enable debug mode with detailed logging."""
        self.execution_config.mode = ExecutionMode.DEBUG
        self.monitoring_config.log_level = LogLevel.DEBUG
        self.monitoring_config.enable_performance_profiling = True
        self.logger.info("Debug mode enabled")
    
    def adjust_quality_thresholds(self, **thresholds) -> None:
        """Adjust quality validation thresholds."""
        for threshold_name, value in thresholds.items():
            if hasattr(self.quality_config, threshold_name):
                setattr(self.quality_config, threshold_name, value)
                self.logger.info(f"Quality threshold {threshold_name} set to {value}")
    
    def get_runtime_parameters(self) -> Dict[str, Any]:
        """Get parameters for runtime execution."""
        return {
            "batch_size": self.batch_config.batch_size,
            "total_batches": self.batch_config.total_batches,
            "execution_mode": self.execution_config.mode.value,
            "log_level": self.monitoring_config.log_level.value,
            "quality_thresholds": {
                "technical_accuracy": self.quality_config.min_technical_accuracy,
                "clarity": self.quality_config.min_clarity_score,
                "explanation": self.quality_config.min_explanation_score,
                "japanese": self.quality_config.min_japanese_quality
            },
            "domain_distribution": {
                name: config.target_questions 
                for name, config in self.domains.items()
            },
            "agent_settings": {
                name: {
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    "timeout": config.timeout_seconds
                }
                for name, config in self.agents.items()
            }
        }
    
    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """
        Validate the current configuration.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Validate domain distribution
        total_questions = sum(config.target_questions for config in self.domains.values())
        if total_questions != 200:
            issues.append(f"Domain distribution totals {total_questions}, expected 200")
        
        total_weight = sum(config.weight_percentage for config in self.domains.values())
        if abs(total_weight - 100.0) > 0.1:
            issues.append(f"Domain weights total {total_weight}%, expected 100%")
        
        # Validate batch configuration
        if self.batch_config.batch_size <= 0:
            issues.append("Batch size must be positive")
        
        if self.batch_config.total_batches <= 0:
            issues.append("Total batches must be positive")
        
        # Validate agent configurations
        for agent_name, config in self.agents.items():
            if config.temperature < 0 or config.temperature > 2:
                issues.append(f"Agent {agent_name} temperature {config.temperature} out of range [0, 2]")
            
            if config.max_tokens <= 0:
                issues.append(f"Agent {agent_name} max_tokens must be positive")
        
        # Validate quality thresholds
        quality_attrs = [
            "min_technical_accuracy", "min_clarity_score", 
            "min_explanation_score", "min_japanese_quality"
        ]
        for attr in quality_attrs:
            value = getattr(self.quality_config, attr)
            if value < 0 or value > 10:
                issues.append(f"Quality threshold {attr} {value} out of range [0, 10]")
        
        # Validate file paths
        database_path = Path(self.database_config.database_path)
        if not database_path.parent.exists():
            issues.append(f"Database directory does not exist: {database_path.parent}")
        
        backup_dir = Path(self.database_config.backup_directory)
        if not backup_dir.exists():
            try:
                backup_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create backup directory: {e}")
        
        return len(issues) == 0, issues
    
    def create_agent_config(self, base_config: AgentConfig) -> AgentConfig:
        """
        Create an AgentConfig instance with current settings.
        
        Args:
            base_config: Base configuration to modify
            
        Returns:
            Modified AgentConfig instance
        """
        # Update logging level
        base_config.log_level = self.monitoring_config.log_level.value
        
        # Update system prompt template if needed
        if hasattr(base_config, 'system_prompt_template'):
            # Add debug information if in debug mode
            if self.execution_config.mode == ExecutionMode.DEBUG:
                base_config.system_prompt_template += "\n\nDEBUG MODE: Provide detailed reasoning for all decisions."
        
        return base_config
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        is_valid, issues = self.validate_configuration()
        
        return {
            "configuration_file": str(self.config_file),
            "is_valid": is_valid,
            "validation_issues": issues,
            "execution_mode": self.execution_config.mode.value,
            "log_level": self.monitoring_config.log_level.value,
            "batch_configuration": {
                "batch_size": self.batch_config.batch_size,
                "total_batches": self.batch_config.total_batches,
                "strategy": self.batch_config.strategy.value,
                "max_parallel": self.batch_config.max_parallel_batches
            },
            "domain_summary": {
                name: {
                    "target_questions": config.target_questions,
                    "weight_percentage": config.weight_percentage,
                    "enabled": config.enabled
                }
                for name, config in self.domains.items()
            },
            "agent_summary": {
                name: {
                    "enabled": config.enabled,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens
                }
                for name, config in self.agents.items()
            },
            "quality_summary": {
                "min_technical_accuracy": self.quality_config.min_technical_accuracy,
                "min_clarity_score": self.quality_config.min_clarity_score,
                "validation_threshold": self.batch_config.validation_threshold
            }
        }
    
    def export_configuration(self, export_path: str) -> None:
        """Export configuration to a different file."""
        export_file = Path(export_path)
        export_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Temporarily change config file path
        original_path = self.config_file
        self.config_file = export_file
        
        try:
            self.save_configuration()
            self.logger.info(f"Configuration exported to {export_path}")
        finally:
            self.config_file = original_path
    
    def import_configuration(self, import_path: str) -> None:
        """Import configuration from a different file."""
        import_file = Path(import_path)
        if not import_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {import_path}")
        
        # Temporarily change config file path
        original_path = self.config_file
        self.config_file = import_file
        
        try:
            self.load_configuration()
            self.logger.info(f"Configuration imported from {import_path}")
        finally:
            self.config_file = original_path
        
        # Save the imported configuration to the original location
        self.save_configuration()
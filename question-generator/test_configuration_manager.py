"""
Test suite for Configuration Management System.

This module tests the comprehensive configuration management functionality
including loading, validation, updating, and persistence of configuration
settings.
"""

import pytest
import json
import yaml
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Local imports
from core.configuration_manager import (
    ConfigurationManager, DomainConfiguration, BatchConfiguration,
    AgentConfiguration, QualityConfiguration, DatabaseConfiguration,
    MonitoringConfiguration, ExecutionConfiguration,
    LogLevel, ExecutionMode, BatchStrategy
)
from config import AgentConfig


class TestConfigurationManager:
    """Test cases for Configuration Manager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_config_data(self):
        """Create sample configuration data."""
        return {
            "domains": {
                "monitoring": {
                    "name": "Monitoring, Logging, and Remediation",
                    "target_questions": 44,
                    "weight_percentage": 22.0,
                    "priority": 1,
                    "difficulty_distribution": {"easy": 0.3, "medium": 0.5, "hard": 0.2},
                    "question_types": {"single": 0.8, "multiple": 0.2},
                    "focus_topics": ["CloudWatch", "CloudTrail"],
                    "aws_services": ["CloudWatch", "CloudTrail", "Config"],
                    "enabled": True
                },
                "reliability": {
                    "name": "Reliability and Business Continuity",
                    "target_questions": 44,
                    "weight_percentage": 22.0,
                    "priority": 1,
                    "difficulty_distribution": {"easy": 0.3, "medium": 0.5, "hard": 0.2},
                    "question_types": {"single": 0.8, "multiple": 0.2},
                    "focus_topics": ["Backup", "Disaster Recovery"],
                    "aws_services": ["Backup", "RDS", "EC2"],
                    "enabled": True
                }
            },
            "batch": {
                "batch_size": 10,
                "total_batches": 19,
                "strategy": "sequential",
                "max_parallel_batches": 3,
                "retry_attempts": 3,
                "retry_delay_seconds": 5.0,
                "timeout_minutes": 30,
                "validation_threshold": 7.0,
                "auto_recovery": True,
                "checkpoint_frequency": 1
            },
            "agents": {
                "question_generator": {
                    "enabled": True,
                    "temperature": 0.7,
                    "max_tokens": 4000,
                    "timeout_seconds": 240,
                    "retry_attempts": 3,
                    "custom_system_prompt": None,
                    "model_overrides": {}
                },
                "quality_validator": {
                    "enabled": True,
                    "temperature": 0.2,
                    "max_tokens": 3000,
                    "timeout_seconds": 180,
                    "retry_attempts": 3,
                    "custom_system_prompt": None,
                    "model_overrides": {}
                }
            },
            "quality": {
                "min_technical_accuracy": 8.0,
                "min_clarity_score": 7.5,
                "min_explanation_score": 8.0,
                "min_japanese_quality": 7.0,
                "enable_duplicate_detection": True,
                "similarity_threshold": 0.85,
                "require_learning_resources": True,
                "validate_aws_services": True
            },
            "database": {
                "database_path": "output/questions.json",
                "backup_directory": "backups",
                "auto_backup": True,
                "backup_retention_days": 30,
                "validate_schema": True,
                "enable_rollback": True,
                "compression_enabled": False
            },
            "monitoring": {
                "log_level": "INFO",
                "log_file": "logs/question_generation.log",
                "enable_real_time_monitoring": True,
                "progress_update_interval": 30,
                "enable_metrics_collection": True,
                "metrics_file": "logs/metrics.json",
                "enable_performance_profiling": False
            },
            "execution": {
                "mode": "full_auto",
                "enable_pause_resume": True,
                "state_file": "execution_state.json",
                "max_execution_time_hours": 24,
                "resource_limits": {
                    "max_memory_mb": 4096,
                    "max_cpu_percent": 80,
                    "max_concurrent_agents": 5
                },
                "notification_settings": {
                    "enable_notifications": False,
                    "email_on_completion": False,
                    "email_on_error": True,
                    "webhook_url": None
                }
            }
        }
    
    def test_initialization_with_default_config(self, temp_dir):
        """Test initialization with default configuration."""
        config_file = temp_dir / "test_config.yaml"
        
        config_manager = ConfigurationManager(str(config_file))
        
        # Check that default configuration was created
        assert len(config_manager.domains) == 5  # 5 exam domains
        assert config_manager.batch_config.batch_size == 10
        assert config_manager.batch_config.total_batches == 19
        assert len(config_manager.agents) == 7  # 7 agents
        
        # Check that config file was created
        assert config_file.exists()
    
    def test_load_configuration_from_yaml(self, temp_dir, sample_config_data):
        """Test loading configuration from YAML file."""
        config_file = temp_dir / "test_config.yaml"
        
        # Create YAML config file
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_config_data, f, default_flow_style=False)
        
        config_manager = ConfigurationManager(str(config_file))
        
        # Verify loaded configuration
        assert len(config_manager.domains) == 2
        assert "monitoring" in config_manager.domains
        assert "reliability" in config_manager.domains
        
        monitoring_config = config_manager.domains["monitoring"]
        assert monitoring_config.name == "Monitoring, Logging, and Remediation"
        assert monitoring_config.target_questions == 44
        assert monitoring_config.weight_percentage == 22.0
        
        assert config_manager.batch_config.batch_size == 10
        assert config_manager.batch_config.strategy == BatchStrategy.SEQUENTIAL
        
        assert len(config_manager.agents) == 2
        assert config_manager.agents["question_generator"].temperature == 0.7
    
    def test_load_configuration_from_json(self, temp_dir, sample_config_data):
        """Test loading configuration from JSON file."""
        config_file = temp_dir / "test_config.json"
        
        # Create JSON config file
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config_data, f, ensure_ascii=False, indent=2)
        
        config_manager = ConfigurationManager(str(config_file))
        
        # Verify loaded configuration
        assert len(config_manager.domains) == 2
        assert config_manager.batch_config.batch_size == 10
        assert len(config_manager.agents) == 2
    
    def test_save_configuration_yaml(self, temp_dir):
        """Test saving configuration to YAML file."""
        config_file = temp_dir / "test_config.yaml"
        
        config_manager = ConfigurationManager(str(config_file))
        config_manager.save_configuration()
        
        # Verify file was created and contains valid YAML
        assert config_file.exists()
        
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_data = yaml.safe_load(f)
        
        assert "domains" in loaded_data
        assert "batch" in loaded_data
        assert "agents" in loaded_data
        assert "saved_at" in loaded_data
    
    def test_save_configuration_json(self, temp_dir):
        """Test saving configuration to JSON file."""
        config_file = temp_dir / "test_config.json"
        
        config_manager = ConfigurationManager(str(config_file))
        config_manager.save_configuration()
        
        # Verify file was created and contains valid JSON
        assert config_file.exists()
        
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert "domains" in loaded_data
        assert "batch" in loaded_data
        assert "agents" in loaded_data
        assert "saved_at" in loaded_data
    
    def test_get_domain_config(self, temp_dir):
        """Test getting domain configuration."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        # Test existing domain
        monitoring_config = config_manager.get_domain_config("monitoring")
        assert monitoring_config is not None
        assert monitoring_config.name == "Monitoring, Logging, and Remediation"
        
        # Test non-existing domain
        invalid_config = config_manager.get_domain_config("invalid_domain")
        assert invalid_config is None
    
    def test_update_domain_config(self, temp_dir):
        """Test updating domain configuration."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        # Update existing domain
        config_manager.update_domain_config(
            "monitoring",
            target_questions=50,
            weight_percentage=25.0
        )
        
        monitoring_config = config_manager.get_domain_config("monitoring")
        assert monitoring_config.target_questions == 50
        assert monitoring_config.weight_percentage == 25.0
        
        # Try to update non-existing domain (should not crash)
        config_manager.update_domain_config("invalid_domain", target_questions=10)
    
    def test_get_agent_config(self, temp_dir):
        """Test getting agent configuration."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        # Test existing agent
        generator_config = config_manager.get_agent_config("question_generator")
        assert generator_config is not None
        assert generator_config.temperature == 0.7
        
        # Test non-existing agent
        invalid_config = config_manager.get_agent_config("invalid_agent")
        assert invalid_config is None
    
    def test_update_agent_config(self, temp_dir):
        """Test updating agent configuration."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        # Update existing agent
        config_manager.update_agent_config(
            "question_generator",
            temperature=0.8,
            max_tokens=5000
        )
        
        generator_config = config_manager.get_agent_config("question_generator")
        assert generator_config.temperature == 0.8
        assert generator_config.max_tokens == 5000
    
    def test_adjust_batch_size(self, temp_dir):
        """Test adjusting batch size."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        # Test valid batch size
        config_manager.adjust_batch_size(15)
        assert config_manager.batch_config.batch_size == 15
        # Total batches should be recalculated: 189 questions / 15 = 13 batches
        assert config_manager.batch_config.total_batches == 13
        
        # Test invalid batch size (should not change)
        original_size = config_manager.batch_config.batch_size
        config_manager.adjust_batch_size(25)  # Invalid (> 20)
        assert config_manager.batch_config.batch_size == original_size
        
        config_manager.adjust_batch_size(0)   # Invalid (<= 0)
        assert config_manager.batch_config.batch_size == original_size
    
    def test_set_execution_mode(self, temp_dir):
        """Test setting execution mode."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        config_manager.set_execution_mode(ExecutionMode.DEBUG)
        assert config_manager.execution_config.mode == ExecutionMode.DEBUG
        
        config_manager.set_execution_mode(ExecutionMode.MANUAL)
        assert config_manager.execution_config.mode == ExecutionMode.MANUAL
    
    def test_enable_debug_mode(self, temp_dir):
        """Test enabling debug mode."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        config_manager.enable_debug_mode()
        
        assert config_manager.execution_config.mode == ExecutionMode.DEBUG
        assert config_manager.monitoring_config.log_level == LogLevel.DEBUG
        assert config_manager.monitoring_config.enable_performance_profiling == True
    
    def test_adjust_quality_thresholds(self, temp_dir):
        """Test adjusting quality thresholds."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        config_manager.adjust_quality_thresholds(
            min_technical_accuracy=9.0,
            min_clarity_score=8.5
        )
        
        assert config_manager.quality_config.min_technical_accuracy == 9.0
        assert config_manager.quality_config.min_clarity_score == 8.5
    
    def test_get_runtime_parameters(self, temp_dir):
        """Test getting runtime parameters."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        params = config_manager.get_runtime_parameters()
        
        assert "batch_size" in params
        assert "total_batches" in params
        assert "execution_mode" in params
        assert "log_level" in params
        assert "quality_thresholds" in params
        assert "domain_distribution" in params
        assert "agent_settings" in params
        
        # Check structure
        assert isinstance(params["quality_thresholds"], dict)
        assert isinstance(params["domain_distribution"], dict)
        assert isinstance(params["agent_settings"], dict)
    
    def test_validate_configuration_valid(self, temp_dir):
        """Test configuration validation with valid configuration."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        is_valid, issues = config_manager.validate_configuration()
        
        assert is_valid
        assert len(issues) == 0
    
    def test_validate_configuration_invalid_domain_distribution(self, temp_dir):
        """Test configuration validation with invalid domain distribution."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        # Make domain distribution invalid
        config_manager.domains["monitoring"].target_questions = 100  # Too many
        
        is_valid, issues = config_manager.validate_configuration()
        
        assert not is_valid
        assert any("Domain distribution totals" in issue for issue in issues)
    
    def test_validate_configuration_invalid_agent_settings(self, temp_dir):
        """Test configuration validation with invalid agent settings."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        # Make agent configuration invalid
        config_manager.agents["question_generator"].temperature = 5.0  # Out of range
        config_manager.agents["quality_validator"].max_tokens = -100   # Invalid
        
        is_valid, issues = config_manager.validate_configuration()
        
        assert not is_valid
        assert any("temperature" in issue for issue in issues)
        assert any("max_tokens must be positive" in issue for issue in issues)
    
    def test_create_agent_config(self, temp_dir):
        """Test creating AgentConfig instance."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        base_config = AgentConfig()
        modified_config = config_manager.create_agent_config(base_config)
        
        assert modified_config.log_level == config_manager.monitoring_config.log_level.value
        
        # Test debug mode modification
        config_manager.enable_debug_mode()
        debug_config = config_manager.create_agent_config(base_config)
        
        if hasattr(debug_config, 'system_prompt_template'):
            assert "DEBUG MODE" in debug_config.system_prompt_template
    
    def test_get_configuration_summary(self, temp_dir):
        """Test getting configuration summary."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        summary = config_manager.get_configuration_summary()
        
        assert "configuration_file" in summary
        assert "is_valid" in summary
        assert "validation_issues" in summary
        assert "execution_mode" in summary
        assert "batch_configuration" in summary
        assert "domain_summary" in summary
        assert "agent_summary" in summary
        assert "quality_summary" in summary
        
        # Check structure
        assert isinstance(summary["batch_configuration"], dict)
        assert isinstance(summary["domain_summary"], dict)
        assert isinstance(summary["agent_summary"], dict)
    
    def test_export_configuration(self, temp_dir):
        """Test exporting configuration."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        export_path = temp_dir / "exported_config.yaml"
        
        config_manager.export_configuration(str(export_path))
        
        assert export_path.exists()
        
        # Verify exported content
        with open(export_path, 'r', encoding='utf-8') as f:
            exported_data = yaml.safe_load(f)
        
        assert "domains" in exported_data
        assert "batch" in exported_data
        assert "agents" in exported_data
    
    def test_import_configuration(self, temp_dir, sample_config_data):
        """Test importing configuration."""
        # Create source config file
        source_config = temp_dir / "source_config.yaml"
        with open(source_config, 'w', encoding='utf-8') as f:
            yaml.dump(sample_config_data, f, default_flow_style=False)
        
        # Create config manager with different file
        target_config = temp_dir / "target_config.yaml"
        config_manager = ConfigurationManager(str(target_config))
        
        # Import configuration
        config_manager.import_configuration(str(source_config))
        
        # Verify imported configuration
        assert len(config_manager.domains) == 2  # From sample data
        assert config_manager.batch_config.batch_size == 10
        
        # Verify target file was updated
        assert target_config.exists()
    
    def test_import_nonexistent_configuration(self, temp_dir):
        """Test importing from non-existent file."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        with pytest.raises(FileNotFoundError):
            config_manager.import_configuration(str(temp_dir / "nonexistent.yaml"))
    
    @patch('logging.getLogger')
    def test_logging_integration(self, mock_logger, temp_dir):
        """Test logging integration."""
        config_manager = ConfigurationManager(str(temp_dir / "config.yaml"))
        
        # Verify logger was created
        mock_logger.assert_called()
        
        # Test that operations trigger logging
        config_manager.update_domain_config("monitoring", target_questions=50)
        config_manager.update_agent_config("question_generator", temperature=0.8)
    
    def test_configuration_persistence(self, temp_dir):
        """Test that configuration changes persist across instances."""
        config_file = temp_dir / "persistent_config.yaml"
        
        # Create first instance and modify configuration
        config_manager1 = ConfigurationManager(str(config_file))
        config_manager1.adjust_batch_size(15)
        config_manager1.set_execution_mode(ExecutionMode.DEBUG)
        config_manager1.save_configuration()
        
        # Create second instance and verify changes persisted
        config_manager2 = ConfigurationManager(str(config_file))
        
        assert config_manager2.batch_config.batch_size == 15
        assert config_manager2.execution_config.mode == ExecutionMode.DEBUG


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
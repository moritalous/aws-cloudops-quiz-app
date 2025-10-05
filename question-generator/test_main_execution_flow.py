"""
Test suite for Main Execution Flow.

This module tests the complete AI automation flow including workflow
orchestration, batch processing, progress tracking, and error recovery.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

# Local imports
from core.main_execution_flow import (
    MainExecutionFlow, FlowStatus, BatchStatus, 
    BatchProgress, FlowProgress
)
from core.configuration_manager import ConfigurationManager
from config import AgentConfig
from models import (
    ExamGuideAnalysis, DomainAnalysis, QuestionBatch, 
    Question, LearningResource, IntegrationResult
)


class TestMainExecutionFlow:
    """Test cases for Main Execution Flow."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_agent_config(self):
        """Create mock agent configuration."""
        config = Mock(spec=AgentConfig)
        config.log_level = "INFO"
        config.system_prompt_template = "You are {role}. Context: {context}. Requirements: {requirements}"
        return config
    
    @pytest.fixture
    def sample_exam_analysis(self):
        """Create sample exam guide analysis."""
        domains = [
            DomainAnalysis(
                name="Monitoring, Logging, and Remediation",
                weight_percentage=22.0,
                target_questions=44,
                tasks=[],
                skills=[],
                related_services=["CloudWatch", "CloudTrail"]
            ),
            DomainAnalysis(
                name="Reliability and Business Continuity", 
                weight_percentage=22.0,
                target_questions=44,
                tasks=[],
                skills=[],
                related_services=["Backup", "RDS"]
            )
        ]
        
        return ExamGuideAnalysis(
            exam_title="AWS Certified CloudOps Engineer - Associate",
            exam_code="SOA-C03",
            target_total_questions=200,
            existing_questions=11,
            questions_to_generate=189,
            domains=domains,
            overall_difficulty_distribution={"easy": 60, "medium": 100, "hard": 40},
            question_type_distribution={"single": 160, "multiple": 40}
        )
    
    @pytest.fixture
    def execution_flow(self, temp_dir, mock_agent_config):
        """Create MainExecutionFlow instance for testing."""
        database_path = temp_dir / "questions.json"
        backup_dir = temp_dir / "backups"
        state_file = temp_dir / "state.json"
        
        # Create logs directory
        logs_dir = temp_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        flow = MainExecutionFlow(
            config=mock_agent_config,
            database_path=str(database_path),
            backup_dir=str(backup_dir),
            state_file=str(state_file),
            log_level="DEBUG"
        )
        
        return flow
    
    def test_initialization(self, execution_flow, temp_dir):
        """Test MainExecutionFlow initialization."""
        assert execution_flow.progress.status == FlowStatus.NOT_STARTED
        assert execution_flow.progress.total_batches == 19
        assert len(execution_flow.progress.batch_progress) == 19
        
        # Check that directories were created
        assert execution_flow.backup_dir.exists()
        
        # Check batch progress initialization
        for i in range(1, 20):
            assert i in execution_flow.progress.batch_progress
            batch_progress = execution_flow.progress.batch_progress[i]
            assert batch_progress.batch_number == i
            assert batch_progress.status == BatchStatus.PENDING
    
    def test_save_and_load_state(self, execution_flow):
        """Test saving and loading execution state."""
        # Modify progress
        execution_flow.progress.status = FlowStatus.RUNNING
        execution_flow.progress.start_time = datetime.now()
        execution_flow.progress.completed_batches = 5
        execution_flow.progress.current_batch = 6
        
        # Modify batch progress
        batch_progress = execution_flow.progress.batch_progress[1]
        batch_progress.status = BatchStatus.COMPLETED
        batch_progress.start_time = datetime.now()
        batch_progress.end_time = datetime.now()
        batch_progress.questions_generated = 10
        batch_progress.validation_score = 8.5
        
        # Save state
        execution_flow.save_state()
        assert execution_flow.state_file.exists()
        
        # Create new instance and load state
        new_flow = MainExecutionFlow(
            config=execution_flow.config,
            database_path=str(execution_flow.database_path),
            backup_dir=str(execution_flow.backup_dir),
            state_file=str(execution_flow.state_file)
        )
        
        loaded = new_flow.load_state()
        assert loaded == True
        
        # Verify loaded state
        assert new_flow.progress.status == FlowStatus.RUNNING
        assert new_flow.progress.completed_batches == 5
        assert new_flow.progress.current_batch == 6
        
        loaded_batch = new_flow.progress.batch_progress[1]
        assert loaded_batch.status == BatchStatus.COMPLETED
        assert loaded_batch.questions_generated == 10
        assert loaded_batch.validation_score == 8.5
    
    def test_load_state_no_file(self, execution_flow):
        """Test loading state when no state file exists."""
        loaded = execution_flow.load_state()
        assert loaded == False
    
    def test_get_progress_report(self, execution_flow):
        """Test getting progress report."""
        # Set up some progress
        execution_flow.progress.status = FlowStatus.RUNNING
        execution_flow.progress.start_time = datetime.now() - timedelta(hours=1)
        execution_flow.progress.completed_batches = 3
        execution_flow.progress.current_batch = 4
        execution_flow.progress.total_questions_generated = 30
        execution_flow.progress.overall_validation_score = 8.2
        
        # Set up batch progress
        for i in range(1, 4):  # First 3 batches completed
            batch_progress = execution_flow.progress.batch_progress[i]
            batch_progress.status = BatchStatus.COMPLETED
            batch_progress.steps_completed = 7
            batch_progress.questions_generated = 10
            batch_progress.validation_score = 8.0 + i * 0.1
        
        # Current batch in progress
        current_batch = execution_flow.progress.batch_progress[4]
        current_batch.status = BatchStatus.GENERATING
        current_batch.current_step = "Generating questions"
        current_batch.steps_completed = 3
        
        report = execution_flow.get_progress_report()
        
        assert report['overall_status'] == 'running'
        assert report['batches_completed'] == 3
        assert report['batches_remaining'] == 16
        assert report['total_questions_generated'] == 30
        assert report['overall_validation_score'] == 8.2
        
        # Check current batch info
        current_batch_info = report['current_batch']
        assert current_batch_info['batch_number'] == 4
        assert current_batch_info['status'] == 'generating'
        assert current_batch_info['current_step'] == 'Generating questions'
        assert current_batch_info['progress'] == '3/7'
        
        # Check batch details
        assert len(report['batch_details']) == 19
        assert report['batch_details'][0]['batch_number'] == 1
        assert report['batch_details'][0]['status'] == 'completed'
    
    @patch('core.main_execution_flow.MainExecutionFlow.exam_analyzer')
    async def test_initialize_flow(self, mock_exam_analyzer, execution_flow, sample_exam_analysis, temp_dir):
        """Test flow initialization."""
        # Create mock exam guide file
        exam_guide_path = temp_dir / "docs" / "AWS_Certified_CloudOps_Engineer_Associate_Exam_Guide.md"
        exam_guide_path.parent.mkdir(parents=True, exist_ok=True)
        exam_guide_path.write_text("Mock exam guide content")
        
        # Mock the exam analyzer
        mock_exam_analyzer.structured_output.return_value = sample_exam_analysis
        
        # Change working directory for the test
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            result = await execution_flow.initialize_flow()
            
            assert result == sample_exam_analysis
            assert execution_flow.progress.status == FlowStatus.INITIALIZING
            assert execution_flow.progress.start_time is not None
            
            # Verify exam analyzer was called
            mock_exam_analyzer.structured_output.assert_called_once()
        
        finally:
            os.chdir(original_cwd)
    
    async def test_initialize_flow_missing_exam_guide(self, execution_flow):
        """Test flow initialization with missing exam guide."""
        with pytest.raises(Exception):  # Should raise QuestionGenerationError
            await execution_flow.initialize_flow()
    
    @patch('core.main_execution_flow.MainExecutionFlow._execute_batch_steps')
    async def test_process_batch_with_workflow_success(self, mock_execute_steps, execution_flow, sample_exam_analysis):
        """Test successful batch processing."""
        # Mock the batch execution
        mock_integration_result = IntegrationResult(
            success=True,
            batch_number=1,
            questions_added=10,
            new_total_questions=21,
            validation_passed=True,
            backup_created=True
        )
        mock_execute_steps.return_value = mock_integration_result
        
        result = await execution_flow.process_batch_with_workflow(1, sample_exam_analysis)
        
        assert result == mock_integration_result
        
        # Check batch progress was updated
        batch_progress = execution_flow.progress.batch_progress[1]
        assert batch_progress.status == BatchStatus.COMPLETED
        assert batch_progress.steps_completed == 7
        assert batch_progress.integration_result == mock_integration_result
        
        # Check overall progress was updated
        assert execution_flow.progress.completed_batches == 1
        assert execution_flow.progress.total_questions_generated == 10
    
    @patch('core.main_execution_flow.MainExecutionFlow._execute_batch_steps')
    async def test_process_batch_with_workflow_failure(self, mock_execute_steps, execution_flow, sample_exam_analysis):
        """Test batch processing failure."""
        # Mock batch execution failure
        mock_execute_steps.side_effect = Exception("Batch processing failed")
        
        with pytest.raises(Exception):
            await execution_flow.process_batch_with_workflow(1, sample_exam_analysis)
        
        # Check batch progress reflects failure
        batch_progress = execution_flow.progress.batch_progress[1]
        assert batch_progress.status == BatchStatus.FAILED
        assert batch_progress.error_message == "Batch processing failed"
        assert batch_progress.retry_count == 1
        assert execution_flow.progress.failed_batches == 1
    
    def test_pause_and_resume_flow(self, execution_flow):
        """Test pausing and resuming execution flow."""
        # Test pause
        execution_flow.pause_flow()
        assert execution_flow.progress.pause_requested == True
        
        # Test resume
        execution_flow.progress.status = FlowStatus.PAUSED
        execution_flow.resume_flow()
        assert execution_flow.progress.pause_requested == False
        assert execution_flow.progress.status == FlowStatus.RUNNING
    
    def test_get_real_time_status(self, execution_flow):
        """Test getting real-time status."""
        status = execution_flow.get_real_time_status()
        
        assert 'timestamp' in status
        assert 'status' in status
        assert 'progress' in status
        assert 'system_health' in status
        
        # Check system health
        system_health = status['system_health']
        assert 'agents_initialized' in system_health
        assert 'database_accessible' in system_health
        assert 'backup_dir_accessible' in system_health
        
        # Initially no agents should be initialized
        agents_status = system_health['agents_initialized']
        assert agents_status['exam_analyzer'] == False
        assert agents_status['batch_manager'] == False
        assert agents_status['question_generator'] == False
    
    def test_lazy_agent_initialization(self, execution_flow):
        """Test lazy initialization of agents."""
        # Initially agents should be None
        assert execution_flow._exam_analyzer is None
        assert execution_flow._batch_manager is None
        assert execution_flow._question_generator is None
        
        # Access agents to trigger initialization
        with patch.object(execution_flow.agent_factory, 'create_exam_guide_analyzer') as mock_create:
            mock_agent = Mock()
            mock_create.return_value = mock_agent
            
            agent = execution_flow.exam_analyzer
            assert agent == mock_agent
            assert execution_flow._exam_analyzer == mock_agent
            mock_create.assert_called_once()
            
            # Second access should not create new agent
            agent2 = execution_flow.exam_analyzer
            assert agent2 == mock_agent
            assert mock_create.call_count == 1
    
    @patch('core.main_execution_flow.MainExecutionFlow.initialize_flow')
    @patch('core.main_execution_flow.MainExecutionFlow.process_batch_with_workflow')
    async def test_run_complete_flow_success(self, mock_process_batch, mock_initialize, execution_flow, sample_exam_analysis):
        """Test successful complete flow execution."""
        # Mock initialization
        mock_initialize.return_value = sample_exam_analysis
        
        # Mock batch processing
        mock_integration_result = IntegrationResult(
            success=True,
            batch_number=1,
            questions_added=10,
            new_total_questions=21,
            validation_passed=True,
            backup_created=True
        )
        mock_process_batch.return_value = mock_integration_result
        
        # Mock database integration agent
        with patch.object(execution_flow, 'db_integration_agent') as mock_db_agent:
            mock_final_db = Mock()
            mock_final_db.total_questions = 200
            mock_db_agent.create_final_database_with_structured_output.return_value = mock_final_db
            
            result = await execution_flow.run_complete_flow()
            
            assert result == mock_final_db
            assert execution_flow.progress.status == FlowStatus.COMPLETED
            assert execution_flow.progress.end_time is not None
            
            # Verify all batches were processed
            assert mock_process_batch.call_count == 19
    
    @patch('core.main_execution_flow.MainExecutionFlow.initialize_flow')
    async def test_run_complete_flow_with_pause(self, mock_initialize, execution_flow, sample_exam_analysis):
        """Test complete flow execution with pause request."""
        # Mock initialization
        mock_initialize.return_value = sample_exam_analysis
        
        # Request pause immediately
        execution_flow.progress.pause_requested = True
        
        result = await execution_flow.run_complete_flow()
        
        assert result is None
        assert execution_flow.progress.status == FlowStatus.PAUSED
    
    @patch('core.main_execution_flow.MainExecutionFlow.load_state')
    @patch('core.main_execution_flow.MainExecutionFlow.process_batch_with_workflow')
    async def test_run_complete_flow_recovery_mode(self, mock_process_batch, mock_load_state, execution_flow, sample_exam_analysis):
        """Test complete flow execution in recovery mode."""
        # Mock state loading
        mock_load_state.return_value = True
        execution_flow.progress.status = FlowStatus.RUNNING
        execution_flow.progress.recovery_mode = True
        
        # Mark some batches as completed
        execution_flow.progress.batch_progress[1].status = BatchStatus.COMPLETED
        execution_flow.progress.batch_progress[2].status = BatchStatus.COMPLETED
        
        # Mock batch processing for remaining batches
        mock_integration_result = IntegrationResult(
            success=True,
            batch_number=3,
            questions_added=10,
            new_total_questions=31,
            validation_passed=True,
            backup_created=True
        )
        mock_process_batch.return_value = mock_integration_result
        
        # Mock database integration agent
        with patch.object(execution_flow, 'db_integration_agent') as mock_db_agent:
            mock_final_db = Mock()
            mock_final_db.total_questions = 200
            mock_db_agent.create_final_database_with_structured_output.return_value = mock_final_db
            
            # Need to set exam_analysis for recovery mode
            execution_flow.exam_analysis = sample_exam_analysis
            
            result = await execution_flow.run_complete_flow()
            
            assert result == mock_final_db
            
            # Should skip completed batches (1, 2) and process remaining (3-19)
            assert mock_process_batch.call_count == 17
    
    @patch('core.main_execution_flow.MainExecutionFlow.initialize_flow')
    async def test_run_complete_flow_failure(self, mock_initialize, execution_flow):
        """Test complete flow execution with failure."""
        # Mock initialization failure
        mock_initialize.side_effect = Exception("Initialization failed")
        
        with pytest.raises(Exception):
            await execution_flow.run_complete_flow()
        
        assert execution_flow.progress.status == FlowStatus.FAILED
    
    def test_batch_progress_dataclass(self):
        """Test BatchProgress dataclass functionality."""
        batch_progress = BatchProgress(batch_number=1)
        
        assert batch_progress.batch_number == 1
        assert batch_progress.status == BatchStatus.PENDING
        assert batch_progress.start_time is None
        assert batch_progress.steps_completed == 0
        assert batch_progress.total_steps == 7
        assert batch_progress.retry_count == 0
        assert batch_progress.max_retries == 3
    
    def test_flow_progress_dataclass(self):
        """Test FlowProgress dataclass functionality."""
        flow_progress = FlowProgress()
        
        assert flow_progress.status == FlowStatus.NOT_STARTED
        assert flow_progress.total_batches == 19
        assert flow_progress.completed_batches == 0
        assert flow_progress.failed_batches == 0
        assert flow_progress.current_batch is None
        assert len(flow_progress.batch_progress) == 0
        assert flow_progress.pause_requested == False
        assert flow_progress.recovery_mode == False
    
    def test_flow_status_enum(self):
        """Test FlowStatus enum values."""
        assert FlowStatus.NOT_STARTED.value == "not_started"
        assert FlowStatus.INITIALIZING.value == "initializing"
        assert FlowStatus.RUNNING.value == "running"
        assert FlowStatus.PAUSED.value == "paused"
        assert FlowStatus.COMPLETED.value == "completed"
        assert FlowStatus.FAILED.value == "failed"
        assert FlowStatus.RECOVERING.value == "recovering"
    
    def test_batch_status_enum(self):
        """Test BatchStatus enum values."""
        assert BatchStatus.PENDING.value == "pending"
        assert BatchStatus.ANALYZING.value == "analyzing"
        assert BatchStatus.PLANNING.value == "planning"
        assert BatchStatus.RESEARCHING.value == "researching"
        assert BatchStatus.GENERATING.value == "generating"
        assert BatchStatus.VALIDATING.value == "validating"
        assert BatchStatus.OPTIMIZING.value == "optimizing"
        assert BatchStatus.INTEGRATING.value == "integrating"
        assert BatchStatus.COMPLETED.value == "completed"
        assert BatchStatus.FAILED.value == "failed"
        assert BatchStatus.RETRYING.value == "retrying"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
Test suite for Database Integration Agent.

This module tests the AI-powered database integration functionality including
structured output, ID continuity, metadata updates, backup/rollback, and
JSON structure integrity validation.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Local imports
from models import (
    QuestionBatch, Question, LearningResource, IntegrationResult,
    DatabaseBackup, QuestionDatabase
)
from core.database_integration_agent import DatabaseIntegrationAgent
from core.error_handling import QuestionGenerationError, ValidationError


class TestDatabaseIntegrationAgent:
    """Test cases for Database Integration Agent."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_database(self):
        """Create sample database data."""
        return {
            "version": "2.0.0",
            "generated_at": "2024-01-01T00:00:00",
            "generation_method": "AI-Strands-Agents-Bedrock",
            "total_questions": 11,
            "domains": {
                "monitoring": 3,
                "reliability": 3,
                "deployment": 2,
                "security": 2,
                "networking": 1
            },
            "difficulty": {
                "easy": 4,
                "medium": 5,
                "hard": 2
            },
            "question_types": {
                "single": 9,
                "multiple": 2
            },
            "questions": [
                {
                    "id": f"q{i:03d}",
                    "domain": "monitoring",
                    "difficulty": "medium",
                    "type": "single",
                    "question": f"Test question {i} with sufficient length to meet the minimum character requirement for question validation",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": f"Test explanation {i} with comprehensive details that meet the minimum character requirement for explanation validation. This explanation provides thorough information about the correct answer and why other options are incorrect.",
                    "learning_resources": [],
                    "related_services": ["CloudWatch"],
                    "tags": ["monitoring"]
                }
                for i in range(1, 12)
            ]
        }
    
    @pytest.fixture
    def sample_question_batch(self):
        """Create sample question batch."""
        questions = []
        for i in range(1, 11):
            learning_resource = LearningResource(
                title=f"AWS Documentation {i}",
                url=f"https://docs.aws.amazon.com/test{i}",
                type="documentation"
            )
            
            question = Question(
                id=f"q{12+i-1:03d}",  # q012 to q021
                domain="reliability",
                difficulty="medium",
                type="single",
                question=f"New test question {i} with sufficient length to meet the minimum character requirement for question validation",
                options=["A", "B", "C", "D"],
                correct_answer="B",
                explanation=f"New test explanation {i} with comprehensive details that meet the minimum character requirement for explanation validation. This explanation provides thorough information about the correct answer and why other options are incorrect.",
                learning_resources=[learning_resource],
                related_services=["EC2", "RDS"],
                tags=["reliability", "backup"]
            )
            questions.append(question)
        
        return QuestionBatch(
            batch_number=1,
            questions=questions,
            batch_metadata={"generated_at": datetime.now().isoformat()}
        )
    
    @pytest.fixture
    def mock_agent(self):
        """Create mock Strands Agent."""
        agent = Mock()
        
        # Mock structured_output method
        def mock_structured_output(model_class, prompt):
            if model_class == IntegrationResult:
                return IntegrationResult(
                    success=True,
                    batch_number=1,
                    questions_added=10,
                    new_total_questions=21,
                    added_question_ids=[f"q{i:03d}" for i in range(12, 22)],
                    updated_metadata={
                        "domains": {"monitoring": 3, "reliability": 13, "deployment": 2, "security": 2, "networking": 1},
                        "difficulty": {"easy": 4, "medium": 15, "hard": 2},
                        "question_types": {"single": 19, "multiple": 2}
                    },
                    validation_passed=True,
                    backup_created=True
                )
            elif model_class == QuestionDatabase:
                return QuestionDatabase(
                    total_questions=200,
                    questions=[Mock() for _ in range(200)]  # Mock questions
                )
            return Mock()
        
        agent.structured_output = mock_structured_output
        return agent
    
    @pytest.fixture
    def db_integration_agent(self, temp_dir, mock_agent):
        """Create Database Integration Agent for testing."""
        database_path = temp_dir / "questions.json"
        backup_dir = temp_dir / "backups"
        
        return DatabaseIntegrationAgent(
            agent=mock_agent,
            database_path=str(database_path),
            backup_dir=str(backup_dir)
        )
    
    def test_initialization(self, temp_dir, mock_agent):
        """Test Database Integration Agent initialization."""
        database_path = temp_dir / "questions.json"
        backup_dir = temp_dir / "backups"
        
        agent = DatabaseIntegrationAgent(
            agent=mock_agent,
            database_path=str(database_path),
            backup_dir=str(backup_dir)
        )
        
        assert agent.database_path == database_path
        assert agent.backup_dir == backup_dir
        assert backup_dir.exists()  # Should be created automatically
    
    def test_create_backup(self, db_integration_agent, sample_database, temp_dir):
        """Test backup creation functionality."""
        # Create initial database file
        database_path = temp_dir / "questions.json"
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(sample_database, f, ensure_ascii=False, indent=2)
        
        # Create backup
        backup_info = db_integration_agent.create_backup(batch_number=1)
        
        assert backup_info.backup_id.startswith("questions_backup_")
        assert backup_info.backup_id.endswith("_batch01")
        assert backup_info.questions_count == 11
        assert backup_info.created_before_batch == 1
        assert backup_info.checksum is not None
        
        # Verify backup file exists
        backup_path = Path(backup_info.backup_file_path)
        assert backup_path.exists()
        
        # Verify backup content
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        assert backup_data == sample_database
    
    def test_validate_json_structure(self, db_integration_agent, sample_database):
        """Test JSON structure validation."""
        # Test valid structure
        is_valid, issues = db_integration_agent.validate_json_structure(sample_database)
        assert is_valid
        assert len(issues) == 0
        
        # Test invalid structure - missing required field
        invalid_data = sample_database.copy()
        del invalid_data['total_questions']
        
        is_valid, issues = db_integration_agent.validate_json_structure(invalid_data)
        assert not is_valid
        assert any("Missing required field: total_questions" in issue for issue in issues)
        
        # Test invalid structure - question count mismatch
        invalid_data = sample_database.copy()
        invalid_data['total_questions'] = 999
        
        is_valid, issues = db_integration_agent.validate_json_structure(invalid_data)
        assert not is_valid
        assert any("Question count mismatch" in issue for issue in issues)
    
    def test_validate_id_continuity(self, db_integration_agent):
        """Test question ID continuity validation."""
        # Test valid ID sequence
        questions = [{"id": f"q{i:03d}"} for i in range(1, 6)]
        is_valid, issues = db_integration_agent.validate_id_continuity(questions)
        assert is_valid
        assert len(issues) == 0
        
        # Test invalid ID sequence - gap
        questions = [{"id": "q001"}, {"id": "q002"}, {"id": "q004"}]  # Missing q003
        is_valid, issues = db_integration_agent.validate_id_continuity(questions)
        assert not is_valid
        assert any("ID mismatch" in issue for issue in issues)
        
        # Test duplicate IDs
        questions = [{"id": "q001"}, {"id": "q002"}, {"id": "q001"}]
        is_valid, issues = db_integration_agent.validate_id_continuity(questions)
        assert not is_valid
        assert any("Duplicate question IDs" in issue for issue in issues)
        
        # Test missing IDs
        questions = [{"id": "q001"}, {}, {"id": "q003"}]  # Missing ID in second question
        is_valid, issues = db_integration_agent.validate_id_continuity(questions)
        assert not is_valid
        assert any("Questions missing IDs" in issue for issue in issues)
    
    def test_integrate_batch_success(self, db_integration_agent, sample_database, sample_question_batch, temp_dir):
        """Test successful batch integration."""
        # Create initial database file
        database_path = temp_dir / "questions.json"
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(sample_database, f, ensure_ascii=False, indent=2)
        
        # Integrate batch
        result = db_integration_agent.integrate_batch_with_structured_output(
            sample_question_batch,
            create_backup=True
        )
        
        assert result.success
        assert result.batch_number == 1
        assert result.questions_added == 10
        assert result.new_total_questions == 21
        assert len(result.added_question_ids) == 10
        assert result.validation_passed
        assert result.backup_created
        assert result.backup_path is not None
        
        # Verify database was updated
        with open(database_path, 'r', encoding='utf-8') as f:
            updated_data = json.load(f)
        
        assert updated_data['total_questions'] == 21
        assert len(updated_data['questions']) == 21
        
        # Verify ID continuity
        question_ids = [q['id'] for q in updated_data['questions']]
        expected_ids = [f'q{i:03d}' for i in range(1, 22)]
        assert question_ids == expected_ids
    
    def test_integrate_batch_with_empty_database(self, db_integration_agent, sample_question_batch, temp_dir):
        """Test batch integration with non-existent database."""
        # Don't create database file - should initialize empty structure
        
        result = db_integration_agent.integrate_batch_with_structured_output(
            sample_question_batch,
            create_backup=False
        )
        
        assert result.success
        assert result.questions_added == 10
        assert result.new_total_questions == 10
        
        # Verify database was created
        database_path = temp_dir / "questions.json"
        assert database_path.exists()
        
        with open(database_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data['total_questions'] == 10
        assert len(data['questions']) == 10
    
    def test_restore_from_backup(self, db_integration_agent, sample_database, temp_dir):
        """Test backup restoration functionality."""
        # Create initial database and backup
        database_path = temp_dir / "questions.json"
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(sample_database, f, ensure_ascii=False, indent=2)
        
        backup_info = db_integration_agent.create_backup()
        
        # Modify database
        modified_data = sample_database.copy()
        modified_data['total_questions'] = 999
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(modified_data, f, ensure_ascii=False, indent=2)
        
        # Restore from backup
        success = db_integration_agent.restore_from_backup(backup_info.backup_id)
        assert success
        
        # Verify restoration
        with open(database_path, 'r', encoding='utf-8') as f:
            restored_data = json.load(f)
        
        assert restored_data == sample_database
    
    def test_list_backups(self, db_integration_agent, sample_database, temp_dir):
        """Test backup listing functionality."""
        # Create database and multiple backups
        database_path = temp_dir / "questions.json"
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(sample_database, f, ensure_ascii=False, indent=2)
        
        backup1 = db_integration_agent.create_backup(batch_number=1)
        backup2 = db_integration_agent.create_backup(batch_number=2)
        
        # List backups
        backups = db_integration_agent.list_backups()
        
        assert len(backups) >= 2
        backup_ids = [b.backup_id for b in backups]
        assert backup1.backup_id in backup_ids
        assert backup2.backup_id in backup_ids
        
        # Verify backup info
        for backup in backups:
            assert backup.questions_count == 11
            assert backup.backup_size_bytes > 0
            assert backup.checksum is not None
    
    def test_create_final_database_structure(self, db_integration_agent, temp_dir):
        """Test final database structure creation."""
        # Create a complete database file
        complete_data = {
            "version": "2.0.0",
            "total_questions": 200,
            "questions": [{"id": f"q{i:03d}"} for i in range(1, 201)]
        }
        
        database_path = temp_dir / "questions.json"
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, ensure_ascii=False, indent=2)
        
        # Create mock integration results
        integration_results = [
            IntegrationResult(
                success=True,
                batch_number=i,
                questions_added=10,
                new_total_questions=11 + (i * 10),
                validation_passed=True,
                backup_created=True
            )
            for i in range(1, 20)  # 19 batches
        ]
        
        # Create final database structure
        final_db = db_integration_agent.create_final_database_with_structured_output(
            integration_results
        )
        
        assert isinstance(final_db, QuestionDatabase)
        assert final_db.total_questions == 200
    
    def test_validate_database_integrity(self, db_integration_agent, sample_database, temp_dir):
        """Test comprehensive database integrity validation."""
        # Create valid database
        database_path = temp_dir / "questions.json"
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(sample_database, f, ensure_ascii=False, indent=2)
        
        is_valid, issues, report = db_integration_agent.validate_database_integrity()
        
        assert report['file_exists']
        assert report['json_valid']
        assert report['file_size_bytes'] > 0
        assert report['question_count'] == 11
        
        # For this test, we expect some validation issues since we don't have 200 questions
        # but the basic structure should be valid
    
    def test_error_handling_backup_creation(self, db_integration_agent):
        """Test error handling in backup creation."""
        # Try to create backup when database doesn't exist
        with pytest.raises(QuestionGenerationError, match="Database file not found"):
            db_integration_agent.create_backup()
    
    def test_error_handling_invalid_backup_restoration(self, db_integration_agent):
        """Test error handling in backup restoration."""
        # Try to restore from non-existent backup
        success = db_integration_agent.restore_from_backup("non_existent_backup")
        assert not success
    
    @patch('shutil.copy2')
    def test_backup_creation_failure(self, mock_copy, db_integration_agent, sample_database, temp_dir):
        """Test backup creation failure handling."""
        # Create database file
        database_path = temp_dir / "questions.json"
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(sample_database, f, ensure_ascii=False, indent=2)
        
        # Mock copy failure
        mock_copy.side_effect = Exception("Copy failed")
        
        with pytest.raises(QuestionGenerationError, match="Failed to create backup"):
            db_integration_agent.create_backup()
    
    def test_integration_with_validation_failure(self, db_integration_agent, sample_question_batch, temp_dir):
        """Test integration behavior when validation fails."""
        # Create database with invalid structure that will cause validation to fail
        invalid_data = {
            "version": "2.0.0",
            "total_questions": 5,  # Mismatch with actual questions
            "questions": [{"id": "q001"}, {"id": "q003"}]  # Missing q002
        }
        
        database_path = temp_dir / "questions.json"
        with open(database_path, 'w', encoding='utf-8') as f:
            json.dump(invalid_data, f, ensure_ascii=False, indent=2)
        
        # Mock the agent to return success but the validation will fail
        result = db_integration_agent.integrate_batch_with_structured_output(
            sample_question_batch,
            create_backup=True
        )
        
        # The integration should detect validation issues
        assert not result.validation_passed or len(result.issues) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
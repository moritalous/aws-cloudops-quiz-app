"""
Database Integration Agent for AWS CloudOps Question Generation System.

This module implements an AI-powered agent that handles the integration of
generated question batches into the existing questions.json database with
structured output, ID continuity, metadata updates, backup/rollback functionality,
and JSON structure integrity validation.
"""

import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

# Strands Agents imports
from strands import Agent

# Local imports
from models import (
    QuestionBatch, QuestionDatabase, IntegrationResult, 
    DatabaseBackup, Question
)
from core.error_handling import (
    QuestionGenerationError, ValidationError, retry_with_backoff
)

logger = logging.getLogger(__name__)


class DatabaseIntegrationAgent:
    """
    AI-powered agent for database integration with structured output.
    
    This agent handles the complete integration process including:
    - JSON integration with structured output
    - Question ID continuity guarantee
    - Automatic metadata updates
    - Backup and rollback functionality
    - JSON structure integrity validation
    """
    
    def __init__(self, agent: Agent, database_path: str, backup_dir: str = "backups"):
        """
        Initialize the Database Integration Agent.
        
        Args:
            agent: Configured Strands Agent for structured output
            database_path: Path to the questions.json file
            backup_dir: Directory for storing backups
        """
        self.agent = agent
        self.database_path = Path(database_path)
        self.backup_dir = Path(backup_dir)
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(exist_ok=True)
        
        logger.info(f"DatabaseIntegrationAgent initialized with database: {database_path}")
    
    def create_backup(self, batch_number: Optional[int] = None) -> DatabaseBackup:
        """
        Create a backup of the current database before integration.
        
        Args:
            batch_number: Optional batch number for backup identification
            
        Returns:
            DatabaseBackup information
            
        Raises:
            QuestionGenerationError: If backup creation fails
        """
        try:
            if not self.database_path.exists():
                raise QuestionGenerationError(f"Database file not found: {self.database_path}")
            
            # Generate backup ID and path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            batch_suffix = f"_batch{batch_number:02d}" if batch_number else ""
            backup_id = f"questions_backup_{timestamp}{batch_suffix}"
            backup_path = self.backup_dir / f"{backup_id}.json"
            
            # Copy the database file
            shutil.copy2(self.database_path, backup_path)
            
            # Calculate checksum for integrity verification
            checksum = self._calculate_checksum(backup_path)
            
            # Get file size and question count
            backup_size = backup_path.stat().st_size
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
                questions_count = len(backup_data.get('questions', []))
            
            backup_info = DatabaseBackup(
                backup_id=backup_id,
                original_file_path=str(self.database_path),
                backup_file_path=str(backup_path),
                backup_size_bytes=backup_size,
                questions_count=questions_count,
                created_before_batch=batch_number,
                checksum=checksum
            )
            
            logger.info(f"Created backup: {backup_id} ({questions_count} questions)")
            return backup_info
            
        except Exception as e:
            error_msg = f"Failed to create backup: {str(e)}"
            logger.error(error_msg)
            raise QuestionGenerationError(error_msg) from e
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def validate_json_structure(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate JSON structure integrity.
        
        Args:
            data: JSON data to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        try:
            # Check required top-level fields
            required_fields = [
                'version', 'generated_at', 'total_questions', 
                'domains', 'difficulty', 'question_types', 'questions'
            ]
            
            for field in required_fields:
                if field not in data:
                    issues.append(f"Missing required field: {field}")
            
            # Validate questions array
            questions = data.get('questions', [])
            if not isinstance(questions, list):
                issues.append("'questions' must be an array")
            else:
                # Check question ID sequence
                expected_ids = [f'q{i:03d}' for i in range(1, len(questions) + 1)]
                actual_ids = [q.get('id', '') for q in questions if isinstance(q, dict)]
                
                if len(actual_ids) != len(questions):
                    issues.append("Some questions missing 'id' field")
                elif actual_ids != expected_ids[:len(actual_ids)]:
                    issues.append("Question ID sequence is not continuous")
            
            # Validate metadata consistency
            total_questions = data.get('total_questions', 0)
            if len(questions) != total_questions:
                issues.append(f"Question count mismatch: {len(questions)} vs {total_questions}")
            
            # Validate domain distribution
            domains = data.get('domains', {})
            if isinstance(domains, dict):
                domain_sum = sum(domains.values())
                if domain_sum != total_questions:
                    issues.append(f"Domain distribution sum ({domain_sum}) != total questions ({total_questions})")
            
            # Validate difficulty distribution
            difficulty = data.get('difficulty', {})
            if isinstance(difficulty, dict):
                difficulty_sum = sum(difficulty.values())
                if difficulty_sum != total_questions:
                    issues.append(f"Difficulty distribution sum ({difficulty_sum}) != total questions ({total_questions})")
            
            # Validate question types distribution
            question_types = data.get('question_types', {})
            if isinstance(question_types, dict):
                types_sum = sum(question_types.values())
                if types_sum != total_questions:
                    issues.append(f"Question types sum ({types_sum}) != total questions ({total_questions})")
            
        except Exception as e:
            issues.append(f"JSON structure validation error: {str(e)}")
        
        return len(issues) == 0, issues
    
    def validate_id_continuity(self, questions: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate question ID continuity.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        try:
            if not questions:
                return True, []
            
            # Extract IDs
            question_ids = [q.get('id', '') for q in questions]
            
            # Check for missing IDs
            missing_ids = [i for i, qid in enumerate(question_ids) if not qid]
            if missing_ids:
                issues.append(f"Questions missing IDs at indices: {missing_ids}")
            
            # Check ID format and sequence
            expected_ids = [f'q{i:03d}' for i in range(1, len(questions) + 1)]
            
            for i, (actual, expected) in enumerate(zip(question_ids, expected_ids)):
                if actual != expected:
                    issues.append(f"ID mismatch at position {i}: expected '{expected}', got '{actual}'")
            
            # Check for duplicates
            seen_ids = set()
            duplicates = []
            for qid in question_ids:
                if qid in seen_ids:
                    duplicates.append(qid)
                seen_ids.add(qid)
            
            if duplicates:
                issues.append(f"Duplicate question IDs: {duplicates}")
            
        except Exception as e:
            issues.append(f"ID continuity validation error: {str(e)}")
        
        return len(issues) == 0, issues
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def integrate_batch_with_structured_output(
        self, 
        question_batch: QuestionBatch,
        create_backup: bool = True
    ) -> IntegrationResult:
        """
        Integrate a question batch using AI structured output.
        
        Args:
            question_batch: Batch of questions to integrate
            create_backup: Whether to create backup before integration
            
        Returns:
            IntegrationResult with detailed integration information
            
        Raises:
            QuestionGenerationError: If integration fails
        """
        start_time = datetime.now()
        backup_info = None
        
        try:
            logger.info(f"Starting integration of batch {question_batch.batch_number}")
            
            # Create backup if requested
            if create_backup:
                backup_info = self.create_backup(question_batch.batch_number)
            
            # Load current database
            if self.database_path.exists():
                with open(self.database_path, 'r', encoding='utf-8') as f:
                    current_data = json.load(f)
            else:
                # Initialize empty database structure
                current_data = {
                    "version": "2.0.0",
                    "generated_at": datetime.now().isoformat(),
                    "generation_method": "AI-Strands-Agents-Bedrock",
                    "total_questions": 0,
                    "domains": {"monitoring": 0, "reliability": 0, "deployment": 0, "security": 0, "networking": 0},
                    "difficulty": {"easy": 0, "medium": 0, "hard": 0},
                    "question_types": {"single": 0, "multiple": 0},
                    "questions": []
                }
            
            # Prepare integration prompt for AI agent
            integration_prompt = f"""
            以下の新しい問題バッチを既存のデータベースに統合してください：

            現在のデータベース:
            {json.dumps(current_data, ensure_ascii=False, indent=2)}

            新しい問題バッチ:
            {question_batch.model_dump_json(indent=2)}

            統合要件：
            1. 既存問題の完全保持
            2. ID連続性の確保（q001, q002, ...）
            3. メタデータの正確な更新（total_questions, domains, difficulty, question_types）
            4. JSON構造の整合性維持
            5. 新しい問題を既存問題の後に追加
            6. generated_at フィールドの更新

            統合処理の詳細な結果を構造化された形式で報告してください。
            統合後のデータベース全体を含めて返してください。
            """
            
            # Use structured output to get integration result
            integration_result = self.agent.structured_output(
                IntegrationResult,
                integration_prompt
            )
            
            # Extract integrated database from the AI response
            # Note: In a real implementation, we would need to modify the prompt
            # to also return the integrated database structure
            
            # For now, perform the integration manually based on the AI guidance
            integrated_data = self._perform_integration(current_data, question_batch)
            
            # Validate the integrated data
            structure_valid, structure_issues = self.validate_json_structure(integrated_data)
            id_valid, id_issues = self.validate_id_continuity(integrated_data['questions'])
            
            all_issues = structure_issues + id_issues
            validation_passed = structure_valid and id_valid
            
            if validation_passed:
                # Write the integrated data back to file
                with open(self.database_path, 'w', encoding='utf-8') as f:
                    json.dump(integrated_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"Successfully integrated batch {question_batch.batch_number}")
            else:
                logger.error(f"Integration validation failed: {all_issues}")
                # Restore from backup if available
                if backup_info:
                    self._restore_from_backup(backup_info)
            
            # Calculate integration time
            integration_time = (datetime.now() - start_time).total_seconds()
            
            # Update integration result with actual values
            integration_result.success = validation_passed
            integration_result.batch_number = question_batch.batch_number
            integration_result.questions_added = len(question_batch.questions) if validation_passed else 0
            integration_result.new_total_questions = integrated_data['total_questions']
            integration_result.added_question_ids = [q.id for q in question_batch.questions] if validation_passed else []
            integration_result.updated_metadata = {
                'domains': integrated_data['domains'],
                'difficulty': integrated_data['difficulty'],
                'question_types': integrated_data['question_types']
            }
            integration_result.validation_passed = validation_passed
            integration_result.schema_compliance = structure_valid
            integration_result.id_sequence_valid = id_valid
            integration_result.backup_created = backup_info is not None
            integration_result.backup_path = str(backup_info.backup_file_path) if backup_info else None
            integration_result.integration_time_seconds = integration_time
            integration_result.issues = all_issues
            integration_result.rollback_available = backup_info is not None
            integration_result.rollback_instructions = f"Use restore_from_backup with backup_id: {backup_info.backup_id}" if backup_info else None
            
            return integration_result
            
        except Exception as e:
            error_msg = f"Failed to integrate batch {question_batch.batch_number}: {str(e)}"
            logger.error(error_msg)
            
            # Restore from backup if available
            if backup_info:
                try:
                    self._restore_from_backup(backup_info)
                    logger.info("Restored database from backup after integration failure")
                except Exception as restore_error:
                    logger.error(f"Failed to restore from backup: {restore_error}")
            
            raise QuestionGenerationError(error_msg) from e
    
    def _perform_integration(self, current_data: Dict[str, Any], question_batch: QuestionBatch) -> Dict[str, Any]:
        """
        Perform the actual integration of questions into the database.
        
        Args:
            current_data: Current database data
            question_batch: Batch of questions to integrate
            
        Returns:
            Integrated database data
        """
        # Create a copy of current data
        integrated_data = current_data.copy()
        
        # Add new questions
        current_questions = integrated_data.get('questions', [])
        new_questions = [q.model_dump() for q in question_batch.questions]
        
        # Ensure proper ID assignment
        next_id_num = len(current_questions) + 1
        for i, question in enumerate(new_questions):
            question['id'] = f'q{next_id_num + i:03d}'
        
        # Combine questions
        integrated_data['questions'] = current_questions + new_questions
        
        # Update metadata
        integrated_data['total_questions'] = len(integrated_data['questions'])
        integrated_data['generated_at'] = datetime.now().isoformat()
        
        # Update domain distribution
        domains = integrated_data.get('domains', {})
        for question in new_questions:
            domain = question.get('domain', '')
            if domain in domains:
                domains[domain] += 1
        
        # Update difficulty distribution
        difficulty = integrated_data.get('difficulty', {})
        for question in new_questions:
            diff = question.get('difficulty', '')
            if diff in difficulty:
                difficulty[diff] += 1
        
        # Update question types distribution
        question_types = integrated_data.get('question_types', {})
        for question in new_questions:
            qtype = question.get('type', '')
            if qtype in question_types:
                question_types[qtype] += 1
        
        return integrated_data
    
    def _restore_from_backup(self, backup_info: DatabaseBackup) -> None:
        """
        Restore database from backup.
        
        Args:
            backup_info: Backup information
            
        Raises:
            QuestionGenerationError: If restoration fails
        """
        try:
            backup_path = Path(backup_info.backup_file_path)
            
            if not backup_path.exists():
                raise QuestionGenerationError(f"Backup file not found: {backup_path}")
            
            # Verify backup integrity
            current_checksum = self._calculate_checksum(backup_path)
            if backup_info.checksum and current_checksum != backup_info.checksum:
                raise QuestionGenerationError("Backup file integrity check failed")
            
            # Restore the backup
            shutil.copy2(backup_path, self.database_path)
            
            logger.info(f"Successfully restored database from backup: {backup_info.backup_id}")
            
        except Exception as e:
            error_msg = f"Failed to restore from backup {backup_info.backup_id}: {str(e)}"
            logger.error(error_msg)
            raise QuestionGenerationError(error_msg) from e
    
    def restore_from_backup(self, backup_id: str) -> bool:
        """
        Restore database from a specific backup.
        
        Args:
            backup_id: ID of the backup to restore
            
        Returns:
            True if restoration successful, False otherwise
        """
        try:
            backup_path = self.backup_dir / f"{backup_id}.json"
            
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Create a backup of current state before restoration
            current_backup = self.create_backup()
            logger.info(f"Created safety backup before restoration: {current_backup.backup_id}")
            
            # Restore from the specified backup
            shutil.copy2(backup_path, self.database_path)
            
            logger.info(f"Successfully restored database from backup: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore from backup {backup_id}: {str(e)}")
            return False
    
    def list_backups(self) -> List[DatabaseBackup]:
        """
        List all available backups.
        
        Returns:
            List of DatabaseBackup information
        """
        backups = []
        
        try:
            for backup_file in self.backup_dir.glob("questions_backup_*.json"):
                try:
                    # Parse backup filename to extract info
                    backup_id = backup_file.stem
                    
                    # Get file stats
                    stat = backup_file.stat()
                    
                    # Load backup to get question count
                    with open(backup_file, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                        questions_count = len(backup_data.get('questions', []))
                    
                    backup_info = DatabaseBackup(
                        backup_id=backup_id,
                        original_file_path=str(self.database_path),
                        backup_file_path=str(backup_file),
                        backup_size_bytes=stat.st_size,
                        questions_count=questions_count,
                        created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        checksum=self._calculate_checksum(backup_file)
                    )
                    
                    backups.append(backup_info)
                    
                except Exception as e:
                    logger.warning(f"Failed to process backup file {backup_file}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x.created_at, reverse=True)
        
        return backups
    
    def create_final_database_with_structured_output(
        self, 
        integration_results: List[IntegrationResult]
    ) -> QuestionDatabase:
        """
        Create final database structure using AI structured output.
        
        Args:
            integration_results: List of all integration results
            
        Returns:
            Complete QuestionDatabase structure
            
        Raises:
            QuestionGenerationError: If database creation fails
        """
        try:
            logger.info("Creating final database structure with AI structured output")
            
            # Load current database
            with open(self.database_path, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            
            # Prepare prompt for AI agent
            database_creation_prompt = f"""
            以下の統合結果から最終的な200問のデータベース構造を構築してください：

            現在のデータベース:
            {json.dumps(current_data, ensure_ascii=False, indent=2)}

            統合結果履歴:
            {json.dumps([result.model_dump() for result in integration_results], ensure_ascii=False, indent=2)}

            要件：
            1. 正確に200問を含む完全なデータベース構造
            2. 適切なメタデータと統計情報
            3. 品質メトリクスの計算
            4. 生成統計の更新
            5. 互換性情報の確認
            6. AWSサービスとトピックの一覧作成

            完全なQuestionDatabaseモデルに準拠した構造化出力を提供してください。
            """
            
            # Use structured output to create final database
            final_database = self.agent.structured_output(
                QuestionDatabase,
                database_creation_prompt
            )
            
            # Validate the final database
            try:
                # This will trigger Pydantic validation
                final_database.model_validate(final_database.model_dump())
                logger.info("Final database structure validation passed")
            except Exception as validation_error:
                logger.error(f"Final database validation failed: {validation_error}")
                raise ValidationError(f"Final database validation failed: {validation_error}")
            
            # Update the actual database file with the final structure
            with open(self.database_path, 'w', encoding='utf-8') as f:
                json.dump(final_database.model_dump(), f, ensure_ascii=False, indent=2)
            
            logger.info("Successfully created final database structure")
            return final_database
            
        except Exception as e:
            error_msg = f"Failed to create final database structure: {str(e)}"
            logger.error(error_msg)
            raise QuestionGenerationError(error_msg) from e
    
    def validate_database_integrity(self) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Perform comprehensive database integrity validation.
        
        Returns:
            Tuple of (is_valid, issues_list, validation_report)
        """
        issues = []
        report = {
            'validation_time': datetime.now().isoformat(),
            'file_exists': False,
            'file_size_bytes': 0,
            'json_valid': False,
            'structure_valid': False,
            'id_continuity_valid': False,
            'metadata_consistent': False,
            'question_count': 0,
            'expected_question_count': 200
        }
        
        try:
            # Check file existence
            if not self.database_path.exists():
                issues.append(f"Database file does not exist: {self.database_path}")
                return False, issues, report
            
            report['file_exists'] = True
            report['file_size_bytes'] = self.database_path.stat().st_size
            
            # Load and validate JSON
            try:
                with open(self.database_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                report['json_valid'] = True
            except json.JSONDecodeError as e:
                issues.append(f"Invalid JSON format: {str(e)}")
                return False, issues, report
            
            # Validate structure
            structure_valid, structure_issues = self.validate_json_structure(data)
            report['structure_valid'] = structure_valid
            issues.extend(structure_issues)
            
            # Validate ID continuity
            questions = data.get('questions', [])
            report['question_count'] = len(questions)
            
            id_valid, id_issues = self.validate_id_continuity(questions)
            report['id_continuity_valid'] = id_valid
            issues.extend(id_issues)
            
            # Check metadata consistency
            total_questions = data.get('total_questions', 0)
            if len(questions) == total_questions == 200:
                report['metadata_consistent'] = True
            else:
                issues.append(f"Metadata inconsistency: file has {len(questions)} questions, metadata says {total_questions}, expected 200")
            
            # Overall validation
            is_valid = (
                report['json_valid'] and 
                report['structure_valid'] and 
                report['id_continuity_valid'] and 
                report['metadata_consistent']
            )
            
            if is_valid:
                logger.info("Database integrity validation passed")
            else:
                logger.warning(f"Database integrity validation failed with {len(issues)} issues")
            
            return is_valid, issues, report
            
        except Exception as e:
            issues.append(f"Validation error: {str(e)}")
            logger.error(f"Database integrity validation error: {str(e)}")
            return False, issues, report
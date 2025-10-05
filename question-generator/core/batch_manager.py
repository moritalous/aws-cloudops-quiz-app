"""
AI-driven batch management agent for intelligent question generation planning.

This module implements the integrated batch management agent that uses structured
output to analyze current database state, plan optimal batches, track progress,
and manage the overall question generation process with interruption/resumption
capabilities.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio

from strands import Agent

from models.batch_models import DatabaseState, BatchPlan, ProgressReport
from models.exam_guide_models import ExamGuideAnalysis
from models.question_models import Question, QuestionBatch
from core.agent_factory import AgentFactory
from config.settings import get_settings

logger = logging.getLogger(__name__)


class BatchManagerAgent:
    """
    AI-driven batch management agent for intelligent question generation.
    
    This agent uses structured output to:
    - Analyze current database state
    - Generate optimal batch plans
    - Track progress and provide reports
    - Handle interruption and resumption
    """
    
    def __init__(self, agent_factory: AgentFactory):
        """
        Initialize the batch management agent.
        
        Args:
            agent_factory: Factory for creating AI agents
        """
        self.agent_factory = agent_factory
        self.settings = get_settings()
        self.batch_manager_agent = agent_factory.create_batch_manager()
        
        # State management
        self.current_state: Optional[DatabaseState] = None
        self.current_batch_plan: Optional[BatchPlan] = None
        self.progress_history: List[ProgressReport] = []
        
        # Persistence paths
        self.state_file = self.settings.agent_config.output_directory / "batch_state.json"
        self.progress_file = self.settings.agent_config.output_directory / "progress_history.json"
        
        logger.info("BatchManagerAgent initialized")
    
    async def analyze_current_state(self, questions_file_path: Optional[Path] = None) -> DatabaseState:
        """
        Analyze the current state of the question database using AI.
        
        Args:
            questions_file_path: Path to questions.json file
            
        Returns:
            DatabaseState with current analysis
        """
        if questions_file_path is None:
            questions_file_path = self.settings.questions_file_path
        
        logger.info(f"Analyzing current database state from: {questions_file_path}")
        
        try:
            # Read current questions database
            current_data = ""
            if questions_file_path.exists():
                with open(questions_file_path, 'r', encoding='utf-8') as f:
                    current_data = f.read()
            else:
                logger.warning(f"Questions file not found: {questions_file_path}")
                current_data = '{"questions": [], "metadata": {"total": 0}}'
            
            # Use AI agent to analyze current state with structured output
            analysis_prompt = f"""
            現在の問題データベースを詳細に分析し、構造化された状態情報を提供してください。

            現在のquestions.jsonデータ:
            {current_data}

            分析要件:
            1. 総問題数と既存問題数の正確な計算
            2. ドメイン別配分の現状分析
            3. 難易度別配分の現状分析
            4. 問題タイプ別配分の現状分析
            5. カバー済みトピックとAWSサービスの抽出
            6. 目標配分との差分計算
            7. 完了率の計算

            目標配分:
            - 総問題数: 200問
            - ドメイン配分: monitoring(44), reliability(44), deployment(44), security(32), networking(36)
            - 難易度配分: easy(60), medium(100), hard(40)
            - 問題タイプ配分: single(160), multiple(40)

            DatabaseStateモデルに準拠した構造化出力を提供してください。
            """
            
            # Get structured output from AI agent
            database_state = await self.batch_manager_agent.structured_output_async(
                DatabaseState,
                analysis_prompt
            )
            
            # Cache the current state
            self.current_state = database_state
            
            # Save state to file for persistence
            await self._save_state()
            
            logger.info(f"Database state analyzed: {database_state.total_questions} questions, "
                       f"{database_state.completion_percentage:.1f}% complete")
            
            return database_state
            
        except Exception as e:
            logger.error(f"Failed to analyze current state: {e}")
            raise
    
    async def plan_next_batch(
        self, 
        current_state: Optional[DatabaseState] = None,
        exam_guide_analysis: Optional[ExamGuideAnalysis] = None
    ) -> BatchPlan:
        """
        Generate an optimal plan for the next batch using AI.
        
        Args:
            current_state: Current database state (will analyze if None)
            exam_guide_analysis: Exam guide analysis for reference
            
        Returns:
            BatchPlan for the next batch
        """
        if current_state is None:
            current_state = await self.analyze_current_state()
        
        logger.info(f"Planning next batch (batch #{self._calculate_next_batch_number(current_state)})")
        
        try:
            # Load exam guide analysis if not provided
            if exam_guide_analysis is None:
                exam_guide_analysis = await self._load_exam_guide_analysis()
            
            # Calculate next batch number
            next_batch_number = self._calculate_next_batch_number(current_state)
            
            # Use AI agent to create optimal batch plan
            planning_prompt = f"""
            現在の状況を分析し、次のバッチ（第{next_batch_number}バッチ）の最適な実行計画を作成してください。

            現在のデータベース状態:
            {current_state.model_dump_json(indent=2)}

            試験ガイド分析:
            {exam_guide_analysis.model_dump_json(indent=2) if exam_guide_analysis else "利用不可"}

            計画要件:
            1. ドメイン配分の目標達成を優先
            2. 難易度バランスの維持
            3. 問題タイプ配分の調整
            4. トピック重複の回避
            5. 効率的なAWSドキュメント検索クエリの生成
            6. 品質要件の設定
            7. 戦略的ノートの提供

            考慮事項:
            - 残り必要問題数: {200 - current_state.total_questions}問
            - 最も不足しているドメインを優先
            - 過去にカバーしたトピックの重複回避
            - 実行可能で具体的な計画

            BatchPlanモデルに準拠した構造化出力を提供してください。
            """
            
            # Get structured output from AI agent
            batch_plan = await self.batch_manager_agent.structured_output_async(
                BatchPlan,
                planning_prompt
            )
            
            # Cache the current batch plan
            self.current_batch_plan = batch_plan
            
            # Save state to file for persistence
            await self._save_state()
            
            logger.info(f"Batch plan created: Domain={batch_plan.target_domain}, "
                       f"Difficulties={batch_plan.target_difficulties}, "
                       f"Estimated time={batch_plan.estimated_completion_time}min")
            
            return batch_plan
            
        except Exception as e:
            logger.error(f"Failed to plan next batch: {e}")
            raise
    
    async def generate_progress_report(
        self, 
        current_state: Optional[DatabaseState] = None
    ) -> ProgressReport:
        """
        Generate a comprehensive progress report using AI.
        
        Args:
            current_state: Current database state (will analyze if None)
            
        Returns:
            ProgressReport with detailed progress analysis
        """
        if current_state is None:
            current_state = await self.analyze_current_state()
        
        logger.info("Generating progress report")
        
        try:
            # Calculate performance metrics
            performance_metrics = await self._calculate_performance_metrics()
            
            # Use AI agent to generate comprehensive progress report
            report_prompt = f"""
            現在の進捗状況を分析し、包括的な進捗レポートを作成してください。

            現在のデータベース状態:
            {current_state.model_dump_json(indent=2)}

            パフォーマンスメトリクス:
            {json.dumps(performance_metrics, indent=2, ensure_ascii=False)}

            過去の進捗履歴:
            {json.dumps([report.model_dump() for report in self.progress_history[-5:]], indent=2, ensure_ascii=False)}

            レポート要件:
            1. 全体進捗率と残り作業量の計算
            2. ドメイン別・難易度別進捗の詳細分析
            3. 品質メトリクスの評価
            4. 完了速度と残り時間の推定
            5. ボトルネックの特定
            6. 最適化提案の提供
            7. リスク評価とマイルストーン状況
            8. 次のバッチのプレビュー

            ProgressReportモデルに準拠した構造化出力を提供してください。
            """
            
            # Get structured output from AI agent
            progress_report = await self.batch_manager_agent.structured_output_async(
                ProgressReport,
                report_prompt
            )
            
            # Add to progress history
            self.progress_history.append(progress_report)
            
            # Keep only last 20 reports to manage memory
            if len(self.progress_history) > 20:
                self.progress_history = self.progress_history[-20:]
            
            # Save progress history
            await self._save_progress_history()
            
            logger.info(f"Progress report generated: {progress_report.current_progress:.1f}% complete, "
                       f"{progress_report.questions_remaining} questions remaining")
            
            return progress_report
            
        except Exception as e:
            logger.error(f"Failed to generate progress report: {e}")
            raise
    
    async def save_checkpoint(self, checkpoint_name: Optional[str] = None) -> Path:
        """
        Save current state as a checkpoint for resumption.
        
        Args:
            checkpoint_name: Optional name for the checkpoint
            
        Returns:
            Path to the saved checkpoint file
        """
        if checkpoint_name is None:
            checkpoint_name = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        checkpoint_path = self.settings.agent_config.backup_directory / f"{checkpoint_name}.json"
        
        logger.info(f"Saving checkpoint: {checkpoint_path}")
        
        try:
            checkpoint_data = {
                "timestamp": datetime.now().isoformat(),
                "current_state": self.current_state.model_dump() if self.current_state else None,
                "current_batch_plan": self.current_batch_plan.model_dump() if self.current_batch_plan else None,
                "progress_history": [report.model_dump() for report in self.progress_history],
                "settings": {
                    "target_questions": self.settings.target_questions,
                    "existing_questions": self.settings.existing_questions,
                    "batch_size": self.settings.agent_config.batch_size
                }
            }
            
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Checkpoint saved successfully: {checkpoint_path}")
            return checkpoint_path
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
            raise
    
    async def load_checkpoint(self, checkpoint_path: Path) -> bool:
        """
        Load state from a checkpoint file.
        
        Args:
            checkpoint_path: Path to the checkpoint file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        logger.info(f"Loading checkpoint: {checkpoint_path}")
        
        try:
            if not checkpoint_path.exists():
                logger.error(f"Checkpoint file not found: {checkpoint_path}")
                return False
            
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            # Restore state
            if checkpoint_data.get("current_state"):
                self.current_state = DatabaseState(**checkpoint_data["current_state"])
            
            if checkpoint_data.get("current_batch_plan"):
                self.current_batch_plan = BatchPlan(**checkpoint_data["current_batch_plan"])
            
            if checkpoint_data.get("progress_history"):
                self.progress_history = [
                    ProgressReport(**report_data) 
                    for report_data in checkpoint_data["progress_history"]
                ]
            
            logger.info(f"Checkpoint loaded successfully from: {checkpoint_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return False
    
    async def can_resume(self) -> bool:
        """
        Check if the generation process can be resumed from saved state.
        
        Returns:
            True if resumption is possible, False otherwise
        """
        try:
            # Check if state file exists and is recent
            if not self.state_file.exists():
                return False
            
            # Check if state file is not too old (24 hours)
            state_age = datetime.now() - datetime.fromtimestamp(self.state_file.stat().st_mtime)
            if state_age > timedelta(hours=24):
                logger.warning("State file is too old for resumption")
                return False
            
            # Try to load and validate state
            await self._load_state()
            
            if self.current_state is None:
                return False
            
            # Check if there's still work to do
            if self.current_state.total_questions >= self.settings.target_questions:
                logger.info("All questions already generated, no resumption needed")
                return False
            
            logger.info("Resumption is possible")
            return True
            
        except Exception as e:
            logger.error(f"Failed to check resumption capability: {e}")
            return False
    
    async def resume_generation(self) -> bool:
        """
        Resume the generation process from saved state.
        
        Returns:
            True if resumed successfully, False otherwise
        """
        logger.info("Attempting to resume generation process")
        
        try:
            if not await self.can_resume():
                logger.error("Cannot resume generation process")
                return False
            
            # Load saved state
            await self._load_state()
            await self._load_progress_history()
            
            logger.info(f"Generation process resumed from {self.current_state.total_questions} questions")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume generation process: {e}")
            return False
    
    def _calculate_next_batch_number(self, current_state: DatabaseState) -> int:
        """Calculate the next batch number based on current state."""
        questions_generated = current_state.total_questions - self.settings.existing_questions
        batch_size = self.settings.agent_config.batch_size
        return (questions_generated // batch_size) + 1
    
    async def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics from progress history."""
        metrics = {
            "total_time_spent": 0,
            "average_batch_time": 0,
            "questions_per_hour": 0,
            "average_quality_score": 0,
            "batch_success_rate": 100.0,
            "total_batches_completed": len(self.progress_history)
        }
        
        if not self.progress_history:
            return metrics
        
        # Calculate time-based metrics
        if len(self.progress_history) > 1:
            first_report = self.progress_history[0]
            last_report = self.progress_history[-1]
            
            first_time = datetime.fromisoformat(first_report.generated_at)
            last_time = datetime.fromisoformat(last_report.generated_at)
            
            total_time_hours = (last_time - first_time).total_seconds() / 3600
            metrics["total_time_spent"] = total_time_hours * 60  # in minutes
            
            if total_time_hours > 0:
                questions_completed = last_report.questions_completed - first_report.questions_completed
                metrics["questions_per_hour"] = questions_completed / total_time_hours
        
        # Calculate quality metrics
        quality_scores = []
        for report in self.progress_history:
            if "average_quality_score" in report.quality_metrics:
                quality_scores.append(report.quality_metrics["average_quality_score"])
        
        if quality_scores:
            metrics["average_quality_score"] = sum(quality_scores) / len(quality_scores)
        
        return metrics
    
    async def _load_exam_guide_analysis(self) -> Optional[ExamGuideAnalysis]:
        """Load exam guide analysis from file."""
        analysis_file = self.settings.agent_config.output_directory / "exam_guide_analysis.json"
        
        if not analysis_file.exists():
            logger.warning("Exam guide analysis not found")
            return None
        
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            return ExamGuideAnalysis(**analysis_data)
            
        except Exception as e:
            logger.error(f"Failed to load exam guide analysis: {e}")
            return None
    
    async def _save_state(self) -> None:
        """Save current state to file."""
        try:
            state_data = {
                "timestamp": datetime.now().isoformat(),
                "current_state": self.current_state.model_dump() if self.current_state else None,
                "current_batch_plan": self.current_batch_plan.model_dump() if self.current_batch_plan else None
            }
            
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    async def _load_state(self) -> None:
        """Load state from file."""
        try:
            if not self.state_file.exists():
                return
            
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            
            if state_data.get("current_state"):
                self.current_state = DatabaseState(**state_data["current_state"])
            
            if state_data.get("current_batch_plan"):
                self.current_batch_plan = BatchPlan(**state_data["current_batch_plan"])
                
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
    
    async def _save_progress_history(self) -> None:
        """Save progress history to file."""
        try:
            history_data = {
                "timestamp": datetime.now().isoformat(),
                "progress_history": [report.model_dump() for report in self.progress_history]
            }
            
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save progress history: {e}")
    
    async def _load_progress_history(self) -> None:
        """Load progress history from file."""
        try:
            if not self.progress_file.exists():
                return
            
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            if history_data.get("progress_history"):
                self.progress_history = [
                    ProgressReport(**report_data)
                    for report_data in history_data["progress_history"]
                ]
                
        except Exception as e:
            logger.error(f"Failed to load progress history: {e}")
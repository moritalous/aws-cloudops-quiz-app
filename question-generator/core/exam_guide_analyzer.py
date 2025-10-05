"""
AI-driven exam guide analysis agent for AWS CloudOps certification.

This module implements an AI agent that uses structured output to analyze
the AWS Certified CloudOps Engineer - Associate exam guide and extract
structured information about domains, tasks, skills, and requirements.
"""

import logging
from pathlib import Path
from typing import Optional

from strands import Agent

from models.exam_guide_models import ExamGuideAnalysis
from config import get_settings
from core.agent_factory import AgentFactory
from core.error_handling import ExamGuideAnalysisError, retry_with_backoff

logger = logging.getLogger(__name__)


class ExamGuideAnalyzer:
    """
    AI-powered exam guide analyzer using Strands Agents with structured output.
    
    This class provides functionality to analyze AWS certification exam guides
    and extract structured information using AI with Pydantic model validation.
    """
    
    def __init__(self, agent_factory: Optional[AgentFactory] = None):
        """
        Initialize the exam guide analyzer.
        
        Args:
            agent_factory: Optional AgentFactory instance. If None, creates default.
        """
        self.settings = get_settings()
        
        if agent_factory is None:
            self.agent_factory = AgentFactory(self.settings.agent_config)
        else:
            self.agent_factory = agent_factory
        
        self.analyzer_agent: Optional[Agent] = None
        
        logger.info("ExamGuideAnalyzer initialized")
    
    def _get_analyzer_agent(self) -> Agent:
        """Get or create the exam guide analyzer agent."""
        if self.analyzer_agent is None:
            self.analyzer_agent = self.agent_factory.create_exam_guide_analyzer()
        return self.analyzer_agent
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def analyze_exam_guide(
        self, 
        guide_path: str | Path,
        target_questions: int = 200
    ) -> ExamGuideAnalysis:
        """
        Analyze the AWS CloudOps exam guide using AI with structured output.
        
        Args:
            guide_path: Path to the exam guide file (markdown or text)
            target_questions: Target number of questions to generate (default: 200)
        
        Returns:
            ExamGuideAnalysis: Structured analysis results
        
        Raises:
            ExamGuideAnalysisError: If analysis fails
            FileNotFoundError: If guide file doesn't exist
        """
        try:
            guide_path = Path(guide_path)
            
            if not guide_path.exists():
                raise FileNotFoundError(f"Exam guide file not found: {guide_path}")
            
            logger.info(f"Starting AI analysis of exam guide: {guide_path}")
            
            # Read the exam guide content
            with open(guide_path, 'r', encoding='utf-8') as f:
                guide_content = f.read()
            
            logger.info(f"Read exam guide content: {len(guide_content)} characters")
            
            # Get the analyzer agent
            analyzer_agent = self._get_analyzer_agent()
            
            # Create the analysis prompt
            analysis_prompt = self._create_analysis_prompt(guide_content, target_questions)
            
            logger.info("Executing AI analysis with structured output")
            
            # Use structured output to get type-safe results
            analysis_result = analyzer_agent.structured_output(
                ExamGuideAnalysis,
                analysis_prompt
            )
            
            logger.info(f"AI analysis completed successfully")
            logger.info(f"Analyzed {len(analysis_result.domains)} domains")
            logger.info(f"Total tasks identified: {analysis_result.analysis_metadata['total_tasks_identified']}")
            logger.info(f"Total skills identified: {analysis_result.analysis_metadata['total_skills_identified']}")
            
            # Validate the analysis results
            self._validate_analysis_results(analysis_result, target_questions)
            
            return analysis_result
            
        except Exception as e:
            error_msg = f"Failed to analyze exam guide {guide_path}: {str(e)}"
            logger.error(error_msg)
            raise ExamGuideAnalysisError(error_msg) from e
    
    def _create_analysis_prompt(self, guide_content: str, target_questions: int) -> str:
        """
        Create the analysis prompt for the AI agent.
        
        Args:
            guide_content: Content of the exam guide
            target_questions: Target number of questions
        
        Returns:
            Formatted analysis prompt
        """
        prompt = f"""
以下のAWS Certified CloudOps Engineer - Associate (SOA-C03) 試験ガイドを詳細に分析し、
構造化された形式で情報を抽出してください。

試験ガイド内容:
{guide_content}

分析要件:
1. 総問題数: {target_questions}問
2. 各ドメインの重み付けに基づいた問題数配分の計算
3. 各ドメイン内のタスクとスキルの階層的抽出
4. 関連AWSサービスの特定
5. 難易度レベルの推定
6. 技術キーワードの抽出

分析指針:
- 試験ガイドに明記された重み付け（パーセンテージ）を正確に使用
- Content Domain 1: 22% → 約44問
- Content Domain 2: 22% → 約44問  
- Content Domain 3: 22% → 約44問
- Content Domain 4: 16% → 約32問
- Content Domain 5: 18% → 約36問
- 各タスクとスキルを詳細に分析し、実装可能な問題生成計画を作成
- AWSサービス名は正確に抽出（略語と正式名称の両方を考慮）
- 難易度は試験レベル（Associate）に適した分布を設定

出力は必ずExamGuideAnalysisのPydanticモデル構造に従ってください。
"""
        return prompt
    
    def _validate_analysis_results(
        self, 
        analysis: ExamGuideAnalysis, 
        target_questions: int
    ) -> None:
        """
        Validate the analysis results for completeness and accuracy.
        
        Args:
            analysis: Analysis results to validate
            target_questions: Expected total questions
        
        Raises:
            ExamGuideAnalysisError: If validation fails
        """
        # Check total questions
        total_calculated = sum(domain.target_questions for domain in analysis.domains)
        if total_calculated != target_questions:
            logger.warning(
                f"Question count mismatch: calculated {total_calculated}, "
                f"expected {target_questions}"
            )
        
        # Check domain count
        if len(analysis.domains) != 5:
            raise ExamGuideAnalysisError(
                f"Expected 5 domains, found {len(analysis.domains)}"
            )
        
        # Check weight distribution
        total_weight = sum(domain.weight for domain in analysis.domains)
        if abs(total_weight - 100.0) > 1.0:  # Allow 1% tolerance
            raise ExamGuideAnalysisError(
                f"Domain weights don't sum to 100%: {total_weight}%"
            )
        
        # Check each domain has tasks and skills
        for domain in analysis.domains:
            if not domain.tasks:
                raise ExamGuideAnalysisError(
                    f"Domain '{domain.domain}' has no tasks"
                )
            
            for task in domain.tasks:
                if not task.skills:
                    logger.warning(
                        f"Task '{task.task_id}' in domain '{domain.domain}' has no skills"
                    )
        
        logger.info("Analysis validation completed successfully")
    
    def save_analysis_results(
        self, 
        analysis: ExamGuideAnalysis, 
        output_path: str | Path
    ) -> None:
        """
        Save analysis results to a JSON file.
        
        Args:
            analysis: Analysis results to save
            output_path: Path to save the results
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as JSON with proper formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(analysis.model_dump_json(indent=2))
            
            logger.info(f"Analysis results saved to: {output_path}")
            
        except Exception as e:
            error_msg = f"Failed to save analysis results to {output_path}: {str(e)}"
            logger.error(error_msg)
            raise ExamGuideAnalysisError(error_msg) from e
    
    def load_analysis_results(self, input_path: str | Path) -> ExamGuideAnalysis:
        """
        Load analysis results from a JSON file.
        
        Args:
            input_path: Path to the analysis results file
        
        Returns:
            ExamGuideAnalysis: Loaded analysis results
        
        Raises:
            ExamGuideAnalysisError: If loading fails
        """
        try:
            input_path = Path(input_path)
            
            if not input_path.exists():
                raise FileNotFoundError(f"Analysis file not found: {input_path}")
            
            with open(input_path, 'r', encoding='utf-8') as f:
                data = f.read()
            
            analysis = ExamGuideAnalysis.model_validate_json(data)
            
            logger.info(f"Analysis results loaded from: {input_path}")
            return analysis
            
        except Exception as e:
            error_msg = f"Failed to load analysis results from {input_path}: {str(e)}"
            logger.error(error_msg)
            raise ExamGuideAnalysisError(error_msg) from e
    
    def get_domain_summary(self, analysis: ExamGuideAnalysis) -> dict:
        """
        Get a summary of the domain analysis.
        
        Args:
            analysis: Analysis results
        
        Returns:
            Dictionary with domain summary information
        """
        summary = {
            "total_questions": analysis.total_questions,
            "total_domains": len(analysis.domains),
            "total_tasks": analysis.analysis_metadata["total_tasks_identified"],
            "total_skills": analysis.analysis_metadata["total_skills_identified"],
            "coverage_completeness": analysis.analysis_metadata["coverage_completeness"],
            "domains": []
        }
        
        for domain in analysis.domains:
            domain_info = {
                "domain": domain.domain,
                "name": domain.domain_name,
                "weight": domain.weight,
                "target_questions": domain.target_questions,
                "tasks_count": len(domain.tasks),
                "skills_count": sum(len(task.skills) for task in domain.tasks),
                "key_services": domain.key_services,
                "complexity": domain.complexity_level
            }
            summary["domains"].append(domain_info)
        
        return summary
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up ExamGuideAnalyzer resources")
        if self.agent_factory:
            self.agent_factory.cleanup()
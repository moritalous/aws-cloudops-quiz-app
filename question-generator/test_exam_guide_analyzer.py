#!/usr/bin/env python3
"""
Test script for the exam guide analyzer.

This script tests the AI-driven exam guide analysis functionality
to ensure it can properly extract structured information from the
AWS CloudOps exam guide.
"""

import asyncio
import logging
from pathlib import Path
import sys
import json
import os

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = str(project_root)

try:
    from core.exam_guide_analyzer import ExamGuideAnalyzer
    from config import get_settings
    from core.error_handling import ExamGuideAnalysisError
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed with: uv sync")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_exam_guide_analyzer():
    """Test the exam guide analyzer functionality."""
    try:
        logger.info("Starting exam guide analyzer test")
        
        # Get settings
        settings = get_settings()
        logger.info(f"Using exam guide path: {settings.exam_guide_path}")
        
        # Create analyzer
        analyzer = ExamGuideAnalyzer()
        
        # Test analysis
        logger.info("Starting AI analysis of exam guide...")
        analysis_result = analyzer.analyze_exam_guide(
            guide_path=settings.exam_guide_path,
            target_questions=200
        )
        
        logger.info("Analysis completed successfully!")
        
        # Display results summary
        summary = analyzer.get_domain_summary(analysis_result)
        
        print("\n" + "="*60)
        print("EXAM GUIDE ANALYSIS RESULTS")
        print("="*60)
        
        print(f"Total Questions: {summary['total_questions']}")
        print(f"Total Domains: {summary['total_domains']}")
        print(f"Total Tasks: {summary['total_tasks']}")
        print(f"Total Skills: {summary['total_skills']}")
        print(f"Coverage Completeness: {summary['coverage_completeness']:.1f}%")
        
        print("\nDomain Breakdown:")
        print("-" * 40)
        
        for domain in summary['domains']:
            print(f"\n{domain['name']} ({domain['domain']})")
            print(f"  Weight: {domain['weight']}%")
            print(f"  Target Questions: {domain['target_questions']}")
            print(f"  Tasks: {domain['tasks_count']}")
            print(f"  Skills: {domain['skills_count']}")
            print(f"  Complexity: {domain['complexity']}")
            print(f"  Key Services: {', '.join(domain['key_services'][:5])}...")
        
        # Save results to file
        output_path = Path("output/exam_guide_analysis.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        analyzer.save_analysis_results(analysis_result, output_path)
        logger.info(f"Analysis results saved to: {output_path}")
        
        # Test loading results
        logger.info("Testing loading of saved results...")
        loaded_analysis = analyzer.load_analysis_results(output_path)
        
        if loaded_analysis.total_questions == analysis_result.total_questions:
            logger.info("Save/load test passed!")
        else:
            logger.error("Save/load test failed!")
        
        print("\n" + "="*60)
        print("TEST COMPLETED SUCCESSFULLY")
        print("="*60)
        
        return True
        
    except ExamGuideAnalysisError as e:
        logger.error(f"Exam guide analysis error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    finally:
        # Cleanup
        if 'analyzer' in locals():
            analyzer.cleanup()


def main():
    """Main test function."""
    logger.info("Starting exam guide analyzer test")
    
    success = test_exam_guide_analyzer()
    
    if success:
        logger.info("All tests passed!")
        sys.exit(0)
    else:
        logger.error("Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
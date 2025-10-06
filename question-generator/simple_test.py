#!/usr/bin/env python3
"""
Simple test script to generate a few questions without complex structured output.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

# Import the basic components
from core.agent_factory import AgentFactory
from models.question_models import Question, LearningResource


async def simple_question_generation():
    """Generate a few simple questions for testing."""
    
    print("🧪 Simple Question Generation Test")
    print("=" * 40)
    
    # Initialize agent factory with config
    from config import AgentConfig
    config = AgentConfig()
    agent_factory = AgentFactory(config)
    
    # Create a simple question generator agent
    question_agent = agent_factory.create_question_generator()
    
    # Simple prompt for generating one question
    prompt = """
    AWS CloudOps試験問題を1問生成してください。以下の要件に従ってください：

    要件：
    - ドメイン: monitoring (監視)
    - 難易度: medium
    - 問題タイプ: single (単一選択)
    - 日本語で作成
    - 4つの選択肢 (A, B, C, D)
    - 詳細な解説を含める
    - 学習リソースを1つ以上含める

    以下のJSON形式で回答してください：
    {
        "id": "q012",
        "domain": "monitoring",
        "difficulty": "medium", 
        "type": "single",
        "question": "問題文をここに",
        "options": [
            "A. 選択肢1",
            "B. 選択肢2", 
            "C. 選択肢3",
            "D. 選択肢4"
        ],
        "correctAnswer": "A",
        "explanation": "詳細な解説をここに",
        "learningResources": [
            {
                "title": "リソースタイトル",
                "url": "https://docs.aws.amazon.com/...",
                "type": "documentation"
            }
        ],
        "relatedServices": ["CloudWatch", "EC2"],
        "tags": ["monitoring", "cloudwatch"]
    }
    """
    
    try:
        print("📝 Generating question...")
        
        # Generate the question
        result = question_agent(prompt)
        print(f"Result type: {type(result)}")
        print(f"Result attributes: {dir(result)}")
        
        # Extract text from AgentResult
        if hasattr(result, 'message') and result.message:
            if isinstance(result.message, dict) and 'content' in result.message:
                content = result.message['content']
                if isinstance(content, list) and len(content) > 0:
                    response = content[0].get('text', str(result))
                else:
                    response = str(content)
            else:
                response = str(result.message)
        else:
            response = str(result)
        
        print("✅ Question generated successfully!")
        print("\n📄 Generated Question:")
        print("-" * 30)
        print(response)
        
        # Try to parse as JSON
        try:
            question_data = json.loads(response)
            print("\n✅ JSON parsing successful!")
            
            # Save to file
            output_file = Path("output/test_question.json")
            output_file.parent.mkdir(exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(question_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Question saved to: {output_file}")
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed: {e}")
            print("Raw response saved instead.")
            
            # Save raw response
            output_file = Path("output/test_question_raw.txt")
            output_file.parent.mkdir(exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(response)
            
            print(f"💾 Raw response saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Question generation failed: {e}")
        return False


async def main():
    """Main test function."""
    success = await simple_question_generation()
    
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
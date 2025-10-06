#!/usr/bin/env python3
"""
Generate 10 AWS CloudOps questions for testing.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

# Import the basic components
from core.agent_factory import AgentFactory
from config import AgentConfig


async def generate_10_questions():
    """Generate 10 questions for testing."""
    
    print("🧪 Generating 10 AWS CloudOps Questions")
    print("=" * 50)
    
    # Initialize agent factory with config
    config = AgentConfig()
    agent_factory = AgentFactory(config)
    
    # Create a simple question generator agent
    question_agent = agent_factory.create_question_generator()
    
    # Domain distribution for 10 questions
    domains = [
        "monitoring", "monitoring", "monitoring",  # 3 questions
        "reliability", "reliability",              # 2 questions  
        "deployment", "deployment",                # 2 questions
        "security", "security",                    # 2 questions
        "networking"                               # 1 question
    ]
    
    difficulties = ["easy", "medium", "hard"]
    
    questions = []
    
    for i, domain in enumerate(domains, 1):
        print(f"\n📝 Generating question {i}/10 (Domain: {domain})...")
        
        # Select difficulty (distribute evenly)
        difficulty = difficulties[(i-1) % 3]
        
        prompt = f"""
        AWS CloudOps試験問題を1問生成してください。以下の要件に従ってください：

        要件：
        - ID: q{i+11:03d}
        - ドメイン: {domain}
        - 難易度: {difficulty}
        - 問題タイプ: single (単一選択)
        - 日本語で作成
        - 4つの選択肢 (A, B, C, D)
        - 詳細な解説を含める
        - 学習リソースを1つ以上含める
        - 実際のAWS CloudOps試験に出題されそうな実践的な問題

        以下のJSON形式で回答してください：
        {{
            "id": "q{i+11:03d}",
            "domain": "{domain}",
            "difficulty": "{difficulty}", 
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
                {{
                    "title": "リソースタイトル",
                    "url": "https://docs.aws.amazon.com/...",
                    "type": "documentation"
                }}
            ],
            "relatedServices": ["Service1", "Service2"],
            "tags": ["tag1", "tag2"]
        }}
        """
        
        try:
            # Generate the question
            result = question_agent(prompt)
            
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
            
            # Parse JSON
            question_data = json.loads(response)
            questions.append(question_data)
            
            print(f"✅ Question {i} generated successfully!")
            
        except Exception as e:
            print(f"❌ Failed to generate question {i}: {e}")
            continue
    
    # Save all questions
    if questions:
        output_file = Path("output/10_test_questions.json")
        output_file.parent.mkdir(exist_ok=True)
        
        # Create a complete database structure
        database = {
            "version": "1.1.0",
            "generatedAt": datetime.now().isoformat() + "Z",
            "totalQuestions": len(questions),
            "domains": {},
            "questions": questions
        }
        
        # Count domains
        for question in questions:
            domain = question.get("domain", "unknown")
            database["domains"][domain] = database["domains"].get(domain, 0) + 1
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 Successfully generated {len(questions)} questions!")
        print(f"💾 Questions saved to: {output_file}")
        
        # Show summary
        print(f"\n📊 Summary:")
        print(f"Total Questions: {len(questions)}")
        for domain, count in database["domains"].items():
            print(f"  {domain}: {count} questions")
        
        return True
    else:
        print("\n❌ No questions were generated successfully!")
        return False


async def main():
    """Main function."""
    success = await generate_10_questions()
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
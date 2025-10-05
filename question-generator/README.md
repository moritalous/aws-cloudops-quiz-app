# AWS CloudOps Question Generator

AI-driven question generator for AWS Certified CloudOps Engineer - Associate exam preparation using Strands Agents and Amazon Bedrock.

## Features

- **AI-Powered Generation**: Uses Strands Agents with Amazon Bedrock OpenAI models
- **Structured Output**: Pydantic models ensure type-safe, validated responses
- **AWS Documentation Integration**: MCP (Model Context Protocol) integration with aws-docs server
- **Quality Validation**: Comprehensive AI-driven quality assessment
- **Batch Processing**: Efficient 10-question batch processing
- **Japanese Language Support**: Natural Japanese question and explanation generation
- **Complete Integration**: Seamless integration with existing quiz application

## Prerequisites

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- AWS credentials configured for Bedrock access
- Access to Amazon Bedrock OpenAI models

## Installation

### 1. Install uv (if not already installed)

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip
pip install uv
```

### 2. Clone and Setup Project

```bash
cd question-generator

# Install dependencies using uv
uv sync

# Install development dependencies (optional)
uv sync --extra dev
```

### 3. Configure AWS Credentials

```bash
# Option 1: AWS CLI
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-west-2

# Option 3: AWS Profile
export AWS_PROFILE=your-profile-name
```

### 4. Request Bedrock Model Access

1. Go to AWS Bedrock Console
2. Navigate to "Model access"
3. Request access to OpenAI models:
   - `openai.gpt-oss-20b-1:0`
   - `openai.gpt-oss-120b-1:0`

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Bedrock Configuration
BEDROCK_MODEL_ID=openai.gpt-oss-120b-1:0
AWS_REGION=us-west-2
BEDROCK_TEMPERATURE=0.3
BEDROCK_MAX_TOKENS=4000

# MCP Configuration
MCP_SERVER_NAME=aws-docs
MCP_SERVER_COMMAND=uv
MCP_SERVER_ARGS=tool,run,awslabs.aws-documentation-mcp-server@latest

# Application Settings
LOG_LEVEL=INFO
DEBUG_MODE=false
BATCH_SIZE=10

# Quality Thresholds
QUESTION_GEN_ENABLE_QUALITY_VALIDATION=true
QUESTION_GEN_ENABLE_DUPLICATE_DETECTION=true
```

### Configuration File

Alternatively, create a `config.json` file:

```json
{
  "agent_config": {
    "bedrock": {
      "model_id": "openai.gpt-oss-120b-1:0",
      "region_name": "us-west-2",
      "temperature": 0.3,
      "max_tokens": 4000,
      "top_p": 0.8
    },
    "mcp": {
      "server_name": "aws-docs",
      "server_command": "uv",
      "server_args": ["tool", "run", "awslabs.aws-documentation-mcp-server@latest"]
    }
  },
  "target_questions": 200,
  "existing_questions": 11
}
```

## Usage

### 1. Test Setup

Verify your configuration:

```bash
# Run setup verification
uv run test-setup

# Or run directly
uv run python test_setup.py
```

### 2. Generate Questions

```bash
# Run the main question generation process
uv run question-generator

# Or run directly
uv run python main.py
```

### 3. Development Mode

```bash
# Install development dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=models --cov=config --cov=core

# Format code
uv run black .
uv run isort .

# Type checking
uv run mypy .
```

## Project Structure

```
question-generator/
├── models/                 # Pydantic data models
│   ├── exam_guide_models.py
│   ├── question_models.py
│   ├── validation_models.py
│   ├── batch_models.py
│   └── integration_models.py
├── config/                 # Configuration management
│   ├── agent_config.py
│   └── settings.py
├── core/                   # Core functionality
│   ├── agent_factory.py
│   └── error_handling.py
├── agents/                 # Specialized AI agents
├── pyproject.toml         # Project configuration
├── uv.lock               # Dependency lock file
├── .python-version       # Python version specification
└── README.md             # This file
```

## Architecture

The system uses a multi-agent architecture with specialized AI agents:

1. **Exam Guide Analyzer**: Analyzes AWS exam guide structure
2. **Batch Manager**: Plans and manages question generation batches
3. **Document Researcher**: Searches AWS documentation via MCP
4. **Question Generator**: Creates exam questions
5. **Quality Validator**: Validates question quality and accuracy
6. **Japanese Optimizer**: Optimizes Japanese language quality
7. **Database Integrator**: Integrates questions into final database
8. **Overall Quality Checker**: Final quality assessment

## Data Models

### Core Models

- `ExamGuideAnalysis`: Structured exam guide analysis
- `Question`: Individual exam question with metadata
- `QuestionBatch`: Collection of 10 questions for processing
- `QuestionValidation`: Quality validation results
- `DatabaseState`: Current database state tracking
- `BatchPlan`: Intelligent batch planning
- `IntegrationResult`: Database integration results

## Quality Assurance

The system includes comprehensive quality validation:

- **Technical Accuracy**: Verification against AWS documentation
- **Language Quality**: Japanese language naturalness assessment
- **Difficulty Appropriateness**: Proper difficulty level assignment
- **Duplicate Detection**: Prevention of duplicate content
- **Resource Validation**: Learning resource link verification

## Error Handling

Robust error handling with:

- **Retry Logic**: Exponential backoff for transient failures
- **Graceful Degradation**: Continued operation despite non-critical errors
- **Comprehensive Logging**: Detailed error tracking and reporting
- **Recovery Mechanisms**: Automatic recovery from common failures

## Monitoring and Observability

- **Progress Tracking**: Real-time progress reporting
- **Quality Metrics**: Comprehensive quality measurement
- **Performance Monitoring**: Execution time and resource usage tracking
- **OpenTelemetry Integration**: Distributed tracing support

## Troubleshooting

### Common Issues

1. **Bedrock Access Denied**
   - Ensure model access is granted in Bedrock console
   - Verify AWS credentials and permissions

2. **MCP Connection Failed**
   - Check that uv is installed and accessible
   - Verify aws-docs MCP server can be installed

3. **Import Errors**
   - Run `uv sync` to install dependencies
   - Check Python version compatibility

4. **Configuration Errors**
   - Validate configuration file format
   - Check environment variable names

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG_MODE=true
export LOG_LEVEL=DEBUG
uv run python main.py
```

## Contributing

1. Install development dependencies: `uv sync --extra dev`
2. Run tests: `uv run pytest`
3. Format code: `uv run black . && uv run isort .`
4. Type check: `uv run mypy .`
5. Submit pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review logs in the `logs/` directory
- Open an issue on the project repository
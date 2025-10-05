"""
Configuration classes for Strands Agents and AWS Bedrock integration.

This module provides comprehensive configuration management for the AI-driven
question generation system, including Bedrock model settings, MCP server
integration, and agent behavior parameters.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Literal
import os
from pathlib import Path


class BedrockConfig(BaseModel):
    """Configuration for Amazon Bedrock OpenAI model integration."""
    
    model_id: str = Field(
        description="Bedrock model identifier",
        default="anthropic.claude-3-5-sonnet-20241022-v2:0"
    )
    region_name: str = Field(
        description="AWS region for Bedrock service",
        default="us-west-2"
    )
    temperature: float = Field(
        description="Model temperature for response randomness",
        default=0.3,
        ge=0.0,
        le=2.0
    )
    max_tokens: int = Field(
        description="Maximum tokens to generate",
        default=4000,
        ge=1,
        le=8192
    )
    top_p: float = Field(
        description="Top-p sampling parameter",
        default=0.8,
        ge=0.0,
        le=1.0
    )
    streaming: bool = Field(
        description="Enable streaming responses",
        default=True
    )
    stop_sequences: List[str] = Field(
        description="Sequences that stop generation",
        default_factory=lambda: ["###", "END", "STOP"]
    )
    guardrail_id: Optional[str] = Field(
        description="Bedrock guardrail ID if using guardrails",
        default=None
    )
    guardrail_version: Optional[str] = Field(
        description="Guardrail version",
        default=None
    )
    guardrail_trace: Literal["enabled", "disabled", "enabled_full"] = Field(
        description="Guardrail trace mode",
        default="enabled"
    )
    cache_prompt: Optional[str] = Field(
        description="Cache point type for system prompt",
        default=None
    )
    cache_tools: Optional[str] = Field(
        description="Cache point type for tools",
        default=None
    )
    retry_attempts: int = Field(
        description="Number of retry attempts for failed requests",
        default=3,
        ge=1,
        le=10
    )
    retry_delay: float = Field(
        description="Delay between retry attempts in seconds",
        default=1.0,
        ge=0.1,
        le=60.0
    )
    timeout_seconds: int = Field(
        description="Request timeout in seconds",
        default=120,
        ge=10,
        le=600
    )
    
    @validator('model_id')
    def validate_model_id(cls, v):
        """Validate that model ID is supported."""
        supported_prefixes = ['openai.', 'anthropic.', 'us.', 'eu.']
        if not any(v.startswith(prefix) for prefix in supported_prefixes):
            raise ValueError(f'Model ID must start with one of: {supported_prefixes}')
        return v
    
    @validator('region_name')
    def validate_region(cls, v):
        """Validate AWS region format."""
        valid_regions = [
            'us-east-1', 'us-west-2', 'eu-west-1', 'eu-central-1',
            'ap-southeast-1', 'ap-northeast-1'
        ]
        if v not in valid_regions:
            raise ValueError(f'Region must be one of: {valid_regions}')
        return v


class MCPConfig(BaseModel):
    """Configuration for MCP (Model Context Protocol) server integration."""
    
    server_name: str = Field(
        description="Name of the MCP server",
        default="aws-docs"
    )
    server_command: str = Field(
        description="Command to start the MCP server",
        default="uv"
    )
    server_args: List[str] = Field(
        description="Arguments for the MCP server command",
        default_factory=lambda: ["tool", "run", "awslabs.aws-documentation-mcp-server@latest"]
    )
    server_env: Dict[str, str] = Field(
        description="Environment variables for the MCP server",
        default_factory=lambda: {
            "FASTMCP_LOG_LEVEL": "ERROR"
        }
    )
    connection_timeout: int = Field(
        description="Connection timeout in seconds",
        default=30,
        ge=5,
        le=300
    )
    request_timeout: int = Field(
        description="Request timeout in seconds",
        default=60,
        ge=10,
        le=600
    )
    max_retries: int = Field(
        description="Maximum number of connection retries",
        default=3,
        ge=1,
        le=10
    )
    retry_delay: float = Field(
        description="Delay between retries in seconds",
        default=2.0,
        ge=0.1,
        le=30.0
    )
    auto_reconnect: bool = Field(
        description="Automatically reconnect on connection loss",
        default=True
    )
    
    def get_stdio_parameters(self):
        """Get StdioServerParameters for MCP client."""
        from mcp import StdioServerParameters
        return StdioServerParameters(
            command=self.server_command,
            args=self.server_args,
            env=self.server_env
        )


class AgentConfig(BaseModel):
    """Main configuration for Strands Agents setup."""
    
    # Model configuration
    bedrock: BedrockConfig = Field(
        description="Bedrock model configuration",
        default_factory=BedrockConfig
    )
    
    # MCP configuration
    mcp: MCPConfig = Field(
        description="MCP server configuration",
        default_factory=MCPConfig
    )
    
    # Agent behavior settings
    system_prompt_template: str = Field(
        description="Template for system prompts",
        default="""あなたは{role}の専門家です。

{context}

以下の要件に従って作業してください：
{requirements}

出力は構造化された形式で提供し、技術的に正確で実用的な内容にしてください。"""
    )
    
    default_system_prompt: str = Field(
        description="Default system prompt for agents",
        default="""あなたはAWS CloudOps認定試験の専門家です。
技術的に正確で実践的な情報を提供し、常に最新のAWSサービスとベストプラクティスに基づいて回答してください。"""
    )
    
    # Quality and validation settings
    quality_thresholds: Dict[str, float] = Field(
        description="Quality thresholds for validation",
        default_factory=lambda: {
            "technical_accuracy_min": 8.0,
            "clarity_min": 7.0,
            "explanation_min": 8.0,
            "japanese_quality_min": 8.0,
            "overall_score_min": 75.0
        }
    )
    
    # Batch processing settings
    batch_size: int = Field(
        description="Number of questions per batch",
        default=10,
        ge=1,
        le=20
    )
    
    max_concurrent_agents: int = Field(
        description="Maximum number of concurrent agents",
        default=3,
        ge=1,
        le=10
    )
    
    # Error handling and logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        description="Logging level",
        default="INFO"
    )
    
    enable_telemetry: bool = Field(
        description="Enable OpenTelemetry tracing",
        default=True
    )
    
    debug_mode: bool = Field(
        description="Enable debug mode for detailed logging",
        default=False
    )
    
    # File paths and directories
    output_directory: Path = Field(
        description="Directory for output files",
        default_factory=lambda: Path("output")
    )
    
    backup_directory: Path = Field(
        description="Directory for backup files",
        default_factory=lambda: Path("backups")
    )
    
    log_directory: Path = Field(
        description="Directory for log files",
        default_factory=lambda: Path("logs")
    )
    
    # AWS credentials (optional - will use default boto3 resolution)
    aws_access_key_id: Optional[str] = Field(
        description="AWS access key ID",
        default=None
    )
    
    aws_secret_access_key: Optional[str] = Field(
        description="AWS secret access key",
        default=None
    )
    
    aws_session_token: Optional[str] = Field(
        description="AWS session token for temporary credentials",
        default=None
    )
    
    aws_profile: Optional[str] = Field(
        description="AWS profile name to use",
        default=None
    )
    
    def model_post_init(self, __context) -> None:
        """Post-initialization setup."""
        # Create directories if they don't exist
        for directory in [self.output_directory, self.backup_directory, self.log_directory]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Create configuration from environment variables."""
        config_data = {}
        
        # Bedrock configuration from environment
        bedrock_config = {}
        if model_id := os.getenv("BEDROCK_MODEL_ID"):
            bedrock_config["model_id"] = model_id
        if region := os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION")):
            bedrock_config["region_name"] = region
        if temp := os.getenv("BEDROCK_TEMPERATURE"):
            bedrock_config["temperature"] = float(temp)
        if max_tokens := os.getenv("BEDROCK_MAX_TOKENS"):
            bedrock_config["max_tokens"] = int(max_tokens)
        if top_p := os.getenv("BEDROCK_TOP_P"):
            bedrock_config["top_p"] = float(top_p)
        
        if bedrock_config:
            config_data["bedrock"] = BedrockConfig(**bedrock_config)
        
        # MCP configuration from environment
        mcp_config = {}
        if server_name := os.getenv("MCP_SERVER_NAME"):
            mcp_config["server_name"] = server_name
        if server_command := os.getenv("MCP_SERVER_COMMAND"):
            mcp_config["server_command"] = server_command
        if server_args := os.getenv("MCP_SERVER_ARGS"):
            mcp_config["server_args"] = server_args.split(",")
        
        if mcp_config:
            config_data["mcp"] = MCPConfig(**mcp_config)
        
        # General configuration from environment
        if log_level := os.getenv("LOG_LEVEL"):
            config_data["log_level"] = log_level
        if debug_mode := os.getenv("DEBUG_MODE"):
            config_data["debug_mode"] = debug_mode.lower() == "true"
        if batch_size := os.getenv("BATCH_SIZE"):
            config_data["batch_size"] = int(batch_size)
        
        # AWS credentials from environment
        if aws_access_key := os.getenv("AWS_ACCESS_KEY_ID"):
            config_data["aws_access_key_id"] = aws_access_key
        if aws_secret_key := os.getenv("AWS_SECRET_ACCESS_KEY"):
            config_data["aws_secret_access_key"] = aws_secret_key
        if aws_session_token := os.getenv("AWS_SESSION_TOKEN"):
            config_data["aws_session_token"] = aws_session_token
        if aws_profile := os.getenv("AWS_PROFILE"):
            config_data["aws_profile"] = aws_profile
        
        return cls(**config_data)
    
    def get_boto_session_kwargs(self) -> Dict[str, Any]:
        """Get kwargs for creating a boto3 session."""
        kwargs = {}
        
        if self.aws_access_key_id:
            kwargs["aws_access_key_id"] = self.aws_access_key_id
        if self.aws_secret_access_key:
            kwargs["aws_secret_access_key"] = self.aws_secret_access_key
        if self.aws_session_token:
            kwargs["aws_session_token"] = self.aws_session_token
        if self.aws_profile:
            kwargs["profile_name"] = self.aws_profile
        
        kwargs["region_name"] = self.bedrock.region_name
        
        return kwargs
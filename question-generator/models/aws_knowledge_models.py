"""
Pydantic models for AWS Knowledge MCP Server integration.

This module defines structured data models for AWS knowledge retrieval,
documentation search, best practices extraction, and regional availability information.
"""

from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Dict, Optional, Any, Literal, Union
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Types of AWS documentation."""
    DOCUMENTATION = "documentation"
    API_REFERENCE = "api-reference"
    WHITEPAPER = "whitepaper"
    BLOG_POST = "blog"
    BEST_PRACTICE = "best-practice"
    TUTORIAL = "tutorial"
    GETTING_STARTED = "getting-started"
    ARCHITECTURE_REFERENCE = "architecture-reference"
    WELL_ARCHITECTED = "well-architected"
    WHATS_NEW = "whats-new"
    BUILDER_CENTER = "builder-center"


class AWSRegion(BaseModel):
    """AWS region information."""
    
    region_code: str = Field(description="AWS region code (e.g., us-east-1)")
    region_name: str = Field(description="Human-readable region name")
    location: str = Field(description="Geographic location")
    availability_zones: Optional[int] = Field(description="Number of availability zones", default=None)
    launch_date: Optional[str] = Field(description="Region launch date", default=None)
    
    @field_validator('region_code')
    @classmethod
    def validate_region_code(cls, v):
        """Validate AWS region code format."""
        if not v or len(v) < 8:
            raise ValueError("Region code must be valid AWS region format")
        return v


class AWSServiceCapability(BaseModel):
    """AWS service capability or feature."""
    
    name: str = Field(description="Capability name")
    description: str = Field(description="Capability description")
    availability: Literal["GA", "Preview", "Beta", "Deprecated"] = Field(
        description="Availability status",
        default="GA"
    )
    supported_regions: List[str] = Field(
        description="Regions where this capability is available",
        default_factory=list
    )
    prerequisites: List[str] = Field(
        description="Prerequisites for using this capability",
        default_factory=list
    )
    limitations: List[str] = Field(
        description="Known limitations",
        default_factory=list
    )


class AWSServiceInfo(BaseModel):
    """Comprehensive AWS service information."""
    
    service_name: str = Field(description="Official AWS service name")
    service_code: str = Field(description="AWS service code (e.g., ec2, s3)")
    category: str = Field(description="Service category (e.g., Compute, Storage)")
    description: str = Field(description="Service description")
    
    # Core information
    key_features: List[str] = Field(description="Key features and capabilities")
    use_cases: List[str] = Field(description="Common use cases")
    capabilities: List[AWSServiceCapability] = Field(
        description="Detailed service capabilities",
        default_factory=list
    )
    
    # Best practices and guidance
    best_practices: List[str] = Field(description="Best practices", default_factory=list)
    security_considerations: List[str] = Field(
        description="Security considerations",
        default_factory=list
    )
    cost_optimization_tips: List[str] = Field(
        description="Cost optimization recommendations",
        default_factory=list
    )
    
    # Technical details
    api_versions: List[str] = Field(description="Available API versions", default_factory=list)
    supported_protocols: List[str] = Field(
        description="Supported protocols",
        default_factory=list
    )
    integration_points: List[str] = Field(
        description="Integration with other AWS services",
        default_factory=list
    )
    
    # Operational information
    pricing_model: Optional[str] = Field(description="Pricing model", default=None)
    sla_guarantees: Optional[str] = Field(description="SLA guarantees", default=None)
    compliance_certifications: List[str] = Field(
        description="Compliance certifications",
        default_factory=list
    )
    
    # Availability
    regional_availability: List[str] = Field(
        description="Available AWS regions",
        default_factory=list
    )
    global_service: bool = Field(
        description="Whether this is a global service",
        default=False
    )
    
    # Documentation links
    documentation_urls: List[str] = Field(
        description="Official documentation URLs",
        default_factory=list
    )
    api_reference_urls: List[str] = Field(
        description="API reference URLs",
        default_factory=list
    )


class AWSDocumentationResult(BaseModel):
    """Result from AWS documentation search or retrieval."""
    
    title: str = Field(description="Document title")
    url: str = Field(description="Document URL")
    content: str = Field(description="Document content in markdown format")
    
    # Metadata
    document_type: DocumentType = Field(description="Type of document")
    last_updated: Optional[str] = Field(description="Last update date", default=None)
    author: Optional[str] = Field(description="Document author", default=None)
    
    # Content analysis
    related_services: List[str] = Field(
        description="AWS services mentioned in the document",
        default_factory=list
    )
    key_concepts: List[str] = Field(
        description="Key concepts covered",
        default_factory=list
    )
    code_examples: List[str] = Field(
        description="Code examples found",
        default_factory=list
    )
    
    # Relevance scoring
    relevance_score: Optional[float] = Field(
        description="Relevance score (0-1)",
        default=None,
        ge=0.0,
        le=1.0
    )
    
    # Additional metadata
    tags: List[str] = Field(description="Document tags", default_factory=list)
    difficulty_level: Optional[Literal["beginner", "intermediate", "advanced"]] = Field(
        description="Content difficulty level",
        default=None
    )


class AWSKnowledgeSearchResult(BaseModel):
    """Structured search result from AWS Knowledge MCP Server."""
    
    query: str = Field(description="Original search query")
    search_timestamp: str = Field(
        description="When the search was performed",
        default_factory=lambda: datetime.now().isoformat()
    )
    
    # Results
    total_results: int = Field(description="Total number of results found", ge=0)
    results: List[AWSDocumentationResult] = Field(description="Search results")
    
    # Search metadata
    search_duration_ms: Optional[int] = Field(
        description="Search duration in milliseconds",
        default=None
    )
    filters_applied: List[str] = Field(
        description="Filters applied to the search",
        default_factory=list
    )
    
    # Recommendations
    recommended_follow_up: List[str] = Field(
        description="Recommended follow-up queries",
        default_factory=list
    )
    related_topics: List[str] = Field(
        description="Related topics to explore",
        default_factory=list
    )
    
    # Quality indicators
    high_confidence_results: int = Field(
        description="Number of high-confidence results",
        default=0,
        ge=0
    )
    
    @field_validator('results')
    @classmethod
    def validate_results_count(cls, v, info):
        """Validate that results count matches total_results."""
        if info.data and 'total_results' in info.data and len(v) > info.data['total_results']:
            raise ValueError("Results count cannot exceed total_results")
        return v


class AWSBestPracticesExtract(BaseModel):
    """Extracted best practices and architectural guidance."""
    
    topic: str = Field(description="Topic or service area")
    extraction_timestamp: str = Field(
        description="When the extraction was performed",
        default_factory=lambda: datetime.now().isoformat()
    )
    
    # Best practices categories
    general_best_practices: List[str] = Field(
        description="General best practices",
        default_factory=list
    )
    architecture_patterns: List[str] = Field(
        description="Recommended architecture patterns",
        default_factory=list
    )
    
    # Well-Architected Framework pillars
    well_architected_principles: List[str] = Field(
        description="Well-Architected framework principles",
        default_factory=list
    )
    operational_excellence: List[str] = Field(
        description="Operational excellence practices",
        default_factory=list
    )
    security_considerations: List[str] = Field(
        description="Security best practices",
        default_factory=list
    )
    reliability_measures: List[str] = Field(
        description="Reliability and resilience measures",
        default_factory=list
    )
    performance_optimization: List[str] = Field(
        description="Performance optimization tips",
        default_factory=list
    )
    cost_optimization: List[str] = Field(
        description="Cost optimization recommendations",
        default_factory=list
    )
    sustainability: List[str] = Field(
        description="Sustainability best practices",
        default_factory=list
    )
    
    # Implementation guidance
    implementation_steps: List[str] = Field(
        description="Implementation steps",
        default_factory=list
    )
    common_pitfalls: List[str] = Field(
        description="Common pitfalls to avoid",
        default_factory=list
    )
    monitoring_recommendations: List[str] = Field(
        description="Monitoring and observability recommendations",
        default_factory=list
    )
    
    # Supporting information
    reference_architectures: List[str] = Field(
        description="Reference architecture URLs",
        default_factory=list
    )
    case_studies: List[str] = Field(
        description="Relevant case studies",
        default_factory=list
    )
    whitepapers: List[str] = Field(
        description="Related whitepapers",
        default_factory=list
    )


class AWSRegionalAvailability(BaseModel):
    """Regional availability information for AWS services."""
    
    service_name: str = Field(description="AWS service name")
    resource_type: Optional[str] = Field(
        description="Specific resource type (for CloudFormation resources)",
        default=None
    )
    
    # Availability information
    available_regions: List[AWSRegion] = Field(
        description="Regions where the service is available",
        default_factory=list
    )
    unavailable_regions: List[AWSRegion] = Field(
        description="Regions where the service is not available",
        default_factory=list
    )
    
    # Service characteristics
    global_service: bool = Field(
        description="Whether this is a global service",
        default=False
    )
    regional_service: bool = Field(
        description="Whether this is a regional service",
        default=True
    )
    
    # Limitations and considerations
    regional_limitations: Dict[str, List[str]] = Field(
        description="Limitations by region",
        default_factory=dict
    )
    feature_variations: Dict[str, List[str]] = Field(
        description="Feature variations by region",
        default_factory=dict
    )
    
    # Metadata
    last_updated: str = Field(
        description="When the availability information was last updated",
        default_factory=lambda: datetime.now().isoformat()
    )
    data_source: str = Field(
        description="Source of the availability data",
        default="AWS Knowledge MCP Server"
    )


class AWSKnowledgeExtractionRequest(BaseModel):
    """Request for AWS knowledge extraction."""
    
    topic: str = Field(description="Topic or service to research")
    extraction_type: Literal[
        "service_info",
        "best_practices", 
        "documentation_search",
        "regional_availability",
        "learning_resources"
    ] = Field(description="Type of extraction to perform")
    
    # Optional parameters
    max_results: int = Field(description="Maximum results to return", default=10, ge=1, le=50)
    include_code_examples: bool = Field(
        description="Include code examples in results",
        default=True
    )
    include_best_practices: bool = Field(
        description="Include best practices",
        default=True
    )
    target_audience: Optional[Literal["beginner", "intermediate", "advanced"]] = Field(
        description="Target audience level",
        default=None
    )
    
    # Context for question generation
    question_context: Optional[str] = Field(
        description="Context of the question being generated",
        default=None
    )
    domain: Optional[str] = Field(
        description="AWS certification domain",
        default=None
    )
    difficulty_level: Optional[Literal["easy", "medium", "hard"]] = Field(
        description="Target difficulty level",
        default=None
    )


class AWSKnowledgeExtractionResult(BaseModel):
    """Result from AWS knowledge extraction."""
    
    request: AWSKnowledgeExtractionRequest = Field(description="Original request")
    extraction_timestamp: str = Field(
        description="When the extraction was performed",
        default_factory=lambda: datetime.now().isoformat()
    )
    
    # Results (one of these will be populated based on extraction_type)
    service_info: Optional[AWSServiceInfo] = Field(default=None)
    best_practices: Optional[AWSBestPracticesExtract] = Field(default=None)
    search_results: Optional[AWSKnowledgeSearchResult] = Field(default=None)
    regional_availability: Optional[AWSRegionalAvailability] = Field(default=None)
    learning_resources: Optional[List[Dict[str, str]]] = Field(default=None)
    
    # Extraction metadata
    success: bool = Field(description="Whether extraction was successful", default=True)
    error_message: Optional[str] = Field(description="Error message if failed", default=None)
    processing_time_ms: Optional[int] = Field(
        description="Processing time in milliseconds",
        default=None
    )
    
    # Quality indicators
    confidence_score: Optional[float] = Field(
        description="Confidence score for the extraction (0-1)",
        default=None,
        ge=0.0,
        le=1.0
    )
    completeness_score: Optional[float] = Field(
        description="Completeness score for the extraction (0-1)",
        default=None,
        ge=0.0,
        le=1.0
    )
    
    @field_validator('service_info', 'best_practices', 'search_results', 'regional_availability', 'learning_resources')
    @classmethod
    def validate_result_consistency(cls, v, info):
        """Validate that the result matches the extraction type."""
        if info.data and 'request' in info.data:
            extraction_type = info.data['request'].extraction_type
            field_name = info.field_name
            
            # Map extraction types to expected fields
            expected_field_map = {
                'service_info': 'service_info',
                'best_practices': 'best_practices',
                'documentation_search': 'search_results',
                'regional_availability': 'regional_availability',
                'learning_resources': 'learning_resources'
            }
            
            expected_field = expected_field_map.get(extraction_type)
            
            # Only the expected field should be populated
            if field_name == expected_field and v is None:
                raise ValueError(f"Expected {field_name} to be populated for extraction type {extraction_type}")
            elif field_name != expected_field and v is not None:
                raise ValueError(f"Unexpected {field_name} populated for extraction type {extraction_type}")
        
        return v
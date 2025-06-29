"""Common type definitions for Substrate MCP servers."""

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """Definition of a tool parameter."""
    name: str
    type: Literal["string", "number", "boolean", "object", "array"]
    description: Optional[str] = None
    required: bool = True
    default: Optional[Any] = None


class Tool(BaseModel):
    """Tool definition."""
    name: str
    description: str
    parameters: List[ToolParameter] = []


class ToolResponse(TypedDict, total=False):
    """Standard tool response structure."""
    success: bool
    data: Optional[Dict[str, Any]]
    message: Optional[str]
    error: Optional[str]
    error_code: Optional[str]
    suggestions: Optional[List[str]]
    _sampling_request: Optional[Dict[str, Any]]
    _annotations: Optional[Dict[str, Any]]
    _progress: Optional[Dict[str, Any]]
    _metadata: Optional[Dict[str, Any]]
    timestamp: float


class SamplingRequest(BaseModel):
    """Sampling request to be injected in responses."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7
    callback_tool: str
    context: Optional[Dict[str, Any]] = None


class Annotation(TypedDict):
    """Annotation metadata for responses."""
    priority: float  # 0.0 to 1.0
    audience: List[Literal["user", "assistant"]]


class ResponseMetadata(TypedDict, total=False):
    """Optional metadata for responses."""
    processing_time_ms: float
    cache_hit: bool
    model_used: Optional[str]
    token_count: Optional[int]


class ProgressUpdate(BaseModel):
    """Progress update information."""
    progress: float = Field(ge=0.0, le=1.0)
    status: str
    details: Optional[Dict[str, Any]] = None
    timestamp: float = Field(default_factory=time.time)


class ErrorInfo(BaseModel):
    """Detailed error information."""
    message: str
    code: Optional[str] = None
    type: str = "generic"
    details: Optional[Dict[str, Any]] = None
    traceback: Optional[str] = None
    suggestions: List[str] = []


class PromptDefinition(BaseModel):
    """Definition of a prompt (for AKAB/SYNAPSE)."""
    id: str
    version: str
    content: str
    parameters: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}


class ProviderConfig(BaseModel):
    """Configuration for an LLM provider."""
    name: str
    size: Literal["xs", "s", "m", "l", "xl", "xxl"]
    model: str
    base_url: Optional[str] = None
    api_key_env: Optional[str] = None
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    max_tokens: int = 4096
    supports_streaming: bool = True
    supports_tools: bool = True


class ComparisonResult(BaseModel):
    """Result from comparing outputs."""
    provider: str
    response: str
    latency_ms: float
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class Campaign(BaseModel):
    """A/B testing campaign definition."""
    id: str
    name: str
    description: Optional[str] = None
    prompts: List[str]  # List of prompt IDs
    providers: List[str]  # List of provider names
    iterations: int = 1
    constraints: Dict[str, Any] = {}
    created_at: float = Field(default_factory=time.time)
    status: Literal["draft", "running", "completed", "failed"] = "draft"


# Import what we need
import time
import uuid

"""
Enhanced Provider Management with Model Size Configuration
Handles multiple LLM providers with unified interface and size-based model selection
"""
import os
import json
import asyncio
from enum import Enum
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Literal
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Optional imports for remote providers
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import google.generativeai as genai
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

try:
    from instructor import Instructor, patch
    HAS_INSTRUCTOR = True
except ImportError:
    HAS_INSTRUCTOR = False

logger = logging.getLogger(__name__)

# Type definitions
ModelSize = Literal["XS", "S", "M", "L", "XL", "XXL"]
ProviderName = Literal["ANTHROPIC", "OPENAI", "GOOGLE", "GROQ"]


class ProviderType(Enum):
    """Provider execution types"""
    LOCAL = "local"      # MCP client execution
    REMOTE = "remote"    # API-based execution


class ModelConfig:
    """Model configuration helper"""
    
    # Model cost mapping (per 1K tokens)
    COSTS = {
        # Anthropic
        "claude-3-5-haiku-20241022": {"input": 0.00025, "output": 0.00125},
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        
        # OpenAI
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "o1-preview": {"input": 0.015, "output": 0.06},
        "o1": {"input": 0.015, "output": 0.06},
        
        # Google
        "gemini-1.5-flash": {"input": 0.00001875, "output": 0.000075},
        "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
        
        # Groq (example costs)
        "llama-3.2-3b-preview": {"input": 0.00001, "output": 0.00001},
        "llama-3.2-7b-preview": {"input": 0.00002, "output": 0.00002},
        "llama-3.2-70b-preview": {"input": 0.0001, "output": 0.0001},
    }
    
    def __init__(self):
        self._model_cache = {}
    
    def get_model_name(self, provider: ProviderName, size: ModelSize) -> str:
        """Get model name from environment variables with caching"""
        cache_key = f"{provider}_{size}"
        
        if cache_key not in self._model_cache:
            env_key = f"{provider}_{size}_MODEL"
            model_name = os.getenv(env_key)
            
            if not model_name:
                raise ValueError(
                    f"Model not configured: {env_key}. "
                    f"Please set {env_key} in your .env file"
                )
            
            self._model_cache[cache_key] = model_name
        
        return self._model_cache[cache_key]
    
    def get_model_cost(self, model_name: str) -> Dict[str, float]:
        """Get cost configuration for a model"""
        return self.COSTS.get(model_name, {"input": 0.001, "output": 0.001})
    
    def list_configured_models(self) -> Dict[str, Dict[str, str]]:
        """List all configured models from environment"""
        models = {}
        
        for provider in ["ANTHROPIC", "OPENAI", "GOOGLE", "GROQ"]:
            models[provider] = {}
            for size in ["XS", "S", "M", "L", "XL", "XXL"]:
                env_key = f"{provider}_{size}_MODEL"
                model_name = os.getenv(env_key)
                if model_name:
                    models[provider][size] = model_name
        
        return models


class Provider(ABC):
    """Base class for all providers"""
    
    def __init__(self, name: str, type: ProviderType):
        self.name = name
        self.type = type
        self.model_config = ModelConfig()
        self.available = self.check_availability()
    
    @abstractmethod
    def check_availability(self) -> bool:
        """Check if provider is available"""
        pass
    
    @abstractmethod
    async def execute(
        self,
        prompt: str,
        model: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Execute prompt and return response with metadata"""
        pass
    
    def estimate_cost(
        self,
        model_name: str,
        prompt_tokens: int,
        max_response_tokens: int = 1000
    ) -> float:
        """Estimate cost for execution"""
        costs = self.model_config.get_model_cost(model_name)
        input_cost = (prompt_tokens / 1000) * costs["input"]
        output_cost = (max_response_tokens / 1000) * costs["output"]
        return round(input_cost + output_cost, 4)


class LocalProvider(Provider):
    """Local MCP execution provider"""
    
    def __init__(self):
        super().__init__("LOCAL", ProviderType.LOCAL)
    
    def check_availability(self) -> bool:
        """Local provider is always available"""
        return True
    
    async def execute(
        self,
        prompt: str,
        model: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Local execution returns prompt for MCP client"""
        metadata = {
            "provider": self.name,
            "type": "local",
            "timestamp": datetime.now().isoformat(),
            "execution_mode": "mcp_client",
            "model": model or "local"
        }
        
        # For local, we return the prompt itself
        # The MCP client will execute it
        return prompt, metadata


class AnthropicProvider(Provider):
    """Anthropic API provider"""
    
    def __init__(self):
        super().__init__("ANTHROPIC", ProviderType.REMOTE)
        if self.available:
            self.client = anthropic.AsyncAnthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
    
    def check_availability(self) -> bool:
        """Check if Anthropic API is available"""
        return HAS_ANTHROPIC and bool(os.getenv("ANTHROPIC_API_KEY"))
    
    async def execute(
        self,
        prompt: str,
        model: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Execute via Anthropic API"""
        if not self.available:
            raise RuntimeError("Anthropic API provider not available")
        
        config = config or {}
        model_name = model or self.model_config.get_model_name("ANTHROPIC", "M")
        
        try:
            start_time = datetime.now()
            
            response = await self.client.messages.create(
                model=model_name,
                max_tokens=config.get("max_tokens", 4000),
                temperature=config.get("temperature", 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            content = response.content[0].text
            
            # Get token usage if available
            if hasattr(response, 'usage'):
                prompt_tokens = response.usage.input_tokens
                completion_tokens = response.usage.output_tokens
            else:
                # Estimate tokens
                prompt_tokens = int(len(prompt.split()) * 1.3)
                completion_tokens = int(len(content.split()) * 1.3)
            
            cost = self.estimate_cost(model_name, prompt_tokens, completion_tokens)
            
            metadata = {
                "provider": self.name,
                "model": model_name,
                "timestamp": end_time.isoformat(),
                "execution_time": execution_time,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "cost": cost
            }
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"Anthropic API execution error: {e}")
            raise


class OpenAIProvider(Provider):
    """OpenAI API provider"""
    
    def __init__(self):
        super().__init__("OPENAI", ProviderType.REMOTE)
        if self.available:
            self.client = openai.AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            if HAS_INSTRUCTOR:
                self.instructor_client = patch(self.client)
    
    def check_availability(self) -> bool:
        """Check if OpenAI is available"""
        return HAS_OPENAI and bool(os.getenv("OPENAI_API_KEY"))
    
    async def execute(
        self,
        prompt: str,
        model: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Execute via OpenAI API"""
        if not self.available:
            raise RuntimeError("OpenAI provider not available")
        
        config = config or {}
        model_name = model or self.model_config.get_model_name("OPENAI", "M")
        
        try:
            start_time = datetime.now()
            
            # Handle o1 models differently (they don't support temperature)
            if model_name.startswith("o1"):
                messages = [{"role": "user", "content": prompt}]
                completion_params = {
                    "model": model_name,
                    "messages": messages,
                    "max_completion_tokens": config.get("max_tokens", 4000)
                }
            else:
                messages = [{"role": "user", "content": prompt}]
                completion_params = {
                    "model": model_name,
                    "messages": messages,
                    "temperature": config.get("temperature", 0.7),
                    "max_tokens": config.get("max_tokens", 4000)
                }
            
            response = await self.client.chat.completions.create(**completion_params)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            content = response.choices[0].message.content
            
            metadata = {
                "provider": self.name,
                "model": model_name,
                "timestamp": end_time.isoformat(),
                "execution_time": execution_time,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "cost": self.estimate_cost(
                    model_name,
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
            }
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"OpenAI execution error: {e}")
            raise


class GoogleProvider(Provider):
    """Google Gemini API provider"""
    
    def __init__(self):
        super().__init__("GOOGLE", ProviderType.REMOTE)
        if self.available:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
    def check_availability(self) -> bool:
        """Check if Google API is available"""
        return HAS_GOOGLE and bool(os.getenv("GOOGLE_API_KEY"))
    
    async def execute(
        self,
        prompt: str,
        model: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Execute via Google API"""
        if not self.available:
            raise RuntimeError("Google provider not available")
        
        config = config or {}
        model_name = model or self.model_config.get_model_name("GOOGLE", "M")
        
        try:
            start_time = datetime.now()
            
            # Create model instance
            model_client = genai.GenerativeModel(model_name)
            
            # Google's async support is different
            response = await asyncio.to_thread(
                model_client.generate_content,
                prompt,
                generation_config={
                    "temperature": config.get("temperature", 0.7),
                    "max_output_tokens": config.get("max_tokens", 4000)
                }
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            content = response.text
            
            # Estimate tokens
            prompt_tokens = int(len(prompt.split()) * 1.3)
            completion_tokens = int(len(content.split()) * 1.3)
            
            metadata = {
                "provider": self.name,
                "model": model_name,
                "timestamp": end_time.isoformat(),
                "execution_time": execution_time,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "cost": self.estimate_cost(model_name, prompt_tokens, completion_tokens)
            }
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"Google execution error: {e}")
            raise


class GroqProvider(Provider):
    """Groq API provider"""
    
    def __init__(self):
        super().__init__("GROQ", ProviderType.REMOTE)
        if self.available:
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def check_availability(self) -> bool:
        """Check if Groq API is available"""
        return HAS_GROQ and bool(os.getenv("GROQ_API_KEY"))
    
    async def execute(
        self,
        prompt: str,
        model: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Execute via Groq API"""
        if not self.available:
            raise RuntimeError("Groq provider not available")
        
        config = config or {}
        model_name = model or self.model_config.get_model_name("GROQ", "M")
        
        try:
            start_time = datetime.now()
            
            # Groq doesn't have native async, so use asyncio.to_thread
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.get("temperature", 0.7),
                max_tokens=config.get("max_tokens", 4000)
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            content = response.choices[0].message.content
            
            metadata = {
                "provider": self.name,
                "model": model_name,
                "timestamp": end_time.isoformat(),
                "execution_time": execution_time,
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response, 'usage') else int(len(prompt.split()) * 1.3),
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else int(len(content.split()) * 1.3),
                "total_tokens": response.usage.total_tokens if hasattr(response, 'usage') else int((len(prompt.split()) + len(content.split())) * 1.3),
                "cost": self.estimate_cost(
                    model_name,
                    response.usage.prompt_tokens if hasattr(response, 'usage') else int(len(prompt.split()) * 1.3),
                    response.usage.completion_tokens if hasattr(response, 'usage') else int(len(content.split()) * 1.3)
                )
            }
            
            return content, metadata
            
        except Exception as e:
            logger.error(f"Groq execution error: {e}")
            raise


class ProviderManager:
    """Enhanced provider manager with model size support"""
    
    def __init__(self):
        self.providers: Dict[str, Provider] = {}
        self.model_config = ModelConfig()
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers"""
        # Always add local provider
        self.providers["LOCAL"] = LocalProvider()
        
        # Initialize API providers
        provider_classes = [
            ("ANTHROPIC", AnthropicProvider),
            ("OPENAI", OpenAIProvider),
            ("GOOGLE", GoogleProvider),
            ("GROQ", GroqProvider)
        ]
        
        for name, provider_class in provider_classes:
            try:
                provider = provider_class()
                if provider.available:
                    self.providers[name] = provider
                    logger.info(f"Initialized {name} provider")
                else:
                    logger.info(f"{name} provider not available")
            except Exception as e:
                logger.warning(f"Failed to initialize {name} provider: {e}")
        
        logger.info(f"Initialized {len(self.providers)} providers total")
    
    async def execute(
        self,
        prompt: str,
        provider: ProviderName = "ANTHROPIC",
        size: ModelSize = "M",
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Tuple[str, Dict[str, Any]]:
        """Execute prompt with specified provider and model size"""
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' not available. Available: {list(self.providers.keys())}")
        
        # Get model name for the provider and size
        try:
            model_name = self.model_config.get_model_name(provider, size)
        except ValueError as e:
            # Fallback to local if model not configured
            if provider == "LOCAL":
                model_name = "local"
            else:
                raise e
        
        # Merge config with kwargs
        final_config = config or {}
        final_config.update(kwargs)
        
        # Execute with the provider
        return await self.providers[provider].execute(
            prompt=prompt,
            model=model_name,
            config=final_config
        )
    
    def get_model_info(self, provider: ProviderName, size: ModelSize) -> Dict:
        """Get information about a specific model configuration"""
        try:
            model_name = self.model_config.get_model_name(provider, size)
            costs = self.model_config.get_model_cost(model_name)
            
            return {
                "provider": provider,
                "size": size,
                "model": model_name,
                "env_key": f"{provider}_{size}_MODEL",
                "costs": costs,
                "available": provider in self.providers
            }
        except ValueError as e:
            return {
                "provider": provider,
                "size": size,
                "model": None,
                "env_key": f"{provider}_{size}_MODEL",
                "error": str(e),
                "available": False
            }
    
    def list_configured_models(self) -> Dict[str, Dict[str, str]]:
        """List all configured models"""
        return self.model_config.list_configured_models()
    
    def list_providers(self) -> List[str]:
        """List available provider names"""
        return list(self.providers.keys())
    
    def estimate_cost(
        self,
        provider: ProviderName,
        size: ModelSize,
        prompt_tokens: int,
        max_response_tokens: int = 1000
    ) -> float:
        """Estimate cost for a specific provider and size"""
        try:
            model_name = self.model_config.get_model_name(provider, size)
            if provider in self.providers:
                return self.providers[provider].estimate_cost(
                    model_name, prompt_tokens, max_response_tokens
                )
        except ValueError:
            pass
        
        return 0.0


# Convenience functions for backward compatibility
async def execute_with_provider(
    prompt: str,
    provider: str = "ANTHROPIC",
    size: str = "M",
    **kwargs
) -> Tuple[str, Dict[str, Any]]:
    """Execute prompt with provider (backward compatible)"""
    manager = ProviderManager()
    return await manager.execute(prompt, provider, size, **kwargs)

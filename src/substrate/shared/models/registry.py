"""
Model Registry - Single Source of Truth from .env
"""
import os
import re
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from enum import Enum


class ModelSize(Enum):
    """Standard model size classifications"""
    XS = "xs"
    S = "s"
    M = "m"
    L = "l"
    XL = "xl"
    XXL = "xxl"


class ModelProvider(Enum):
    """Supported model providers"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    GROQ = "groq"


@dataclass
class ModelInfo:
    """Model information container"""
    provider: ModelProvider
    size: ModelSize
    api_name: str
    nickname: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    
    # Performance characteristics (can be extended)
    max_tokens: int = 4096
    supports_system: bool = True
    supports_streaming: bool = True
    
    # Cost tier (for AKAB experiments)
    cost_tier: int = field(init=False)
    
    def __post_init__(self):
        """Calculate cost tier based on size"""
        size_to_tier = {
            ModelSize.XS: 1,
            ModelSize.S: 1,
            ModelSize.M: 2,
            ModelSize.L: 3,
            ModelSize.XL: 4,
            ModelSize.XXL: 5
        }
        self.cost_tier = size_to_tier.get(self.size, 3)
    
    @property
    def identifier(self) -> str:
        """Get standard identifier like 'anthropic_m'"""
        return f"{self.provider.value}_{self.size.value}"


class ModelRegistry:
    """Registry for all available models loaded from environment"""
    
    def __init__(self):
        self.models: Dict[str, ModelInfo] = {}
        self._load_from_environment()
    
    def _load_from_environment(self):
        """Load all model configurations from environment variables"""
        # Pattern to match model definitions
        model_pattern = re.compile(r"^(ANTHROPIC|OPENAI|GOOGLE|GROQ)_(XS|S|M|L|XL|XXL)_MODEL$")
        
        for key, value in os.environ.items():
            match = model_pattern.match(key)
            if match and value:
                provider_str = match.group(1)
                size_str = match.group(2)
                
                provider = ModelProvider(provider_str.lower())
                size = ModelSize(size_str.lower())
                
                # Get API key
                api_key = os.getenv(f"{provider_str}_API_KEY")
                
                # Get base URL if specified
                base_url = os.getenv(f"{provider_str}_BASE_URL")
                
                # Create model info
                model = ModelInfo(
                    provider=provider,
                    size=size,
                    api_name=value,
                    nickname=f"{provider.value}_{size.value}",
                    api_key=api_key,
                    base_url=base_url
                )
                
                # Add provider-specific settings
                self._configure_model_specifics(model)
                
                # Store by identifier
                self.models[model.identifier] = model
    
    def _configure_model_specifics(self, model: ModelInfo):
        """Configure provider-specific model settings"""
        if model.provider == ModelProvider.ANTHROPIC:
            # All Anthropic models support large contexts
            if model.size in [ModelSize.XL, ModelSize.XXL]:
                model.max_tokens = 8192
            else:
                model.max_tokens = 4096
                
        elif model.provider == ModelProvider.OPENAI:
            # O1 models don't support system prompts
            if model.api_name.startswith("o1"):
                model.supports_system = False
                model.max_tokens = 32768
            else:
                model.max_tokens = 4096
                
        elif model.provider == ModelProvider.GOOGLE:
            # Gemini models have large contexts
            model.max_tokens = 8192
            
        elif model.provider == ModelProvider.GROQ:
            # Groq has limited output tokens
            model.max_tokens = 1024
    
    def get(self, identifier: str) -> Optional[ModelInfo]:
        """Get model by identifier (e.g., 'anthropic_m')"""
        return self.models.get(identifier)
    
    def get_by_api_name(self, api_name: str) -> Optional[ModelInfo]:
        """Get model by API name (e.g., 'claude-3-5-sonnet-20241022')"""
        for model in self.models.values():
            if model.api_name == api_name:
                return model
        return None
    
    def list_providers(self) -> List[ModelProvider]:
        """List all available providers"""
        return list(set(m.provider for m in self.models.values()))
    
    def list_models(self, provider: Optional[ModelProvider] = None,
                   size: Optional[ModelSize] = None) -> List[ModelInfo]:
        """List models with optional filtering"""
        models = list(self.models.values())
        
        if provider:
            models = [m for m in models if m.provider == provider]
        
        if size:
            models = [m for m in models if m.size == size]
            
        return models
    
    def get_scrambled_models(self) -> Dict[str, str]:
        """Get scrambled model mappings for Level 3 experiments"""
        import hashlib
        
        scrambled = {}
        for identifier, model in self.models.items():
            # Create deterministic scrambled ID
            hash_input = f"{identifier}_{os.getenv('EXPERIMENT_SALT', 'atlas')}"
            scrambled_id = f"model_{hashlib.sha256(hash_input.encode()).hexdigest()[:8]}"
            scrambled[scrambled_id] = identifier
            
        return scrambled
    
    def validate(self) -> Dict[str, List[str]]:
        """Validate model configuration completeness"""
        issues = {
            "missing_models": [],
            "missing_api_keys": [],
            "duplicate_models": []
        }
        
        # Check for expected models
        for provider in ModelProvider:
            for size in ModelSize:
                identifier = f"{provider.value}_{size.value}"
                if identifier not in self.models:
                    issues["missing_models"].append(identifier)
                elif not self.models[identifier].api_key:
                    issues["missing_api_keys"].append(identifier)
        
        # Check for duplicate API names
        api_names = {}
        for model in self.models.values():
            if model.api_name in api_names:
                issues["duplicate_models"].append(
                    f"{model.identifier} and {api_names[model.api_name]} both use {model.api_name}"
                )
            api_names[model.api_name] = model.identifier
            
        return {k: v for k, v in issues.items() if v}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get registry summary for documentation"""
        providers = list(set(m.provider.value for m in self.models.values()))
        return {
            "providers": providers,
            "models": len(self.models),
            "sizes": list(set(m.size.value for m in self.models.values()))
        }


# Singleton instance
_registry = None

def get_model_registry() -> ModelRegistry:
    """Get the singleton model registry instance"""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry

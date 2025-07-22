"""Clear (unblinded) API wrapper for making LLM calls across providers"""
import os
import time
import httpx
import json
from typing import Dict, Any, Optional
from ..models import ModelInfo, get_model_registry

# Import provider-specific libraries with fallbacks
try:
    import anthropic
except ImportError:
    anthropic = None
    
try:
    import openai
except ImportError:
    openai = None
    
try:
    import google.generativeai as genai
except ImportError:
    genai = None


class ClearHermes:
    """Unified API wrapper for all supported LLM providers
    
    This is a shared substrate component used by multiple servers:
    - AKAB: For Level 1 quick comparisons
    - Synapse: For testing enhanced prompts
    - Any server needing direct LLM API calls
    """
    
    def __init__(self):
        """Initialize provider clients"""
        self.clients = {}
        self._init_clients()
    
    def _init_clients(self):
        """Initialize all provider clients with API keys from environment"""
        # Anthropic
        if anthropic and (api_key := os.getenv("ANTHROPIC_API_KEY")):
            self.clients["anthropic"] = anthropic.AsyncAnthropic(api_key=api_key)
        
        # OpenAI
        if openai and (api_key := os.getenv("OPENAI_API_KEY")):
            self.clients["openai"] = openai.AsyncOpenAI(api_key=api_key)
        
        # Google
        if genai and (api_key := os.getenv("GOOGLE_API_KEY")):
            genai.configure(api_key=api_key)
            self.clients["google"] = genai
        
        # Groq
        if openai and (api_key := os.getenv("GROQ_API_KEY")):
            # Groq uses OpenAI-compatible client
            self.clients["groq"] = openai.AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
    
    async def complete(
        self, 
        model: ModelInfo, 
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Make completion call to appropriate provider
        
        Args:
            model: ModelInfo from MODEL_REGISTRY
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Standardized response dict with:
            - content: Generated text
            - tokens: Token count
            - latency: Response time in seconds
            - model: Model identifier
            - provider: Provider name
        """
        provider_name = model.provider.value if hasattr(model.provider, 'value') else str(model.provider)
        
        if provider_name not in self.clients:
            raise ValueError(f"Provider {provider_name} not configured. Set {provider_name.upper()}_API_KEY")
        
        start_time = time.time()
        
        # Route to provider-specific method
        method_name = f"_complete_{provider_name}"
        if not hasattr(self, method_name):
            raise NotImplementedError(f"Provider {provider_name} not implemented")
        
        method = getattr(self, method_name)
        result = await method(
            self.clients[provider_name],
            model,
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        # Add timing and metadata
        result["latency"] = time.time() - start_time
        result["model"] = model.api_name
        result["provider"] = provider_name
        
        return result
    
    async def _complete_anthropic(
        self, 
        client: anthropic.AsyncAnthropic,
        model: ModelInfo,
        prompt: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> Dict[str, Any]:
        """Anthropic-specific completion"""
        response = await client.messages.create(
            model=model.api_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        return {
            "content": response.content[0].text,
            "tokens": response.usage.input_tokens + response.usage.output_tokens,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }
    
    async def _complete_openai(
        self,
        client: openai.AsyncOpenAI,
        model: ModelInfo,
        prompt: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> Dict[str, Any]:
        """OpenAI-specific completion"""
        response = await client.chat.completions.create(
            model=model.api_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        return {
            "content": response.choices[0].message.content,
            "tokens": response.usage.total_tokens,
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens
        }
    
    async def _complete_google(
        self,
        client,  # genai module
        model: ModelInfo,
        prompt: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> Dict[str, Any]:
        """Google-specific completion"""
        # Google uses synchronous API, so we run in executor
        import asyncio
        
        def sync_generate():
            model_instance = client.GenerativeModel(model.api_name)
            response = model_instance.generate_content(
                prompt,
                generation_config=client.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
            )
            return response
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, sync_generate)
        
        # Estimate tokens (Google doesn't always provide exact counts)
        estimated_tokens = len(prompt.split()) + len(response.text.split())
        
        return {
            "content": response.text,
            "tokens": estimated_tokens,
            "input_tokens": len(prompt.split()),
            "output_tokens": len(response.text.split())
        }
    
    async def _complete_groq(
        self,
        client: openai.AsyncOpenAI,  # Groq uses OpenAI-compatible client
        model: ModelInfo,
        prompt: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> Dict[str, Any]:
        """Groq-specific completion (OpenAI-compatible)"""
        # Groq uses same interface as OpenAI
        return await self._complete_openai(client, model, prompt, max_tokens, temperature, **kwargs)
    
    async def batch_complete(
        self,
        requests: list[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> list[Dict[str, Any]]:
        """Execute multiple completion requests concurrently
        
        Args:
            requests: List of dicts with keys: model, prompt, max_tokens, etc.
            max_concurrent: Maximum concurrent API calls
            
        Returns:
            List of results in same order as requests
        """
        import asyncio
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_complete(request):
            async with semaphore:
                model_id = request.pop("model", "anthropic_m")
                
                # Get registry instance
                registry = get_model_registry()
                
                # Get model by identifier
                model = registry.get(model_id)
                
                if not model:
                    return {"error": f"Unknown model: {model_id}"}
                
                try:
                    return await self.complete(model, **request)
                except Exception as e:
                    return {"error": str(e), "model": model_id}
        
        tasks = [limited_complete(req.copy()) for req in requests]
        return await asyncio.gather(*tasks)
    
    def get_configured_providers(self) -> list[str]:
        """Get list of providers with configured API keys"""
        return list(self.clients.keys())

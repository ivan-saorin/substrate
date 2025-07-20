"""
YAML Prompt Loader - Manages all prompts and patterns as data
"""
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Prompt:
    """Individual prompt with metadata"""
    content: str
    metadata: Dict[str, Any]
    name: str
    source_file: str
    
    def format(self, **kwargs) -> str:
        """Format prompt with variables"""
        try:
            return self.content.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required variable in prompt '{self.name}': {e}")
    
    @property
    def models(self) -> List[str]:
        """Get recommended models for this prompt"""
        return self.metadata.get('models', [])
    
    @property
    def effectiveness(self) -> float:
        """Get effectiveness score if available"""
        return self.metadata.get('effectiveness', 0.0)


class PromptLoader:
    """Centralized YAML prompt loading and management"""
    
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self._cache: Dict[str, Dict[str, Prompt]] = {}
        self._pattern_cache: Dict[str, Any] = {}
    
    def load(self, path: str, force_reload: bool = False) -> Dict[str, Prompt]:
        """Load prompts from YAML file"""
        # Normalize path
        if not path.endswith(('.yaml', '.yml')):
            path = f"{path}.yaml"
        
        # Check cache
        if not force_reload and path in self._cache:
            return self._cache[path]
        
        # Find file
        file_path = self._resolve_path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        
        # Load YAML
        data = self.load_yaml(str(file_path))
        
        # Validate structure
        if 'prompts' not in data:
            raise ValueError(f"Invalid prompt file structure in {path}: missing 'prompts' key")
        
        # Parse prompts
        prompts = {}
        for name, prompt_data in data['prompts'].items():
            if isinstance(prompt_data, str):
                # Simple string prompt
                prompt = Prompt(
                    content=prompt_data,
                    metadata={},
                    name=name,
                    source_file=str(file_path)
                )
            elif isinstance(prompt_data, dict):
                # Prompt with metadata
                content = prompt_data.get('content', '')
                metadata = {k: v for k, v in prompt_data.items() if k != 'content'}
                prompt = Prompt(
                    content=content,
                    metadata=metadata,
                    name=name,
                    source_file=str(file_path)
                )
            else:
                raise ValueError(f"Invalid prompt format for '{name}' in {path}")
            
            prompts[name] = prompt
        
        # Cache and return
        self._cache[path] = prompts
        return prompts
    
    def load_pattern(self, path: str, force_reload: bool = False) -> Dict[str, Any]:
        """Load pattern/workflow from YAML file"""
        if not force_reload and path in self._pattern_cache:
            return self._pattern_cache[path]
        
        file_path = self._resolve_path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Pattern file not found: {path}")
        
        pattern = self.load_yaml(str(file_path))
        self._pattern_cache[path] = pattern
        return pattern
    
    def load_yaml(self, file_path: str) -> Dict[str, Any]:
        """Load and parse YAML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def save_yaml(self, data: Dict[str, Any], file_path: str):
        """Save data to YAML file"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    def get_prompt(self, file: str, name: str) -> Prompt:
        """Get specific prompt by file and name"""
        prompts = self.load(file)
        if name not in prompts:
            raise KeyError(f"Prompt '{name}' not found in {file}")
        return prompts[name]
    
    def format_prompt(self, file: str, name: str, **kwargs) -> str:
        """Load and format a prompt in one call"""
        prompt = self.get_prompt(file, name)
        return prompt.format(**kwargs)
    
    def list_prompts(self, pattern: Optional[str] = None) -> List[tuple]:
        """List all available prompts with optional pattern matching"""
        results = []
        
        # Search for YAML files
        search_paths = [
            self.base_dir,
            os.path.join(self.base_dir, '..', '..', 'features'),
            os.path.join(self.base_dir, '..', '..', 'patterns')
        ]
        
        for search_path in search_paths:
            if os.path.exists(search_path):
                for root, _, files in os.walk(search_path):
                    for file in files:
                        if file.endswith(('.yaml', '.yml')):
                            rel_path = os.path.relpath(
                                os.path.join(root, file), 
                                self.base_dir
                            )
                            
                            if pattern and pattern not in rel_path:
                                continue
                            
                            try:
                                prompts = self.load(rel_path)
                                for prompt_name in prompts:
                                    results.append((rel_path, prompt_name))
                            except Exception:
                                # Skip invalid files
                                pass
        
        return results
    
    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to base directory"""
        # Try absolute path first
        abs_path = Path(path)
        if abs_path.exists():
            return abs_path
        
        # Try relative to base
        rel_path = Path(self.base_dir) / path
        if rel_path.exists():
            return rel_path
        
        # Try common locations
        locations = [
            Path(self.base_dir).parent.parent / 'features' / path,
            Path(self.base_dir).parent.parent / 'patterns' / path,
            Path(self.base_dir).parent.parent / path
        ]
        
        for loc in locations:
            if loc.exists():
                return loc
        
        # Return original for error message
        return Path(path)
    
    def create_prompt_file(self, path: str, prompts: Dict[str, Any], 
                          version: str = "1.0"):
        """Create a new prompt YAML file"""
        data = {
            'version': version,
            'created': datetime.now().isoformat(),
            'prompts': prompts
        }
        
        file_path = self._resolve_path(path)
        self.save_yaml(data, str(file_path))
        
        # Clear cache
        if path in self._cache:
            del self._cache[path]
    
    def validate_variables(self, file: str, name: str, 
                          variables: Dict[str, Any]) -> List[str]:
        """Validate that all required variables are provided"""
        prompt = self.get_prompt(file, name)
        
        # Find all {variable} patterns
        pattern = re.compile(r'\{(\w+)\}')
        required = set(pattern.findall(prompt.content))
        provided = set(variables.keys())
        
        missing = required - provided
        return list(missing)

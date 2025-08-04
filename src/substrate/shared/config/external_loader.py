"""External configuration loader for substrate

This module loads external configurations from atlas-meta when available,
allowing substrate to work both standalone and with enhanced features.
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class ExternalConfigLoader:
    """Load external configurations from atlas-meta if available"""
    
    def __init__(self):
        # Get external path from environment, default to None
        self.external_path = os.getenv('ATLAS_META_PATH')
        self.system_docs_path = None
        
        if self.external_path:
            # Convert to Path object and handle Windows paths
            self.external_path = Path(self.external_path)
            self.system_docs_path = self.external_path / 'system-docs'
            
            if not self.system_docs_path.exists():
                # Try alternative Docker path if Windows path doesn't exist
                if os.name == 'nt' and not self.external_path.is_absolute():
                    # On Windows, try the Docker mount path
                    docker_path = Path('/projects/atlas/atlas-meta/system-docs')
                    if docker_path.exists():
                        self.system_docs_path = docker_path
                    else:
                        logger.warning(f"ATLAS_META_PATH set but system-docs not found at {self.system_docs_path}")
                        self.system_docs_path = None
                else:
                    logger.warning(f"ATLAS_META_PATH set but system-docs not found at {self.system_docs_path}")
                    self.system_docs_path = None
    
    def is_available(self) -> bool:
        """Check if external configuration is available"""
        return self.system_docs_path is not None and self.system_docs_path.exists()
    
    def load_instance_configs(self) -> Dict[str, Any]:
        """Load instance configurations from external source"""
        configs = {}
        
        if not self.is_available():
            return configs
            
        config_file = self.system_docs_path / 'instances' / 'config.yaml'
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    configs = yaml.safe_load(f) or {}
                logger.info(f"Loaded {len(configs)} instance configurations from {config_file}")
            except Exception as e:
                logger.error(f"Failed to load instance configs: {e}")
                
        return configs
    
    def load_documentation(self, doc_type: str) -> Optional[Dict[str, Any]]:
        """Load documentation from external source
        
        Args:
            doc_type: Type of documentation to load (e.g., 'atlas', 'synapse')
            
        Returns:
            Documentation content if found, None otherwise
        """
        if not self.is_available():
            return None
        
        # Check instances directory first
        instance_doc = self.system_docs_path / 'instances' / f'{doc_type}.yaml'
        if instance_doc.exists():
            try:
                with open(instance_doc, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                logger.info(f"Loaded instance documentation for {doc_type}")
                return content
            except Exception as e:
                logger.error(f"Failed to load instance doc {doc_type}: {e}")
                
        # Check servers directory
        server_doc = self.system_docs_path / 'servers' / f'{doc_type}.yaml'
        if server_doc.exists():
            try:
                with open(server_doc, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                logger.info(f"Loaded server documentation for {doc_type}")
                return content
            except Exception as e:
                logger.error(f"Failed to load server doc {doc_type}: {e}")
                
        return None
    
    def get_all_documentation_types(self) -> List[str]:
        """Get list of all available documentation types from external source"""
        doc_types = []
        
        if not self.is_available():
            return doc_types
        
        # Check instances directory
        instances_dir = self.system_docs_path / 'instances'
        if instances_dir.exists():
            for file in instances_dir.glob('*.yaml'):
                if file.name != 'config.yaml':
                    doc_types.append(file.stem)
        
        # Check servers directory
        servers_dir = self.system_docs_path / 'servers'
        if servers_dir.exists():
            for file in servers_dir.glob('*.yaml'):
                doc_types.append(file.stem)
                
        return sorted(set(doc_types))  # Remove duplicates and sort


# Global instance for easy access
_loader = None

def get_external_loader() -> ExternalConfigLoader:
    """Get or create the global external loader instance"""
    global _loader
    if _loader is None:
        _loader = ExternalConfigLoader()
    return _loader

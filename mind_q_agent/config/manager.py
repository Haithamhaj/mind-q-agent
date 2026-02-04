import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from mind_q_agent.utils.errors import MindQError

class ConfigError(MindQError):
    """Raised when configuration loading fails."""
    pass

class ConfigManager:
    """
    Singleton configuration manager.
    Loads from default.yaml and overrides with environment variables.
    """
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
        
    def _load_config(self) -> None:
        """Load configuration from file and environment."""
        # Determine config path
        base_dir = Path(__file__).parent.parent.parent
        config_path = base_dir / "config" / "default.yaml"
        
        # Load YAML
        try:
            if config_path.exists():
                with open(config_path, "r") as f:
                    self._config = yaml.safe_load(f) or {}
            else:
                self._config = {}
        except Exception as e:
            raise ConfigError(f"Failed to load config from {config_path}", original_exception=e)
            
        # Override with Environment Variables
        # Format: MINDQ_SECTION_KEY (e.g. MINDQ_DB_GRAPH_PATH)
        self._override_from_env()

    def _override_from_env(self) -> None:
        """Override config values with MINDQ_ prefixed env vars."""
        prefix = "MINDQ_"
        for env_key, value in os.environ.items():
            if not env_key.startswith(prefix):
                continue
                
            # Remove prefix and convert to lowercase parts
            # e.g. MINDQ_DB_GRAPH_PATH -> db_graph_path
            key_without_prefix = env_key[len(prefix):].lower()
            
            # Try to match against config structure
            self._recursive_update(self._config, key_without_prefix, value)

    def _recursive_update(self, config: Dict[str, Any], key_string: str, value: str) -> None:
        """
        Recursively find the best matching key in the config.
        Example: key_string="db_graph_path", config={"db": {"graph_path": "..."}}
        Should match "db" then "graph_path".
        """
        # 1. Direct match (leaf)
        if key_string in config:
            config[key_string] = value
            return

        # 2. Key prefix match (nested)
        # Sort keys by length (descending) to match longest prefixes first
        # e.g. if we have "logging" and "log", match "logging" first
        for key in sorted(config.keys(), key=len, reverse=True):
            if key_string.startswith(key + "_"):
                # Found a matching section
                remaining_key = key_string[len(key)+1:] # skip key and underscore
                if isinstance(config[key], dict):
                    self._recursive_update(config[key], remaining_key, value)
                    return
        
        # 3. Fallback: If no match found in existing structure, we can optionally create it.
        # For now, let's assume we ONLY override existing keys to be safe.
        # Or, simplistic fallback: split by first underscore
        # parts = key_string.split('_', 1)
        # if len(parts) > 1:
        #    section, rest = parts
        #    if section not in config: config[section] = {}
        #    self._recursive_update(config[section], rest, value)

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get the full configuration dictionary."""
        if cls._instance is None:
            cls()
        return cls._instance._config
        
    @classmethod
    def get(cls, section: str, key: str, default: Any = None) -> Any:
        """Get a specific config value safely."""
        config = cls.get_config()
        return config.get(section, {}).get(key, default)
    
    @classmethod
    def reset(cls):
        """Reset the singleton instance (mostly for testing)."""
        cls._instance = None
        cls._config = {}

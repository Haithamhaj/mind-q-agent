import os
import pytest
import yaml
from mind_q_agent.config.manager import ConfigManager, ConfigError

class TestConfigManager:
    """Tests for configuration management."""
    
    @pytest.fixture(autouse=True)
    def reset_config(self):
        """Reset ConfigManager singleton before each test."""
        ConfigManager.reset()
        yield
        ConfigManager.reset()
        if "MINDQ_TEST_VAL" in os.environ:
            del os.environ["MINDQ_TEST_VAL"]
        if "MINDQ_DB_GRAPH_PATH" in os.environ:
            del os.environ["MINDQ_DB_GRAPH_PATH"]
            
    def test_load_default(self, tmp_path):
        """Test loading defaults."""
        # ConfigManager loads from relative path, so it might fail if we don't mock the file
        # But we created the actual default.yaml, so it should load that.
        config = ConfigManager.get_config()
        assert "db" in config
        assert "watcher" in config
        assert config["logging"]["level"] == "INFO"
        
    def test_singleton(self):
        """Test singleton pattern."""
        c1 = ConfigManager()
        c2 = ConfigManager()
        assert c1 is c2
        assert ConfigManager.get_config() is ConfigManager.get_config()
        
    def test_env_override(self):
        """Test overriding via environment variables."""
        os.environ["MINDQ_LOGGING_LEVEL"] = "DEBUG"
        os.environ["MINDQ_DB_GRAPH_PATH"] = "/custom/graph"
        
        ConfigManager.reset() # Reload
        
        val = ConfigManager.get("logging", "level")
        assert val == "DEBUG"
        
        db_path = ConfigManager.get("db", "graph_path")
        assert db_path == "/custom/graph"
        
    def test_get_helper(self):
        """Test the convenient .get() method."""
        val = ConfigManager.get("watcher", "debounce_seconds")
        assert val == 1.0 # From default.yaml
        
        missing = ConfigManager.get("nonexistent", "key", default="fallback")
        assert missing == "fallback"

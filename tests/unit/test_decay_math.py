import pytest
import math
from mind_q_agent.learning.decay_math import calculate_decay, calculate_days_since

class TestDecayMath:
    """Unit tests for temporal decay math functions."""

    @pytest.fixture
    def custom_config(self):
        """Custom config with known decay rate."""
        return {"decay_rate": 0.1}  # Faster decay for testing

    def test_decay_zero_days(self, custom_config):
        """No decay if 0 days have passed."""
        weight = calculate_decay(0.8, days_since_update=0, config=custom_config)
        assert weight == 0.8

    def test_decay_seven_days(self, custom_config):
        """Weight should decrease after 7 days."""
        initial = 0.8
        weight = calculate_decay(initial, days_since_update=7, config=custom_config)
        expected = initial * math.exp(-0.1 * 7)  # ~0.397
        assert weight == pytest.approx(expected, abs=0.01)
        assert weight < initial

    def test_decay_thirty_days(self, custom_config):
        """Weight should be significantly lower after 30 days."""
        initial = 0.8
        weight = calculate_decay(initial, days_since_update=30, config=custom_config)
        expected = initial * math.exp(-0.1 * 30)  # ~0.04
        assert weight == pytest.approx(expected, abs=0.01)
        assert weight < 0.1

    def test_decay_never_negative(self, custom_config):
        """Weight should never go below 0."""
        weight = calculate_decay(0.5, days_since_update=1000, config=custom_config)
        assert weight >= 0.0

    def test_decay_from_zero_weight(self, custom_config):
        """Zero weight should stay zero."""
        weight = calculate_decay(0.0, days_since_update=10, config=custom_config)
        assert weight == 0.0

    def test_calculate_days_since_valid(self):
        """Test parsing of timestamp."""
        from datetime import datetime, timedelta
        
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        days = calculate_days_since(yesterday)
        assert 0.9 < days < 1.1  # Approximately 1 day

    def test_calculate_days_since_invalid(self):
        """Invalid timestamp should return 0."""
        days = calculate_days_since("not-a-date")
        assert days == 0.0

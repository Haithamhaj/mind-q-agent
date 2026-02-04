import pytest
from mind_q_agent.learning.hebbian_math import calculate_new_weight, calculate_interaction_score

class TestHebbianMath:
    """Unit tests for Hebbian learning math functions."""

    @pytest.fixture
    def custom_config(self):
        """Custom config for testing."""
        return {
            "alpha": 0.2,
            "event_scores": {
                "CLICK": 1.0,
                "SEARCH": 0.6,
                "VIEW_BASE": 0.4,
                "VIEW_MAX": 1.0
            }
        }

    def test_calculate_interaction_score_click(self, custom_config):
        score = calculate_interaction_score("CLICK", config=custom_config)
        assert score == 1.0

    def test_calculate_interaction_score_search(self, custom_config):
        score = calculate_interaction_score("SEARCH", config=custom_config)
        assert score == 0.6

    def test_calculate_interaction_score_view_short(self, custom_config):
        """Short view should get base score."""
        score = calculate_interaction_score("VIEW", duration_sec=0.0, config=custom_config)
        assert score == 0.4 # VIEW_BASE

    def test_calculate_interaction_score_view_long(self, custom_config):
        """30 sec view should approach VIEW_MAX."""
        score = calculate_interaction_score("VIEW", duration_sec=30.0, config=custom_config)
        assert score == pytest.approx(1.0, abs=0.01) # VIEW_MAX

    def test_calculate_new_weight_increase(self, custom_config):
        """Weight should increase after positive interaction."""
        old_w = 0.5
        new_w = calculate_new_weight(old_w, interaction_score=1.0, config=custom_config)
        # w_new = 0.5 + 0.2 * (1-0.5) * 1.0 = 0.5 + 0.1 = 0.6
        assert new_w == pytest.approx(0.6, abs=0.01)

    def test_calculate_new_weight_bounds(self, custom_config):
        """Weight should never exceed 1.0."""
        old_w = 0.99
        new_w = calculate_new_weight(old_w, interaction_score=1.0, config=custom_config)
        # w_new = 0.99 + 0.2 * (1-0.99) * 1.0 = 0.99 + 0.002 = 0.992
        assert new_w < 1.0
        assert new_w > old_w

    def test_calculate_new_weight_no_change_at_max(self, custom_config):
        """If weight is already 1.0, it should stay 1.0."""
        old_w = 1.0
        new_w = calculate_new_weight(old_w, interaction_score=1.0, config=custom_config)
        assert new_w == 1.0

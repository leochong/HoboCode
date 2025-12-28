"""Tests for models module."""

import pytest

from hobo_code.models.provider import ModelProvider


class TestModelProvider:
    """Tests for ModelProvider class."""

    def test_list_providers(self):
        """Test listing providers."""
        mp = ModelProvider()
        providers = mp.list_providers()

        assert isinstance(providers, list)
        assert "openai" in providers
        assert "anthropic" in providers

    def test_list_models_for_openai(self):
        """Test listing OpenAI models."""
        mp = ModelProvider()
        models = mp.list_models("openai")

        assert "gpt-4" in models
        assert "gpt-3.5-turbo" in models

    def test_list_models_for_anthropic(self):
        """Test listing Anthropic models."""
        mp = ModelProvider()
        models = mp.list_models("anthropic")

        assert len(models) > 0

    def test_get_model_info_gpt4(self):
        """Test getting GPT-4 model info."""
        mp = ModelProvider()
        info = mp.get_model_info("openai/gpt-4")

        assert info["model"] == "openai/gpt-4"
        assert info["provider"] == "openai"
        assert info["cost_per_1k_tokens"] == 0.03
        assert info["context_window"] == 8192

    def test_get_model_info_unknown(self):
        """Test getting info for unknown model."""
        mp = ModelProvider()
        info = mp.get_model_info("unknown/model")

        assert info["model"] == "unknown/model"
        assert info["provider"] == "unknown"
        assert info["cost_per_1k_tokens"] > 0

    def test_count_tokens(self):
        """Test token counting."""
        mp = ModelProvider()
        text = "Hello, world! This is a test."
        count = mp.count_tokens("gpt-4", text)

        assert isinstance(count, int)
        assert count > 0

    def test_estimate_cost(self):
        """Test cost estimation."""
        mp = ModelProvider()
        cost = mp.estimate_cost("gpt-4", input_tokens=100, output_tokens=50)

        assert isinstance(cost, float)
        assert cost > 0

    def test_estimate_cost_free_model(self):
        """Test cost estimation for free model."""
        mp = ModelProvider()
        cost = mp.estimate_cost("gpt-3.5-turbo", input_tokens=100, output_tokens=50)

        assert cost > 0
        assert cost < 0.001

    def test_get_completion_placeholder(self):
        """Test completion returns placeholder when no API."""
        mp = ModelProvider()
        messages = [{"role": "user", "content": "Hello"}]
        response = mp.get_completion("gpt-4", messages)

        assert "choices" in response or "error" in response

    def test_cost_per_1k_tokens_has_values(self):
        """Test that cost table has entries."""
        mp = ModelProvider()

        assert len(mp.COST_PER_1K_TOKENS) > 0
        assert mp.COST_PER_1K_TOKENS["gpt-4"] > 0

    def test_list_models_unknown_provider(self):
        """Test listing models for unknown provider."""
        mp = ModelProvider()
        models = mp.list_models("unknown_provider")

        assert len(models) > 0
        assert "unknown_provider/model-1" in models

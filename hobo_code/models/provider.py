"""Model provider management with LiteLLM integration."""

from typing import Any

try:
    import litellm
except ImportError:
    litellm = None


class ModelProvider:
    """Wrapper for LiteLLM model management."""

    COST_PER_1K_TOKENS = {
        "gpt-4": 0.03,
        "gpt-4-turbo": 0.01,
        "gpt-3.5-turbo": 0.0005,
        "claude-3-opus-20240229": 0.015,
        "claude-3-sonnet-20240229": 0.003,
        "claude-3-haiku-20240307": 0.00025,
        "ollama/llama2": 0.0,
    }

    def __init__(self):
        self._providers: list[str] = [
            "openai",
            "anthropic",
            "google_vertex_ai",
            "azure",
            "aws_bedrock",
            "ollama",
            "huggingface",
            "groq",
            "deepseek",
            "mistral",
            "openrouter",
        ]

    def list_providers(self) -> list[str]:
        """List available model providers."""
        if litellm:
            try:
                return litellm.provider_list()
            except Exception:
                pass
        return self._providers

    def list_models(self, provider: str) -> list[str]:
        """List models for a provider."""
        if not litellm:
            return self._get_default_models(provider)

        provider_models = {
            "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ],
            "ollama": ["llama2", "codellama", "mistral", "phi"],
            "groq": ["llama2-70b-4096", "mixtral-8x7b-32768"],
            "deepseek": ["deepseek-chat"],
            "mistral": ["mistral-large-latest", "mistral-small-latest"],
            "openrouter": [
                "openrouter/auto",
                "openrouter/google/gemini-pro",
                "openrouter/anthropic/claude-3-opus",
                "openrouter/meta-llama/llama-3-70b",
            ],
        }
        return provider_models.get(provider, self._get_default_models(provider))

    def _get_default_models(self, provider: str) -> list[str]:
        """Get default models for unknown provider."""
        return [f"{provider}/model-1", f"{provider}/model-2"]

    def get_model_info(self, model: str) -> dict[str, Any]:
        """Get information about a model."""
        base_model = model.split("/")[-1] if "/" in model else model
        full_model_key = model if "/" in model else ""
        cost = self.COST_PER_1K_TOKENS.get(full_model_key) or self.COST_PER_1K_TOKENS.get(
            base_model, 0.001
        )
        provider = model.split("/")[0] if "/" in model else "unknown"

        return {
            "model": model,
            "provider": provider,
            "cost_per_1k_tokens": cost,
            "context_window": self._get_context_window(base_model),
            "max_output_tokens": self._get_max_output(base_model),
        }

    def _get_context_window(self, model: str) -> int:
        """Get context window size for model."""
        windows = {
            "gpt-4": 8192,
            "gpt-4-turbo": 128000,
            "gpt-3.5-turbo": 16385,
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
        }
        return windows.get(model, 4096)

    def _get_max_output(self, model: str) -> int:
        """Get max output tokens for model."""
        outputs = {
            "gpt-4": 4096,
            "gpt-4-turbo": 4096,
            "gpt-3.5-turbo": 4096,
            "claude-3-opus-20240229": 4096,
            "claude-3-sonnet-20240229": 4096,
            "claude-3-haiku-20240307": 4096,
        }
        return outputs.get(model, 2048)

    def count_tokens(self, model: str, text: str) -> int:
        """Estimate token count for text."""
        if litellm:
            try:
                return litellm.token_counter(model=model, text=text)
            except Exception:
                pass
        return len(text) // 4

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a request."""
        info = self.get_model_info(model)
        cost_per_1k = info["cost_per_1k_tokens"]
        return (input_tokens + output_tokens) / 1000 * cost_per_1k

    def get_completion(
        self, model: str, messages: list[dict[str, str]], api_key: str | None = None
    ) -> dict[str, Any]:
        """Get completion from a model (placeholder for actual API call)."""
        if not litellm:
            return {
                "choices": [
                    {"message": {"content": f"Response from {model} (LiteLLM not installed)"}}
                ],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20},
            }
        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                api_key=api_key,
            )
            return response
        except Exception as e:
            return {"error": str(e)}

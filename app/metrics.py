from __future__ import annotations


# Approximate placeholder pricing in USD per 1M tokens.
# Update these constants as provider pricing changes.
OPENAI_PRICING_USD_PER_1M_TOKENS = {
    "gpt-4.1-mini": {
        "input": 0.40,
        "output": 1.60,
    },
    "gpt-4.1": {
        "input": 2.00,
        "output": 8.00,
    },
}


# Approximate context windows for models exposed in the Streamlit selector.
MODEL_CONTEXT_WINDOWS = {
    "gpt-4.1-mini": 1_000_000,
    "gpt-4.1": 1_000_000,
}


def estimate_tokens(text: str) -> int:
    if not text:
        return 0

    return max(1, len(text) // 4)


def estimate_openai_cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float | None:
    pricing = OPENAI_PRICING_USD_PER_1M_TOKENS.get(model)
    if pricing is None:
        return None

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def estimate_context_pressure(
    total_tokens: int,
    model_name: str,
) -> float | None:
    context_window = MODEL_CONTEXT_WINDOWS.get(model_name)
    if context_window is None or context_window <= 0:
        return None

    safe_total_tokens = max(0, total_tokens)
    return (safe_total_tokens / context_window) * 100

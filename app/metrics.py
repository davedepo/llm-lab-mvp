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
    "gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60,
    },
    "gpt-4o": {
        "input": 2.50,
        "output": 10.00,
    },
    "o4-mini": {
        "input": 1.10,
        "output": 4.40,
    },
}

ANTHROPIC_PRICING_USD_PER_1M_TOKENS = {
    "claude-sonnet-4-6": {
        "input": 3.00,
        "output": 15.00,
    },
    "claude-3-5-sonnet-latest": {
        "input": 3.00,
        "output": 15.00,
    },
    "claude-3-5-haiku-latest": {
        "input": 0.80,
        "output": 4.00,
    },
}


# Approximate context windows for models exposed in the Streamlit selector.
MODEL_CONTEXT_WINDOWS = {
    "gpt-4.1-mini": 1_000_000,
    "gpt-4.1": 1_000_000,
    "gpt-4o-mini": 128_000,
    "gpt-4o": 128_000,
    "o4-mini": 200_000,
    "claude-sonnet-4-6": 200_000,
    "claude-3-5-sonnet-latest": 200_000,
    "claude-3-5-haiku-latest": 200_000,
}


def estimate_tokens(text: str) -> int:
    if not text:
        return 0

    # Heuristic: 1 token ≈ 4 characters; ensure a minimum of 1 token for non-empty text
    return max(1, len(text) // 4)


def estimate_openai_cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """
    Estimates the cost of an OpenAI API call in USD.

    Args:
        model (str): The specific model ID used.
        input_tokens (int): The number of prompt tokens.
        output_tokens (int): The number of generated tokens.

    Returns:
        float: The total estimated cost in USD.
    """
    # Look up exact model pricing, otherwise use gpt-4o-mini as a safe baseline
    pricing = OPENAI_PRICING_USD_PER_1M_TOKENS.get(model)
    if pricing is None:
        pricing = {"input": 0.15, "output": 0.60}  # Fallback to gpt-4o-mini rates

    # Prorate the cost by dividing tokens by 1 million
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def estimate_anthropic_cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    """
    Estimates the cost of an Anthropic API call in USD.

    Args:
        model (str): The specific model ID used.
        input_tokens (int): The number of prompt tokens.
        output_tokens (int): The number of generated tokens.

    Returns:
        float: The total estimated cost in USD.
    """
    # Look up exact model pricing, otherwise use claude-3-5-sonnet-latest as a safe baseline
    pricing = ANTHROPIC_PRICING_USD_PER_1M_TOKENS.get(model)
    if pricing is None:
        pricing = {"input": 3.00, "output": 15.00}  # Fallback to claude-3-5-sonnet-latest rates

    # Prorate the cost by dividing tokens by 1 million
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def estimate_context_pressure(
    total_tokens: int,
    model_name: str,
) -> float:
    """
    Calculates the percentage of the model's maximum context window utilized by the prompt.

    Args:
        total_tokens (int): The combined input and output tokens.
        model_name (str): The specific model ID to look up limits for.

    Returns:
        float: A percentage representing context utilization.
    """
    # Look up the context window for the model, defaulting to 128k if unavailable
    context_window = MODEL_CONTEXT_WINDOWS.get(model_name)
    if context_window is None or context_window <= 0:
        context_window = 128_000  # Safe fallback window size

    # Prevent negative token calculations before calculating the percentage
    safe_total_tokens = max(0, total_tokens)
    return (safe_total_tokens / context_window) * 100

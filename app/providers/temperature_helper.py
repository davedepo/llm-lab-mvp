"""
temperature_helper.py

Provides utility functions for handling provider-specific temperature constraints
and UI guidance. Ensures temperature parameters stay within valid ranges.
"""


def get_max_temperature(provider: str) -> float:
    """
    Returns the maximum allowed temperature based on the provider.

    Args:
        provider (str): The name of the LLM provider.

    Returns:
        float: The maximum valid temperature for the specified provider.
    """
    # Anthropic restricts temperature to a maximum of 1.0
    if provider == "Anthropic":
        return 1.0

    # Most other providers (like OpenAI) allow up to 2.0
    return 2.0


def get_temperature_guidance(provider: str) -> str:
    """
    Returns provider-aware guidance for temperature selection.

    Args:
        provider (str): The name of the LLM provider.

    Returns:
        str: A descriptive string guiding the user on temperature limits.
    """
    # Standard explanation for what temperature does
    base_guidance = "Lower = more focused and repeatable. Higher = more creative and varied."

    # Append provider-specific bounds
    if provider == "Anthropic":
        return f"{base_guidance} (Max 1.0 for Anthropic)"
    return f"{base_guidance} (Max 2.0)"
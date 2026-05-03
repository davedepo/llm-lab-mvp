def get_max_temperature(provider: str) -> float:
    """Returns the maximum allowed temperature based on the provider."""
    if provider == "Anthropic":
        return 1.0
    return 2.0

def get_temperature_guidance(provider: str) -> str:
    """Returns provider-aware guidance for temperature selection."""
    base_guidance = "Lower = more focused and repeatable. Higher = more creative and varied."
    if provider == "Anthropic":
        return f"{base_guidance} (Max 1.0 for Anthropic)"
    return f"{base_guidance} (Max 2.0)"
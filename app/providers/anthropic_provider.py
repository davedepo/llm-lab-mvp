"""
anthropic_provider.py

Provides the integration with the Anthropic API. Handles request formatting,
execution, text extraction, and metric estimations for Claude models, returning
a standardized ProviderExperimentResult.
"""
import os
from time import perf_counter

from metrics import (
    estimate_anthropic_cost_usd,
    estimate_context_pressure,
    estimate_tokens,
)
from providers.base import ProviderExperimentResult


def extract_anthropic_text(response) -> str:
    """
    Extracts the combined text content from an Anthropic message response.

    Args:
        response: The response object returned by the Anthropic client.

    Returns:
        str: The extracted text output.
    """
    text_parts = []
    for block in getattr(response, "content", []) or []:
        block_text = getattr(block, "text", None)
        if block_text:
            text_parts.append(block_text)
    return "\n".join(text_parts).strip()


def run_anthropic_experiment(
    prompt: str,
    model: str,
    temperature: float,
    max_output_tokens: int,
    api_key: str | None = None,
    system_instruction: str | None = None,
) -> ProviderExperimentResult:
    """
    Executes an experiment using the Anthropic API.

    Args:
        prompt (str): The user prompt to evaluate.
        model (str): The Claude model ID.
        temperature (float): The generation temperature.
        max_output_tokens (int): The upper limit on generated tokens.
        api_key (str | None): Optional API key; falls back to the environment variable.
        system_instruction (str | None): Optional system instructions.

    Returns:
        ProviderExperimentResult: The standardized execution metrics and output.
    """
    # Resolve API key from parameter or environment
    resolved_api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not resolved_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is missing. Enter an Anthropic API key for this run "
            "or add it to your .env file."
        )

    # Ensure the Anthropic SDK is installed before attempting to use it
    try:
        import anthropic
    except ImportError as error:
        raise RuntimeError(
            "The anthropic package is not installed. Run pip install -r requirements.txt."
        ) from error

    # Initialize client and build the request payload
    client = anthropic.Anthropic(api_key=resolved_api_key)
    request_args = {
        "model": model,
        "max_tokens": max_output_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system_instruction and system_instruction.strip():
        request_args["system"] = system_instruction.strip()

    # Execute the API call and measure latency
    try:
        start_time = perf_counter()
        response = client.messages.create(**request_args)
        latency_seconds = perf_counter() - start_time
    except Exception as e:
        raise RuntimeError(f"Anthropic API call failed: {e}") from e

    # Parse the response payload for the generated text
    output_text = extract_anthropic_text(response)
    if not output_text:
        raise RuntimeError("Anthropic returned a response without output text.")

    try:
        # Estimate tokens using the heuristic text length approach
        input_text = "\n".join(
            value for value in [system_instruction, prompt] if value and value.strip()
        )
        approximate_input_tokens = estimate_tokens(input_text)
        approximate_output_tokens = estimate_tokens(output_text)
        approximate_total_tokens = approximate_input_tokens + approximate_output_tokens
    except Exception:
        approximate_input_tokens = 0
        approximate_output_tokens = 0
        approximate_total_tokens = 0

    try:
        # Calculate how much of the context window was utilized
        approximate_context_pressure_percent = estimate_context_pressure(
            total_tokens=approximate_total_tokens,
            model_name=model,
        )
    except Exception:
        approximate_context_pressure_percent = None

    try:
        # Calculate the estimated cost using static provider pricing
        approximate_cost_usd = estimate_anthropic_cost_usd(
            model=model,
            input_tokens=approximate_input_tokens,
            output_tokens=approximate_output_tokens,
        )
    except Exception:
        approximate_cost_usd = None

    return ProviderExperimentResult(
        output_text=output_text,
        latency_seconds=latency_seconds,
        approximate_input_tokens=approximate_input_tokens,
        approximate_output_tokens=approximate_output_tokens,
        approximate_total_tokens=approximate_total_tokens,
        approximate_context_pressure_percent=approximate_context_pressure_percent,
        approximate_cost_usd=approximate_cost_usd,
    )

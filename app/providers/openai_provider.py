import os
from dataclasses import dataclass
from time import perf_counter

from openai import OpenAI

from metrics import (
    estimate_context_pressure,
    estimate_openai_cost_usd,
    estimate_tokens,
)


@dataclass(frozen=True)
class OpenAIExperimentResult:
    output_text: str
    latency_seconds: float
    approximate_input_tokens: int
    approximate_output_tokens: int
    approximate_total_tokens: int
    approximate_context_pressure_percent: float | None
    approximate_cost_usd: float | None


def run_openai_experiment(
    prompt: str,
    model: str,
    temperature: float,
    max_output_tokens: int,
    api_key: str | None = None,
) -> OpenAIExperimentResult:
    resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not resolved_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Enter an OpenAI API key for this run "
            "or add it to your .env file."
        )

    client = OpenAI(api_key=resolved_api_key)
    start_time = perf_counter()
    response = client.responses.create(
        model=model,
        input=prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )
    latency_seconds = perf_counter() - start_time

    output_text = getattr(response, "output_text", None)
    if not output_text:
        raise RuntimeError("OpenAI returned a response without output text.")

    approximate_input_tokens = estimate_tokens(prompt)
    approximate_output_tokens = estimate_tokens(output_text)
    approximate_total_tokens = approximate_input_tokens + approximate_output_tokens
    approximate_context_pressure_percent = estimate_context_pressure(
        total_tokens=approximate_total_tokens,
        model_name=model,
    )
    approximate_cost_usd = estimate_openai_cost_usd(
        model=model,
        input_tokens=approximate_input_tokens,
        output_tokens=approximate_output_tokens,
    )

    return OpenAIExperimentResult(
        output_text=output_text,
        latency_seconds=latency_seconds,
        approximate_input_tokens=approximate_input_tokens,
        approximate_output_tokens=approximate_output_tokens,
        approximate_total_tokens=approximate_total_tokens,
        approximate_context_pressure_percent=approximate_context_pressure_percent,
        approximate_cost_usd=approximate_cost_usd,
    )

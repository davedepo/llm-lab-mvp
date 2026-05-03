from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderExperimentResult:
    output_text: str
    latency_seconds: float
    approximate_input_tokens: int
    approximate_output_tokens: int
    approximate_total_tokens: int
    approximate_context_pressure_percent: float | None
    approximate_cost_usd: float | None

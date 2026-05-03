from datetime import datetime, timezone

from dotenv import load_dotenv
import streamlit as st

from providers.anthropic_provider import run_anthropic_experiment
from providers.openai_provider import run_openai_experiment
from providers.temperature_helper import get_max_temperature, get_temperature_guidance


PROVIDERS = ["OpenAI", "Anthropic", "Google Gemini", "Mistral", "Cohere"]
LIVE_PROVIDERS = {"OpenAI", "Anthropic"}
CUSTOM_MODEL_OPTION = "Other"

MODEL_PRESETS = {
    "OpenAI": [
        "gpt-4.1-mini",
        "gpt-4.1",
        "gpt-4o-mini",
        "gpt-4o",
        "o4-mini",
    ],
    "Anthropic": [
        "claude-sonnet-4-6",
        "claude-3-5-sonnet-latest",
        "claude-3-5-haiku-latest",
    ],
    "Google Gemini": [
        "gemini-3.1-pro-preview",
        "gemini-3.1-flash-preview",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.0-flash",
    ],
    "Mistral": [
        "mistral-large-latest",
        "mistral-medium-latest",
        "mistral-small-latest",
        "codestral-latest",
        "ministral-8b-latest",
    ],
    "Cohere": [
        "command-a-03-2025",
        "command-r-plus",
        "command-r",
        "command-light",
        "command",
    ],
}


load_dotenv()

st.set_page_config(page_title="LLM Lab MVP", layout="wide")

st.markdown(
    """
    <style>
    /* Enterprise Blue Theme UI Components */
    :root { --primary-color: #0066cc; }
    .stButton > button[kind="primary"] {
        background-color: #0066cc !important;
        color: white !important;
        border-color: #0066cc !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #0052a3 !important;
        border-color: #0052a3 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

DEFAULT_SYSTEM_INSTRUCTION = (
    "Return a concise, structured answer with decision-ready bullets."
)

COMPARISON_PRESETS = {
    "Custom Configuration": {
        "description": "Start with empty prompts and cross-provider defaults.",
        "a": {
            "provider": "OpenAI",
            "preset_model": "gpt-4o-mini",
            "custom_model": "",
            "system_instruction": "",
            "prompt": "",
            "temperature": 0.7,
            "max_output_tokens": 1024,
        },
        "b": {
            "provider": "Anthropic",
            "preset_model": "claude-3-5-haiku-latest",
            "custom_model": "",
            "system_instruction": "",
            "prompt": "",
            "temperature": 0.7,
            "max_output_tokens": 1024,
        },
    },
    "Same Prompt, Different Models": {
        "description": "Compare OpenAI and Anthropic models on the same task and instruction.",
        "a": {
            "provider": "OpenAI",
            "preset_model": "gpt-4o",
            "custom_model": "",
            "system_instruction": DEFAULT_SYSTEM_INSTRUCTION,
            "prompt": "Summarize the tradeoffs of building an internal LLM evaluation tool.",
            "temperature": 0.7,
            "max_output_tokens": 1024,
        },
        "b": {
            "provider": "Anthropic",
            "preset_model": "claude-3-5-sonnet-latest",
            "custom_model": "",
            "system_instruction": DEFAULT_SYSTEM_INSTRUCTION,
            "prompt": "Summarize the tradeoffs of building an internal LLM evaluation tool.",
            "temperature": 0.7,
            "max_output_tokens": 1024,
        },
    },
    "Same Model, Different System Instructions": {
        "description": "Keep the model and prompt fixed while changing only the instruction.",
        "a": {
            "provider": "OpenAI",
            "preset_model": "gpt-4o-mini",
            "custom_model": "",
            "system_instruction": "Return a concise executive summary with decision-ready bullets.",
            "prompt": "Evaluate whether a team should adopt an LLM experimentation workflow.",
            "temperature": 0.7,
            "max_output_tokens": 1024,
        },
        "b": {
            "provider": "OpenAI",
            "preset_model": "gpt-4o-mini",
            "custom_model": "",
            "system_instruction": "Return a detailed technical analysis with risks, mitigations, and implementation notes.",
            "prompt": "Evaluate whether a team should adopt an LLM experimentation workflow.",
            "temperature": 0.7,
            "max_output_tokens": 1024,
        },
    },
    "Concise vs Detailed Answer": {
        "description": "Compare a short answer style against a more expansive answer style.",
        "a": {
            "provider": "Anthropic",
            "preset_model": "claude-3-5-sonnet-latest",
            "custom_model": "",
            "system_instruction": "Answer in no more than five concise bullets.",
            "prompt": "Explain how to evaluate two LLM responses for a product decision.",
            "temperature": 0.5,
            "max_output_tokens": 768,
        },
        "b": {
            "provider": "Anthropic",
            "preset_model": "claude-3-5-sonnet-latest",
            "custom_model": "",
            "system_instruction": "Answer with detailed reasoning, examples, and implementation guidance.",
            "prompt": "Explain how to evaluate two LLM responses for a product decision.",
            "temperature": 0.5,
            "max_output_tokens": 1536,
        },
    },
    "Creative vs Analytical Answer": {
        "description": "Compare a more imaginative response style against a structured analytical style.",
        "a": {
            "provider": "Anthropic",
            "preset_model": "claude-3-5-haiku-latest",
            "custom_model": "",
            "system_instruction": "Generate creative, unconventional options while staying practical.",
            "prompt": "Propose ways to make an LLM experimentation tool more useful for product teams.",
            "temperature": 1.0,
            "max_output_tokens": 1024,
        },
        "b": {
            "provider": "OpenAI",
            "preset_model": "gpt-4o-mini",
            "custom_model": "",
            "system_instruction": "Analyze the problem systematically with criteria, tradeoffs, and risks.",
            "prompt": "Propose ways to make an LLM experimentation tool more useful for product teams.",
            "temperature": 0.3,
            "max_output_tokens": 1024,
        },
    },
}

EXPERIMENT_KEY_MAP = {
    "provider": "provider",
    "preset_model": "preset_model",
    "custom_model": "custom_model",
    "system_instruction": "system_instruction",
    "prompt": "prompt",
    "temperature": "temperature",
    "max_output_tokens": "max_output_tokens",
}

NEGLIGIBLE_COST_DIFF_USD = 0.0001
MATERIAL_RATIO_DIFF = 0.2


def format_cost(value: float | None) -> str:
    return f"${value:.6f}" if value is not None else "Metrics Unavailable for this Run: Pricing Data Not Found or API Error"


def format_context_pressure(value: float | None) -> str:
    return f"{value:.2f}%" if value is not None else "Metrics Unavailable for this Run: Context Window Data Not Found or API Error"


def model_options(provider: str) -> list[str]:
    return MODEL_PRESETS[provider] + [CUSTOM_MODEL_OPTION]


def display_model(model: str) -> str:
    return model or "Custom Model Required"


def status_label(experiment: dict, result, status_message: str) -> str:
    if experiment["provider"] not in LIVE_PROVIDERS:
        return "Unsupported Provider Placeholder"
    if result is not None:
        return "Completed"
    return status_message


def candidate_metrics_rows(label: str, experiment: dict, result, status_message: str):
    if result is None:
        return [
            {
                "Candidate": label,
                "Provider": experiment["provider"],
                "Model": display_model(experiment["model"]),
                "Run Status": status_label(experiment, result, status_message),
                "Response Time": "Unavailable",
                "Est. Input Tokens": "Unavailable",
                "Est. Output Tokens": "Unavailable",
                "Est. Total Tokens": "Unavailable",
                "Output Length": "Unavailable",
                "Est. Cost": "Unavailable",
                "Approx. Context Pressure": "Unavailable",
            }
        ]

    return [
        {
            "Candidate": label,
            "Provider": experiment["provider"],
            "Model": display_model(experiment["model"]),
            "Run Status": status_label(experiment, result, status_message),
            "Response Time": f"{result.latency_seconds:.2f}s",
            "Est. Input Tokens": str(result.approximate_input_tokens),
            "Est. Output Tokens": str(result.approximate_output_tokens),
            "Est. Total Tokens": str(result.approximate_total_tokens),
            "Output Length": f"{len(result.output_text)} chars",
            "Est. Cost": format_cost(result.approximate_cost_usd),
            "Approx. Context Pressure": format_context_pressure(
                result.approximate_context_pressure_percent
            ),
        }
    ]


def render_output_card(label: str, experiment: dict, result, status_message: str) -> None:
    with st.container(border=True):
        st.markdown(
            f"**{label}: {experiment['provider']} / "
            f"`{display_model(experiment['model'])}`**"
        )
        st.caption(f"Run Status: {status_label(experiment, result, status_message)}")

        if experiment["provider"] not in LIVE_PROVIDERS:
            st.info(
                f"{experiment['provider']} is a placeholder provider and is not "
                "implemented yet."
            )
        elif result is None:
            st.warning(status_message)
        else:
            st.write(result.output_text)


def render_model_outputs(
    experiment_a: dict,
    experiment_b: dict,
    result_a,
    result_b,
    status_a: str,
    status_b: str,
) -> None:
    st.subheader("Model Output")
    output_cols = st.columns(2)
    with output_cols[0]:
        render_output_card("Candidate A", experiment_a, result_a, status_a)
    with output_cols[1]:
        render_output_card("Candidate B", experiment_b, result_b, status_b)


def render_approximate_metrics(
    experiment_a: dict,
    experiment_b: dict,
    result_a,
    result_b,
    status_a: str,
    status_b: str,
) -> None:
    st.subheader("Approximate Metrics")
    st.caption(
        "Definitions: Response Time = elapsed provider call time | "
        "Token Usage = heuristic character estimate | "
        "Est. Cost = static placeholder estimation | "
        "Context Pressure = % of configured window | "
        "Output Length = generated text length"
    )

    metrics_cols = st.columns(2)

    rows_a = candidate_metrics_rows("Candidate A", experiment_a, result_a, status_a)[0]
    with metrics_cols[0]:
        with st.container(border=True):
            st.markdown(f"**{rows_a['Candidate']} / {rows_a['Provider']} / `{rows_a['Model']}`**")
            st.markdown(f"*Status: {rows_a['Run Status']}*")
            for key, value in rows_a.items():
                if key not in ["Candidate", "Provider", "Model", "Run Status"]:
                    st.markdown(f"**{key}:** {value}")

    rows_b = candidate_metrics_rows("Candidate B", experiment_b, result_b, status_b)[0]
    with metrics_cols[1]:
        with st.container(border=True):
            st.markdown(f"**{rows_b['Candidate']} / {rows_b['Provider']} / `{rows_b['Model']}`**")
            st.markdown(f"*Status: {rows_b['Run Status']}*")
            for key, value in rows_b.items():
                if key not in ["Candidate", "Provider", "Model", "Run Status"]:
                    st.markdown(f"**{key}:** {value}")


def ratio_difference(value_a: float | int | None, value_b: float | int | None):
    if value_a is None or value_b is None:
        return None

    baseline = max(abs(value_a), abs(value_b), 1)
    return abs(value_a - value_b) / baseline


def lower_candidate(value_a: float | None, value_b: float | None):
    if value_a is None or value_b is None or value_a == value_b:
        return None
    return "Candidate A" if value_a < value_b else "Candidate B"


def higher_candidate(value_a: float | int | None, value_b: float | int | None):
    if value_a is None or value_b is None or value_a == value_b:
        return None
    return "Candidate A" if value_a > value_b else "Candidate B"


def comparison_type_statement(experiment_a: dict, experiment_b: dict) -> str:
    provider_differs = experiment_a["provider"] != experiment_b["provider"]
    model_differs = experiment_a["model"] != experiment_b["model"]
    system_differs = (
        experiment_a["system_instruction"].strip()
        != experiment_b["system_instruction"].strip()
    )
    prompt_differs = experiment_a["prompt"].strip() != experiment_b["prompt"].strip()
    parameter_differs = (
        experiment_a["temperature"] != experiment_b["temperature"]
        or experiment_a["max_output_tokens"] != experiment_b["max_output_tokens"]
    )

    if provider_differs:
        if (
            experiment_a["provider"] not in LIVE_PROVIDERS
            or experiment_b["provider"] not in LIVE_PROVIDERS
        ):
            return "Different providers; only OpenAI and Anthropic are currently live."
        return "Different providers."
    if model_differs:
        return "Same provider, different models."
    if prompt_differs and not system_differs:
        return "Same model, different prompts."
    if system_differs and not prompt_differs:
        return "Same model, different system instructions."
    if parameter_differs:
        return "Same model, different generation parameters."
    return "Same setup."


def setup_change_count(experiment_a: dict, experiment_b: dict) -> int:
    changed = 0
    changed += experiment_a["provider"] != experiment_b["provider"]
    changed += experiment_a["model"] != experiment_b["model"]
    changed += (
        experiment_a["system_instruction"].strip()
        != experiment_b["system_instruction"].strip()
    )
    changed += experiment_a["prompt"].strip() != experiment_b["prompt"].strip()
    changed += experiment_a["temperature"] != experiment_b["temperature"]
    changed += experiment_a["max_output_tokens"] != experiment_b["max_output_tokens"]
    return changed


def build_decision_intelligence(
    experiment_a: dict,
    experiment_b: dict,
    result_a,
    result_b,
) -> list[str]:
    insights = []
    unsupported = unsupported_providers(experiment_a, experiment_b)

    if unsupported:
        insights.append(
            "Decision intelligence is incomplete because "
            + ", ".join(unsupported)
            + " uses an unsupported provider placeholder."
        )

    if not experiment_a["prompt"].strip() or not experiment_b["prompt"].strip():
        insights.append(
            "Decision intelligence is incomplete because one or both user prompts are missing."
        )

    if result_a is None and result_b is None:
        insights.append(
            "No live comparison result is available yet, so guidance is limited to setup review."
        )
    elif result_a is None:
        insights.append(
            "Only Candidate B produced a live result. Decision intelligence is partial."
        )
    elif result_b is None:
        insights.append(
            "Only Candidate A produced a live result. Decision intelligence is partial."
        )

    if result_a is not None and result_b is not None:
        cheaper = lower_candidate(
            result_a.approximate_cost_usd,
            result_b.approximate_cost_usd,
        )
        cost_ratio = ratio_difference(
            result_a.approximate_cost_usd,
            result_b.approximate_cost_usd,
        )
        if cheaper and cost_ratio is not None:
            cost_delta = abs(result_a.approximate_cost_usd - result_b.approximate_cost_usd)
            if cost_delta <= NEGLIGIBLE_COST_DIFF_USD:
                insights.append("**Cost Efficiency**: The estimated cost difference is negligible. Selection should primarily depend on output quality and structural fit.")
            else:
                insights.append(f"**Cost Efficiency**: {cheaper} appears more cost-efficient based on the estimated token rates.")

        token_heavier = higher_candidate(
            result_a.approximate_total_tokens,
            result_b.approximate_total_tokens,
        )
        token_ratio = ratio_difference(
            result_a.approximate_total_tokens,
            result_b.approximate_total_tokens,
        )
        if token_heavier and token_ratio is not None:
            if token_ratio >= MATERIAL_RATIO_DIFF:
                insights.append(f"**Token Utilization**: {token_heavier} is more token-heavy, which may matter for cost-sensitive or high-volume use.")
            else:
                insights.append("**Token Utilization**: Both candidates have similar estimated total token usage.")

        longer_output = higher_candidate(
            result_a.approximate_output_tokens,
            result_b.approximate_output_tokens,
        )
        output_ratio = ratio_difference(
            result_a.approximate_output_tokens,
            result_b.approximate_output_tokens,
        )
        if longer_output and output_ratio is not None:
            if output_ratio >= MATERIAL_RATIO_DIFF:
                shorter_output = "Candidate A" if longer_output == "Candidate B" else "Candidate B"
                insights.append(f"**Structural Difference**: {longer_output} produced a longer, more detailed response, while {shorter_output} was more concise.")
                insights.append(f"**Recommendation**: Use {shorter_output} for **Production/Extraction** workflows where brevity and predictable parsing are required. Use {longer_output} for **Brainstorming/Exploration** workflows where depth and creative variation provide more value.")
            else:
                insights.append("**Structural Difference**: Both candidates produced similarly sized responses with comparable structural depth.")

        higher_context = higher_candidate(
            result_a.approximate_context_pressure_percent,
            result_b.approximate_context_pressure_percent,
        )
        context_ratio = ratio_difference(
            result_a.approximate_context_pressure_percent,
            result_b.approximate_context_pressure_percent,
        )
        if higher_context and context_ratio is not None:
            if context_ratio >= MATERIAL_RATIO_DIFF:
                insights.append(f"**Context Pressure**: {higher_context} has higher context pressure, which may matter for long prompts or multi-turn workflows.")
            else:
                insights.append("**Context Pressure**: Both candidates have similar estimated context pressure.")

    if setup_change_count(experiment_a, experiment_b) > 1:
        insights.append("**Test Design Note**: This comparison changes multiple setup variables simultaneously, so differences in output cannot be attributed to a single parameter alone.")

    return insights


def render_decision_intelligence(insights: list[str]) -> None:
    st.subheader("Decision Intelligence")
    with st.container(border=True):
        st.caption(
            "Deterministic estimation based on available outputs and approximate metrics; "
            "not an exact LLM judge."
        )
        for insight in insights:
            st.markdown(insight)


def render_run_summary(summary: list[str]) -> None:
    st.subheader("Run Summary")
    with st.container(border=True):
        for item in summary:
            st.markdown(f"- {item}")


def resolve_model(preset_model: str, custom_model: str) -> str:
    if custom_model.strip():
        return custom_model.strip()
    if preset_model == CUSTOM_MODEL_OPTION:
        return ""
    return preset_model


def provided_label(value: str) -> str:
    return "Provided" if value.strip() else "Not Provided"


def same_or_different(value_a, value_b) -> str:
    return "Same" if value_a == value_b else "Different"


def apply_preset_to_session_state(preset_name: str) -> None:
    preset = COMPARISON_PRESETS[preset_name]
    for side, key_prefix in [("a", "experiment_a"), ("b", "experiment_b")]:
        for preset_key, widget_key in EXPERIMENT_KEY_MAP.items():
            st.session_state[f"{key_prefix}_{widget_key}"] = preset[side][preset_key]


def initialize_experiment_defaults(key_prefix: str, default_model_index: int) -> None:
    st.session_state.setdefault(f"{key_prefix}_provider", "OpenAI")
    st.session_state.setdefault(
        f"{key_prefix}_preset_model",
        MODEL_PRESETS["OpenAI"][default_model_index],
    )
    st.session_state.setdefault(f"{key_prefix}_custom_model", "")
    st.session_state.setdefault(
        f"{key_prefix}_system_instruction",
        DEFAULT_SYSTEM_INSTRUCTION,
    )
    st.session_state.setdefault(f"{key_prefix}_prompt", "")
    st.session_state.setdefault(f"{key_prefix}_temperature", 0.7)
    st.session_state.setdefault(f"{key_prefix}_max_output_tokens", 1024)


def markdown_block(value: str) -> str:
    return f"```\n{value.strip() if value else ''}\n```"


def experiment_config_markdown(label: str, experiment: dict) -> str:
    return "\n".join(
        [
            f"### {label} Configuration",
            "",
            f"- Provider: {experiment['provider']}",
            f"- Model: {display_model(experiment['model'])}",
            f"- Preset Model Selection: {experiment['preset_model']}",
            f"- Temperature: {experiment['temperature']:.1f}",
            f"- Max Output Tokens: {experiment['max_output_tokens']}",
            f"- System Instruction: {provided_label(experiment['system_instruction'])}",
            f"- User Prompt: {provided_label(experiment['prompt'])}",
            "",
            "System Instruction:",
            markdown_block(experiment["system_instruction"]),
            "",
            "User Prompt:",
            markdown_block(experiment["prompt"]),
        ]
    )


def result_markdown(label: str, experiment: dict, result, status_message: str) -> str:
    lines = [
        f"### {label} Output",
        "",
        f"- Status: {status_label(experiment, result, status_message)}",
        f"- Provider: {experiment['provider']}",
        f"- Model: {display_model(experiment['model'])}",
    ]

    lines.extend(["", "Output:", markdown_block(result.output_text if result else "")])
    return "\n".join(lines)


def comparison_summary_markdown(experiment_a: dict, experiment_b: dict) -> str:
    lines = [
        "## Comparison Setup Summary",
        "",
        f"Comparison type: {comparison_type_statement(experiment_a, experiment_b)}",
        "",
        "| Field | Status | Configuration A | Configuration B |",
        "| --- | --- | --- | --- |",
    ]
    for row in comparison_setup_rows(experiment_a, experiment_b):
        lines.append(
            f"| {row['Field']} | {row['Status']} | "
            f"{row['Configuration A']} | {row['Configuration B']} |"
        )
    return "\n".join(lines)


def approximate_metrics_markdown(
    experiment_a: dict,
    experiment_b: dict,
    result_a,
    result_b,
    status_a: str,
    status_b: str,
) -> str:
    lines = [
        "## Approximate Metrics",
        "",
        "Token, cost, and context pressure values are approximate local estimates. "
        "Response time is elapsed provider call time; output length is generated "
        "text length. Unavailable means metadata is not configured for that model "
        "or the run did not complete.",
        "",
        "| Candidate | Provider | Model | Run Status | Est. Input Tokens | "
        "Est. Output Tokens | Est. Total Tokens | Output Length | "
        "Response Time | Est. Cost | "
        "Approx. Context Pressure |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in candidate_metrics_rows(
        "Candidate A", experiment_a, result_a, status_a
    ) + candidate_metrics_rows("Candidate B", experiment_b, result_b, status_b):
        lines.append(
            f"| {row['Candidate']} | {row['Provider']} | {row['Model']} | "
            f"{row['Run Status']} | {row['Est. Input Tokens']} | "
            f"{row['Est. Output Tokens']} | {row['Est. Total Tokens']} | "
            f"{row['Output Length']} | {row['Response Time']} | "
            f"{row['Est. Cost']} | {row['Approx. Context Pressure']} |"
        )
    return "\n".join(lines)


def decision_intelligence_markdown(insights: list[str]) -> str:
    lines = [
        "## Decision Intelligence",
        "",
        "Deterministic helper based on available outputs and approximate metrics; "
        "not an LLM judge.",
        "",
    ]
    lines.extend(f"{insight}" for insight in insights)
    return "\n".join(lines)


def build_run_summary(
    experiment_a: dict,
    experiment_b: dict,
    result_a,
    result_b,
    status_a: str,
    status_b: str,
) -> list[str]:
    unsupported = unsupported_providers(experiment_a, experiment_b)
    summary = [
        f"Candidate A: {status_label(experiment_a, result_a, status_a)}",
        f"Candidate B: {status_label(experiment_b, result_b, status_b)}",
        "OpenAI and Anthropic are currently live execution providers.",
        "Token, Cost, and Context Pressure values are approximate.",
    ]

    if unsupported:
        summary.append(
            "Unsupported provider placeholders selected for: "
            + ", ".join(unsupported)
            + "."
        )
    if not experiment_a["prompt"].strip() or not experiment_b["prompt"].strip():
        summary.append("One or both user prompts are missing.")
    return summary


def run_summary_markdown(summary: list[str]) -> str:
    return "\n".join(["## Run Summary", ""] + [f"- {item}" for item in summary])


def build_markdown_report(
    experiment_a: dict,
    experiment_b: dict,
    result_a=None,
    result_b=None,
    status_a: str = "Not run",
    status_b: str = "Not run",
    preset_name: str | None = None,
    insights: list[str] | None = None,
    run_summary: list[str] | None = None,
) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    insights = insights or build_decision_intelligence(
        experiment_a, experiment_b, result_a, result_b
    )
    run_summary = run_summary or build_run_summary(
        experiment_a, experiment_b, result_a, result_b, status_a, status_b
    )
    return "\n\n".join(
        [
            "# LLM Lab MVP Comparison Report",
            f"Generated: {timestamp}",
            "OpenAI and Anthropic are currently live execution providers. Other "
            "providers are placeholders.",
            "## Comparison Preset Used",
            preset_name or "No preset applied in this session.",
            "## User Input / Candidate Configuration",
            experiment_config_markdown("Candidate A", experiment_a),
            experiment_config_markdown("Candidate B", experiment_b),
            comparison_summary_markdown(experiment_a, experiment_b),
            "## Model Outputs",
            result_markdown("Candidate A", experiment_a, result_a, status_a),
            result_markdown("Candidate B", experiment_b, result_b, status_b),
            approximate_metrics_markdown(
                experiment_a,
                experiment_b,
                result_a,
                result_b,
                status_a,
                status_b,
            ),
            decision_intelligence_markdown(insights),
            run_summary_markdown(run_summary),
            "Note: Token, Cost, Context Pressure, Response Time, and Output Length "
            "values are approximate or locally measured for this run.",
        ]
    )


def build_experiment_panel(label: str, key_prefix: str, default_model_index: int) -> dict:
    with st.container(border=True):
        st.subheader(label)
        provider = st.selectbox("Provider", PROVIDERS, key=f"{key_prefix}_provider")

        api_key = st.text_input(
            "API Key",
            type="password",
            placeholder=f"Enter {provider} API Key here...",
            key=f"{key_prefix}_api_key",
        )
        st.caption("Your API Key is used only for this run and is not stored by this app.")

        preset_model_key = f"{key_prefix}_preset_model"
        custom_model_key = f"{key_prefix}_custom_model"
        provider_model_options = model_options(provider)
        if st.session_state.get(custom_model_key, "").strip():
            st.session_state[preset_model_key] = CUSTOM_MODEL_OPTION
        if st.session_state.get(preset_model_key) not in provider_model_options:
            st.session_state[preset_model_key] = MODEL_PRESETS[provider][
                min(default_model_index, len(MODEL_PRESETS[provider]) - 1)
            ]

        preset_model = st.selectbox(
            "Preset Model",
            provider_model_options,
            key=preset_model_key,
        )
        custom_model = st.text_input(
            "Custom Model",
            placeholder="e.g., your-custom-model-id",
            key=custom_model_key,
        )
        st.caption(
            "Custom model IDs must match the selected provider’s official model name. "
            "Invalid, unavailable, or deprecated models may fail at runtime."
        )

        model = resolve_model(preset_model, custom_model)
        st.caption(f"Selected Model: `{display_model(model)}`")

        system_instruction = st.text_area(
            "System Instruction",
            placeholder="Enter optional system instructions...",
            height=120,
            key=f"{key_prefix}_system_instruction",
        )
        prompt = st.text_area(
            "User Prompt",
            placeholder="Enter the prompt you want to test outputs with...",
            height=190,
            key=f"{key_prefix}_prompt",
        )

        param_cols = st.columns(2)
        with param_cols[0]:
            temperature_key = f"{key_prefix}_temperature"
            max_temperature = get_max_temperature(provider)
            if st.session_state[temperature_key] > max_temperature:
                st.session_state[temperature_key] = max_temperature
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=max_temperature,
                step=0.1,
                key=temperature_key,
            )
            st.caption(get_temperature_guidance(provider))
        with param_cols[1]:
            max_output_tokens = st.slider(
                "Max Output Tokens",
                min_value=128,
                max_value=4096,
                step=128,
                key=f"{key_prefix}_max_output_tokens",
            )
            st.caption(
                "Upper bound on generated response length; actual output may be shorter."
            )

    return {
        "label": label,
        "provider": provider,
        "api_key": api_key.strip() or None,
        "model": model,
        "preset_model": preset_model,
        "system_instruction": system_instruction,
        "prompt": prompt,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }


def comparison_setup_rows(experiment_a: dict, experiment_b: dict):
    return [
        {
            "Field": "Provider",
            "Status": same_or_different(
                experiment_a["provider"], experiment_b["provider"]
            ),
            "Configuration A": experiment_a["provider"],
            "Configuration B": experiment_b["provider"],
        },
        {
            "Field": "Model",
            "Status": same_or_different(experiment_a["model"], experiment_b["model"]),
            "Configuration A": display_model(experiment_a["model"]),
            "Configuration B": display_model(experiment_b["model"]),
        },
        {
            "Field": "System Instruction",
            "Status": same_or_different(
                experiment_a["system_instruction"].strip(),
                experiment_b["system_instruction"].strip(),
            ),
            "Configuration A": provided_label(experiment_a["system_instruction"]),
            "Configuration B": provided_label(experiment_b["system_instruction"]),
        },
        {
            "Field": "User Prompt",
            "Status": same_or_different(
                experiment_a["prompt"].strip(), experiment_b["prompt"].strip()
            ),
            "Configuration A": provided_label(experiment_a["prompt"]),
            "Configuration B": provided_label(experiment_b["prompt"]),
        },
        {
            "Field": "Temperature",
            "Status": same_or_different(
                experiment_a["temperature"], experiment_b["temperature"]
            ),
            "Configuration A": f"{experiment_a['temperature']:.1f}",
            "Configuration B": f"{experiment_b['temperature']:.1f}",
        },
        {
            "Field": "Max Output Tokens",
            "Status": same_or_different(
                experiment_a["max_output_tokens"], experiment_b["max_output_tokens"]
            ),
            "Configuration A": str(experiment_a["max_output_tokens"]),
            "Configuration B": str(experiment_b["max_output_tokens"]),
        },
    ]


def experiments_are_identical(experiment_a: dict, experiment_b: dict) -> bool:
    compared_fields = [
        "provider",
        "model",
        "temperature",
        "max_output_tokens",
    ]
    return all(experiment_a[field] == experiment_b[field] for field in compared_fields) and (
        experiment_a["system_instruction"].strip()
        == experiment_b["system_instruction"].strip()
    ) and (experiment_a["prompt"].strip() == experiment_b["prompt"].strip())


def unsupported_providers(experiment_a: dict, experiment_b: dict) -> list[str]:
    return [
        experiment["label"]
        for experiment in [experiment_a, experiment_b]
        if experiment["provider"] not in LIVE_PROVIDERS
    ]


def missing_custom_model_experiments(experiment_a: dict, experiment_b: dict) -> list[str]:
    return [
        experiment["label"]
        for experiment in [experiment_a, experiment_b]
        if experiment["preset_model"] == CUSTOM_MODEL_OPTION
        and not experiment["model"].strip()
    ]


def run_provider_candidate(experiment: dict):
    provider = experiment["provider"]
    shared_args = {
        "prompt": experiment["prompt"],
        "model": experiment["model"],
        "temperature": experiment["temperature"],
        "max_output_tokens": experiment["max_output_tokens"],
        "api_key": experiment["api_key"],
        "system_instruction": experiment["system_instruction"],
    }
    if provider == "OpenAI":
        return run_openai_experiment(**shared_args)
    if provider == "Anthropic":
        return run_anthropic_experiment(**shared_args)
    raise RuntimeError(f"{provider} integration is not implemented yet.")


st.title("LLM Lab MVP")
st.markdown(
    "<div style='font-size: 1.15rem; color: #4a5568; margin-bottom: 0.5rem;'>"
    "A lightweight LLM experimentation tool for comparing prompts, models, "
    "parameters, and outputs across providers."
    "</div>",
    unsafe_allow_html=True,
)
st.caption(
    "Presets are optional starting points. Reports are local Markdown downloads "
    "generated from the current run. OpenAI and Anthropic are currently live."
)

initialize_experiment_defaults("experiment_a", 0)
initialize_experiment_defaults("experiment_b", 1)

st.subheader("Comparison Presets")
selected_preset = st.selectbox(
    "Select a template to pre-fill the configuration",
    list(COMPARISON_PRESETS.keys()),
    key="comparison_preset",
)
with st.container(border=True):
    preset_cols = st.columns([4, 1])
    with preset_cols[0]:
        st.markdown(f"**{selected_preset}**")
        st.markdown(f"<span style='color: #555555;'>{COMPARISON_PRESETS[selected_preset]['description']}</span>", unsafe_allow_html=True)
    with preset_cols[1]:
        st.write("")
        if st.button("Apply Preset", type="primary", use_container_width=True):
            apply_preset_to_session_state(selected_preset)
            st.session_state["last_applied_preset"] = selected_preset
            st.success(f"Applied preset: {selected_preset}")

st.subheader("User Input")
setup_cols = st.columns(2)
with setup_cols[0]:
    experiment_a = build_experiment_panel("Configuration A", "experiment_a", 0)
with setup_cols[1]:
    experiment_b = build_experiment_panel("Configuration B", "experiment_b", 1)

st.subheader("Comparison Setup Summary")
st.caption(comparison_type_statement(experiment_a, experiment_b))
st.table(comparison_setup_rows(experiment_a, experiment_b))

action_cols = st.columns([2, 2, 8])
with action_cols[0]:
    run_pressed = st.button("Run Evaluation", type="primary", use_container_width=True)
with action_cols[1]:
    if st.button("Reset All", use_container_width=True):
        st.session_state.clear()
        st.rerun()

if run_pressed:
    result_a = None
    result_b = None
    status_a = "Not Run"
    status_b = "Not Run"
    blocked_experiments = unsupported_providers(experiment_a, experiment_b)
    missing_custom_models = missing_custom_model_experiments(experiment_a, experiment_b)

    if missing_custom_models:
        status_a = (
            "Not Run: Custom Model ID Required"
            if experiment_a["label"] in missing_custom_models
            else "Not Run: Comparison Blocked by Missing Custom Model"
        )
        status_b = (
            "Not Run: Custom Model ID Required"
            if experiment_b["label"] in missing_custom_models
            else "Not Run: Comparison Blocked by Missing Custom Model"
        )
        st.warning(
            "Enter a custom model ID for: "
            + ", ".join(missing_custom_models)
            + ". The literal value `Other` is never sent to providers."
        )
        st.session_state["last_report_filename"] = "llm-lab-missing-model.md"
    elif blocked_experiments:
        status_a = (
            "Not Run: Provider Placeholder"
            if experiment_a["provider"] not in LIVE_PROVIDERS
            else "Not Run: Comparison Blocked by Placeholder Provider"
        )
        status_b = (
            "Not Run: Provider Placeholder"
            if experiment_b["provider"] not in LIVE_PROVIDERS
            else "Not Run: Comparison Blocked by Placeholder Provider"
        )
        st.info(
            "Only OpenAI and Anthropic execution are supported in MVP v0.1. "
            "Other providers are UI placeholders for now."
        )
        st.caption(
            "Placeholder selected for: "
            + ", ".join(blocked_experiments)
            + ". No live API call was attempted."
        )
        st.session_state["last_report_filename"] = "llm-lab-placeholder-comparison.md"
    elif not experiment_a["prompt"].strip() or not experiment_b["prompt"].strip():
        status_a = "Not Run: Missing User Prompt"
        status_b = "Not Run: Missing User Prompt"
        st.warning("Enter a user prompt for both experiments before running.")
    else:
        if experiments_are_identical(experiment_a, experiment_b):
            st.warning(
                "Configuration A and Configuration B are identical. Outputs may be "
                "similar unless randomness introduces variation."
            )

        with st.spinner("Running Configuration A..."):
            try:
                result_a = run_provider_candidate(experiment_a)
                status_a = "Completed"
            except RuntimeError as error:
                status_a = str(error)
            except Exception as e:
                status_a = f"Failed: {experiment_a['provider']} API call did not complete. ({e})"

        with st.spinner("Running Configuration B..."):
            try:
                result_b = run_provider_candidate(experiment_b)
                status_b = "Completed"
            except RuntimeError as error:
                status_b = str(error)
            except Exception as e:
                status_b = f"Failed: {experiment_b['provider']} API call did not complete. ({e})"

        if result_a is not None and result_b is not None:
            st.session_state["last_report_filename"] = "llm-lab-live-comparison.md"
        else:
            st.session_state["last_report_filename"] = "llm-lab-failed-comparison.md"

    render_model_outputs(experiment_a, experiment_b, result_a, result_b, status_a, status_b)
    render_approximate_metrics(
        experiment_a,
        experiment_b,
        result_a,
        result_b,
        status_a,
        status_b,
    )
    insights = build_decision_intelligence(experiment_a, experiment_b, result_a, result_b)
    render_decision_intelligence(insights)
    run_summary = build_run_summary(
        experiment_a,
        experiment_b,
        result_a,
        result_b,
        status_a,
        status_b,
    )
    render_run_summary(run_summary)
    st.session_state["last_report_markdown"] = build_markdown_report(
        experiment_a,
        experiment_b,
        result_a=result_a,
        result_b=result_b,
        status_a=status_a,
        status_b=status_b,
        preset_name=st.session_state.get("last_applied_preset"),
        insights=insights,
        run_summary=run_summary,
    )

if "last_report_markdown" in st.session_state:
    st.subheader("Download")
    st.caption(
        "This Markdown report is generated locally from the current run and excludes API keys."
    )
    st.download_button(
        "Download Markdown Report",
        data=st.session_state["last_report_markdown"],
        file_name=st.session_state.get(
            "last_report_filename", "llm-lab-comparison-report.md"
        ),
        mime="text/markdown",
    )

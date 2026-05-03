from datetime import datetime, timezone

from dotenv import load_dotenv
import streamlit as st

from providers.openai_provider import run_openai_experiment


PROVIDERS = ["OpenAI", "Anthropic", "Google Gemini", "Mistral", "Cohere"]

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
        "claude-opus-4-7",
        "claude-haiku-4-5",
        "claude-sonnet-4-5",
        "claude-haiku-3-5",
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

DEFAULT_SYSTEM_INSTRUCTION = (
    "Return a concise, structured answer with decision-ready bullets."
)

COMPARISON_PRESETS = {
    "Blank comparison": {
        "description": "Start with empty prompts and default OpenAI model suggestions.",
        "a": {
            "provider": "OpenAI",
            "preset_model": "gpt-4.1-mini",
            "custom_model": "",
            "system_instruction": "",
            "prompt": "",
            "temperature": 0.7,
            "max_output_tokens": 1024,
        },
        "b": {
            "provider": "OpenAI",
            "preset_model": "gpt-4.1",
            "custom_model": "",
            "system_instruction": "",
            "prompt": "",
            "temperature": 0.7,
            "max_output_tokens": 1024,
        },
    },
    "Same prompt, different models": {
        "description": "Compare two OpenAI models on the same task and instruction.",
        "a": {
            "provider": "OpenAI",
            "preset_model": "gpt-4.1-mini",
            "custom_model": "",
            "system_instruction": DEFAULT_SYSTEM_INSTRUCTION,
            "prompt": "Summarize the tradeoffs of building an internal LLM evaluation tool.",
            "temperature": 0.7,
            "max_output_tokens": 1024,
        },
        "b": {
            "provider": "OpenAI",
            "preset_model": "gpt-4.1",
            "custom_model": "",
            "system_instruction": DEFAULT_SYSTEM_INSTRUCTION,
            "prompt": "Summarize the tradeoffs of building an internal LLM evaluation tool.",
            "temperature": 0.7,
            "max_output_tokens": 1024,
        },
    },
    "Same model, different system instructions": {
        "description": "Keep the model and prompt fixed while changing only the instruction.",
        "a": {
            "provider": "OpenAI",
            "preset_model": "gpt-4.1-mini",
            "custom_model": "",
            "system_instruction": "Return a concise executive summary with decision-ready bullets.",
            "prompt": "Evaluate whether a team should adopt an LLM experimentation workflow.",
            "temperature": 0.7,
            "max_output_tokens": 1024,
        },
        "b": {
            "provider": "OpenAI",
            "preset_model": "gpt-4.1-mini",
            "custom_model": "",
            "system_instruction": "Return a detailed technical analysis with risks, mitigations, and implementation notes.",
            "prompt": "Evaluate whether a team should adopt an LLM experimentation workflow.",
            "temperature": 0.7,
            "max_output_tokens": 1024,
        },
    },
    "Concise vs detailed answer": {
        "description": "Compare a short answer style against a more expansive answer style.",
        "a": {
            "provider": "OpenAI",
            "preset_model": "gpt-4.1-mini",
            "custom_model": "",
            "system_instruction": "Answer in no more than five concise bullets.",
            "prompt": "Explain how to evaluate two LLM responses for a product decision.",
            "temperature": 0.5,
            "max_output_tokens": 768,
        },
        "b": {
            "provider": "OpenAI",
            "preset_model": "gpt-4.1-mini",
            "custom_model": "",
            "system_instruction": "Answer with detailed reasoning, examples, and implementation guidance.",
            "prompt": "Explain how to evaluate two LLM responses for a product decision.",
            "temperature": 0.5,
            "max_output_tokens": 1536,
        },
    },
    "Creative vs analytical answer": {
        "description": "Compare a more imaginative response style against a structured analytical style.",
        "a": {
            "provider": "OpenAI",
            "preset_model": "gpt-4.1-mini",
            "custom_model": "",
            "system_instruction": "Generate creative, unconventional options while staying practical.",
            "prompt": "Propose ways to make an LLM experimentation tool more useful for product teams.",
            "temperature": 1.0,
            "max_output_tokens": 1024,
        },
        "b": {
            "provider": "OpenAI",
            "preset_model": "gpt-4.1-mini",
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


def format_cost(value: float | None) -> str:
    return f"${value:.6f}" if value is not None else "Pricing unavailable"


def format_context_pressure(value: float | None) -> str:
    return f"{value:.2f}%" if value is not None else "Context window unavailable"


def model_metrics_rows(result, cost_value: str, context_pressure_value: str):
    return [
        {"Metric": "Latency", "Value": f"{result.latency_seconds:.2f}s"},
        {"Metric": "Input tokens", "Value": str(result.approximate_input_tokens)},
        {"Metric": "Output tokens", "Value": str(result.approximate_output_tokens)},
        {"Metric": "Total tokens", "Value": str(result.approximate_total_tokens)},
        {"Metric": "Approx. context pressure", "Value": context_pressure_value},
        {"Metric": "Est. cost", "Value": cost_value},
    ]


def render_model_panel(label: str, experiment: dict, result) -> tuple[str, str]:
    cost_value = format_cost(result.approximate_cost_usd)
    context_pressure_value = format_context_pressure(
        result.approximate_context_pressure_percent
    )

    with st.container(border=True):
        st.markdown(
            f"**{label}: {experiment['provider']} / `{experiment['model']}`**"
        )
        st.write(result.output_text)
        st.markdown("**Approximate metrics**")
        st.table(model_metrics_rows(result, cost_value, context_pressure_value))

        notes = []
        if result.approximate_cost_usd is None:
            notes.append("pricing is not available for this model")
        if result.approximate_context_pressure_percent is None:
            notes.append("context window is not available for this model")
        if notes:
            st.caption("Fallback note: " + "; ".join(notes) + ".")

    return cost_value, context_pressure_value


def resolve_model(preset_model: str, custom_model: str) -> str:
    return custom_model.strip() or preset_model


def provided_label(value: str) -> str:
    return "Provided" if value.strip() else "Not provided"


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


def result_metrics_for_report(result) -> list[tuple[str, str]]:
    if result is None:
        return []

    return [
        ("Latency", f"{result.latency_seconds:.2f}s"),
        ("Approx. input tokens", str(result.approximate_input_tokens)),
        ("Approx. output tokens", str(result.approximate_output_tokens)),
        ("Approx. total tokens", str(result.approximate_total_tokens)),
        ("Approx. estimated cost", format_cost(result.approximate_cost_usd)),
        (
            "Approx. context pressure",
            format_context_pressure(result.approximate_context_pressure_percent),
        ),
    ]


def experiment_config_markdown(label: str, experiment: dict) -> str:
    return "\n".join(
        [
            f"### {label} Configuration",
            "",
            f"- Provider: {experiment['provider']}",
            f"- Model: {experiment['model']}",
            f"- Temperature: {experiment['temperature']:.1f}",
            f"- Max output tokens: {experiment['max_output_tokens']}",
            f"- System instruction: {provided_label(experiment['system_instruction'])}",
            f"- User prompt: {provided_label(experiment['prompt'])}",
            "",
            "System instruction:",
            markdown_block(experiment["system_instruction"]),
            "",
            "User prompt:",
            markdown_block(experiment["prompt"]),
        ]
    )


def result_markdown(label: str, experiment: dict, result, status_message: str) -> str:
    lines = [
        f"### {label} Result",
        "",
        f"- Status: {status_message}",
        f"- Provider: {experiment['provider']}",
        f"- Model: {experiment['model']}",
    ]

    for metric, value in result_metrics_for_report(result):
        lines.append(f"- {metric}: {value}")

    lines.extend(["", "Output:", markdown_block(result.output_text if result else "")])
    return "\n".join(lines)


def comparison_summary_markdown(experiment_a: dict, experiment_b: dict) -> str:
    lines = ["## Comparison Summary", "", "| Field | Status |", "| --- | --- |"]
    for row in comparison_setup_rows(experiment_a, experiment_b):
        lines.append(f"| {row['Field']} | {row['Status']} |")
    return "\n".join(lines)


def build_markdown_report(
    experiment_a: dict,
    experiment_b: dict,
    result_a=None,
    result_b=None,
    status_a: str = "Not run",
    status_b: str = "Not run",
) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return "\n\n".join(
        [
            "# LLM Lab MVP Comparison Report",
            f"Generated: {timestamp}",
            "OpenAI is currently the only live execution provider. Other providers are placeholders.",
            experiment_config_markdown("Candidate A", experiment_a),
            experiment_config_markdown("Candidate B", experiment_b),
            result_markdown("Candidate A", experiment_a, result_a, status_a),
            result_markdown("Candidate B", experiment_b, result_b, status_b),
            comparison_summary_markdown(experiment_a, experiment_b),
            "Note: token, cost, and context pressure values are approximate.",
        ]
    )


def build_experiment_panel(label: str, key_prefix: str, default_model_index: int) -> dict:
    with st.container(border=True):
        st.subheader(label)
        provider = st.selectbox("Provider", PROVIDERS, key=f"{key_prefix}_provider")

        api_key = st.text_input("API key", type="password", key=f"{key_prefix}_api_key")
        st.caption("Your API key is used only for this run and is not stored by this app.")

        preset_model_key = f"{key_prefix}_preset_model"
        if st.session_state.get(preset_model_key) not in MODEL_PRESETS[provider]:
            st.session_state[preset_model_key] = MODEL_PRESETS[provider][
                min(default_model_index, len(MODEL_PRESETS[provider]) - 1)
            ]

        preset_model = st.selectbox(
            "Preset model",
            MODEL_PRESETS[provider],
            key=preset_model_key,
        )
        custom_model = st.text_input("Custom model", key=f"{key_prefix}_custom_model")
        st.caption(
            "Custom model IDs must match the selected provider’s official model name. "
            "Invalid, unavailable, or deprecated models may fail at runtime."
        )

        model = resolve_model(preset_model, custom_model)
        st.caption(f"Selected model: `{model}`")

        system_instruction = st.text_area(
            "System instruction",
            height=120,
            key=f"{key_prefix}_system_instruction",
        )
        prompt = st.text_area(
            "User prompt",
            placeholder="Enter the prompt you want to experiment with...",
            height=190,
            key=f"{key_prefix}_prompt",
        )

        param_cols = st.columns(2)
        with param_cols[0]:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                step=0.1,
                key=f"{key_prefix}_temperature",
            )
        with param_cols[1]:
            max_output_tokens = st.slider(
                "Max output tokens",
                min_value=128,
                max_value=4096,
                step=128,
                key=f"{key_prefix}_max_output_tokens",
            )

    return {
        "label": label,
        "provider": provider,
        "api_key": api_key.strip() or None,
        "model": model,
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
            "Experiment A": experiment_a["provider"],
            "Experiment B": experiment_b["provider"],
        },
        {
            "Field": "Model",
            "Status": same_or_different(experiment_a["model"], experiment_b["model"]),
            "Experiment A": experiment_a["model"],
            "Experiment B": experiment_b["model"],
        },
        {
            "Field": "System instruction",
            "Status": same_or_different(
                experiment_a["system_instruction"].strip(),
                experiment_b["system_instruction"].strip(),
            ),
            "Experiment A": provided_label(experiment_a["system_instruction"]),
            "Experiment B": provided_label(experiment_b["system_instruction"]),
        },
        {
            "Field": "User prompt",
            "Status": same_or_different(
                experiment_a["prompt"].strip(), experiment_b["prompt"].strip()
            ),
            "Experiment A": provided_label(experiment_a["prompt"]),
            "Experiment B": provided_label(experiment_b["prompt"]),
        },
        {
            "Field": "Temperature",
            "Status": same_or_different(
                experiment_a["temperature"], experiment_b["temperature"]
            ),
            "Experiment A": f"{experiment_a['temperature']:.1f}",
            "Experiment B": f"{experiment_b['temperature']:.1f}",
        },
        {
            "Field": "Max output tokens",
            "Status": same_or_different(
                experiment_a["max_output_tokens"], experiment_b["max_output_tokens"]
            ),
            "Experiment A": str(experiment_a["max_output_tokens"]),
            "Experiment B": str(experiment_b["max_output_tokens"]),
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
        if experiment["provider"] != "OpenAI"
    ]


st.title("LLM Lab MVP")
st.caption(
    "A lightweight LLM experimentation tool for comparing prompts, models, "
    "parameters, and outputs across providers."
)
st.caption(
    "Presets are optional starting points. Reports are local Markdown downloads "
    "generated from the current run. OpenAI is currently the only live provider."
)

initialize_experiment_defaults("experiment_a", 0)
initialize_experiment_defaults("experiment_b", 1)

with st.container(border=True):
    preset_cols = st.columns([2, 4, 1])
    with preset_cols[0]:
        selected_preset = st.selectbox(
            "Comparison preset",
            list(COMPARISON_PRESETS.keys()),
            key="comparison_preset",
        )
    with preset_cols[1]:
        st.caption(COMPARISON_PRESETS[selected_preset]["description"])
    with preset_cols[2]:
        if st.button("Apply preset"):
            apply_preset_to_session_state(selected_preset)
            st.success(f"Applied preset: {selected_preset}")

setup_cols = st.columns(2)
with setup_cols[0]:
    experiment_a = build_experiment_panel("Experiment A", "experiment_a", 0)
with setup_cols[1]:
    experiment_b = build_experiment_panel("Experiment B", "experiment_b", 1)

st.subheader("Comparison setup summary")
st.table(comparison_setup_rows(experiment_a, experiment_b))

if st.button("Run experiment", type="primary"):
    blocked_experiments = unsupported_providers(experiment_a, experiment_b)
    if blocked_experiments:
        status_a = (
            "Not run: provider placeholder"
            if experiment_a["provider"] != "OpenAI"
            else "Not run: comparison blocked by placeholder provider"
        )
        status_b = (
            "Not run: provider placeholder"
            if experiment_b["provider"] != "OpenAI"
            else "Not run: comparison blocked by placeholder provider"
        )
        st.info(
            "Only OpenAI execution is supported in MVP v0.1. "
            "Other providers are UI placeholders for now."
        )
        st.caption(
            "Placeholder selected for: "
            + ", ".join(blocked_experiments)
            + ". No live API call was attempted."
        )
        st.session_state["last_report_markdown"] = build_markdown_report(
            experiment_a,
            experiment_b,
            status_a=status_a,
            status_b=status_b,
        )
        st.session_state["last_report_filename"] = "llm-lab-placeholder-comparison.md"
    elif not experiment_a["prompt"].strip() or not experiment_b["prompt"].strip():
        st.warning("Enter a user prompt for both experiments before running.")
    else:
        if experiments_are_identical(experiment_a, experiment_b):
            st.warning(
                "Experiment A and Experiment B configurations are identical. Outputs may be "
                "similar unless randomness introduces variation."
            )

        try:
            with st.spinner("Running Experiment A..."):
                result_a = run_openai_experiment(
                    prompt=experiment_a["prompt"],
                    model=experiment_a["model"],
                    temperature=experiment_a["temperature"],
                    max_output_tokens=experiment_a["max_output_tokens"],
                    api_key=experiment_a["api_key"],
                    system_instruction=experiment_a["system_instruction"],
                )

            with st.spinner("Running Experiment B..."):
                result_b = run_openai_experiment(
                    prompt=experiment_b["prompt"],
                    model=experiment_b["model"],
                    temperature=experiment_b["temperature"],
                    max_output_tokens=experiment_b["max_output_tokens"],
                    api_key=experiment_b["api_key"],
                    system_instruction=experiment_b["system_instruction"],
                )

            st.subheader("Model comparison")
            comparison_cols = st.columns(2)
            with comparison_cols[0]:
                cost_a, context_pressure_a = render_model_panel(
                    "Experiment A", experiment_a, result_a
                )
            with comparison_cols[1]:
                cost_b, context_pressure_b = render_model_panel(
                    "Experiment B", experiment_b, result_b
                )
            st.caption("Token, context pressure, and cost values are approximate estimates.")

            st.subheader("Run summary")
            st.table(comparison_setup_rows(experiment_a, experiment_b))
            st.session_state["last_report_markdown"] = build_markdown_report(
                experiment_a,
                experiment_b,
                result_a=result_a,
                result_b=result_b,
                status_a="Completed",
                status_b="Completed",
            )
            st.session_state["last_report_filename"] = "llm-lab-openai-comparison.md"
        except RuntimeError as error:
            st.error(str(error))
            st.session_state["last_report_markdown"] = build_markdown_report(
                experiment_a,
                experiment_b,
                status_a="Failed: run did not complete",
                status_b="Not completed",
            )
            st.session_state["last_report_filename"] = "llm-lab-failed-comparison.md"
        except Exception as error:
            st.error(f"OpenAI API call failed: {error}")
            st.session_state["last_report_markdown"] = build_markdown_report(
                experiment_a,
                experiment_b,
                status_a="Failed: OpenAI API call did not complete",
                status_b="Not completed",
            )
            st.session_state["last_report_filename"] = "llm-lab-failed-comparison.md"

if "last_report_markdown" in st.session_state:
    st.subheader("Export report")
    st.caption(
        "This Markdown report is generated locally from the current run and excludes API keys."
    )
    st.download_button(
        "Download Markdown report",
        data=st.session_state["last_report_markdown"],
        file_name=st.session_state.get(
            "last_report_filename", "llm-lab-comparison-report.md"
        ),
        mime="text/markdown",
    )

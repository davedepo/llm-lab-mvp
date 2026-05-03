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

st.set_page_config(page_title="LLM Lab MVP")


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


def render_model_panel(label: str, model: str, result) -> tuple[str, str]:
    cost_value = format_cost(result.approximate_cost_usd)
    context_pressure_value = format_context_pressure(
        result.approximate_context_pressure_percent
    )

    with st.container(border=True):
        st.markdown(f"**{label}: `{model}`**")
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

st.title("LLM Lab MVP")
st.caption(
    "A lightweight LLM experimentation tool for comparing prompts, models, "
    "parameters, and outputs across providers."
)

with st.sidebar:
    st.header("Experiment Settings")
    provider = st.selectbox("Provider", PROVIDERS)
    run_api_key = st.text_input("API key", type="password")
    st.caption("Your API key is used only for this run and is not stored by this app.")
    if provider == "OpenAI":
        preset_model_a = st.selectbox("Model A preset", MODEL_PRESETS["OpenAI"])
        custom_model_a = st.text_input("Custom Model A")
        preset_model_b = st.selectbox("Model B preset", MODEL_PRESETS["OpenAI"], index=1)
        custom_model_b = st.text_input("Custom Model B")
        st.caption(
            "Custom model IDs must match the selected provider’s official model name. "
            "Invalid, unavailable, or deprecated models may fail at runtime."
        )
        model_a = custom_model_a.strip() or preset_model_a
        model_b = custom_model_b.strip() or preset_model_b
    else:
        preset_model = st.selectbox("Preset model", MODEL_PRESETS[provider])
        custom_model = st.text_input("Custom model")
        st.caption(
            "Custom model IDs must match the selected provider’s official model name. "
            "Invalid, unavailable, or deprecated models may fail at runtime."
        )
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
    max_output_tokens = st.slider("Max output tokens", 128, 4096, 1024, 128)

system_instruction = st.text_area(
    "System instruction",
    value="Return a concise, structured answer with decision-ready bullets.",
    height=110,
)

prompt = st.text_area(
    "User prompt",
    placeholder="Enter the prompt you want to experiment with...",
    height=180,
)

if st.button("Run experiment", type="primary"):
    if provider != "OpenAI":
        st.info(
            "Only OpenAI execution is supported in MVP v0.1. "
            "Other providers are UI placeholders for now."
        )
    elif not prompt.strip():
        st.warning("Enter a prompt before running an experiment.")
    else:
        if model_a == model_b:
            st.warning(
                "Model A and Model B configurations are identical. Outputs may be "
                "similar unless randomness introduces variation."
            )

        try:
            with st.spinner("Running Model A..."):
                result_a = run_openai_experiment(
                    prompt=prompt,
                    model=model_a,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    api_key=run_api_key.strip() or None,
                    system_instruction=system_instruction,
                )

            with st.spinner("Running Model B..."):
                result_b = run_openai_experiment(
                    prompt=prompt,
                    model=model_b,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    api_key=run_api_key.strip() or None,
                    system_instruction=system_instruction,
                )

            st.subheader("Model comparison")
            comparison_cols = st.columns(2)
            with comparison_cols[0]:
                cost_a, context_pressure_a = render_model_panel(
                    "Model A", model_a, result_a
                )
            with comparison_cols[1]:
                cost_b, context_pressure_b = render_model_panel(
                    "Model B", model_b, result_b
                )
            st.caption("Token, context pressure, and cost values are approximate estimates.")

            st.subheader("Run summary")
            st.markdown(
                f"""
| Field | Value |
| --- | --- |
| Provider | {provider} |
| Model A | {model_a} |
| Model B | {model_b} |
| Temperature | {temperature:.1f} |
| Max output tokens | {max_output_tokens} |
| System instruction | {"Provided" if system_instruction.strip() else "Not provided"} |
"""
            )
        except RuntimeError as error:
            st.error(str(error))
        except Exception as error:
            st.error(f"OpenAI API call failed: {error}")

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
    preset_model = st.selectbox("Preset model", MODEL_PRESETS[provider])
    custom_model = st.text_input("Custom model")
    st.caption(
        "Custom model IDs must match the selected provider’s official model name. "
        "Invalid, unavailable, or deprecated models may fail at runtime."
    )
    model = custom_model.strip() or preset_model
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
    if not prompt.strip():
        st.warning("Enter a prompt before running an experiment.")
    elif provider == "OpenAI":
        try:
            with st.spinner("Running OpenAI experiment..."):
                result = run_openai_experiment(
                    prompt=prompt,
                    model=model,
                    temperature=temperature,
                    max_output_tokens=max_output_tokens,
                    api_key=run_api_key.strip() or None,
                )
            st.subheader("Model response")
            st.write(result.output_text)

            st.subheader("Approximate metrics")
            cost_value = (
                f"${result.approximate_cost_usd:.6f}"
                if result.approximate_cost_usd is not None
                else "N/A"
            )
            context_pressure_value = (
                f"{result.approximate_context_pressure_percent:.2f}%"
                if result.approximate_context_pressure_percent is not None
                else "N/A"
            )
            cols = st.columns(4)
            cols[0].metric("Latency", f"{result.latency_seconds:.2f}s")
            cols[1].metric("Input tokens", result.approximate_input_tokens)
            cols[2].metric("Output tokens", result.approximate_output_tokens)
            cols[3].metric("Total tokens", result.approximate_total_tokens)

            detail_cols = st.columns(2)
            detail_cols[0].metric("Approx. context pressure", context_pressure_value)
            detail_cols[1].metric("Est. cost", cost_value)
            st.caption("Token, context pressure, and cost values are approximate estimates.")

            st.subheader("Run summary")
            st.markdown(
                f"""
| Field | Value |
| --- | --- |
| Provider | {provider} |
| Model | {model} |
| Temperature | {temperature:.1f} |
| Max output tokens | {max_output_tokens} |
| System instruction | {"Provided" if system_instruction.strip() else "Not provided"} |
| Approx. input tokens | {result.approximate_input_tokens} |
| Approx. output tokens | {result.approximate_output_tokens} |
| Approx. total tokens | {result.approximate_total_tokens} |
| Approx. estimated cost | {cost_value} |
| Latency | {result.latency_seconds:.2f}s |
| Approx. context pressure | {context_pressure_value} |
"""
            )
        except RuntimeError as error:
            st.error(str(error))
        except Exception as error:
            st.error(f"OpenAI API call failed: {error}")
    else:
        st.info(f"Provider integration for {provider} is not implemented yet.")

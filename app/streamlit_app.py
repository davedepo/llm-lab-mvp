from dotenv import load_dotenv
import streamlit as st

from providers.openai_provider import run_openai_experiment


load_dotenv()

st.set_page_config(page_title="LLM Lab MVP")

st.title("LLM Lab MVP")
st.caption(
    "A lightweight LLM experimentation tool for comparing prompts, models, "
    "parameters, and outputs across providers."
)

with st.sidebar:
    st.header("Experiment Settings")
    provider = st.selectbox("Provider", ["OpenAI", "Anthropic"])
    if provider == "OpenAI":
        model = st.selectbox("Model", ["gpt-4.1-mini", "gpt-4.1"])
    else:
        model = st.selectbox(
            "Model",
            [
                "claude-placeholder",
                "claude-sonnet-placeholder",
            ],
        )
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
    max_output_tokens = st.slider("Max output tokens", 128, 4096, 1024, 128)

prompt = st.text_area(
    "Prompt",
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
        st.info("Anthropic integration is not implemented yet.")

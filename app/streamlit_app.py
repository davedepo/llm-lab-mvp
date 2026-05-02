import streamlit as st


st.set_page_config(page_title="LLM Lab MVP")

st.title("LLM Lab MVP")
st.caption(
    "A lightweight LLM experimentation tool for comparing prompts, models, "
    "parameters, and outputs across providers."
)

with st.sidebar:
    st.header("Experiment Settings")
    provider = st.selectbox("Provider", ["OpenAI", "Anthropic"])
    model = st.selectbox(
        "Model",
        [
            "Select a model",
            "gpt-placeholder",
            "claude-placeholder",
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
    st.info("Provider integration is not implemented yet.")

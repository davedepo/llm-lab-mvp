"""
providers package initialization

This package contains the integrations and helpers for connecting to various
Large Language Model (LLM) APIs (e.g., OpenAI, Anthropic, Gemini, Mistral).
It standardizes the execution of experiments and the formatting of results
across different provider constraints.
"""

# Provider Initialization Sequence:
# 1. Environment variables and API keys are loaded via the Streamlit UI or .env.
# 2. Specific provider execution modules (e.g., openai_provider, anthropic_provider)
#    are invoked dynamically based on the user's comparison configuration.
# 3. Each provider wrapper formats the request, executes the live API call,
#    and returns a standardized ProviderExperimentResult object for metrics mapping.
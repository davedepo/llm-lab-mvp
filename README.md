![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Live-brightgreen)
![Simulator](https://img.shields.io/badge/simulator-static-lightgrey)

# llm-lab-app

**llm-lab-app is a lightweight, public LLM experimentation MVP that helps users compare model/provider/prompt configurations using side-by-side outputs, approximate cost and context metrics, and a decision intelligence layer that explains which configuration is more useful and why.**


> Public release: static simulator + Streamlit MVP

---

## 🖼 Preview

![llm-lab preview](assets/screen-prints/screenprint-1.png)

*The interface preview above shows the top configuration section. Additional full-page screen prints covering the entire output and report generation process are available in the [assets/screen-prints/](assets/screen-prints/) folder.*

---

## What This Is

`llm-lab-app` (repository working name: `llm-lab-mvp`) is built for the **control, comparison, and understanding** of large language model behavior. It is designed for prompt engineering, model and parameter experimentation, token & cost visibility, context usage analysis, and output behavior evaluation.

---

## Core Capabilities

* **Multi-Provider Support**: Working live integrations for **OpenAI** and **Anthropic**. Google Gemini, Mistral, and Cohere are included as UI placeholders for future expansion.
* **Dynamic A/B Comparison**: Independent controls for each configuration, allowing variable comparison (system instructions, user prompts, models, and parameters) side-by-side.
* **Decision Intelligence**: A qualitative, deterministic layer assessing completeness, structural differences, and use-case recommendations.
* **Approximate Metrics**: Calculates run latency, estimated tokens, cost, and context pressure relative to the model window.
* **Security-First Architecture**: Uses bring-your-own-key runtime variables without persisting credentials.

---

## Quick Start

```bash
git clone [https://github.com/davedepo/llm-lab-mvp.git](https://github.com/davedepo/llm-lab-mvp.git)
cd llm-lab-mvp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app/streamlit_app.py
```

Provide API keys in the Streamlit UI or place them in the local `.env` file. Keys entered in the UI are used for the current run only.

---

## Configuration

### Model Selection
Each test/use-case can use a preset model or a custom model ID. If a custom model ID is entered, the preset model selector is treated as `Other`. Ensure that custom model identifiers match the provider's official naming convention.

### Metric Calculations and Customization
The application calculates runtime and token-utilization heuristics natively. To calibrate or add pricing data for new models, update the values directly in `app/metrics.py`:

```python
# app/metrics.py structure for updating costs and context limits
PRICING_DEFAULTS = {
    "gpt-4o-mini": {"input_cost_per_m": 0.15, "output_cost_per_m": 0.60},
    "claude-3-5-sonnet-latest": {"input_cost_per_m": 3.00, "output_cost_per_m": 15.00},
}
```
* **Response time:** Elapsed provider call time.
* **Cost estimates:** Calculated by multiplying the token counts by the pricing metadata constants defined in `app/metrics.py`.

---

## Deployment Note

* **Streamlit deployment is coming soon.**

---

## Repository Structure

```text
app/         → Streamlit MVP and provider wrappers
docs/        → Static HTML simulator concept demo
assets/      → High-resolution screenshots
examples/    → Test configurations
```

---

## Possible Extensions

* Google Gemini, Mistral, and Cohere provider integrations.
* Persistent experiment history and database support.
* Enhanced, production-grade token tracking.

---

## Security

* Do not commit the `.env` file to source control.
* Keys entered in the UI are transient and are not stored by the application.

---

## License

MIT
![Status](https://img.shields.io/badge/status-MVP-blue)
![Demo](https://img.shields.io/badge/demo-live-green)

# llm-lab-mvp

**A lightweight LLM experimentation workspace for exploring prompt behavior, model parameters, latency, token usage, cost, context pressure, and decision-relevant output differences.**

> Public release: static simulator + Streamlit MVP

> Status: OpenAI live testing is currently implemented. Anthropic is currently placeholder-only.

---

## Try the product experience

👉 [Launch the live simulator](https://davedepo.github.io/llm-lab-mvp/)

The GitHub Pages simulator demonstrates the intended product workflow. The Streamlit app provides the current live OpenAI MVP.

---

## 🖼 Preview

![llm-lab preview](assets/llm-lab-preview.png)

---

## What This Is

`llm-lab-mvp` is built for **control, comparison, and understanding** of LLM behavior.

It is designed for:

* prompt engineering
* model and parameter experimentation
* token & cost visibility
* context usage analysis
* output behavior evaluation

---

## Current MVP Capabilities

Implemented now:

* Static HTML simulator available through GitHub Pages
* Streamlit app shell at `app/streamlit_app.py`
* OpenAI live testing through the official OpenAI Python package
* Local environment loading from `.env`
* Clear missing-key handling for `OPENAI_API_KEY`
* Simple prompt input and controls for provider, model, temperature, and max output tokens
* Basic metrics for OpenAI runs:
  * latency
  * approximate input token estimate
  * approximate output token estimate
  * approximate total token estimate
  * approximate estimated cost

Not implemented yet:

* Anthropic live calls
* Multi-provider comparison
* Database or experiment history
* Export functionality
* Full analyzer or difference explanation in the Streamlit app
* Production-ready pricing, tokenization, or observability

Anthropic is currently placeholder-only. Multi-provider comparison is planned, not yet implemented.

---

## Current Status

This repository currently includes:

* Interactive static simulator in `docs/index.html`
* GitHub Pages demo
* Streamlit MVP with OpenAI live testing
* Approximate latency, token, and cost metrics
* Example experiment configuration
* Placeholder Anthropic UI path for future work

---

## Intended Product Workflow

| Layer                     | Purpose                                                           |
| --------                  | ----------------------------------------------------------------- |
| Inputs                    | Configure provider, model, prompt, system instruction, parameters |
| Outputs                   | Compare responses side-by-side                                    |
| Analyzer                  | Inspect tokens, cost, latency, and context pressure               |
| Difference Explanation    | Understand behavior difference, likely cause, and decision note   |

---

## Repository Structure

```bash
app/         → Streamlit MVP and provider wrapper
docs/        → simulator (live demo)
assets/      → screenshots
examples/    → experiment configs
src/         → legacy placeholder
```

---

## Simulator

The simulator demonstrates:

* input configuration (multi-provider)
* execution pipeline (visual flow)
* side-by-side outputs
* analyzer metrics: tokens, cost, latency, context pressure
* difference explanation: behavior difference, likely cause, decision note

---

## Run Locally

OpenAI is the first supported real provider in the Streamlit app. Anthropic is currently placeholder-only.

```bash
git clone https://github.com/davedepo/llm-lab-mvp.git
cd llm-lab-mvp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app/streamlit_app.py
```

Add your OpenAI key locally in `.env` before running an OpenAI experiment:

```bash
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=
```

Do not commit `.env`.

---

## Environment Variables

| Variable            | Status                         |
| ------------------- | ------------------------------ |
| `OPENAI_API_KEY`    | Required for OpenAI live tests |
| `ANTHROPIC_API_KEY` | Placeholder for future support |

API keys are read locally from environment variables. `.env.example` is only for placeholders.

---

## Metrics Note

Metrics are approximate.

Token estimates use a simple heuristic rather than a tokenizer dependency. Estimated cost uses static placeholder pricing constants in `app/metrics.py`; review and update those constants before relying on cost numbers for budgeting or reporting.

---

## Why this exists

Most LLM tools optimize for **chat**.

`llm-lab-mvp` optimizes for:

* experimentation
* measurement
* control

It helps answer:

* Which model is better for this task?
* What is the cost impact?
* How do parameters affect output?
* How close am I to context limits?

---

## Roadmap

Planned next steps:

* Anthropic provider integration
* Multi-provider comparison
* More accurate token and cost tracking
* Context pressure metrics in the Streamlit app
* Analyzer and difference explanation implementation
* Experiment history
* Exportable results

---

## Security

* Do not commit `.env`
* Use `.env.example` only for placeholder variable names
* API keys are read locally from environment variables
* Do not paste real API keys into issues, docs, commits, or screenshots

---

## License

MIT

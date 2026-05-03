![Status](https://img.shields.io/badge/status-MVP-blue)
![Simulator](https://img.shields.io/badge/simulator-static-lightgrey)

# llm-lab-mvp

**A lightweight LLM experimentation workspace for exploring prompt behavior, model parameters, latency, token usage, cost, context pressure, and decision-relevant output differences.**

> Public release: static simulator + Streamlit MVP

> Status: OpenAI Model A vs Model B comparison is implemented in Streamlit. Other providers are UI placeholders.

---

## Product Experience

The active MVP is the local Streamlit app at `app/streamlit_app.py`.

The static HTML simulator in `docs/index.html` is the original concept demo. It preserves the intended product workflow and visual direction, but it is not the primary active app while GitHub Pages repair is deferred.

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

* Static HTML simulator preserved in `docs/index.html`
* Streamlit MVP at `app/streamlit_app.py`
* OpenAI live testing through the official OpenAI Python package
* OpenAI Model A vs Model B comparison in one run
* Separate Experiment A and Experiment B setup panels
* Independent provider, model, API key, system instruction, user prompt, temperature, and max output token controls for each experiment
* Preset and custom model IDs for OpenAI comparison
* Password-style API key fields for bring-your-own-key runs
* Local environment loading from `.env`
* Clear missing-key handling for `OPENAI_API_KEY`
* Side-by-side OpenAI outputs
* Approximate metrics for each OpenAI model:
  * latency
  * approximate input token estimate
  * approximate output token estimate
  * approximate total token estimate
  * approximate estimated cost
  * approximate context pressure
* Lightweight comparison setup summary
* Compact display-only run summary

Not implemented yet:

* Anthropic live calls
* Google Gemini, Mistral, or Cohere live calls
* Cross-provider execution or comparison
* Database or experiment history
* Export functionality
* Full analyzer or difference explanation in the Streamlit app
* Production-ready pricing, tokenization, or observability

Anthropic, Google Gemini, Mistral, and Cohere are currently UI placeholders only. OpenAI is the only implemented execution provider.

---

## Current Status

This repository currently includes:

* Interactive static simulator in `docs/index.html`
* Root `index.html` simulator entrypoint
* Streamlit MVP with OpenAI live testing and two-model comparison
* Separate Streamlit configuration panels for Experiment A and Experiment B
* Approximate latency, token, cost, and context pressure metrics
* Example experiment configuration
* Placeholder UI paths for Anthropic, Google Gemini, Mistral, and Cohere

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
docs/        → static simulator concept demo
assets/      → screenshots
examples/    → experiment configs
src/         → legacy placeholder
index.html   → root static simulator entrypoint
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

OpenAI is the only supported execution provider in the Streamlit app. Other providers are visible as UI placeholders only.

```bash
git clone https://github.com/davedepo/llm-lab-mvp.git
cd llm-lab-mvp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app/streamlit_app.py
```

You can provide an OpenAI API key in either place:

* Enter it in the Streamlit password field for the current run only.
* Add it locally to `.env` for repeated local testing.

Example `.env`:

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

The Streamlit UI also accepts a password-style API key for bring-your-own-key testing. Keys entered in the UI are used only for the current run and are not stored by the app. `.env.example` is only for placeholder variable names.

---

## Metrics Note

Metrics are approximate.

Token estimates use a simple heuristic rather than a tokenizer dependency. Estimated cost and context pressure use static placeholder constants in `app/metrics.py`; review and update those constants before relying on cost or context numbers for budgeting, reporting, or model-limit decisions.

---

## Manual MVP Test Checklist

After local setup:

* Start the app with `streamlit run app/streamlit_app.py`.
* Select `OpenAI` as the provider.
* Enter an OpenAI API key in the password field, or set `OPENAI_API_KEY` in `.env`.
* Enter a system instruction and user prompt.
* Select two different OpenAI preset models and run the experiment.
* Confirm Model A and Model B outputs render side-by-side.
* Confirm each model shows latency, approximate token counts, estimated cost, and approximate context pressure.
* Select the same model for Model A and Model B and confirm the identical-configuration warning appears without blocking execution.
* Select a placeholder provider such as Anthropic and confirm the app does not make a provider call.
* Confirm no API key appears in the run summary, logs, screenshots, or committed files.

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

Deferred and planned:

* Anthropic provider integration
* Google Gemini, Mistral, and Cohere provider integrations
* Cross-provider comparison
* More accurate token and cost tracking
* Analyzer and difference explanation implementation
* Experiment history
* Exportable results
* GitHub Pages repair for the static simulator

---

## Security

* Do not commit `.env`
* Use `.env.example` only for placeholder variable names
* API keys can be read locally from environment variables
* API keys entered in the Streamlit UI are used only for that run and are not stored by the app
* Do not paste real API keys into issues, docs, commits, or screenshots

---

## License

MIT

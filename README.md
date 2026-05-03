![Status](https://img.shields.io/badge/status-MVP-blue)
![Simulator](https://img.shields.io/badge/simulator-static-lightgrey)

# llm-lab-mvp

**A lightweight LLM experimentation workspace for exploring prompt behavior, model parameters, latency, token usage, cost, context pressure, and decision-relevant output differences.**

> Public release: static simulator + Streamlit MVP

> Status: OpenAI and Anthropic comparison is implemented in Streamlit. Gemini, Mistral, and Cohere are UI placeholders.

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
* Anthropic live testing through the official Anthropic Python package
* OpenAI and Anthropic Model A vs Model B comparison in one run
* Separate Experiment A and Experiment B setup panels
* Independent provider, model, API key, system instruction, user prompt, temperature, and max output token controls for each experiment
* Preset and custom model IDs for OpenAI and Anthropic comparison
* Password-style API key fields for bring-your-own-key runs
* Local environment loading from `.env`
* Clear missing-key handling for `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`
* Side-by-side provider outputs
* Deterministic Decision Intelligence guidance based on setup, run status, and approximate metrics
* Approximate metrics for each live model:
  * latency
  * approximate input token estimate
  * approximate output token estimate
  * approximate total token estimate
  * output length
  * approximate estimated cost
  * approximate context pressure
* Lightweight comparison setup summary
* Compact display-only run summary
* Optional comparison presets for common evaluation scenarios
* Local Markdown report download after a run or placeholder-provider check

Not implemented yet:

* Google Gemini, Mistral, or Cohere live calls
* Database or experiment history
* PDF export or persistent saved reports
* LLM-as-judge evaluation or semantic difference explanation in the Streamlit app
* Production-ready pricing, tokenization, or observability

Google Gemini, Mistral, and Cohere are currently UI placeholders only. OpenAI and Anthropic are the implemented execution providers.

---

## Current Status

This repository currently includes:

* Interactive static simulator in `docs/index.html`
* Root `index.html` simulator entrypoint
* Streamlit MVP with OpenAI and Anthropic live testing and two-model comparison
* Separate Streamlit configuration panels for Experiment A and Experiment B
* Optional comparison presets and Markdown report export
* Deterministic Decision Intelligence guidance for comparison decisions
* Approximate latency, token, cost, and context pressure metrics
* Example experiment configuration
* Placeholder UI paths for Google Gemini, Mistral, and Cohere

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

OpenAI and Anthropic are the supported execution providers in the Streamlit app. Gemini, Mistral, and Cohere are visible as UI placeholders only.

```bash
git clone https://github.com/davedepo/llm-lab-mvp.git
cd llm-lab-mvp
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app/streamlit_app.py
```

You can provide OpenAI and Anthropic API keys in either place:

* Enter a key in the Streamlit password field for the current run only.
* Add keys locally to `.env` for repeated local testing.

Example `.env`:

```bash
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

Do not commit `.env`.

---

## Environment Variables

| Variable            | Status                         |
| ------------------- | ------------------------------ |
| `OPENAI_API_KEY`    | Required for OpenAI live tests |
| `ANTHROPIC_API_KEY` | Required for Anthropic live tests |

The Streamlit UI also accepts a password-style API key for bring-your-own-key testing. Keys entered in the UI are used only for the current run and are not stored by the app. `.env.example` is only for placeholder variable names.

---

## Model Selection

Each experiment can use a preset model or a custom model ID.

If a custom model ID is entered, the preset model selector is treated as `Other` and the custom model ID is sent to the selected provider. The app never sends the literal value `Other` to a provider. If `Other` is selected, a custom model ID is required before live execution.

Known custom model IDs can still receive approximate cost and context pressure estimates when metadata exists in `app/metrics.py`. Unknown custom models can still run, but pricing and context pressure display as unavailable until metadata is added.

Anthropic currently includes `claude-sonnet-4-6`, `claude-3-5-sonnet-latest`, and `claude-3-5-haiku-latest` as preset options.

---

## Metrics Note

Metrics are approximate.

Token estimates use a simple heuristic rather than a tokenizer dependency. Estimated cost and context pressure use static placeholder constants in `app/metrics.py`; review and update those constants before relying on cost or context numbers for budgeting, reporting, or model-limit decisions.

Metric definitions:

* Response time: elapsed provider call time for the current run
* Token usage: approximate input, output, and total token estimates
* Estimated cost: static pricing metadata multiplied by approximate token estimates
* Context pressure: approximate total tokens divided by configured context window
* Output length: generated text length in characters

---

## Manual MVP Test Checklist

After local setup:

* Start the app with `streamlit run app/streamlit_app.py`.
* Select `OpenAI` or `Anthropic` as the provider.
* Enter provider API keys in the password fields, or set `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` in `.env`.
* Enter a system instruction and user prompt.
* Run OpenAI vs OpenAI, OpenAI vs Anthropic, Anthropic vs OpenAI, and Anthropic vs Anthropic comparisons when credentials are available.
* Confirm Anthropic preset `claude-sonnet-4-6` works.
* Enter `claude-sonnet-4-6` as a custom Anthropic model and confirm the selector displays `Other`.
* Confirm Model A and Model B outputs render side-by-side.
* Confirm approximate metrics appear in their own section after model outputs.
* Confirm estimated cost and approximate context pressure appear for known custom model IDs with metadata.
* Confirm unknown custom model IDs can run but show unavailable pricing/context metadata.
* Confirm the temperature helper note appears: lower values are focused/repeatable, higher values are creative/varied.
* Confirm Decision Intelligence appears and does not claim objective answer quality.
* Apply each comparison preset and confirm it fills fields without running automatically.
* Download the Markdown report after a run and confirm it includes Decision Intelligence and excludes API keys.
* Select the same model for Model A and Model B and confirm the identical-configuration warning appears without blocking execution.
* Select a placeholder provider such as Gemini, Mistral, or Cohere and confirm the app does not make a provider call.
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

* Google Gemini, Mistral, and Cohere provider integrations
* Broader cross-provider comparison beyond OpenAI and Anthropic
* More accurate token and cost tracking
* Analyzer and difference explanation implementation
* Experiment history
* PDF export and persistent saved reports
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

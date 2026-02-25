# IDAI1-2505566--HetThakkar

# AgroNova — Smart Farming Assistant (FA-2)

This repository contains a Streamlit demo app for the FA-2 formative assessment: a Smart Farming Assistant using Gemini 1.5 (or OpenAI) for generation, output formatting, and simple validation.

Files:
- `app.py`: main Streamlit app.
- `requirements.txt`: Python dependencies.

Quick start (local):
1. Create a virtual environment and activate it.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Run the app locally:

```bash
streamlit run app.py
```

Deployment on Streamlit Cloud:
1. Push this repository to GitHub.
2. Log in to https://streamlit.io/cloud and click "New app".
3. Connect your GitHub repo, select the branch and `app.py` file, then deploy.

Notes for the assignment (FA-2):
- The app includes a mock mode for offline testing. For real queries, add your Gemini/OpenAI API key in the UI or set `GEMINI_API_KEY` / `OPENAI_API_KEY` env variables.
- The app formats model outputs into bullet lists and appends short reasons to each suggestion to improve clarity for farmers.
- Use the "Model Validation & Testing" panel to run canned prompts and download validation JSON to include in your submission.

Suggested deliverables for FA-2 submission:
- Public GitHub repo URL with `app.py` and `requirements.txt`.
- Streamlit Cloud public URL.
- A short `README` (this file) with test screenshots and a `validation_results.json` produced by the app.
# CoachBot AI — Smart Fitness Assistance

CoachBot AI is a Streamlit demo that builds structured prompts from athlete inputs and requests coaching guidance from a generative model (Gemini or OpenAI). This repository is a scaffold you can extend for research or small demo deployments.

**Repository name:** workspace

**Main files**
- `app.py` — Streamlit application and prompt builder (main entry).
- `requirements.txt` — Python dependencies.

# AgroNova — Smart Farming Assistant

A concise Streamlit scaffold that demonstrates region-aware farming guidance using generative AI (Gemini 1.5 or OpenAI). Includes a mock mode for offline testing, simple formatting of model outputs, and canned validation prompts.

## Features
- Prompt builder UI and generation controls (provider, temperature, tokens)
- Mock responses for offline testing and reproducible validation
- Output formatting helper to create bulleted recommendations with short reasoning
- Validation runner with downloadable JSON results

## Main file
- App entry: [workspace/app.py](workspace/app.py)

## Requirements
- Python 3.9 or newer

Install the essentials:

```bash
pip install streamlit pandas requests
# Optional (if using the official Gemini client):
pip install google-generativeai
```

## Environment variables
- `GEMINI_API_KEY` — Gemini API key (optional)
- `OPENAI_API_KEY` — OpenAI API key (optional)

If neither variable is set, enable `Use mock responses (no network)` in the app to avoid network calls.

## Run locally

```bash
streamlit run workspace/app.py
```

Open the UI at the URL printed by Streamlit (usually[https://agronoapy-bzkbdecpdmkgtmvqknwp67.streamlit.app/).

## Usage
- Open the "API Key & Settings" expander and choose a provider (`Auto`, `Gemini`, `OpenAI`).
- Paste an API key or rely on the environment variable. Use `Auto` to detect OpenAI keys starting with `sk-`.
- Edit or build a prompt in the Prompt Builder and click `Generate Guidance`.
- Toggle `Use mock responses` for offline testing and deterministic outputs.
- Use `Run validation prompts (mock)` to generate a set of canned responses and download `validation_results.json`.

## Customization
- Update `sample_prompts` in [workspace/app.py](workspace/app.py) to change default prompts.
- Adjust `format_gemini_output()` for different formatting or stricter validation.
- Replace the REST/client snippets in the generation block with your production client code and secure key handling.

## Security & Production Notes
- Do not commit API keys. Use environment variables or a secure secret manager for deployments.
- Validate model outputs before using them for operational decisions; the scaffold app includes simple reason tags but is not a certified agronomic advisor.

## Want more?
I can add a focused `requirements.txt`, a minimal `Dockerfile`, or deployment instructions for Streamlit Cloud. Tell me which and I'll add it.

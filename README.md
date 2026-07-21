# PrivateFin

PrivateFin is a local financial advisory prototype that combines market data, technical indicators, and an optional local large language model (LLM) to produce structured, explainable analysis.

The app is designed for coursework and demonstration purposes, with an emphasis on:

- Local-first execution
- Transparent indicator-driven recommendations
- Reproducible setup for peer review

## Features

- Downloads historical stock data using `yfinance`
- Computes technical indicators:
  - RSI (14)
  - MACD (12/26/9), signal, and histogram
- Builds structured prompts using the headings:
  - Observe
  - Interpret
  - Infer
  - Recommend
- Runs in a Streamlit interface for easy interaction
- Optionally connects to a local Ollama model (default: `llama3`)

## Requirements

### Software

- Python 3.11 (recommended)
- `pip`
- `venv` (virtual environment support)
- Optional: [Ollama](https://ollama.com/) for local LLM generation

### Hardware

- 8 GB RAM minimum (16 GB recommended for smoother local model use)
- Modern CPU (Apple Silicon or equivalent recommended)
- ~5 GB free disk space (dependencies, cache, optional model files)

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/dsarney/privatefin-docs.git
cd privatefin
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Install and prepare Ollama

Install Ollama from the official website, then pull the model:

```bash
ollama pull llama3
```

If Ollama is not installed/running, the app still works and shows a structured fallback response template.

## Run the Application

From the project root:

```bash
streamlit run app.py
```

Then in the UI:

1. Choose a company
2. Set date range and risk profile
3. Click **Generate analysis**

The app will:

1. Download historical market data
2. Compute indicators
3. Build and display the structured prompt
4. Generate a model response (if Ollama is available)

## Run Tests

Run all tests:

```bash
pytest
```

Or run targeted tests:

```bash
pytest tests/test_indicator_engine.py tests/test_prompt_builder.py
```

# pdf-invoice-extractor

**Invoice extraction GUI + Streamlit launcher** — a professional, production-ready starter repository for extracting structured invoice data from PDFs using an OpenRouter-compatible model (chat completions). Designed for engineers who want a production-ready codebase, CI, and deployment artifacts.

![Flowchart](flowchart_colored.png)

## Features

- Upload or select a PDF invoice (via Streamlit `app.py`).
- Extract text using `pdfplumber` (OCR fallback optional).
- Send the text to an OpenRouter-compatible chat completions endpoint and request strict JSON output.
- Parse model response into structured JSON and convert to pretty XML.
- Preview extracted text, JSON, and XML in the UI.
- Save XML to disk.
- Production-ready repository layout: Dockerfile, CI, Dependabot, pre-commit, tests scaffold.

## Quickstart (local)

1. Install Python 3.11+ and create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create `.env` from the example and fill in values:

```bash
cp .env.example .env
# edit .env and set OPENROUTER_API_KEY, API_BASE, MODEL
```

3. Run the Streamlit launcher:

```bash
streamlit run app.py
```

4. In the app, upload a PDF, enter your API key (or rely on `.env`), choose a model and click **Extract**.

## Docker

Build and run:

```bash
docker build -t pdf-invoice-extractor:latest .
docker run --rm -p 8501:8501 --env-file .env pdf-invoice-extractor:latest
```

## CI / Code Quality

This repository includes GitHub Actions to run tests and linters, Dependabot config for automated dependency updates, and a pre-commit configuration (Black, isort, flake8).

## Files in this repo

- `app.py` — Streamlit launcher and orchestration (extract, preview, save).
- `flowchart_colored.mmd` — Mermaid source of the flowchart.
- `flowchart_colored.png` — Rendered flowchart image.
- `README.md`, `FLOWCHART_DETAILED.md` — docs.
- `Dockerfile`, `requirements.txt`, `.env.example`, `.gitignore`.
- `.github/workflows/ci.yml`, `.github/dependabot.yml`, `.pre-commit-config.yaml`.
- `tests/` — pytest scaffold.
- `LICENSE` (MIT), `CONTRIBUTING.md`.

## Security notes

- **Do not commit secrets.** Use `.env` and your host's secret manager.
- This repo intentionally keeps a strict instruction to models (system message) to return **only JSON**. Always validate and sanitize upstream responses.

---

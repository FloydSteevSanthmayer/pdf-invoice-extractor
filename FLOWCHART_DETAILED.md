# Flowchart — Detailed Step-by-Step

This document provides an in-depth, technical explanation of each step shown in `flowchart_colored.png` for reviewers and engineers.

## Overview

The system orchestrates extraction from a PDF invoice to structured JSON and a pretty-printed XML file. The process is resilient to common failures (network timeouts, non-JSON model output) and is designed for easy extension.

## Steps

1. **Start**
   - The user launches `app.py` (Streamlit) and lands on the UI.

2. **Select PDF File**
   - User chooses a PDF via upload or local path.
   - The app validates file type and size; for large PDFs, the UI warns about chunking.

3. **Enter API Key & Model**
   - The app accepts an API key (masked input) and optional API base and model.
   - Keys may be provided via `.env` or the UI. They are never logged.

4. **Click Extract**
   - The user triggers the extraction flow.

5. **Extract Text from PDF**
   - Primary: `pdfplumber` extracts selectable text from pages.
   - If no text found and OCR enabled, fallback to `pytesseract` via `pdf2image`.

6. **Preprocess Text**
   - Normalizes whitespace, removes empty lines, and optionally redacts PII for analytics.

7. **Send Text to API**
   - The app builds a strict prompt asking for only a single JSON object containing these fields:
     - `Invoice Number`, `Invoice Date`, `Customer Name`, `Subtotal`, `Tax`, `Total Amount`.
   - A `system` role message is included instructing the model to output pure JSON.
   - For long texts, the app chunks content and merges responses field-wise.

8. **API Returned JSON?** (Decision)
   - If the API returns extractable JSON, proceed to preview.
   - If not, the raw response is saved to `debug_output/<timestamp>.txt` and the user is shown an error with a link to the debug file.

9. **Show JSON**
   - The parsed JSON is pretty-printed and shown in UI.

10. **Convert to XML**
    - The JSON is converted into XML using `dicttoxml` and pretty-printed with `xml.dom.minidom`.
    - For more complex invoice line-item representations, custom XML formatting is recommended.

11. **Show XML**
    - XML preview tab is populated.

12. **Save XML File**
    - If the user requested an output path, the XML is saved. Otherwise, the user may choose "Save As".

## Reliability & Edge Cases

- **Network / API errors**: HTTP retries (exponential backoff), informative error messages, and timestamped debug logs.
- **Model hallucinations**: Strict system prompt and JSON extraction with brace-matching to prevent non-JSON text from being parsed.
- **Scanned PDFs**: Optional OCR fallback controlled by config.
- **Concurrency**: UI tasks run in background threads; UI controls are disabled while extraction runs.

## Security & Privacy

- Secrets via `.env` or host secret managers; never printed in logs.
- When saving debug responses that may contain PII, store them locally and encourage secure sharing.

## Extensibility

- Add an LRU cache for repeated files.
- Add a table extractor for line items using OCR + heuristic table parsing.
- Add vendor-specific parsers for more accurate field extraction.

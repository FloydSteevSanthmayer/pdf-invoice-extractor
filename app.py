import os
import json
import requests
import streamlit as st
import pdfplumber
from dicttoxml import dicttoxml
import xml.dom.minidom
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="PDF Invoice Extractor", layout="wide")

st.title("PDF Invoice Extractor — Streamlit Launcher")
left, right = st.columns([3,1])

with right:
    st.info("Settings")
    api_key = st.text_input("API Key", value=os.getenv("OPENROUTER_API_KEY",""), type="password")
    api_base = st.text_input("API Base URL", value=os.getenv("API_BASE","https://openrouter.ai/api/v1/chat/completions"))
    model_name = st.selectbox("Model", options=[os.getenv("MODEL","gpt-3.5-turbo"), "gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o"])
    submit_btn = st.button("Extract")

uploaded = st.file_uploader("Upload PDF invoice", type=["pdf"])
st.caption("This demo extracts text with pdfplumber and sends to an OpenRouter-compatible chat completion API.")

def extract_text_from_pdf_obj(file_obj):
    try:
        with pdfplumber.open(file_obj) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        return "\n".join(pages).strip()
    except Exception as e:
        st.error(f"Failed to extract PDF text: {e}")
        return ""

def build_prompt(text):
    return ("You are an AI assistant that extracts structured data from invoices. "
            "Convert the following invoice text into valid JSON. Include these fields exactly: "
            "'Invoice Number', 'Invoice Date', 'Customer Name', 'Subtotal', 'Tax', and 'Total Amount'.\n"
            "If any field is missing in the text, include it with an empty string value.\n"
            "ONLY output the JSON object -- no extra explanation or commentary.\n\n"
            f"Invoice Text:\n{text}\n\nJSON:")

def call_api(api_key, api_base, model_name, prompt):
    headers = { "Authorization": f"Bearer {api_key}", "Content-Type": "application/json" }
    payload = {
        "model": model_name,
        "messages": [
            {"role":"system","content":"You are a JSON extractor that returns ONLY a single JSON object."},
            {"role":"user","content":prompt}
        ],
        "temperature": 0,
        "max_tokens": 1024,
        "n": 1
    }
    sess = requests.Session()
    resp = sess.post(api_base, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "choices" in data and len(data["choices"])>0:
        c = data["choices"][0]
        if "message" in c and "content" in c["message"]:
            return c["message"]["content"]
        if "text" in c:
            return c["text"]
    return json.dumps(data, ensure_ascii=False)

if submit_btn:
    if not uploaded:
        st.warning("Please upload a PDF file first.")
    elif not api_key:
        st.warning("Please provide an API key (or set OPENROUTER_API_KEY in .env). ")
    else:
        with st.spinner("Extracting text..."):
            raw = extract_text_from_pdf_obj(uploaded)
        if not raw:
            st.error("No extractable text found. Consider using OCR fallback.")
        else:
            st.subheader("Extracted Text")
            st.text_area("extracted_text", value=raw, height=250)
            prompt = build_prompt(raw)
            st.info("Calling API — response may take a few seconds.")
            try:
                resp = call_api(api_key, api_base, model_name, prompt)
                st.subheader("Model response (raw)")
                st.code(resp)
                # Attempt to extract JSON using simple search for braces
                start = resp.find('{')
                end = resp.rfind('}')
                json_str = None
                if start!=-1 and end!=-1 and end>start:
                    candidate = resp[start:end+1]
                    try:
                        parsed = json.loads(candidate)
                        json_str = json.dumps(parsed, indent=2, ensure_ascii=False)
                    except Exception:
                        json_str = candidate
                if json_str:
                    st.subheader("Extracted JSON")
                    st.code(json_str)
                    try:
                        parsed = json.loads(json_str)
                        xml_bytes = dicttoxml(parsed, custom_root="InvoiceData", attr_type=False)
                        dom = xml.dom.minidom.parseString(xml_bytes.decode("utf-8"))
                        pretty_xml = dom.toprettyxml(indent="  ")
                        st.subheader("Converted XML")
                        st.code(pretty_xml)
                        st.download_button("Download XML", pretty_xml, file_name="invoice.xml", mime="application/xml")
                    except Exception as e:
                        st.warning(f"Could not convert to XML: {e}")
                else:
                    st.error("Failed to extract JSON from model response.")
            except requests.HTTPError as he:
                st.error(f"API request failed: {he}\n{getattr(he,'response',None)}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")

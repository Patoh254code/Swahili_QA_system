# ken_swa_qa_streamlit.py

import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup
import requests
import re
import json
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# =========================
# Page configuration
# =========================
st.set_page_config(page_title="KenSwaQAChat", layout="wide")
st.title("🧐 KenSwaQAChat — Swahili Question Answering System")

# =========================
# Session state
# =========================
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []
if "context" not in st.session_state:
    st.session_state.context = ""
if "source" not in st.session_state:
    st.session_state.source = "📝 Text"

# =========================
# Helper functions
# =========================
def estimate_tokens(txt: str) -> int:
    words = len(txt.split())
    return int(words * 1.2)

def extract_text_from_pdf(uploaded_file) -> str:
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(pages)
        text = re.sub(r"\s+", " ", text).strip()
        return text
    except Exception as e:
        st.error(f"⚠️ Error reading PDF: {e}")
        return ""

def fetch_url_text(url: str, timeout: int = 12) -> str:
    try:
        resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        candidates = []
        for sel in ["article", "main", "div", "section"]:
            for node in soup.select(sel):
                txt = node.get_text(separator=" ", strip=True)
                if txt and len(txt.split()) > 50:
                    candidates.append(txt)
        text = max(candidates, key=len) if candidates else soup.get_text(separator=" ", strip=True)
        return re.sub(r"\s+", " ", text).strip()
    except Exception as e:
        st.error(f"⚠️ Error reading URL: {e}")
        return ""

def df_from_history(history):
    if not history:
        return pd.DataFrame(columns=["Time", "Source", "Question", "Answer"])
    rows = [{"Time": i["time"], "Source": i["source"], "Question": i["question"], "Answer": i["answer"]} for i in history]
    return pd.DataFrame(rows)

def export_as(format_name: str, df: pd.DataFrame):
    if format_name == "CSV":
        return df.to_csv(index=False).encode("utf-8"), "qa_results.csv", "text/csv"
    if format_name == "Excel":
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as wr:
            df.to_excel(wr, index=False, sheet_name="QA")
        return buf.getvalue(), "qa_results.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if format_name == "TXT":
        txt = "\n\n".join([
            f"Time: {r['Time']}\nSource: {r['Source']}\nQuestion: {r['Question']}\nAnswer: {r['Answer']}"
            for _, r in df.iterrows()
        ])
        return txt.encode("utf-8"), "qa_results.txt", "text/plain"
    if format_name == "JSON":
        return json.dumps(st.session_state.qa_history, ensure_ascii=False, indent=2).encode("utf-8"), "qa_session.json", "application/json"
    return None, None, None

# =========================
# Load HuggingFace model
# =========================
@st.cache_resource(show_spinner=True)
def load_model():
    model_name = "Patohh254/mt5_swahili_QA"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)
    return tokenizer, model, device

tokenizer, model, device = load_model()

def chunk_text(text, max_tokens=400):
    words = text.split()
    return [" ".join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]

def answer_question(context, question):
    chunks = chunk_text(context)
    answers = []
    for chunk in chunks:
        prompt = f"muktadha: {chunk} swali: {question}"
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
        with torch.no_grad():
            output_ids = model.generate(inputs["input_ids"], max_length=64)
        answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        answers.append(answer)
    return " ".join(answers).strip()

# =========================
# Sidebar — Input & History
# =========================
st.sidebar.header("🔧 Input Options")
input_method = st.sidebar.radio("Context input method:", ["📝 Type directly", "📄 Upload PDF", "🌐 Enter URL"], index=0)

if input_method == "📄 Upload PDF":
    uploaded_pdf = st.sidebar.file_uploader("Upload PDF", type="pdf")
    if uploaded_pdf:
        text = extract_text_from_pdf(uploaded_pdf)
        if text:
            st.session_state.context = text
            st.session_state.source = "📄 PDF"
            st.sidebar.success("✅ PDF loaded!")

elif input_method == "🌐 Enter URL":
    url_input = st.sidebar.text_input("Enter Article URL")
    if st.sidebar.button("📥 Fetch URL"):
        if url_input:
            text = fetch_url_text(url_input)
            if text:
                st.session_state.context = text
                st.session_state.source = "🌐 URL"
                st.sidebar.success("✅ URL content retrieved!")
        else:
            st.sidebar.warning("Enter a valid URL.")

else:
    st.session_state.context = st.sidebar.text_area("📘 Type/Edit Context:", value=st.session_state.context, height=220)
    st.session_state.source = "📝 Text"

# Context info
if st.session_state.context:
    words = len(st.session_state.context.split())
    tokens = estimate_tokens(st.session_state.context)
    st.sidebar.info(f"🧮 Words: {words} | Estimated tokens: {tokens}")
    if tokens > 900:
        st.sidebar.warning("⚠️ Context is long. Consider shortening.")

# History management
st.sidebar.markdown("---")
if st.sidebar.button("🧹 Clear History"):
    st.session_state.qa_history = []
    st.success("History cleared.")

st.sidebar.markdown("### 💾 Download Session")
save_choice = st.sidebar.selectbox("Format:", ["CSV", "Excel", "TXT", "JSON"])
df_hist = df_from_history(st.session_state.qa_history)
data_bytes, fname, mime = export_as(save_choice, df_hist if save_choice != "JSON" else None)
if data_bytes:
    st.sidebar.download_button(f"⬇️ Download {save_choice}", data=data_bytes, file_name=fname, mime=mime)

# =========================
# Question input & answer
# =========================
st.markdown("### ❓ Ask your question")
question = st.text_input("Type your question:")

col1, col2 = st.columns([1,1])
with col1:
    ask_clicked = st.button("💬 Get Answer")
with col2:
    clear_ctx = st.button("🧽 Clear Context")

if clear_ctx:
    st.session_state.context = ""
    st.info("Context cleared.")

if ask_clicked:
    if not st.session_state.context:
        st.warning("Provide context first.")
    elif not question.strip():
        st.warning("Type a question first.")
    else:
        with st.spinner("Generating answer..."):
            answer = answer_question(st.session_state.context, question)
        st.success(f"💡 Answer: {answer}")
        st.session_state.qa_history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": st.session_state.source,
            "question": question,
            "answer": answer
        })

# =========================
# Display QA history
# =========================
st.markdown("### 📚 Question & Answer History")
if st.session_state.qa_history:
    st.dataframe(df_from_history(st.session_state.qa_history), use_container_width=True)
else:
    st.info("No history yet. Ask a question to see results.")

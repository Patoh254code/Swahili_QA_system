import streamlit as st
import requests
import pdfplumber
import pandas as pd
from io import BytesIO
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

# =========================
# Page configuration
# =========================
st.set_page_config(page_title="KenSwaQAChat", layout="wide")
st.title("🧐 KenSwaQAChat — Swahili Question Answering System")

# =========================
# Session state initialization
# =========================
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []  # list of {time, question, answer, source}

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
    if format_name == "PDF":
        try:
            from fpdf import FPDF
        except Exception:
            st.error("📦 Please install package: pip install fpdf")
            return None, None, None
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font("Arial", "", "", uni=True)
        pdf.set_font("Arial", size=12)
        for _, r in df.iterrows():
            block = f"Time: {r['Time']}\nSource: {r['Source']}\nQuestion: {r['Question']}\nAnswer: {r['Answer']}\n"
            pdf.multi_cell(0, 8, block)
            pdf.ln(2)
        out = BytesIO()
        pdf.output(out)
        return out.getvalue(), "qa_results.pdf", "application/pdf"
    if format_name == "JSON":
        return json.dumps(st.session_state.qa_history, ensure_ascii=False, indent=2).encode("utf-8"), "qa_session.json", "application/json"
    return None, None, None

# =========================
# Sidebar — Input & API
# =========================
st.sidebar.header("🔧 Input Options & API")
api_url = st.sidebar.text_input(
    "📡 API URL", 
    value="http://127.0.0.1:8000/answer"
)

input_method = st.sidebar.radio(
    "Choose context input method:",
    ["📝 Type directly", "📄 Upload PDF", "🌐 Enter URL"],
    index=0
)

# PDF Upload
if input_method == "📄 Upload PDF":
    uploaded_pdf = st.sidebar.file_uploader("Upload PDF", type="pdf")
    if uploaded_pdf:
        text = extract_text_from_pdf(uploaded_pdf)
        if text:
            st.session_state.context = text
            st.session_state.source = "📄 PDF"
            st.sidebar.success("✅ PDF successfully read!")

# URL Input
elif input_method == "🌐 Enter URL":
    url_input = st.sidebar.text_input("Enter Article URL")
    if st.sidebar.button("📥 Fetch URL Content"):
        if url_input:
            text = fetch_url_text(url_input)
            if text:
                st.session_state.context = text
                st.session_state.source = "🌐 URL"
                st.sidebar.success("✅ Content retrieved from URL!")
        else:
            st.sidebar.warning("🔎 Please enter a valid URL.")

# Type directly
else:
    st.session_state.context = st.sidebar.text_area("📘 Type/Edit Context here:", value=st.session_state.context, height=220)
    st.session_state.source = "📝 Text"

# Context info
if st.session_state.context:
    words = len(st.session_state.context.split())
    tokens = estimate_tokens(st.session_state.context)
    st.sidebar.info(f"🧮 Words: {words} | Estimated tokens: {tokens}")
    if tokens > 900:
        st.sidebar.warning("⚠️ Context is long. Shorten to avoid truncation.")

# History management
st.sidebar.markdown("---")
if st.sidebar.button("🧹 Clear History"):
    st.session_state.qa_history = []
    st.success("🧼 History cleared.")

# Save / Load session
st.sidebar.markdown("### 💾 Save & Restore Session")
save_choice = st.sidebar.selectbox("Download format:", ["CSV", "Excel", "TXT", "PDF", "JSON"])
df_hist = df_from_history(st.session_state.qa_history)
data_bytes, fname, mime = export_as(save_choice, df_hist if save_choice != "JSON" else None)
if data_bytes:
    st.sidebar.download_button(f"⬇️ Download {save_choice}", data=data_bytes, file_name=fname, mime=mime)

restore_file = st.sidebar.file_uploader("♻️ Restore session (JSON)", type=["json"])
if restore_file is not None:
    try:
        restored = json.load(restore_file)
        if isinstance(restored, list):
            st.session_state.qa_history = restored
            st.sidebar.success("✅ Session restored!")
        else:
            st.sidebar.error("File is not a list structure.")
    except Exception as e:
        st.sidebar.error(f"⚠️ Error reading JSON: {e}")

# =========================
# Question input area
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

# =========================
# API request logic
# =========================
if ask_clicked:
    if not st.session_state.context:
        st.warning("⚠️ Please provide a context first.")
    elif not question.strip():
        st.warning("⚠️ Please type a question.")
    else:
        payload = {"context": st.session_state.context, "question": question}
        try:
            resp = requests.post(api_url, json=payload, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            answer = result.get("answer", "").strip()
            st.success(f"💡 Answer: {answer if answer else '(No answer returned)'}")

            st.session_state.qa_history.append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": st.session_state.source,
                "question": question,
                "answer": answer
            })
        except requests.exceptions.HTTPError as e:
            st.error(f"⚠️ API returned an error: {e}")
        except requests.exceptions.RequestException as e:
            st.error(f"🚫 Connection error: {e}")
        except ValueError:
            st.error("⚠️ Failed to parse API response as JSON.")

# =========================
# Display QA history
# =========================
st.markdown("### 📚 Question & Answer History")
if st.session_state.qa_history:
    st.dataframe(df_from_history(st.session_state.qa_history), use_container_width=True)
else:
    st.info("No history yet. Ask a question to see results.")



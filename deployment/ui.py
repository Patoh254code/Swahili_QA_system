# import streamlit as st
# import requests
# import io
# import base64
# import zipfile
# from PyPDF2 import PdfReader

# # Streamlit UI
# st.set_page_config(page_title="Swahili QA System", page_icon="📘")
# st.title("📘 Mfumo wa Maswali na Majibu kwa Kiswahili")

# # Session state for history and feedback
# if 'history' not in st.session_state:
#     st.session_state.history = []
# if 'feedback' not in st.session_state:
#     st.session_state.feedback = []

# # Input source selector
# input_source = st.radio("Chagua chanzo cha muktadha:", ("Andika mwenyewe", "Pakia PDF"))

# # Handle different input sources
# context = ""
# if input_source == "Andika mwenyewe":
#     context = st.text_area("📘 Muktadha", height=200)
# elif input_source == "Pakia PDF":
#     uploaded_file = st.file_uploader("Pakia PDF yenye muktadha", type="pdf")
#     if uploaded_file:
#         pdf_reader = PdfReader(uploaded_file)
#         context = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
#         st.success("✅ PDF imesomwa kwa mafanikio")

# # User inputs
# question = st.text_input("❓ Swali lako hapa")

# # Answer button
# if st.button("🔍 Pata Jibu"):
#     if context and question:
#         token_count = len(context.split()) + len(question.split())
#         if token_count > 512:
#             st.warning(f"⚠️ Jumla ya maneno ni {token_count}, ambayo inaweza kuathiri utendaji wa mfano.")

#         payload = {"context": context, "question": question}
#         try:
#             response = requests.post("http://127.0.0.1:8000/answer", json=payload)
#             if response.status_code == 200:
#                 answer = response.json()["answer"]
#                 st.success(f"💡 Jibu: {answer}")

#                 # Save session history
#                 st.session_state.history.append({
#                     "context": context,
#                     "question": question,
#                     "answer": answer
#                 })
#             else:
#                 st.error("⚠️ Imeshindwa kupata jibu kutoka kwa API.")
#         except requests.exceptions.RequestException as e:
#             st.error(f"🚫 Hitilafu ya muunganisho: {e}")
#     else:
#         st.warning("Tafadhali weka muktadha na swali.")

# # Show session history
# if st.checkbox("📜 Onesha Historia ya Maswali"):
#     for idx, item in enumerate(st.session_state.history[::-1]):
#         st.markdown(f"**Swali:** {item['question']}\n\n**Jibu:** {item['answer']}")

# # Download results
# if st.session_state.history:
#     if st.button("⬇️ Pakua Majibu kama Faili"):
#         output = io.StringIO()
#         for item in st.session_state.history:
#             output.write(f"Swali: {item['question']}\nJibu: {item['answer']}\n---\n")
#         b64 = base64.b64encode(output.getvalue().encode()).decode()
#         href = f'<a href="data:file/txt;base64,{b64}" download="majibu.txt">Bonyeza hapa kupakua majibu</a>'
#         st.markdown(href, unsafe_allow_html=True)

# # Feedback collection
# if st.session_state.history:
#     st.markdown("## 🗣️ Toa Maoni")
#     feedback_text = st.text_area("Una maoni au mapendekezo gani?")
#     if st.button("📤 Tuma Maoni"):
#         if feedback_text:
#             st.session_state.feedback.append(feedback_text)
#             st.success("✅ Asante kwa maoni yako!")
#         else:
#             st.warning("⚠️ Tafadhali andika maoni kabla ya kutuma.")

# import streamlit as st
# import requests
# import pdfplumber  # Replaces fitz for PDF parsing
# import base64
# import pandas as pd
# from io import BytesIO

# st.set_page_config(page_title="Swahili QA System", layout="wide")
# st.title("🧠 Mfumo wa Kujibu Maswali kwa Kiswahili")

# # Session state initialization
# if "qa_history" not in st.session_state:
#     st.session_state.qa_history = []

# if "context" not in st.session_state:
#     st.session_state.context = ""

# # Sidebar for uploading and options
# st.sidebar.header("🔧 Chaguzi za Ingizo")
# input_method = st.sidebar.radio("Chagua njia ya kuweka muktadha:", ["📝 Andika moja kwa moja", "📄 Pakia PDF", "🌐 Weka URL"])

# # Handle PDF using pdfplumber
# def extract_text_from_pdf(uploaded_file):
#     text = ""
#     with pdfplumber.open(uploaded_file) as pdf:
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return text

# # Input options
# if input_method == "📝 Andika moja kwa moja":
#     st.session_state.context = st.text_area("📘 Andika Muktadha hapa:", height=200)
# elif input_method == "📄 Pakia PDF":
#     uploaded_pdf = st.sidebar.file_uploader("Pakia PDF", type="pdf")
#     if uploaded_pdf:
#         st.session_state.context = extract_text_from_pdf(uploaded_pdf)
#         st.success("✅ PDF imesomwa kikamilifu!")
# elif input_method == "🌐 Weka URL":
#     url_input = st.sidebar.text_input("Ingiza URL ya Makala")
#     if url_input:
#         st.warning("⚠️ Kipengele cha URL kimezimwa kwa sasa. Tafadhali tumia PDF au maandishi ya moja kwa moja.")

# # Question input
# question = st.text_input("❓ Uliza swali lako:")

# # Output format selection
# output_format = st.sidebar.selectbox("💾 Pakua matokeo kama:", ["CSV", "Excel"])

# # Submit button
# if st.button("📤 Pata Jibu"):
#     if st.session_state.context and question:
#         payload = {"context": st.session_state.context, "question": question}
#         try:
#             response = requests.post("http://127.0.0.1:8000/answer", json=payload)
#             if response.status_code == 200:
#                 result = response.json()
#                 answer = result["answer"]
#                 score = result.get("score", 0)
#                 st.success(f"💡 Jibu: {answer}")
#                 st.progress(min(int(score * 100), 100), text=f"Uhakika wa jibu: {score:.2%}")

#                 # Save to session history
#                 st.session_state.qa_history.append({
#                     "Swali": question,
#                     "Jibu": answer,
#                     "Uhakika": score
#                 })
#             else:
#                 st.error("⚠️ Imeshindikana kupata jibu kutoka kwa API.")
#         except requests.exceptions.RequestException as e:
#             st.error(f"🚫 Hitilafu ya muunganisho: {e}")
#     else:
#         st.warning("Tafadhali weka muktadha na swali.")

# # Display session history
# if st.session_state.qa_history:
#     st.subheader("📚 Historia ya Maswali na Majibu")
#     df_history = pd.DataFrame(st.session_state.qa_history)
#     st.dataframe(df_history)

#     # Downloadable link
#     def convert_df(df):
#         if output_format == "CSV":
#             return df.to_csv(index=False).encode("utf-8"), "text/csv", "qa_results.csv"
#         else:
#             buffer = BytesIO()
#             with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
#                 df.to_excel(writer, index=False)
#             return buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "qa_results.xlsx"

#     data, mime, filename = convert_df(df_history)
#     st.download_button(
#         label=f"⬇️ Pakua matokeo kama {output_format}",
#         data=data,
#         file_name=filename,
#         mime=mime
#     )

# # Feedback section
# st.sidebar.markdown("---")
# st.sidebar.subheader("💬 Maoni Yako")
# feedback = st.sidebar.text_area("Tuambie maoni yako au matatizo uliyokutana nayo:")
# if st.sidebar.button("Tuma Maoni"):
#     if feedback:
#         st.sidebar.success("✅ Asante kwa maoni yako!")
#     else:
#         st.sidebar.warning("⚠️ Tafadhali andika kitu kabla ya kutuma.")

# # Token length info
# if st.session_state.context:
#     token_count = len(st.session_state.context.split())
#     if token_count > 400:
#         st.warning(f"⚠️ Muktadha una maneno {token_count}, ambayo ni mengi. Fupisha muktadha kwa usahihi bora.")




# import streamlit as st
# import requests
# import pdfplumber
# import base64
# import pandas as pd
# from io import BytesIO

# st.set_page_config(page_title="Swahili QA System", layout="wide")
# st.title("🧐 KenSwaQAChat")

# # Session state initialization
# if "qa_history" not in st.session_state:
#     st.session_state.qa_history = []

# if "context" not in st.session_state:
#     st.session_state.context = ""

# # Sidebar for uploading and options
# st.sidebar.header("🔧 Chaguzi za Ingizo")
# input_method = st.sidebar.radio("Chagua njia ya kuweka muktadha:", ["📝 Andika moja kwa moja", "📄 Pakia PDF", "🌐 Weka URL"])

# # Handle PDF

# def extract_text_from_pdf(uploaded_file):
#     with pdfplumber.open(uploaded_file) as pdf:
#         return "\n".join([page.extract_text() or "" for page in pdf.pages])

# # Input options
# if input_method == "📝 Andika moja kwa moja":
#     st.session_state.context = st.text_area("📘 Andika Muktadha hapa:", height=200)
# elif input_method == "📄 Pakia PDF":
#     uploaded_pdf = st.sidebar.file_uploader("Pakia PDF", type="pdf")
#     if uploaded_pdf:
#         st.session_state.context = extract_text_from_pdf(uploaded_pdf)
#         st.success("✅ PDF imesomwa kikamilifu!")
# elif input_method == "🌐 Weka URL":
#     url_input = st.sidebar.text_input("Ingiza URL ya Makala")
#     if url_input:
#         st.warning("⚠️ Kipengele cha URL kimezimwa kwa sasa. Tafadhali tumia PDF au maandishi ya moja kwa moja.")

# # Question input
# question = st.text_input("❓ Uliza swali lako:")

# # Output format selection
# output_format = st.sidebar.selectbox("📂 Pakua matokeo kama:", ["CSV", "Excel", "TXT", "PDF"])

# # Submit button
# if st.button("📄 Pata Jibu"):
#     if st.session_state.context and question:
#         payload = {"context": st.session_state.context, "question": question}
#         try:
#             response = requests.post("http://127.0.0.1:8000/answer", json=payload)
#             if response.status_code == 200:
#                 result = response.json()
#                 answer = result["answer"]
#                 score = result.get("score", 0)
#                 st.success(f"💡 Jibu: {answer}")
#                 st.progress(min(int(score * 100), 100), text=f"Uhakika wa jibu: {score:.2%}")

#                 # Save to session history
#                 st.session_state.qa_history.append({
#                     "Swali": question,
#                     "Jibu": answer,
#                     "Uhakika": score
#                 })
#             else:
#                 st.error("⚠️ Imeshindikana kupata jibu kutoka kwa API.")
#         except requests.exceptions.RequestException as e:
#             st.error(f"🚘 Hitilafu ya muunganisho: {e}")
#     else:
#         st.warning("Tafadhali weka muktadha na swali.")

# # Display session history
# if st.session_state.qa_history:
#     st.subheader("📚 Historia ya Maswali na Majibu")
#     df_history = pd.DataFrame(st.session_state.qa_history)
#     st.dataframe(df_history)

#     # Downloadable link
#     def convert_df(df):
#         if output_format == "CSV":
#             return df.to_csv(index=False).encode("utf-8"), "text/csv", "qa_results.csv"
#         elif output_format == "Excel":
#             buffer = BytesIO()
#             with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
#                 df.to_excel(writer, index=False)
#             return buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "qa_results.xlsx"
#         elif output_format == "TXT":
#             text_data = "\n".join([f"Swali: {row['Swali']}\nJibu: {row['Jibu']}\nUhakika: {row['Uhakika']:.2%}\n" for _, row in df.iterrows()])
#             return text_data.encode("utf-8"), "text/plain", "qa_results.txt"
#         elif output_format == "PDF":
#             from fpdf import FPDF
#             pdf = FPDF()
#             pdf.add_page()
#             pdf.set_auto_page_break(auto=True, margin=15)
#             pdf.set_font("Arial", size=12)
#             for _, row in df.iterrows():
#                 pdf.multi_cell(0, 10, f"Swali: {row['Swali']}\nJibu: {row['Jibu']}\nUhakika: {row['Uhakika']:.2%}\n")
#             buffer = BytesIO()
#             pdf.output(buffer)
#             return buffer.getvalue(), "application/pdf", "qa_results.pdf"

#     data, mime, filename = convert_df(df_history)
#     st.download_button(
#         label=f"⬇️ Pakua matokeo kama {output_format}",
#         data=data,
#         file_name=filename,
#         mime=mime
#     )

# # Feedback section
# st.sidebar.markdown("---")
# st.sidebar.subheader("💬 Maoni Yako")
# feedback = st.sidebar.text_area("Tuambie maoni yako au matatizo uliyokutana nayo:")
# if st.sidebar.button("Tuma Maoni"):
#     if feedback:
#         st.sidebar.success("✅ Asante kwa maoni yako!")
#     else:
#         st.sidebar.warning("⚠️ Tafadhali andika kitu kabla ya kutuma.")

# # Token length info
# if st.session_state.context:
#     token_count = len(st.session_state.context.split())
#     if token_count > 400:
#         st.warning(f"⚠️ Muktadha una maneno {token_count}, ambayo ni mengi. Fupisha muktadha kwa usahihi bora.")

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
    """Roughly estimate token count from text."""
    words = len(txt.split())
    return int(words * 1.2)

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract text from uploaded PDF."""
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
    """Fetch and clean main content from a webpage."""
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
        text = re.sub(r"\s+", " ", text).strip()
        return text
    except Exception as e:
        st.error(f"⚠️ Error reading URL: {e}")
        return ""

def df_from_history(history):
    """Convert stored history to DataFrame."""
    if not history:
        return pd.DataFrame(columns=["Time", "Source", "Question", "Answer"])
    rows = []
    for item in history:
        rows.append({
            "Time": item.get("time"),
            "Source": item.get("source"),
            "Question": item.get("question"),
            "Answer": item.get("answer"),
        })
    return pd.DataFrame(rows)

def export_as(format_name: str, df: pd.DataFrame):
    """Export QA history in various formats."""
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
# Sidebar — Input & API settings
# =========================
st.sidebar.header("🔧 Input Options & API")

api_url = st.sidebar.text_input("📡 API URL", value="https://huggingface.co/spaces/Patohh254/kenswaqachat-api")
input_method = st.sidebar.radio(
    "Choose context input method:",
    ["📝 Type directly", "📄 Upload PDF", "🌐 Enter URL"],
    index=0
)

# Upload PDF
if input_method == "📄 Upload PDF":
    uploaded_pdf = st.sidebar.file_uploader("Upload PDF", type="pdf")
    if uploaded_pdf:
        text = extract_text_from_pdf(uploaded_pdf)
        if text:
            st.session_state.context = text
            st.session_state.source = "📄 PDF"
            st.sidebar.success("✅ PDF successfully read!")

# Enter URL
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

# Word/token length info
if st.session_state.context:
    words = len(st.session_state.context.split())
    tokens = estimate_tokens(st.session_state.context)
    st.sidebar.info(f"🧮 Words: {words} | Estimated tokens: {tokens}")
    if tokens > 900:
        st.sidebar.warning("⚠️ Context is too long. Shorten it to avoid truncation.")

# History management
st.sidebar.markdown("---")
if st.sidebar.button("🧹 Clear History"):
    st.session_state.qa_history = []
    st.success("🧼 History cleared.")

# Save / Load session
st.sidebar.markdown("### 💾 Save & Restore Session")
save_choice = st.sidebar.selectbox("Choose download format:", ["CSV", "Excel", "TXT", "PDF", "JSON"])
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

col1, col2 = st.columns([1, 1])
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
            if resp.status_code == 200:
                result = resp.json()
                answer = result.get("answer", "").strip()
                st.success(f"💡 Answer: {answer if answer else '(No answer returned)'}")

                st.session_state.qa_history.append({
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source": st.session_state.source,
                    "question": question,
                    "answer": answer
                })
            else:
                st.error(f"⚠️ Failed to get answer from API. Status code: {resp.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"🚫 Connection error: {e}")
            
# =========================
# Display question-answer history
# =========================
st.markdown("### 📚 Question & Answer History")
if st.session_state.qa_history:
    df_view = df_from_history(st.session_state.qa_history)
    st.dataframe(df_view, use_container_width=True)
else:
    st.info("No history yet. Ask a question to see results.")


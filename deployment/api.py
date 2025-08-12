# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# import torch
# import os

# # ========================
# # MODEL LOADING
# # ========================
# model_dir = "mt5-swahili-qa"
# if not os.path.exists(model_dir):
#     raise FileNotFoundError(f"Model directory '{model_dir}' not found. Please run unzip_model.py first.")

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# tokenizer = AutoTokenizer.from_pretrained(model_dir)
# model = AutoModelForSeq2SeqLM.from_pretrained(model_dir).to(device)

# app = FastAPI(title="Swahili QA API", description="Answer Swahili questions from context, PDF or URL")

# # ========================
# # REQUEST BODY
# # ========================
# class QARequest(BaseModel):
#     context: str
#     question: str

# # ========================
# # CHUNKING FUNCTION
# # ========================
# def chunk_text(text, max_tokens=400):
#     words = text.split()
#     chunks = [" ".join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]
#     return chunks

# # ========================
# # API ENDPOINT
# # ========================
# @app.post("/answer")
# def answer_question(request: QARequest):
#     try:
#         chunks = chunk_text(request.context)
#         answers = []
#         for chunk in chunks:
#             prompt = f"muktadha: {chunk} swali: {request.question}"
#             inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
#             with torch.no_grad():
#                 output_ids = model.generate(inputs["input_ids"], max_length=64)
#             answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)
#             answers.append(answer)
#         final_answer = " ".join(answers)
#         return {"answer": final_answer}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/")
# def root():
#     return {"message": "Swahili QA API is running"}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os
from huggingface_hub import hf_hub_download

# ========================
# CONFIGURATION
# ========================
HF_REPO_ID = "Patohh254/mt5_swahili_QA"  # Change if your repo name is different
MODEL_FILENAME = None  # If using standard HF model format, keep None

# ========================
# MODEL LOADING
# ========================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Download model from Hugging Face if not cached
if MODEL_FILENAME:
    model_path = hf_hub_download(repo_id=HF_REPO_ID, filename=MODEL_FILENAME)
else:
    model_path = HF_REPO_ID  # Transformers can load directly from repo

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(device)

app = FastAPI(title="Swahili QA API", description="Answer Swahili questions from context, PDF or URL")

# ========================
# REQUEST BODY
# ========================
class QARequest(BaseModel):
    context: str
    question: str

# ========================
# CHUNKING FUNCTION
# ========================
def chunk_text(text, max_tokens=400):
    words = text.split()
    chunks = [" ".join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]
    return chunks

# ========================
# API ENDPOINT
# ========================
@app.post("/answer")
def answer_question(request: QARequest):
    try:
        chunks = chunk_text(request.context)
        answers = []
        for chunk in chunks:
            prompt = f"muktadha: {chunk} swali: {request.question}"
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
            with torch.no_grad():
                output_ids = model.generate(inputs["input_ids"], max_length=64)
            answer = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            answers.append(answer)
        final_answer = " ".join(answers)
        return {"answer": final_answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Swahili QA API is running"}


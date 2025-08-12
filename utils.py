import re
import ast
import pandas as pd
import evaluate
import numpy as np
from sklearn.model_selection import GroupShuffleSplit
from bert_score import score as bert_score
from transformers import AutoTokenizer



# Function to extract the answer text from the 'text' key with array format
def extract_answer(s):

    try:
        # Fix the array format: remove NumPy-style wrapper
        s = re.sub(r"array\(\[([^\]]+)\],\s*dtype=object\)", r"\1", s)
        
        # Convert to dictionary
        answer_dict = ast.literal_eval(s)

        # Return the value under 'text', cleaned of quotes/spaces
        return str(answer_dict['text']).strip().strip("'").strip('"')
    except:

        # If something goes wrong, return original
        return s  
    

# Simple lexical overlap function
def lexical_overlap(q, c):
    q_tokens = set(str(q).lower().split())
    c_tokens = set(str(c).lower().split())
    if len(q_tokens) == 0:
        return 0
    return len(q_tokens & c_tokens) / len(q_tokens)


# Function to clean_text
def clean_text(text):
    text = str(text)
    # Remove repeated punctuation (e.g., "......", "!!!", "***")
    text = re.sub(r"[\.\*\!@#\$\%\^\&\*]{2,}", "", text)
    # Remove stray non-word characters (except .,?,!)
    text = re.sub(r"[^\w\s\.,!?]", "", text)
    # Normalize multiple spaces to one
    text = re.sub(r"\s+", " ", text)
    # Strip leading/trailing whitespace
    return text.strip()


# Chunk and preprocess the dataset
def chunk_text(text, max_words=200):
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]


def preprocess_and_chunk(df):
    new_rows = []
    for _, row in df.iterrows():
        context_chunks = chunk_text(row['context'])
        for chunk in context_chunks:
            new_rows.append({
                'Story_ID': row['Story_ID'],
                'context': chunk,
                'question': row['question'],
                'answers': row['answers']
            })
    return pd.DataFrame(new_rows)


# Split for training, validation and testing based on unique story IDs
def group_split(df, group_col='Story_ID'):
    splitter = GroupShuffleSplit(train_size=0.8, test_size=0.2, random_state=42)
    train_idx, test_idx = next(splitter.split(df, groups=df[group_col]))
    train_val_df = df.iloc[train_idx]
    test_df = df.iloc[test_idx]

    val_splitter = GroupShuffleSplit(train_size=0.875, test_size=0.125, random_state=42)
    train_idx, val_idx = next(val_splitter.split(train_val_df, groups=train_val_df[group_col]))
    train_df = train_val_df.iloc[train_idx]
    val_df = train_val_df.iloc[val_idx]

    return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)


# Instantiate the tokenizer
tokenizer = None
try:
    model_ckpt = "google/mt5-small"
    tokenizer = AutoTokenizer.from_pretrained(model_ckpt, use_fast=False)
except ImportError as e:
    print("")


# tokenize the split data
def convert_to_features(example):
    input_text = f"question: {example['question']} context: {example['context']}"
    model_inputs = tokenizer(input_text, max_length=512, truncation=True)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(example['answers'], max_length=64, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


# Function to compute the relevant metrics
def compute_metrics(eval_preds):
    # Load ROUGE metric
    rouge_metric = evaluate.load("rouge")

    preds, labels = eval_preds

    # Ensure numpy arrays
    preds = np.asarray(preds, dtype=np.int32)
    labels = np.asarray(labels, dtype=np.int32)

    # Clip predictions to valid vocab range
    preds = np.clip(preds, 0, tokenizer.vocab_size - 1)

    # Replace -100 in labels with pad_token_id for decoding
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)

    # Decode predictions and labels to strings
    decoded_preds = tokenizer.batch_decode(preds.tolist(), skip_special_tokens=True)
    decoded_labels = tokenizer.batch_decode(labels.tolist(), skip_special_tokens=True)

    # --- ROUGE ---
    rouge_results = rouge_metric.compute(predictions=decoded_preds,
                                         references=decoded_labels,
                                         use_stemmer=True)

    # --- BERTScore ---
    P, R, F1 = bert_score(decoded_preds, decoded_labels,
                          lang="sw",
                          model_type="xlm-roberta-base",
                          verbose=False)

    # --- Semantic Accuracy ---
    semantic_accuracy = np.mean((F1.numpy() >= 0.8).astype(float))

    # --- String Exact Match (strict) ---
    string_em = np.mean([pred.strip().lower() == ref.strip().lower()
                         for pred, ref in zip(decoded_preds, decoded_labels)])

    return {
        "rouge1": round(rouge_results["rouge1"], 4),
        "rougeL": round(rouge_results["rougeL"], 4),
        "bert_precision": round(P.mean().item(), 4),
        "bert_recall": round(R.mean().item(), 4),
        "bert_f1": round(F1.mean().item(), 4),
        "semantic_accuracy": round(semantic_accuracy, 4),
        "string_exact_match": round(string_em, 4)  # strict string match
    }
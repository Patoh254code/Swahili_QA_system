# 🧠 **Swahili Question Answering with mT5**

## 📌 **1.0 Overview**

This project fine-tunes the multilingual transformer model mT5-small for the task of sequence to sequence question answering in Swahili. The goal is to build a robust QA system that can accurately provide answers to natural-language questions using Swahili context passages. This initiative supports the advancement of NLP tools in underrepresented African languages, helping make intelligent systems more inclusive.

## 🏢 **2.0 Business and Data Understanding**

### 🎯 **2.1 Stakeholder Audience**

Our key stakeholders include:
- Educational organizations and NGOs promoting Swahili-language accessibility.
- Developers and researchers working on low-resource NLP applications.
- Technology companies aiming to deploy intelligent assistants and chatbots in East African markets.

The project supports real-world use cases like:
- Virtual tutoring systems in Swahili.
- Customer support bots.
- Government service chat systems that can operate in local languages.

### 📊  **2.2 Dataset Choice**

We use the KenSwQuAD dataset: https://huggingface.co/datasets/lightblue/KenSwQuAD with the following features adapted for Swahili, consisting of:

- `Story_ID`: unique identifier for different stories
- `context`: paragraph of text.
- `question`: natural-language inquiry related to the context.
- `answers`: a span extracted directly from the context.

### 📊 **2.3 Data Distribution Visualization**

- Distribution of Swahili linguitic patterns

![WordCloud](images/wordcloud.png)

- Relationship between questions and context

![Lexical Overlap](images/lex_overlap.png)

Data preprocessing ensures:

- Cleaning and Chunking of the text.
- Tokenization using mT5-compatible tokenizer with truncation and padding.
- Dataset splits into training, testing and validation subsets through group splitting.

## 🧪 **3.0 Modeling**

###  ⚙️ **3.1 Approach**

- Model: `mT5-small`
- Tokenization: Truncation and padding handled by `AutoTokenizer`
- Task: Sequence-to-sequence training (input = context + question, output = answer)
- Trainer: Hugging Face `Seq2SeqTrainer`

### 🔧 **3.2 Training Configuration**

| Parameter      | Value       |
|----------------|-------------|
| Epochs         | 4           |
| Learning Rate  | 2e-4        |
| Batch Size     | 4           |
| Early Stopping | Enabled     |
| Weight Decay   | 0.01        |

The model is trained on Swahili QA pairs using both context and question as input and predicting the answer text.

## 📈 **4.0 Evaluation**

The fine-tuned model is evaluated using both automatic and semantic metrics:


| Metric              | Explanation|
|---------------------|------------|
| ROUGE-1 / ROUGE-L   | Measures n-gram overlap between predicted and reference answers. |
| BERTScore (P/R/F1)  | Measures semantic similarity using contextual embeddings, ideal for QA tasks.|

### 🔍 **4.1 Results**

| Metric          | Baseline (mT5) | Fine-tuned mT5 |
|-----------------|----------------|----------------|
| ROUGE-1         |	0.0103         | 0.1487         |
| ROUGE-L         |	0.0102         | 0.1486         |
| BERT Precision  | 0.7439         | 0.8347         |
| BERT Recall     | 0.7912         | 0.8282         |
| BERT F1         |	0.7664         | 0.8310         |
| Validation Loss |	22.6045        | 3.3745         |

### 🧵 **4.2 Metric Comparison Chart**

![Bert Score](images/bert_score.png)

![Rouge Score](images/rouge.png)

These improvements demonstrate the effectiveness of fine-tuning mT5 for Swahili question answering tasks.

## ✅ **5.0 Conclusion**

This project successfully demonstrates that multilingual models like mT5-small can be fine-tuned to perform competitively on sequence to sequence question answering tasks in Swahili—a low-resource language.

### ✔️ Key Takeaways:

- mT5 shows significant performance gains after fine-tuning.
- The model generalizes reasonably well, especially on unseen Swahili QA examples.
- Evaluation metrics indicate both lexical and semantic improvements over the baseline.

### 🔮 Future Work:

- Experiment with larger variants like mT5-base.
- Improve the data quality to include more long structered answers 



🎯 AI Interview Preparation Assistant

An AI-powered interview preparation tool that generates role-specific
questions, evaluates your answers using NLP, and gives you a detailed
confidence score — completely offline, no API keys needed.

🚀 What Makes This Different

Most interview prep tools just show you questions.
This tool **evaluates your answers** like a real interviewer would —
checking relevance, completeness, clarity, and confidence
using Natural Language Processing built from scratch.

✨ Features

|  Feature                  | Description |

| 📝 Question Generator   | 200+ questions across 5 roles and 3 difficulty levels |
| 🤖 Answer Evaluator     | NLP scoring using TF-IDF + Cosine Similarity |
| 🎯 Relevance Score      | Measures how well your answer matches the topic |
| 📚 Completeness Score   | Checks if key concepts are covered |
| ✍️ Clarity Score        | Analyzes sentence structure and word count |
| 💪 Confidence Score     | Detects filler words and hedging language |
| 💡 Recommendations      | Personalized tips to improve each answer |
| 📊 Session History      | Track your progress across multiple sessions |

🎓 Supported Roles

👨‍💼 **Data Analyst** — SQL, Excel, Statistics, Python
🐍 **Python Developer** — Core Python, OOP, Web/API
🤖 **ML Engineer** — ML Concepts, Deep Learning, MLOps
⚙️ **Backend Developer** — Concepts, System Design

🛠️ Tech Stack

Language    →  Python 3.12
UI          →  Streamlit
NLP         →  TF-IDF + Cosine Similarity (built from scratch)
Data        →  JSON datasets (200+ questions)
Storage     →  JSON-based session persistence

🧠 How the NLP Works

No ChatGPT. No external APIs. Pure mathematics.

Tokenization      →  splits your answer into meaningful words
TF-IDF Vectors    →  converts words into numerical representation
Cosine Similarity →  measures angle between your answer and ideal answer
Keyword Matching  →  checks for must-have technical terms
Filler Detection  →  finds "um, uh, basically, like, I think..."

The closer your answer vector is to the ideal answer vector,
the higher your relevance score

📦 Installation & Setup

1. Clone the repository
git clone https://github.com/eshna-ds/AI-Interview-Preparation-Assistant

2. Navigate to project folder
cd AI-Interview-Preparation-Assistant

3. Install dependencies
pip install -r requirements.txt

4. Run the application
streamlit run app.py

Open **http://localhost:8501** in your browser. That's it! ✅

📊 Scoring Formula

Overall Score = Relevance × 35%   (TF-IDF cosine similarity)
                Completeness   × 30%   (key concept coverage)
                Clarity        × 20%   (structure and word analysis)
                Confidence     × 15%   (filler word detection)









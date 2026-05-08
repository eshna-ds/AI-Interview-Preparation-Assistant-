"""
AI Interview Preparation Assistant
====================================
Main Streamlit Application
Run with: streamlit run app.py
"""

import streamlit as st
import json
import sys
import os
import random

sys.path.insert(0, os.path.dirname(__file__))

from utils.question_generator import (
    get_available_roles, get_available_levels,
    get_available_topics, generate_questions
)
from utils.evaluator import evaluate_answer
from utils.session_manager import InterviewSession, list_sessions

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Interview Prep",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }

    .score-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-top: 4px solid;
    }

    .score-high { border-color: #10b981; }
    .score-mid  { border-color: #f59e0b; }
    .score-low  { border-color: #ef4444; }

    .question-box {
        background: linear-gradient(135deg, #f0f4ff, #e8eeff);
        border-left: 5px solid #667eea;
        padding: 1.5rem;
        border-radius: 0 12px 12px 0;
        margin: 1rem 0;
        font-size: 1.1rem;
        font-weight: 500;
    }

    .recommendation-item {
        background: #f8fafc;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #667eea;
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }

    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Load Answer References
# ──────────────────────────────────────────────
@st.cache_data
def load_answer_refs():
    ref_path = os.path.join(os.path.dirname(__file__), 'data', 'answer_references.py')
    with open(ref_path) as f:
        return json.load(f)


ANSWER_REFS = load_answer_refs()


def get_question_data(question: str) -> dict:
    """Get reference data for a question, or generate generic one."""
    if question in ANSWER_REFS:
        return ANSWER_REFS[question]
    # Generic fallback using question words
    words = question.lower().replace("?", "").split()
    keywords = [w for w in words if len(w) > 4][:8]
    return {
        "keywords": keywords,
        "ideal_answer": f"A complete answer about {question.lower().replace('?','')}",
        "key_concepts": keywords[:3]
    }


# ──────────────────────────────────────────────
# Session State
# ──────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "home",
        "session": None,
        "questions": [],
        "current_q": 0,
        "evaluations": [],
        "role": None,
        "level": None,
        "topic": None,
        "answer_submitted": False,
        "last_eval": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_state()


# ──────────────────────────────────────────────
# Sidebar Navigation
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 Interview Prep")
    st.markdown("---")

    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

    if st.button("🚀 Start Interview", use_container_width=True):
        st.session_state.page = "setup"
        st.rerun()

    if st.button("📊 Past Sessions", use_container_width=True):
        st.session_state.page = "history"
        st.rerun()

    if st.button("📖 Study Tips", use_container_width=True):
        st.session_state.page = "tips"
        st.rerun()

    st.markdown("---")
    st.markdown("### 📈 Quick Stats")

    sessions = list_sessions()
    if sessions:
        avg_scores = [s["score"] for s in sessions if isinstance(s["score"], (int, float))]
        if avg_scores:
            st.metric("Sessions Completed", len(sessions))
            st.metric("Average Score", f"{sum(avg_scores)/len(avg_scores):.1f}/10")
    else:
        st.info("No sessions yet. Start your first interview!")


# ──────────────────────────────────────────────
# Pages
# ──────────────────────────────────────────────

def page_home():
    st.markdown("""
    <div class='main-header'>
        <h1>🎯 AI Interview Preparation Assistant</h1>
        <p style='font-size:1.1rem; opacity:0.9'>
            Practice interviews • Get AI feedback • Track your progress
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📝 Generate Questions")
        st.write("Pick your role, difficulty level, and topic to get personalized interview questions.")

    with col2:
        st.markdown("### 🤖 AI Evaluation")
        st.write("Type your answer and get instant scores on relevance, clarity, completeness, and confidence.")

    with col3:
        st.markdown("### 📊 Track Progress")
        st.write("Review your performance history and get targeted recommendations to improve.")

    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🎓 Supported Roles")
        roles = get_available_roles()
        for role in roles:
            st.markdown(f"- **{role}**")

    with col2:
        st.markdown("### 🎯 Features")
        st.markdown("""
        - ✅ 200+ interview questions
        - ✅ NLP-based answer scoring
        - ✅ Confidence estimation
        - ✅ Keyword gap analysis
        - ✅ Personalized recommendations
        - ✅ Session history
        """)

    st.markdown("---")
    if st.button("🚀 Start Practicing Now!", type="primary", use_container_width=True):
        st.session_state.page = "setup"
        st.rerun()


def page_setup():
    st.markdown("## ⚙️ Configure Your Interview Session")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        roles = get_available_roles()
        role = st.selectbox("👤 Select Role", roles)

    with col2:
        levels = get_available_levels(role)
        level = st.selectbox("🎯 Difficulty Level", levels)

    with col3:
        topics = ["All"] + get_available_topics(role, level)
        topic = st.selectbox("📚 Topic", topics)

    num_questions = st.slider("Number of Questions", min_value=3, max_value=10, value=5)

    st.markdown("---")

    if st.button("🎯 Generate Questions & Start", type="primary", use_container_width=True):
        questions = generate_questions(role, level,
                                       "All" if topic == "All" else topic,
                                       count=num_questions)

        session = InterviewSession(role, level, topic)
        for q in questions:
            session.add_question(q)

        st.session_state.session = session
        st.session_state.questions = questions
        st.session_state.current_q = 0
        st.session_state.evaluations = []
        st.session_state.role = role
        st.session_state.level = level
        st.session_state.topic = topic
        st.session_state.answer_submitted = False
        st.session_state.last_eval = None
        st.session_state.page = "interview"
        st.rerun()

    # Preview sample questions
    if st.button("👀 Preview Sample Questions"):
        sample = generate_questions(role, level,
                                    "All" if topic == "All" else topic,
                                    count=3)
        st.markdown("### Sample Questions:")
        for i, q in enumerate(sample, 1):
            st.markdown(f"**Q{i}.** {q}")


def page_interview():
    questions = st.session_state.questions
    current = st.session_state.current_q
    session: InterviewSession = st.session_state.session

    if current >= len(questions):
        st.session_state.page = "results"
        st.rerun()
        return

    # Header
    progress = current / len(questions)
    st.markdown(f"### 📝 Interview — {st.session_state.role} | {st.session_state.level}")
    st.progress(progress, text=f"Question {current + 1} of {len(questions)}")
    st.markdown("---")

    # Question
    question = questions[current]
    st.markdown(f"""
    <div class='question-box'>
        <span style='color:#667eea; font-size:0.9rem; font-weight:700; letter-spacing:0.1em'>
            QUESTION {current + 1}
        </span><br><br>
        {question}
    </div>
    """, unsafe_allow_html=True)

    # If answer already submitted, show evaluation
    if st.session_state.answer_submitted and st.session_state.last_eval:
        eval_result = st.session_state.last_eval
        show_evaluation(eval_result)

        col1, col2 = st.columns(2)
        with col1:
            if current + 1 < len(questions):
                if st.button("➡️ Next Question", type="primary", use_container_width=True):
                    st.session_state.current_q += 1
                    st.session_state.answer_submitted = False
                    st.session_state.last_eval = None
                    st.rerun()
            else:
                if st.button("🏁 Finish Interview", type="primary", use_container_width=True):
                    session.completed = True
                    session.save()
                    st.session_state.page = "results"
                    st.rerun()
        with col2:
            if st.button("⏭️ Skip to Results", use_container_width=True):
                session.completed = True
                session.save()
                st.session_state.page = "results"
                st.rerun()
        return

    # Answer input
    st.markdown("### ✍️ Your Answer")
    user_answer = st.text_area(
        "Type your answer here...",
        height=150,
        placeholder="Write a clear, concise answer. Aim for 50-100 words with specific technical terms.",
        key=f"answer_{current}"
    )

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        if st.button("✅ Submit Answer", type="primary", use_container_width=True):
            if not user_answer.strip():
                st.warning("Please write an answer before submitting.")
            else:
                question_data = get_question_data(question)
                with st.spinner("🤖 Evaluating your answer..."):
                    eval_result = evaluate_answer(question, user_answer, question_data)

                session.record_answer(question, user_answer, eval_result)
                st.session_state.evaluations.append(eval_result)
                st.session_state.answer_submitted = True
                st.session_state.last_eval = eval_result
                st.rerun()

    with col2:
        if st.button("💡 Show Hint", use_container_width=True):
            q_data = get_question_data(question)
            keywords = q_data.get("keywords", [])
            if keywords:
                st.info(f"**Key concepts to mention:** {', '.join(keywords[:5])}")

    with col3:
        if st.button("⏭️ Skip Question", use_container_width=True):
            st.session_state.current_q += 1
            st.session_state.answer_submitted = False
            st.session_state.last_eval = None
            st.rerun()


def show_evaluation(eval_result: dict):
    """Display the evaluation results in a nice layout."""
    st.markdown("### 📊 Evaluation Results")

    # Score cards
    col1, col2, col3, col4, col5 = st.columns(5)
    scores = {
        "Overall": eval_result["overall_score"],
        "Relevance": eval_result["relevance"]["score"],
        "Complete": eval_result["completeness"]["score"],
        "Clarity": eval_result["clarity"]["score"],
        "Confidence": eval_result["confidence"]["score"]
    }

    for col, (label, score) in zip([col1, col2, col3, col4, col5], scores.items()):
        cls = "score-high" if score >= 7 else "score-mid" if score >= 5 else "score-low"
        color = "#10b981" if score >= 7 else "#f59e0b" if score >= 5 else "#ef4444"
        with col:
            st.markdown(f"""
            <div class='score-card {cls}'>
                <div class='metric-label'>{label}</div>
                <div class='metric-value' style='color:{color}'>{score}</div>
                <div style='color:#9ca3af; font-size:0.75rem'>/ 10</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # Details
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔑 Keyword Analysis")
        matched = eval_result["relevance"].get("matched_keywords", [])
        missing = eval_result["relevance"].get("missing_keywords", [])

        if matched:
            st.success(f"✅ Covered: {', '.join(matched[:6])}")
        if missing:
            st.error(f"❌ Missing: {', '.join(missing[:6])}")

        st.markdown("#### 📚 Concept Coverage")
        covered = eval_result["completeness"].get("covered_concepts", [])
        missing_c = eval_result["completeness"].get("missing_concepts", [])

        for c in covered:
            st.markdown(f"✅ {c}")
        for c in missing_c:
            st.markdown(f"❌ {c}")

    with col2:
        st.markdown("#### 🎯 Recommendations")
        for rec in eval_result.get("recommendations", []):
            st.markdown(f"""
            <div class='recommendation-item'>{rec}</div>
            """, unsafe_allow_html=True)

    # Ideal answer (collapsed)
    with st.expander("📖 View Ideal Answer"):
        st.info(eval_result.get("ideal_answer", "No reference answer available."))


def page_results():
    session: InterviewSession = st.session_state.session

    if not session:
        st.error("No session found.")
        return

    summary = session.get_summary()

    st.markdown("## 🏁 Interview Complete!")
    st.markdown("---")

    # Grade banner
    grade = summary.get("performance_grade", "N/A")
    avg = summary.get("average_overall", 0)
    color = "#10b981" if avg >= 7 else "#f59e0b" if avg >= 5 else "#ef4444"

    st.markdown(f"""
    <div style='text-align:center; padding:2rem; background:linear-gradient(135deg, #f0f4ff, #e8eeff);
                border-radius:12px; margin-bottom:2rem;'>
        <h2 style='color:{color}; margin:0'>Grade: {grade}</h2>
        <p style='font-size:1.2rem; color:#374151; margin-top:0.5rem'>
            Average Score: <strong>{avg}/10</strong> across {summary.get('questions_attempted',0)} questions
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Score breakdown
    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("Avg Relevance", summary.get("average_relevance", 0)),
        ("Avg Completeness", summary.get("average_completeness", 0)),
        ("Avg Clarity", summary.get("average_clarity", 0)),
        ("Avg Confidence", summary.get("average_confidence", 0))
    ]

    for col, (label, val) in zip([col1, col2, col3, col4], metrics):
        with col:
            color = "#10b981" if val >= 7 else "#f59e0b" if val >= 5 else "#ef4444"
            st.markdown(f"""
            <div class='score-card' style='border-top-color:{color}'>
                <div class='metric-label'>{label}</div>
                <div class='metric-value' style='color:{color}'>{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # Topics to revise
    topics_to_revise = summary.get("topics_to_revise", [])
    if topics_to_revise:
        st.markdown("### 📚 Topics to Revise")
        cols = st.columns(min(3, len(topics_to_revise)))
        for i, topic in enumerate(topics_to_revise[:6]):
            with cols[i % 3]:
                st.warning(f"📖 {topic}")

    # Per-question breakdown
    st.markdown("### 📋 Question-by-Question Breakdown")
    for i, ans in enumerate(session.answers):
        score = ans["evaluation"]["overall_score"]
        icon = "✅" if score >= 7 else "⚠️" if score >= 5 else "❌"
        with st.expander(f"{icon} Q{i+1}: {ans['question'][:70]}... | Score: {score}/10"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Your Answer:**")
                st.info(ans["answer"])
            with col2:
                st.markdown("**Scores:**")
                ev = ans["evaluation"]
                st.write(f"- Relevance: {ev['relevance']['score']}/10")
                st.write(f"- Completeness: {ev['completeness']['score']}/10")
                st.write(f"- Clarity: {ev['clarity']['score']}/10")
                st.write(f"- Confidence: {ev['confidence']['score']}/10")
                st.markdown("**Recommendations:**")
                for rec in ev.get("recommendations", [])[:3]:
                    st.markdown(f"- {rec}")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Start New Session", type="primary", use_container_width=True):
            st.session_state.page = "setup"
            st.rerun()
    with col2:
        if st.button("🏠 Go Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()


def page_history():
    st.markdown("## 📊 Session History")
    sessions = list_sessions()

    if not sessions:
        st.info("No sessions yet. Start your first interview!")
        if st.button("🚀 Start Interview"):
            st.session_state.page = "setup"
            st.rerun()
        return

    for s in sessions:
        score = s["score"]
        color = "🟢" if isinstance(score, float) and score >= 7 else "🟡" if isinstance(score, float) and score >= 5 else "🔴"
        st.markdown(f"""
        **{color} {s['date']}** — {s['role']} | {s['level']} | {s['topic']}
        — Score: **{score}/10**
        """)
    st.markdown("---")
    st.info("💡 Keep practicing! Aim to improve your score by 0.5 points each session.")


def page_tips():
    st.markdown("## 📖 Interview Study Tips")
    st.markdown("---")

    tips = {
        "🎯 Answer Structure": [
            "Use the **STAR method** for behavioral questions: Situation, Task, Action, Result",
            "For technical questions, define the term, explain how it works, then give an example",
            "Aim for 50-100 words per answer — concise but complete"
        ],
        "🔑 Keywords Matter": [
            "Always use technical terminology specific to your role",
            "Interviewers scan for keywords — use them naturally",
            "Don't just define — explain WHY it matters"
        ],
        "💡 Common Mistakes": [
            "Giving vague answers without specific examples",
            "Using too many filler words (um, uh, basically, like)",
            "Memorizing answers word-for-word — sounds robotic"
        ],
        "📚 Study Strategy": [
            "Practice the same questions multiple times — improvement takes repetition",
            "Record yourself speaking answers out loud",
            "Review the 'missing keywords' from your evaluations regularly"
        ]
    }

    for section, items in tips.items():
        st.markdown(f"### {section}")
        for item in items:
            st.markdown(f"- {item}")
        st.markdown("")


# ──────────────────────────────────────────────
# Router
# ──────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    page_home()
elif page == "setup":
    page_setup()
elif page == "interview":
    page_interview()
elif page == "results":
    page_results()
elif page == "history":
    page_history()
elif page == "tips":
    page_tips()

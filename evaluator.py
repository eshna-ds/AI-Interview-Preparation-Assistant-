"""
Answer Evaluation Engine
Uses TF-IDF, Cosine Similarity, and NLP heuristics
to evaluate interview answers.
"""

import re
import json
import math
from collections import Counter

# ─── Filler words for confidence detection ───────────────────────────────────
FILLER_WORDS = {
    "um", "uh", "like", "you know", "basically", "literally",
    "actually", "so", "right", "well", "hmm", "er", "ah",
    "kind of", "sort of", "i mean", "i think", "i guess", "maybe",
    "probably", "something like that", "and stuff"
}

POSITIVE_WORDS = {
    "definitely", "clearly", "specifically", "precisely", "exactly",
    "importantly", "essentially", "fundamentally", "primarily",
    "effectively", "efficiently", "significantly"
}


# ─── TF-IDF from scratch (no sklearn needed) ──────────────────────────────────

def tokenize(text: str) -> list[str]:
    """Lowercase, remove punctuation, split into words."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return [w for w in text.split() if len(w) > 2]


def compute_tf(tokens: list[str]) -> dict:
    """Term Frequency for a single document."""
    count = Counter(tokens)
    total = len(tokens) if tokens else 1
    return {word: freq / total for word, freq in count.items()}


def compute_idf(documents: list[list[str]]) -> dict:
    """Inverse Document Frequency across documents."""
    n = len(documents)
    idf = {}
    all_words = set(w for doc in documents for w in doc)
    for word in all_words:
        df = sum(1 for doc in documents if word in doc)
        idf[word] = math.log((n + 1) / (df + 1)) + 1
    return idf


def tfidf_vector(tokens: list[str], idf: dict) -> dict:
    """Compute TF-IDF vector for tokens."""
    tf = compute_tf(tokens)
    return {word: tf[word] * idf.get(word, 1) for word in tf}


def cosine_similarity(vec1: dict, vec2: dict) -> float:
    """Cosine similarity between two TF-IDF vectors."""
    common = set(vec1.keys()) & set(vec2.keys())
    if not common:
        return 0.0
    dot = sum(vec1[w] * vec2[w] for w in common)
    mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


# ─── Main Evaluation Functions ────────────────────────────────────────────────

def evaluate_relevance(user_answer: str, ideal_answer: str, keywords: list[str]) -> dict:
    """
    Score relevance using:
    1. Cosine similarity with ideal answer
    2. Keyword overlap
    Returns score 0-10 with breakdown.
    """
    user_tokens = tokenize(user_answer)
    ideal_tokens = tokenize(ideal_answer)

    # Build IDF on both documents
    idf = compute_idf([user_tokens, ideal_tokens])

    user_vec = tfidf_vector(user_tokens, idf)
    ideal_vec = tfidf_vector(ideal_tokens, idf)

    cosine_score = cosine_similarity(user_vec, ideal_vec)

    # Keyword overlap
    user_lower = user_answer.lower()
    matched_keywords = [kw for kw in keywords if kw.lower() in user_lower]
    keyword_ratio = len(matched_keywords) / max(len(keywords), 1)

    # Weighted blend: 60% cosine, 40% keywords
    raw_score = 0.6 * cosine_score + 0.4 * keyword_ratio
    score = round(min(10, raw_score * 12), 1)  # scale to 0-10

    return {
        "score": score,
        "cosine_similarity": round(cosine_score, 3),
        "keyword_ratio": round(keyword_ratio, 3),
        "matched_keywords": matched_keywords,
        "missing_keywords": [kw for kw in keywords if kw.lower() not in user_lower]
    }


def evaluate_completeness(user_answer: str, key_concepts: list[str]) -> dict:
    """
    Check if key concepts are addressed.
    Score based on how many core concepts appear.
    """
    user_lower = user_answer.lower()
    covered = []
    missing = []

    for concept in key_concepts:
        concept_words = tokenize(concept)
        # Check if at least half the concept words appear
        hits = sum(1 for w in concept_words if w in user_lower)
        if hits >= max(1, len(concept_words) * 0.5):
            covered.append(concept)
        else:
            missing.append(concept)

    ratio = len(covered) / max(len(key_concepts), 1)
    score = round(ratio * 10, 1)

    return {
        "score": score,
        "covered_concepts": covered,
        "missing_concepts": missing,
        "coverage_ratio": ratio
    }


def evaluate_clarity(user_answer: str) -> dict:
    """
    Assess grammar, structure, and clarity.
    Uses heuristics: sentence length, filler words, passive voice indicators.
    """
    sentences = [s.strip() for s in re.split(r'[.!?]+', user_answer) if s.strip()]
    words = user_answer.lower().split()

    if not words:
        return {"score": 0, "issues": ["Empty answer"], "word_count": 0}

    issues = []
    score = 10.0

    # Word count check
    word_count = len(words)
    if word_count < 15:
        issues.append("Answer is too short — aim for 40+ words")
        score -= 2.5
    elif word_count > 250:
        issues.append("Answer may be too long — aim for conciseness")
        score -= 1.0

    # Sentence length check
    avg_sentence_len = word_count / max(len(sentences), 1)
    if avg_sentence_len > 35:
        issues.append("Sentences are too long — break them up")
        score -= 1.0
    elif avg_sentence_len < 5 and len(sentences) > 1:
        issues.append("Sentences are very fragmented")
        score -= 0.5

    # Filler word detection
    answer_lower = user_answer.lower()
    found_fillers = [fw for fw in FILLER_WORDS if fw in answer_lower]
    if len(found_fillers) > 3:
        issues.append(f"Too many filler words: {', '.join(found_fillers[:5])}")
        score -= len(found_fillers) * 0.3

    # Starts with "I" too many times (sign of poor structure)
    i_starts = sum(1 for s in sentences if s.strip().lower().startswith("i "))
    if i_starts > len(sentences) * 0.6 and len(sentences) > 2:
        issues.append("Vary your sentence starters")
        score -= 0.5

    # Repetition check
    freq = Counter(words)
    repeated = [w for w, c in freq.most_common(5) if c > 3 and len(w) > 4]
    if repeated:
        issues.append(f"Repeated words detected: {', '.join(repeated[:3])}")
        score -= 0.5

    score = round(max(0, min(10, score)), 1)

    return {
        "score": score,
        "issues": issues if issues else ["Good clarity!"],
        "word_count": word_count,
        "sentence_count": len(sentences),
        "filler_words_found": found_fillers,
        "avg_sentence_length": round(avg_sentence_len, 1)
    }


def estimate_confidence(user_answer: str) -> dict:
    """
    Estimate confidence from text-based signals:
    - Filler word density
    - Hedging language
    - Assertiveness
    - Answer length vs hesitation ratio
    """
    words = user_answer.lower().split()
    total_words = max(len(words), 1)

    # Count filler words
    filler_count = sum(1 for fw in FILLER_WORDS if fw in user_answer.lower())
    filler_density = filler_count / total_words

    # Hedging phrases
    hedges = ["i think", "i guess", "maybe", "probably", "not sure", "i believe", "i feel like", "might be", "could be", "i'm not"]
    hedge_count = sum(1 for h in hedges if h in user_answer.lower())

    # Assertive phrases
    assertive = ["is", "are", "means", "refers to", "defined as", "works by", "used to", "ensures", "provides"]
    assertive_count = sum(1 for a in assertive if a in user_answer.lower())

    # Score calculation
    score = 10.0
    score -= filler_density * 20  # penalize fillers heavily
    score -= hedge_count * 1.5
    score += min(assertive_count * 0.3, 2.0)  # reward assertiveness

    # Length bonus: a fuller answer usually shows confidence
    if total_words >= 50:
        score += 0.5
    if total_words < 20:
        score -= 1.0

    score = round(max(1, min(10, score)), 1)

    level = "Low" if score < 4 else "Medium" if score < 7 else "High"

    return {
        "score": score,
        "level": level,
        "filler_density": round(filler_density * 100, 1),
        "hedge_count": hedge_count,
        "assertive_count": assertive_count
    }


def generate_recommendations(
    relevance: dict,
    completeness: dict,
    clarity: dict,
    question: str,
    ideal_answer: str
) -> list[str]:
    """Generate actionable improvement recommendations."""
    recommendations = []

    # Relevance-based
    if relevance["score"] < 6:
        recs = []
        if relevance["missing_keywords"]:
            recs.append(f"Include keywords: **{', '.join(relevance['missing_keywords'][:4])}**")
        recommendations.append(
            f"🎯 **Improve Relevance ({relevance['score']}/10):** Your answer drifts from the core topic. " +
            (recs[0] if recs else "Stay focused on the exact question asked.")
        )
    elif relevance["score"] < 8:
        if relevance["missing_keywords"]:
            recommendations.append(
                f"📌 **Add Keywords:** Strengthen your answer by mentioning: {', '.join(relevance['missing_keywords'][:3])}"
            )

    # Completeness-based
    if completeness["missing_concepts"]:
        recommendations.append(
            f"📚 **Missing Concepts:** Your answer didn't cover: **{', '.join(completeness['missing_concepts'])}**. "
            f"These are important parts of a complete answer."
        )

    # Clarity-based
    for issue in clarity["issues"]:
        if issue != "Good clarity!":
            recommendations.append(f"✍️ **Clarity:** {issue}")

    # Length-based
    if clarity["word_count"] < 30:
        recommendations.append(
            "📏 **Expand Your Answer:** A good interview answer is typically 50-100 words. "
            "Add an example or real-world use case."
        )

    # General encouragement if doing well
    if not recommendations:
        recommendations.append("✅ Excellent answer! You covered the topic well. Practice delivering it confidently.")

    return recommendations


# ─── Full Evaluation Pipeline ──────────────────────────────────────────────────

def evaluate_answer(question: str, user_answer: str, question_data: dict) -> dict:
    """
    Run full evaluation on a user's answer.
    Returns structured scores and recommendations.
    """
    ideal = question_data.get("ideal_answer", "")
    keywords = question_data.get("keywords", [])
    key_concepts = question_data.get("key_concepts", [])

    relevance = evaluate_relevance(user_answer, ideal, keywords)
    completeness = evaluate_completeness(user_answer, key_concepts)
    clarity = evaluate_clarity(user_answer)
    confidence = estimate_confidence(user_answer)
    recommendations = generate_recommendations(
        relevance, completeness, clarity, question, ideal
    )

    # Overall score (weighted average)
    overall = round(
        relevance["score"] * 0.35 +
        completeness["score"] * 0.30 +
        clarity["score"] * 0.20 +
        confidence["score"] * 0.15,
        1
    )

    return {
        "question": question,
        "overall_score": overall,
        "relevance": relevance,
        "completeness": completeness,
        "clarity": clarity,
        "confidence": confidence,
        "recommendations": recommendations,
        "ideal_answer": ideal
    }


if __name__ == "__main__":
    # Quick test
    question = "What is data cleaning?"
    answer = "Data cleaning is basically removing bad data and um, fixing errors in the dataset. It involves handling null values and removing duplicates I think."

    ref = {
        "keywords": ["missing values", "duplicates", "inconsistencies", "outliers", "formatting", "null"],
        "ideal_answer": "Data cleaning is the process of detecting and correcting corrupt or inaccurate records from a dataset.",
        "key_concepts": ["missing value handling", "duplicate removal", "outlier detection"]
    }

    result = evaluate_answer(question, answer, ref)
    print(json.dumps(result, indent=2))

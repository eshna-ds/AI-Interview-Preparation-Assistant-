"""
Interview Question Generator
Selects and randomizes questions from the dataset
based on role, level, and topic.
"""

import json
import random
import os


DATA_PATH = r"C:\Users\HP\projects\AI Interview Preparation Assistant\questions_dataset.py"


def load_questions() -> dict:
    with open(DATA_PATH, 'r') as f:
        return json.load(f)


def get_available_roles() -> list[str]:
    return list(load_questions().keys())


def get_available_levels(role: str) -> list[str]:
    questions = load_questions()
    if role in questions:
        return list(questions[role].keys())
    return []


def get_available_topics(role: str, level: str) -> list[str]:
    questions = load_questions()
    if role in questions and level in questions[role]:
        return list(questions[role][level].keys())
    return []


def generate_questions(
    role: str,
    level: str,
    topic: str = "All",
    count: int = 5
) -> list[str]:
    """
    Generate interview questions.
    If topic is 'All', picks from all topics for that role+level.
    Returns a list of `count` questions.
    """
    questions = load_questions()

    if role not in questions:
        return [f"No questions found for role: {role}"]

    if level not in questions[role]:
        return [f"No questions found for level: {level} under {role}"]

    level_data = questions[role][level]

    if topic == "All":
        # Collect from all topics
        all_questions = []
        for t, qs in level_data.items():
            all_questions.extend(qs)
    else:
        if topic not in level_data:
            return [f"No questions found for topic: {topic}"]
        all_questions = level_data[topic]

    # Shuffle and pick
    sampled = random.sample(all_questions, min(count, len(all_questions)))
    return sampled


def get_question_by_index(
    role: str,
    level: str,
    topic: str,
    index: int
) -> str:
    """Get a specific question by index."""
    questions = load_questions()
    try:
        q_list = questions[role][level][topic]
        return q_list[index % len(q_list)]
    except (KeyError, IndexError):
        return "Question not found."


def format_question_set(questions: list[str], role: str, level: str, topic: str) -> str:
    """Format questions as a readable string."""
    lines = [f"=== Interview Questions ===",
             f"Role: {role} | Level: {level} | Topic: {topic}",
             ""]
    for i, q in enumerate(questions, 1):
        lines.append(f"Q{i}. {q}")
    return "\n".join(lines)


# Sample question packs for quick demo
QUICK_PACKS = {
    "Data Analyst Starter": {
        "role": "Data Analyst",
        "level": "Beginner",
        "topic": "SQL",
        "count": 5
    },
    "Python Developer Core": {
        "role": "Python Developer",
        "level": "Intermediate",
        "topic": "Core Python",
        "count": 5
    },
    "ML Engineer Basics": {
        "role": "ML Engineer",
        "level": "Beginner",
        "topic": "ML Concepts",
        "count": 5
    }
}


if __name__ == "__main__":
    questions = generate_questions("Data Analyst", "Beginner", "SQL", count=5)
    print(format_question_set(questions, "Data Analyst", "Beginner", "SQL"))

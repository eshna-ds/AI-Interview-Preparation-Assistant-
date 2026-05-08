"""
Session Manager
Tracks interview session progress, scores, and history.
Saves sessions to JSON for persistence.
"""

import json
import os
import time
from datetime import datetime


SESSION_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'sessions')
os.makedirs(SESSION_DIR, exist_ok=True)


class InterviewSession:
    """Manages a single interview session."""

    def __init__(self, role: str, level: str, topic: str):
        self.session_id = f"{role}_{level}_{int(time.time())}"
        self.role = role
        self.level = level
        self.topic = topic
        self.start_time = datetime.now().isoformat()
        self.questions: list[str] = []
        self.answers: list[dict] = []
        self.current_index: int = 0
        self.completed: bool = False

    def add_question(self, question: str):
        self.questions.append(question)

    def record_answer(self, question: str, answer: str, evaluation: dict):
        self.answers.append({
            "question_index": self.current_index,
            "question": question,
            "answer": answer,
            "evaluation": evaluation,
            "timestamp": datetime.now().isoformat()
        })
        self.current_index += 1

    def get_summary(self) -> dict:
        """Calculate session summary statistics."""
        if not self.answers:
            return {"message": "No answers recorded yet."}

        scores = [a["evaluation"]["overall_score"] for a in self.answers]
        relevance = [a["evaluation"]["relevance"]["score"] for a in self.answers]
        completeness = [a["evaluation"]["completeness"]["score"] for a in self.answers]
        clarity = [a["evaluation"]["clarity"]["score"] for a in self.answers]
        confidence = [a["evaluation"]["confidence"]["score"] for a in self.answers]

        all_missing = []
        for a in self.answers:
            all_missing.extend(a["evaluation"]["completeness"]["missing_concepts"])

        return {
            "session_id": self.session_id,
            "role": self.role,
            "level": self.level,
            "topic": self.topic,
            "questions_attempted": len(self.answers),
            "total_questions": len(self.questions),
            "average_overall": round(sum(scores) / len(scores), 1),
            "average_relevance": round(sum(relevance) / len(relevance), 1),
            "average_completeness": round(sum(completeness) / len(completeness), 1),
            "average_clarity": round(sum(clarity) / len(clarity), 1),
            "average_confidence": round(sum(confidence) / len(confidence), 1),
            "best_score": max(scores),
            "lowest_score": min(scores),
            "topics_to_revise": list(set(all_missing)),
            "performance_grade": _grade(sum(scores) / len(scores)),
            "start_time": self.start_time,
            "end_time": datetime.now().isoformat()
        }

    def save(self):
        """Persist session to file."""
        path = os.path.join(SESSION_DIR, f"{self.session_id}.json")
        with open(path, 'w') as f:
            json.dump({
                "session_id": self.session_id,
                "role": self.role,
                "level": self.level,
                "topic": self.topic,
                "start_time": self.start_time,
                "questions": self.questions,
                "answers": self.answers,
                "current_index": self.current_index,
                "completed": self.completed,
                "summary": self.get_summary()
            }, f, indent=2)
        return path

    @classmethod
    def load(cls, session_id: str) -> 'InterviewSession':
        """Load session from file."""
        path = os.path.join(SESSION_DIR, f"{session_id}.json")
        with open(path) as f:
            data = json.load(f)
        session = cls(data["role"], data["level"], data["topic"])
        session.session_id = data["session_id"]
        session.questions = data["questions"]
        session.answers = data["answers"]
        session.current_index = data["current_index"]
        session.completed = data["completed"]
        return session


def _grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 9:
        return "A+ (Exceptional)"
    elif score >= 8:
        return "A (Excellent)"
    elif score >= 7:
        return "B (Good)"
    elif score >= 6:
        return "C (Needs Improvement)"
    elif score >= 5:
        return "D (Below Average)"
    else:
        return "F (Needs Significant Work)"


def list_sessions() -> list[dict]:
    """List all saved sessions."""
    sessions = []
    for f in os.listdir(SESSION_DIR):
        if f.endswith('.json'):
            with open(os.path.join(SESSION_DIR, f)) as fh:
                try:
                    data = json.load(fh)
                    sessions.append({
                        "id": data["session_id"],
                        "role": data["role"],
                        "level": data["level"],
                        "topic": data["topic"],
                        "date": data["start_time"][:10],
                        "score": data.get("summary", {}).get("average_overall", "N/A")
                    })
                except Exception:
                    pass
    return sorted(sessions, key=lambda x: x["date"], reverse=True)

from __future__ import annotations as _annotations
from dataclasses import dataclass, field
from pydantic import BaseModel
from pydantic_ai.messages import ModelMessage

@dataclass
class Question:
    text: str


@dataclass
class Answer:
    text: str


@dataclass
class State:
    history: list[ModelMessage] = field(default_factory=list)
    user_answers: list[Answer] = field(default_factory=list)
    feedback_history: list[Feedback] = field(default_factory=list)


class Feedback(BaseModel):
    text: str

class EvaluationResponse(BaseModel):
    score: int
    comments: str
    detailed_report: dict | None = None






class InterviewerResponse(BaseModel):
    question: str | None
    difficulty: str | None
    finished: bool

class FinalReport(BaseModel):
    session_id: str
    total_questions: int
    average_score: float
    overall_performance: str
    conversation_summary: str
    detailed_analysis: dict
    strengths: list[str]
    areas_for_improvement: list[str]
    recommendations: list[str]
    generated_at: str

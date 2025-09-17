from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from database import InterviewSession, Question, Answer, Evaluation
from models import EvaluationResponse

class DatabaseOperations:
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, session_id: str) -> InterviewSession:
        session = InterviewSession(
            id=session_id,
            created_at=datetime.now(datetime.timezone.utc),
            is_finished=False
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        print(f"Created new session in database: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        return self.db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    
    def save_question(self, session_id: str, question_text: str, difficulty: str = None, question_order: int = 1) -> Question:
        question = Question(
            session_id=session_id,
            question_text=question_text,
            difficulty=difficulty,
            question_order=question_order,
            created_at=datetime.now(datetime.timezone.utc)
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        print(f" Saved question to database: {question_text[:50]}...")
        return question
    
    def save_answer(self, session_id: str, question_id: int, answer_text: str) -> Answer:
        answer = Answer(
            session_id=session_id,
            question_id=question_id,
            answer_text=answer_text,
            created_at=datetime.now(datetime.timezone.utc)
        )
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        print(f"Saved answer to database: {answer_text[:50]}...")
        return answer
    
    def save_evaluation(self, session_id: str, question_id: int, answer_id: int, evaluation: EvaluationResponse) -> Evaluation:
        evaluation_record = Evaluation(
            session_id=session_id,
            question_id=question_id,
            answer_id=answer_id,
            score=evaluation.score,
            comments=evaluation.comments,
            detailed_report=evaluation.detailed_report,
            created_at=datetime.now(datetime.timezone.utc)
        )
        self.db.add(evaluation_record)
        self.db.commit()
        self.db.refresh(evaluation_record)
        print(f"saved evaluation to database: Score {evaluation.score}")
        return evaluation_record
    
    def finish_session(self, session_id: str, average_score: float = None, overall_performance: str = None):
        session = self.get_session(session_id)
        if session:
            session.is_finished = True
            session.finished_at = datetime.now(datetime.timezone.utc)
            session.total_questions = len(session.questions)
            if average_score is not None:
                session.average_score = average_score
            if overall_performance is not None:
                session.overall_performance = overall_performance
            self.db.commit()
            print(f" Marked session as finished: {session_id}")
    
    def get_session_transcript(self, session_id: str) -> dict:
        session = self.get_session(session_id)
        if not session:
            return None
        
        questions_data = []
        for question in session.questions:
            question_data = {
                "question_id": question.id,
                "question_text": question.question_text,
                "difficulty": question.difficulty,
                "question_order": question.question_order,
                "created_at": question.created_at.isoformat(),
                "answers": []
            }
            
            for answer in question.answers:
                answer_data = {
                    "answer_id": answer.id,
                    "answer_text": answer.answer_text,
                    "created_at": answer.created_at.isoformat(),
                    "evaluations": []
                }
                
                for evaluation in answer.evaluations:
                    evaluation_data = {
                        "evaluation_id": evaluation.id,
                        "score": evaluation.score,
                        "comments": evaluation.comments,
                        "detailed_report": evaluation.detailed_report,
                        "created_at": evaluation.created_at.isoformat()
                    }
                    answer_data["evaluations"].append(evaluation_data)
                
                question_data["answers"].append(answer_data)
            
            questions_data.append(question_data)
        
        return {
            "session_id": session.id,
            "created_at": session.created_at.isoformat(),
            "finished_at": session.finished_at.isoformat() if session.finished_at else None,
            "is_finished": session.is_finished,
            "total_questions": session.total_questions,
            "average_score": session.average_score,
            "overall_performance": session.overall_performance,
            "questions": questions_data
        }
    

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime

DATABASE_URL = "sqlite:///./interview_transcripts.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now())
    finished_at = Column(DateTime, nullable=True)
    is_finished = Column(Boolean, default=False)
    total_questions = Column(Integer, default=0)
    average_score = Column(Float, nullable=True)
    overall_performance = Column(String, nullable=True)
    
    questions = relationship("Question", back_populates="session")
    answers = relationship("Answer", back_populates="session")
    evaluations = relationship("Evaluation", back_populates="session")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, ForeignKey("interview_sessions.id"))
    question_text = Column(Text, nullable=False)
    difficulty = Column(String, nullable=True)
    question_order = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    
    session = relationship("InterviewSession", back_populates="questions")
    answers = relationship("Answer", back_populates="question")
    evaluations = relationship("Evaluation", back_populates="question")

class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, ForeignKey("interview_sessions.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    
    session = relationship("InterviewSession", back_populates="answers")
    question = relationship("Question", back_populates="answers")
    evaluations = relationship("Evaluation", back_populates="answer")

class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, ForeignKey("interview_sessions.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer_id = Column(Integer, ForeignKey("answers.id"))
    score = Column(Integer, nullable=False)
    comments = Column(Text, nullable=False)
    detailed_report = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    
    session = relationship("InterviewSession", back_populates="evaluations")
    question = relationship("Question", back_populates="evaluations")
    answer = relationship("Answer", back_populates="evaluations")

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    create_tables()
    print("✅ Database initialized successfully")

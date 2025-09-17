from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from pydantic_graph import Graph
from contextlib import asynccontextmanager
import uuid
from datetime import datetime
from interviewer import Interviewer
from evaluator import evaluator_agent, generate_interview_summary
from models import State, Answer, Feedback,  Question
from pdf_gen import generate_pdf_bytes
from database import get_db, init_database
from db_operations import DatabaseOperations

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    print("Database initialized successfully")
    yield
    print("Database closed successfully")

app = FastAPI(title="Mock Interview API", version="1.0.0" , lifespan=lifespan)
sessions = {}

class InterviewRequest(BaseModel):
    session_id: str = None
    user_input: str = None

interview_graph = Graph(nodes=(Interviewer,))

@app.get("/interview/{session_id}")
async def get_interview_state(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    state = session["state"]
    
    last_output = session["last_output"]
    if last_output:
        if hasattr(last_output, 'question'):
            message = last_output.question if last_output.question else "Waiting for your response..."
        else:
            message = last_output.text if hasattr(last_output, 'text') else "Waiting for your response..."
    else:
        message = "Waiting for your response..."
    
    return {
        "session_id": session_id,
        "message": message,
        "finished": session["finished"],
        "conversation_history": [
            {"type": "question", "content": f"Question {i+1}"} if i % 2 == 0 
            else {"type": "answer", "content": answer.text}
            for i, answer in enumerate(state.user_answers)
        ],
        "debug_info": {
            "total_answers": len(state.user_answers),
            "total_feedback": len(state.feedback_history),
            "total_questions": len(session.get("questions", []))
        }
    }

@app.post("/interview/")
async def interview(req: InterviewRequest, db = Depends(get_db)):
    
    if not req.session_id:
        print("🔄 Starting new interview...")
        session_id = str(uuid.uuid4())
        state = State()  # Fresh state with no answers or feedback
        print(f"Created new session: {session_id}")
        print(f"Initial state - Answers: {len(state.user_answers)}, Feedback: {len(state.feedback_history)}")
        
        print("Running interviewer node...")
        result = await interview_graph.run(Interviewer(), state=state)
        print(f"Interviewer result: {result.output}")
        
        if result.output.question:
            current_question = Question(text=result.output.question)
        else:
            current_question = Question(text="No question provided")
        
        db_ops = DatabaseOperations(db)
        
        db_session = db_ops.create_session(session_id)
        
        db_question = db_ops.save_question(
            session_id=session_id,
            question_text=result.output.question or "Introduction",
            difficulty=result.output.difficulty,
            question_order=1
        )
        
        sessions[session_id] = {
            "graph": interview_graph,
            "state": state,
            "finished": result.output.finished,
            "last_output": result.output,
            "current_question": current_question,
            "questions": [result.output],
            "db_ops": db_ops,
            "db_question_id": db_question.id
        }
        
        print(f"Session saved with {len(sessions)} total sessions")
        return {
            "session_id": session_id, 
            "message": result.output.question or "Interview started",
            "finished": result.output.finished,
            "conversation_history": []
        }
    
    if req.session_id not in sessions:
        print(f"❌ Session not found: {req.session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    
    print(f"Continuing session: {req.session_id}")
    session = sessions[req.session_id]
    state = session["state"]
    print(f"Current state - Answers: {len(state.user_answers)}, Feedback: {len(state.feedback_history)}")
    
    if req.user_input:
        print(f"User input received: {req.user_input[:50]}...")
        answer = Answer(req.user_input)
        state.user_answers.append(answer)
        print(f"Added answer. Total answers: {len(state.user_answers)}")
        
        current_question = session.get("current_question")
        if not current_question:
            print("No current question found in session")
            raise HTTPException(status_code=400, detail="No current question found")
        
        print(f"Current question: {current_question.text[:50] if current_question.text else 'None'}...")
        
        print("Evaluating answer...")
        
        evaluation_input = f"Question: {current_question.text}\nAnswer: {answer.text}"
        print(f"Evaluation input: {evaluation_input[:100]}...")
        
        evaluation_result = await evaluator_agent.run(
            evaluation_input,
            message_history=[],
        )
        state.history += evaluation_result.new_messages()
        print(f"Evaluation result: {evaluation_result.output}")
        
        evaluation_data = evaluation_result.output
        feedback = Feedback(text=evaluation_data.comments)
        state.feedback_history.append(feedback)
        
        if "evaluation_data" not in session:
            session["evaluation_data"] = []
        session["evaluation_data"].append(evaluation_data)
        
        db_ops = session.get("db_ops")
        if db_ops:
            db_answer = db_ops.save_answer(
                session_id=req.session_id,
                question_id=session.get("db_question_id"),
                answer_text=answer.text
            )
            
            db_ops.save_evaluation(
                session_id=req.session_id,
                question_id=session.get("db_question_id"),
                answer_id=db_answer.id,
                evaluation=evaluation_data
            )
        
        print(f"Saved feedback. Total feedback: {len(state.feedback_history)}")
        
        
        print("Asking next question...")
        next_result = await session["graph"].run(Interviewer(), state=state)
        session["last_output"] = next_result.output
        
        if next_result.output.question:
            current_question = Question(text=next_result.output.question)
        else:
            current_question = Question(text="No question provided")
        
        session["current_question"] = current_question
        session["questions"].append(next_result.output)
        
        if db_ops and next_result.output.question:
            db_question = db_ops.save_question(
                session_id=req.session_id,
                question_text=next_result.output.question,
                difficulty=next_result.output.difficulty,
                question_order=len(session["questions"])
            )
            session["db_question_id"] = db_question.id
        
        print(f" Next question: {next_result.output}")
        
        if next_result.output.finished:
            print(" Interview completed by interviewer")
            session["finished"] = True
            
            evaluation_data = session.get("evaluation_data", [])
            if evaluation_data:
                print(" Generating comprehensive interview summary...")
                final_report = await generate_interview_summary(
                    session_id=req.session_id,
                    state=state,
                    evaluation_data=evaluation_data
                )
                
                session["final_report"] = final_report
                
                if db_ops:
                    avg_score = sum(eval_data.score for eval_data in evaluation_data) / len(evaluation_data)
                    db_ops.finish_session(
                        session_id=req.session_id,
                        average_score=avg_score,
                        overall_performance=final_report.overall_performance
                    )
            return {
                "session_id": req.session_id,
                "message": next_result.output.question or "Interview completed",
                "finished": True,
                "conversation_history": [
                    {"type": "question", "content": f"Question {i+1}"} if i % 2 == 0 
                    else {"type": "answer", "content": answer.text}
                    for i, answer in enumerate(state.user_answers)
                ]
            }
        
        print(" Continuing interview...")
        return {
            "session_id": req.session_id,
            "message": next_result.output.question or "Next question",
            "finished": False,
            "conversation_history": [
                {"type": "question", "content": f"Question {i+1}"} if i % 2 == 0 
                else {"type": "answer", "content": answer.text}
                for i, answer in enumerate(state.user_answers)
            ]
        }
    return {
        "session_id": req.session_id,
        "message": "Waiting for your response...",
        "finished": session["finished"],
        "conversation_history": [
            {"type": "question", "content": f"Question {i+1}"} if i % 2 == 0 
            else {"type": "answer", "content": answer.text}
            for i, answer in enumerate(state.user_answers)
        ]
    }

@app.get("/report/{session_id}")
async def get_pdf_report(session_id: str):
    print(f" Generating PDF report for session: {session_id}")
    
    if session_id not in sessions:
        print(f" Session not found: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    state = session["state"]
    stored_questions = session.get("questions", [])
    
    print(f" Report data - Questions: {len(stored_questions)}, Answers: {len(state.user_answers)}, Feedback: {len(state.feedback_history)}")

    transcript = []
    
    for i, (question, answer, feedback) in enumerate(zip(
        stored_questions,
        state.user_answers,
        state.feedback_history
    ), 1):
        if hasattr(question, 'question'):
            question_text = question.question if question.question else f"Question {i}"
            print(f" Processing Q&A pair {i}: {question_text[:30]}...")
        else:
            question_text = question.text if question else f"Question {i}"
            print(f" Processing Q&A pair {i}: {question_text[:30]}...")
        
        transcript.append({
            "kind": "question",
            "payload": question_text
        })
        
        transcript.append({
            "kind": "answer", 
            "payload": answer.text
        })
        
        evaluation_data = session.get("evaluation_data", [])
        if i <= len(evaluation_data):
            eval_data = evaluation_data[i-1]
            transcript.append({
                "kind": "evaluation",
                "payload": {
                    "score": eval_data.score,
                    "comments": eval_data.comments,
                    "detailed_report": eval_data.detailed_report
                }
            })
        else:
            transcript.append({
                "kind": "evaluation",
                "payload": {
                    "score": 7.5,
                    "comments": feedback.text,
                    "detailed_report": {
                        "executive_summary": "Evaluation data not available",
                        "technical_competency": "Unable to assess",
                        "practical_application": "Unable to assess",
                        "communication_skills": "Unable to assess",
                        "strengths": ["Unable to assess"],
                        "areas_for_improvement": ["Unable to assess"],
                        "recommendations": ["Unable to assess"]
                    }
                }
            })

    evaluation_data = session.get("evaluation_data", [])
    print(f"Evaluation data: {evaluation_data}")
    if evaluation_data:
        avg_score = sum(eval_data.score for eval_data in evaluation_data) / len(evaluation_data)
        all_strengths = []
        all_weaknesses = []
        all_recommendations = []
        
        for eval_data in evaluation_data:
            if eval_data.detailed_report and "strengths" in eval_data.detailed_report:
                all_strengths.extend(eval_data.detailed_report["strengths"])
            if eval_data.detailed_report and "areas_for_improvement" in eval_data.detailed_report:
                all_weaknesses.extend(eval_data.detailed_report["areas_for_improvement"])
            if eval_data.detailed_report and "recommendations" in eval_data.detailed_report:
                all_recommendations.extend(eval_data.detailed_report["recommendations"])
        
        if not all_strengths and not all_weaknesses and not all_recommendations:
            print(" No detailed reports found, generating fallback summary...")
            high_scores = [eval_data for eval_data in evaluation_data if eval_data.score >= 7]
            low_scores = [eval_data for eval_data in evaluation_data if eval_data.score < 6]
            
            if high_scores:
                all_strengths = ["Strong understanding of Excel concepts", "Good practical application skills", "Clear communication of technical concepts"]
            if low_scores:
                all_weaknesses = ["Need to provide more detailed explanations", "Could benefit from more specific examples", "Consider expanding knowledge of advanced features"]
            
            all_recommendations = [
                "Practice explaining Excel concepts with specific examples",
                "Focus on real-world application scenarios",
                "Consider advanced Excel training for complex data analysis"
            ]
        
        if avg_score >= 8:
            performance_level = "Excellent"
            performance_desc = "Outstanding Excel proficiency with advanced understanding"
        elif avg_score >= 6:
            performance_level = "Good"
            performance_desc = "Solid Excel skills with room for growth"
        else:
            performance_level = "Needs Improvement"
            performance_desc = "Basic understanding with significant areas for development"
        
        summary = f"""
Interview Summary:
- Total Questions: {len(state.user_answers)}
- Average Score: {avg_score:.1f}/10
- Overall Performance: {performance_level} - {performance_desc}
- Score Range: {min(eval_data.score for eval_data in evaluation_data)}-{max(eval_data.score for eval_data in evaluation_data)}

Key Strengths:
{chr(10).join(f"• {strength}" for strength in list(set(all_strengths))[:5]) if all_strengths else "• Unable to assess"}

Areas for Improvement:
{chr(10).join(f"• {weakness}" for weakness in list(set(all_weaknesses))[:5]) if all_weaknesses else "• Unable to assess"}

Recommendations:
{chr(10).join(f"• {rec}" for rec in list(set(all_recommendations))[:5]) if all_recommendations else "• Unable to assess"}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    else:
        summary = f"""
Interview Summary:
- Total Questions: {len(state.user_answers)}
- Session ID: {session_id}
- Overall Performance: Unable to assess (evaluation data missing)
- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    print(f" Created transcript with {len(transcript)} items")
    print(" Generating PDF...")

    final_report = session.get("final_report")
    if not final_report:
        print(" No final report available for PDF generation")
        raise HTTPException(status_code=400, detail="Final report not available")
    
    print(f"Using final report for PDF generation")
    

    final_report_dict = {
        "session_id": final_report.session_id,
        "total_questions": final_report.total_questions,
        "average_score": final_report.average_score,
        "overall_performance": final_report.overall_performance,
        "conversation_summary": final_report.conversation_summary,
        "detailed_analysis": final_report.detailed_analysis,
        "strengths": final_report.strengths,
        "areas_for_improvement": final_report.areas_for_improvement,
        "recommendations": final_report.recommendations,
        "generated_at": final_report.generated_at
    }
    
    pdf_buffer = generate_pdf_bytes(session_id, final_report_dict)
    print(" PDF generated successfully")
    
    pdf_bytes = pdf_buffer.getvalue()
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=excel_interview_report_{session_id[:8]}.pdf"}
    )

@app.get("/transcript/{session_id}")
async def get_transcript(session_id: str, db = Depends(get_db)):
    db_ops = DatabaseOperations(db)
    transcript = db_ops.get_session_transcript(session_id)
    
    if not transcript:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return transcript

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

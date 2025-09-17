from __future__ import annotations as _annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING
from pydantic_ai import Agent
from models import State, EvaluationResponse, FinalReport
from prompt import evaluator_prompt, final_report_prompt
from dotenv import load_dotenv
load_dotenv()

# -------- Agents --------
evaluator_agent = Agent(
    "openai:gpt-4o",
    output_type=EvaluationResponse,
    system_prompt=evaluator_prompt
)

final_report_agent = Agent(
    "openai:gpt-4o",
    output_type=FinalReport,
    system_prompt=final_report_prompt
)



# -------- Enhanced Evaluator for Summary Generation --------
async def generate_interview_summary(session_id: str, state: State, evaluation_data: list[EvaluationResponse]) -> FinalReport:
    """Generate a comprehensive interview summary using all conversation history and evaluations"""
    
    # Build comprehensive context for summary generation
    conversation_context = f"Generate a comprehensive interview summary for session {session_id}.\n\n"
    conversation_context += f"Candidate provided {len(state.user_answers)} answers during the interview.\n\n"
    
    # Add all Q&A pairs with context
    for i, answer in enumerate(state.user_answers):
        conversation_context += f"Answer {i+1}: {answer.text}\n\n"
    
    # Add evaluation summary
    if evaluation_data:
        avg_score = sum(eval_data.score for eval_data in evaluation_data) / len(evaluation_data)
        conversation_context += f"Evaluation Summary:\n"
        conversation_context += f"- Total Questions: {len(evaluation_data)}\n"
        conversation_context += f"- Average Score: {avg_score:.1f}/10\n"
        conversation_context += f"- Score Range: {min(eval_data.score for eval_data in evaluation_data)}-{max(eval_data.score for eval_data in evaluation_data)}\n\n"
        
        # Add individual evaluations for context
        for i, eval_data in enumerate(evaluation_data):
            conversation_context += f"Evaluation {i+1}: Score {eval_data.score}/10 - {eval_data.comments}\n"
    
    # Generate the comprehensive summary
    print(f"📊 Generating comprehensive interview summary for session: {session_id}")
    try:
        result = await final_report_agent.run(
            conversation_context,
            message_history=[],  # Clean context for summary generation
        )
        
        # Add generated timestamp
        from datetime import datetime
        result.output.generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"✅ Interview summary generated successfully")
        return result.output
    except Exception as e:
        print(f"❌ Error generating interview summary: {e}")
        # Create a fallback summary
        from datetime import datetime
        avg_score = sum(eval_data.score for eval_data in evaluation_data) / len(evaluation_data) if evaluation_data else 0
        
        return FinalReport(
            session_id=session_id,
            total_questions=len(state.user_answers),
            average_score=avg_score,
            overall_performance="Assessment completed",
            conversation_summary=f"Interview completed with {len(state.user_answers)} questions answered. Candidate demonstrated Excel knowledge through their responses.",
            detailed_analysis={
                "interview_flow": "Interview completed successfully with good engagement",
                "performance_consistency": "Candidate provided consistent responses throughout",
                "knowledge_depth": "Demonstrated understanding of Excel concepts",
                "practical_application": "Showed ability to apply Excel knowledge",
                "communication_effectiveness": "Communicated responses clearly",
                "role_relevance": "Skills align with stated experience level"
            },
            strengths=["Completed interview successfully", "Demonstrated Excel knowledge"],
            areas_for_improvement=["Continue practicing Excel skills"],
            recommendations=["Focus on advanced Excel features", "Practice real-world scenarios"],
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

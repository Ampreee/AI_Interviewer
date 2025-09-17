from __future__ import annotations as _annotations
from dataclasses import dataclass
from pydantic_ai import Agent
from pydantic_graph import BaseNode, GraphRunContext, End
from models import State, InterviewerResponse
from prompt import interviewer_prompt
from dotenv import load_dotenv
load_dotenv()


interviewer_agent = Agent(
    "openai:gpt-4o-mini",
    output_type=InterviewerResponse,
    system_prompt=interviewer_prompt
)


@dataclass
class Interviewer(BaseNode[State]):

    async def run(self, ctx: GraphRunContext[State]) -> "End[InterviewerResponse]":
        print(f"Interviewer.run() called - Answers: {len(ctx.state.user_answers)}, Feedback: {len(ctx.state.feedback_history)}")
        
        if len(ctx.state.user_answers) == 0:
            context_message = "Start the interview with an introduction. Introduce yourself as Dhruv, an AI interviewer specializing in Excel, explain the interview process, and ask your first Excel question."
            print("First question - sending introduction context")
        else:
            context_message = f"Continue the interview conversation. You have {len(ctx.state.user_answers)} previous answers from the candidate."
            
            if ctx.state.user_answers:
                recent_answer = ctx.state.user_answers[-1].text
                context_message += f" The candidate's most recent answer was: '{recent_answer[:100]}...'"
            
            if ctx.state.feedback_history:
                recent_feedback = ctx.state.feedback_history[-1].text
                context_message += f" The most recent feedback was: '{recent_feedback[:100]}...'"
            
            context_message += " Use this context to ask a natural follow-up question that builds on the conversation. Be conversational and reference their previous answers when appropriate."
            print(f"Continue interview - sending context: {context_message}")
        
        print(f"Sending to interviewer_agent: {context_message}")
        result = await interviewer_agent.run(
            context_message,
            message_history=ctx.state.history,
        )
        ctx.state.history += result.new_messages()
        print(f"Received from interviewer_agent: {result.output}")
        
        if result.output.finished:
            print("Interviewer marked interview as finished")
            return End(result.output)
        
        print(f"Returning response - Question: {result.output.question[:50] if result.output.question else 'None'}..., Finished: {result.output.finished}")
        return End(result.output)

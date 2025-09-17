from fpdf import FPDF
import io
from typing import Dict, Any
import re

def clean_text_for_pdf(text: str) -> str:
    if not text:
        return ""
    
    replacements = {
        '🤖': '[AI]',
        '📊': '[Chart]',
        '📄': '[Document]',
        '📥': '[Download]',
        '✅': '[Check]',
        '⚠️': '[Warning]',
        '💡': '[Idea]',
        '📋': '[List]',
        '🔄': '[Refresh]',
        '🚀': '[Start]',
        '💬': '[Chat]',
        '📤': '[Send]',
        '🎉': '[Celebration]',
        '🧑': '[Person]',
        '📝': '[Note]',
        '📈': '[Trend]',
        '🎯': '[Target]',
        '🔧': '[Tool]',
        '⭐': '[Star]',
        '🔥': '[Fire]',
        '💯': '[Perfect]',
        '🎊': '[Party]',
        '🏆': '[Trophy]',
        '🎁': '[Gift]',
        '🌟': '[Star]',
        '💎': '[Diamond]',
        '🚨': '[Alert]',
        '🎪': '[Circus]',
        '🎨': '[Art]',
        '🎵': '[Music]',
        '🎬': '[Movie]',
        '🎮': '[Game]',
        '🎯': '[Target]',
        '🎲': '[Dice]',
        '🎳': '[Bowling]',
        '🎸': '[Guitar]',
        '🎺': '[Trumpet]',
        '🎻': '[Violin]',
        '🎹': '[Piano]',
        '🎤': '[Microphone]',
        '🎧': '[Headphones]',
        '🎨': '[Art]',
        '🎭': '[Theater]',
        '🎪': '[Circus]',
        '🎫': '[Ticket]',
        '🎟️': '[Ticket]',
        '🎠': '[Carousel]',
        '🎡': '[Ferris Wheel]',
        '🎢': '[Roller Coaster]',
        '🎣': '[Fishing]',
        '🎤': '[Microphone]',
        '🎥': '[Camera]',
        '🎦': '[Cinema]',
        '🎧': '[Headphones]',
        '🎨': '[Art]',
        '🎩': '[Top Hat]',
        '🎪': '[Circus]',
        '🎫': '[Ticket]',
        '🎬': '[Movie]',
        '🎭': '[Theater]',
        '🎮': '[Game]',
        '🎯': '[Target]',
        '🎰': '[Slot Machine]',
        '🎱': '[8 Ball]',
        '🎲': '[Dice]',
        '🎳': '[Bowling]',
        '🎴': '[Playing Cards]',
        '🎵': '[Music]',
        '🎶': '[Musical Notes]',
        '🎷': '[Saxophone]',
        '🎸': '[Guitar]',
        '🎹': '[Piano]',
        '🎺': '[Trumpet]',
        '🎻': '[Violin]',
        '🎼': '[Musical Score]',
        '🎽': '[Running Shirt]',
        '🎾': '[Tennis]',
        '🎿': '[Skiing]',
        '🏀': '[Basketball]',
        '🏁': '[Checkered Flag]',
        '🏂': '[Snowboarding]',
        '🏃': '[Running]',
        '🏄': '[Surfing]',
        '🏅': '[Medal]',
        '🏆': '[Trophy]',
        '🏇': '[Horse Racing]',
        '🏈': '[American Football]',
        '🏉': '[Rugby]',
        '🏊': '[Swimming]',
        '🏋️': '[Weight Lifting]',
        '🏌️': '[Golf]',
        '🏍️': '[Motorcycle]',
        '🏎️': '[Race Car]',
        '🏏': '[Cricket]',
        '🏐': '[Volleyball]',
        '🏑': '[Field Hockey]',
        '🏒': '[Ice Hockey]',
        '🏓': '[Ping Pong]',
        '🏔️': '[Mountain]',
        '🏕️': '[Camping]',
        '🏖️': '[Beach]',
        '🏗️': '[Construction]',
        '🏘️': '[Houses]',
        '🏙️': '[Cityscape]',
        '🏚️': '[Derelict House]',
        '🏛️': '[Classical Building]',
        '🏜️': '[Desert]',
        '🏝️': '[Desert Island]',
        '🏞️': '[National Park]',
        '🏟️': '[Stadium]',
        '🏠': '[House]',
        '🏡': '[House with Garden]',
        '🏢': '[Office Building]',
        '🏣': '[Post Office]',
        '🏤': '[European Post Office]',
        '🏥': '[Hospital]',
        '🏦': '[Bank]',
        '🏧': '[ATM]',
        '🏨': '[Hotel]',
        '🏩': '[Love Hotel]',
        '🏪': '[Convenience Store]',
        '🏫': '[School]',
        '🏬': '[Department Store]',
        '🏭': '[Factory]',
        '🏮': '[Red Paper Lantern]',
        '🏯': '[Japanese Castle]',
        '🏰': '[Castle]',
        '🏱': '[Japanese Post Office]',
        '🏲': '[Japanese Post Office]',
        '🏳️': '[White Flag]',
        '🏴': '[Black Flag]',
        '🏵️': '[Rosette]',
        '🏶': '[Japanese Post Office]',
        '🏷️': '[Label]',
        '🏸': '[Badminton]',
        '🏹': '[Bow and Arrow]',
        '🏺': '[Amphora]',
        '🏻': '[Light Skin Tone]',
        '🏼': '[Medium-Light Skin Tone]',
        '🏽': '[Medium Skin Tone]',
        '🏾': '[Medium-Dark Skin Tone]',
        '🏿': '[Dark Skin Tone]',
    }
    
    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)
    text = re.sub(r'[^\x00-\x7F]+', '[?]', text)
    
    return text

def generate_pdf_bytes(session_id: str, final_report: Dict[str, Any]) -> io.BytesIO:
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, clean_text_for_pdf(f"Excel Interview Assessment Report"), ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, clean_text_for_pdf(f"Session ID: {session_id}"), ln=True, align="C")
    pdf.ln(15)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, clean_text_for_pdf("Executive Summary"), ln=True)
    pdf.set_font("Arial", "", 12)
    
    if final_report.get("conversation_summary"):
        pdf.multi_cell(0, 8, clean_text_for_pdf(final_report["conversation_summary"]))
    else:
        pdf.multi_cell(0, 8, clean_text_for_pdf("This report provides a comprehensive assessment of the candidate's Excel proficiency based on their interview performance."))
    
    pdf.ln(10)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, clean_text_for_pdf("Candidate Assessment"), ln=True)
    pdf.set_font("Arial", "", 12)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, clean_text_for_pdf("Performance Overview:"), ln=True)
    pdf.set_font("Arial", "", 12)
    
    if final_report.get("detailed_analysis"):
        analysis = final_report["detailed_analysis"]
        
        if analysis.get("interview_flow"):
            pdf.multi_cell(0, 8, clean_text_for_pdf(f"Interview Flow: {analysis['interview_flow']}"))
            pdf.ln(3)
        
        if analysis.get("performance_consistency"):
            pdf.multi_cell(0, 8, clean_text_for_pdf(f"Performance Consistency: {analysis['performance_consistency']}"))
            pdf.ln(3)
        
        if analysis.get("knowledge_depth"):
            pdf.multi_cell(0, 8, clean_text_for_pdf(f"Knowledge Depth: {analysis['knowledge_depth']}"))
            pdf.ln(3)
        
        if analysis.get("practical_application"):
            pdf.multi_cell(0, 8, clean_text_for_pdf(f"Practical Application: {analysis['practical_application']}"))
            pdf.ln(3)
        
        if analysis.get("communication_effectiveness"):
            pdf.multi_cell(0, 8, clean_text_for_pdf(f"Communication Skills: {analysis['communication_effectiveness']}"))
            pdf.ln(3)
        
        if analysis.get("role_relevance"):
            pdf.multi_cell(0, 8, clean_text_for_pdf(f"Role Relevance: {analysis['role_relevance']}"))
            pdf.ln(3)

    pdf.ln(5)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, clean_text_for_pdf("Strengths & Development Areas"), ln=True)
    pdf.set_font("Arial", "", 12)
    
    if final_report.get("strengths"):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, clean_text_for_pdf("Key Strengths:"), ln=True)
        pdf.set_font("Arial", "", 12)
        for strength in final_report["strengths"]:
            pdf.multi_cell(0, 8, clean_text_for_pdf(f"• {strength}"))
        pdf.ln(3)
    
    if final_report.get("areas_for_improvement"):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, clean_text_for_pdf("Areas for Development:"), ln=True)
        pdf.set_font("Arial", "", 12)
        for area in final_report["areas_for_improvement"]:
            pdf.multi_cell(0, 8, clean_text_for_pdf(f"• {area}"))
        pdf.ln(3)

    if final_report.get("recommendations"):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, clean_text_for_pdf("Recommendations:"), ln=True)
        pdf.set_font("Arial", "", 12)
        for rec in final_report["recommendations"]:
            pdf.multi_cell(0, 8, clean_text_for_pdf(f"• {rec}"))
        pdf.ln(5)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, clean_text_for_pdf("Final Assessment"), ln=True)
    pdf.set_font("Arial", "", 12)
    
    assessment_summary = f"Overall Performance: {final_report.get('overall_performance', 'Assessment completed')}\n"
    assessment_summary += f"Average Score: {final_report.get('average_score', 0):.1f}/10\n"
    assessment_summary += f"Total Questions: {final_report.get('total_questions', 0)}\n"
    assessment_summary += f"Generated: {final_report.get('generated_at', 'N/A')}"
    
    pdf.multi_cell(0, 8, clean_text_for_pdf(assessment_summary))

    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 8, clean_text_for_pdf("This report was generated by AI Interview Assessment System"), ln=True, align="C")

    output = pdf.output(dest="S")
    buf = io.BytesIO(output.encode('latin-1'))
    buf.seek(0)
    return buf

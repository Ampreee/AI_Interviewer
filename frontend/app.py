import streamlit as st
import requests
import os
import json

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Interviewer", page_icon="📊")
st.title("📊 AI-Powered Interviewer")
st.markdown("Get ready for an AI-powered interview experience!")

if "session_id" not in st.session_state:
    st.session_state.session_id = None
    st.session_state.finished = False
    st.session_state.current_message = ""

def make_api_call(endpoint, data=None, method="POST"):
    try:
        if method.upper() == "GET":
            response = requests.get(f"{BACKEND}{endpoint}")
        else:
            response = requests.post(f"{BACKEND}{endpoint}", json=data)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return None, f"Connection Error: {str(e)}"

if st.session_state.session_id is None:
    st.markdown("### Welcome to the Excel Interview!")
    st.markdown("This AI-powered interviewer will ask you Excel-related questions to test your knowledge.")
    st.markdown("**Instructions:**")
    st.markdown("- Answer each question to the best of your ability")
    
    if st.button("🚀 Start Interview", type="primary"):
        with st.spinner("Starting interview..."):
            data, error = make_api_call("/interview/", {})
            
            if error:
                st.error(error)
            else:
                st.session_state.session_id = data["session_id"]
                st.session_state.current_message = data["message"]
                st.session_state.finished = data["finished"]
                st.rerun()

else:
    status = "✅ Complete" if st.session_state.finished else "🔄 In Progress"
    st.info(f"**Status:** {status}")
    st.markdown("---")
    
    if st.session_state.current_message:
        st.markdown("### 🤖 Interviewer's Question")
        st.info(st.session_state.current_message)
    

    if not st.session_state.finished:
        st.markdown("### 💬 Your Response")
        
        if "input_key" not in st.session_state:
            st.session_state.input_key = 0
        
        user_input = st.text_area(
            "Type your answer here:", 
            height=150,
            placeholder="Enter your detailed answer...",
            key=f"user_input_{st.session_state.input_key}"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_btn = st.button("📤 Submit Answer", type="primary")
        
        if submit_btn and user_input.strip():
            with st.spinner("Processing your answer..."):
                data, error = make_api_call("/interview/", {
                    "session_id": st.session_state.session_id,
                    "user_input": user_input
                })
                
                if error:
                    st.error(error)
                else:
                    st.session_state.current_message = data["message"]
                    st.session_state.finished = data["finished"]
                    
                    st.session_state.input_key += 1
                    st.rerun()
        elif submit_btn and not user_input.strip():
            st.warning("Please enter your answer before submitting.")
            
    else:
        st.success("🎉 Interview Complete!")
        st.markdown("Thank you for participating in the Excel mock interview!")
        
        st.markdown("### 📊 Interview Summary")
        st.markdown("Thank you for completing the Excel mock interview!")
        
        st.markdown("### 📄 Interview Reports")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Generate PDF Report", type="primary"):
                with st.spinner("Generating PDF report..."):
                    try:
                        response = requests.get(f"{BACKEND}/report/{st.session_state.session_id}")
                        if response.status_code == 200:
                            st.download_button(
                                "📥 Download PDF Report",
                                data=response.content,
                                file_name="excel_interview_report.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.error(f"Error generating report: {response.text}")
                    except Exception as e:
                        st.error(f"Error downloading report: {str(e)}")
        
        with col2:
            if st.button("📋 Get Transcript"):
                with st.spinner("Fetching transcript..."):
                    try:
                        response = requests.get(f"{BACKEND}/transcript/{st.session_state.session_id}")
                        if response.status_code == 200:
                            transcript_data = response.json()
                            transcript_json = json.dumps(transcript_data, indent=2)
                            st.download_button(
                                "📥 Download Transcript",
                                data=transcript_json,
                                file_name="interview_transcript.json",
                                mime="application/json"
                            )
                        else:
                            st.error(f"Error fetching transcript: {response.text}")
                    except Exception as e:
                        st.error(f"Error downloading transcript: {str(e)}")
        
        with col3:
            if st.button("🔄 Start New Interview"):
                for key in ["session_id", "finished", "current_message"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
